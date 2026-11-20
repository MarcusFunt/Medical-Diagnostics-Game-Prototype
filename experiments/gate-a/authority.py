"""SQLite-backed synthetic case authority used only by the Gate A fixture."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Mapping, Sequence

from port import Actor, ArtifactAccess, ClinicalEvent, Command, Projection, Receipt

MAX_CLINICAL_TIME_MS = 2**31 - 1
MAX_SAME_TIME_EVENTS = 1000
SCHEMA_VERSION = 1


def _empty_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_revision": 0,
        "publication_count": 0,
        "cases": {},
        "plays": {},
        "catalog_events": [],
    }


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fingerprint(command: Command) -> str:
    content = {
        "target_id": command.target_id,
        "expected_revision": command.expected_revision,
        "kind": command.kind,
        "payload": dict(command.payload),
    }
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


class SQLiteAuthority:
    """Small, transactional implementation of the public GateAPort."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS authority_state ("
                "singleton INTEGER PRIMARY KEY CHECK (singleton = 1), "
                "payload TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS command_receipts ("
                "actor_id TEXT NOT NULL, command_id TEXT NOT NULL, "
                "fingerprint TEXT NOT NULL, receipt TEXT NOT NULL, "
                "PRIMARY KEY (actor_id, command_id))"
            )
            connection.execute(
                "INSERT OR IGNORE INTO authority_state(singleton, payload) VALUES(1, ?)",
                (_canonical_json(_empty_state()),),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _load_state(connection: sqlite3.Connection) -> dict[str, Any]:
        row = connection.execute(
            "SELECT payload FROM authority_state WHERE singleton = 1"
        ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("authority state row is missing")
        return json.loads(row["payload"])

    @staticmethod
    def _save_state(connection: sqlite3.Connection, state: Mapping[str, Any]) -> None:
        connection.execute(
            "UPDATE authority_state SET payload = ? WHERE singleton = 1",
            (_canonical_json(state),),
        )

    def execute(self, actor: Actor, command: Command) -> Receipt:
        """Authorize, deduplicate, revise and commit a single command atomically."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            state = self._load_state(connection)

            if not self._authorized_command(state, actor, command):
                connection.rollback()
                return Receipt("forbidden", command.target_id)

            fingerprint = _fingerprint(command)
            existing = connection.execute(
                "SELECT fingerprint, receipt FROM command_receipts "
                "WHERE actor_id = ? AND command_id = ?",
                (actor.actor_id, command.command_id),
            ).fetchone()
            if existing is not None:
                connection.rollback()
                if existing["fingerprint"] != fingerprint:
                    return Receipt("idempotency_conflict", command.target_id)
                original = json.loads(existing["receipt"])
                return Receipt(
                    status=original["status"],
                    target_id=original["target_id"],
                    revision=original.get("revision"),
                    data=original.get("data", {}),
                    replayed=True,
                )

            current_revision = self._current_revision(state, command.target_id)
            if command.target_id in state["plays"]:
                if command.expected_revision != current_revision:
                    connection.rollback()
                    return Receipt("revision_conflict", command.target_id, current_revision)
            elif command.target_id == "catalog":
                if command.expected_revision is not None and command.expected_revision != current_revision:
                    connection.rollback()
                    return Receipt("revision_conflict", command.target_id, current_revision)

            receipt, changed = self._dispatch(state, actor, command)
            if changed:
                self._save_state(connection, state)
            if receipt.status in {"committed", "generation_failed"}:
                connection.execute(
                    "INSERT INTO command_receipts(actor_id, command_id, fingerprint, receipt) "
                    "VALUES(?, ?, ?, ?)",
                    (
                        actor.actor_id,
                        command.command_id,
                        fingerprint,
                        _canonical_json(
                            {
                                "status": receipt.status,
                                "target_id": receipt.target_id,
                                "revision": receipt.revision,
                                "data": dict(receipt.data),
                            }
                        ),
                    ),
                )
            connection.commit()
            return receipt
        except sqlite3.Error:
            if connection.in_transaction:
                connection.rollback()
            return Receipt("storage_failed", command.target_id)
        finally:
            connection.close()

    @staticmethod
    def _current_revision(state: Mapping[str, Any], target_id: str) -> int:
        if target_id == "catalog":
            return int(state["catalog_revision"])
        play = state["plays"].get(target_id)
        if play is not None:
            return int(play["revision"])
        return 0

    @staticmethod
    def _authorized_command(state: Mapping[str, Any], actor: Actor, command: Command) -> bool:
        if command.kind == "generate_case":
            return command.target_id == "catalog" and actor.role in {"learner", "authority"}
        if command.kind == "start_playthrough":
            case_id = command.target_id.removeprefix("case:")
            return (
                command.target_id.startswith("case:")
                and case_id in state["cases"]
                and actor.role == "learner"
            )
        play = state["plays"].get(command.target_id)
        if play is None:
            return False
        if actor.role == "authority" and command.kind in {"release_result"}:
            return True
        return actor.role == "learner" and actor.actor_id == play["owner_id"]

    def _dispatch(
        self, state: dict[str, Any], actor: Actor, command: Command
    ) -> tuple[Receipt, bool]:
        if command.kind == "generate_case":
            return self._generate_case(state, command)
        if command.kind == "start_playthrough":
            return self._start_playthrough(state, actor, command)
        play = state["plays"].get(command.target_id)
        if play is None:
            return Receipt("not_found", command.target_id), False
        if play["status"] != "active":
            return Receipt("encounter_complete", command.target_id, play["revision"]), False
        if command.kind == "order_tests":
            return self._order_tests(play, command)
        if command.kind == "wait":
            return self._wait(play, command)
        return Receipt("unsupported_command", command.target_id, play["revision"]), False

    def _generate_case(
        self, state: dict[str, Any], command: Command
    ) -> tuple[Receipt, bool]:
        case_id = str(command.payload.get("case_id", ""))
        if not case_id:
            return Receipt("invalid_command", command.target_id), False
        if not command.payload.get("mandatory_evidence", False):
            state["generation_attempts"] = state.get("generation_attempts", []) + [
                {"case_id": case_id, "status": "generation_failed", "reason": "mandatory_evidence_missing"}
            ]
            state["catalog_revision"] += 1
            return (
                Receipt(
                    "generation_failed",
                    command.target_id,
                    state["catalog_revision"],
                    {"reason": "mandatory_evidence_missing"},
                ),
                True,
            )
        if case_id in state["cases"]:
            return Receipt("case_exists", command.target_id, state["catalog_revision"]), False

        version_id = f"{case_id}:v1"
        state["cases"][case_id] = {
            "case_id": case_id,
            "case_version_id": version_id,
            "schema_version": 1,
            "initial_state": {"x": 1},
            "trajectory": [{"time_ms": 5000, "x": 2}, {"time_ms": 11000, "x": 3}],
            "reference_key": ["DX-A"],
            "published": True,
        }
        state["catalog_revision"] += 1
        state["publication_count"] += 1
        state.setdefault("generation_attempts", []).append(
            {"case_id": case_id, "status": "published", "case_version_id": version_id}
        )
        event = {
            "event_id": f"catalog-{state['catalog_revision']}",
            "clinical_time_ms": 0,
            "event_sequence": state["catalog_revision"],
            "phase": 6,
            "kind": "case_published",
            "subject_id": case_id,
            "payload": {"case_version_id": version_id},
        }
        state["catalog_events"].append(event)
        return (
            Receipt(
                "committed",
                command.target_id,
                state["catalog_revision"],
                {"case_id": case_id, "case_version_id": version_id},
            ),
            True,
        )

    def _start_playthrough(
        self, state: dict[str, Any], actor: Actor, command: Command
    ) -> tuple[Receipt, bool]:
        case_id = command.target_id.removeprefix("case:")
        playthrough_id = str(command.payload.get("playthrough_id", ""))
        if not playthrough_id or case_id not in state["cases"]:
            return Receipt("invalid_command", command.target_id), False
        if playthrough_id in state["plays"]:
            return Receipt("playthrough_exists", command.target_id), False
        case = state["cases"][case_id]
        play = {
            "playthrough_id": playthrough_id,
            "owner_id": actor.actor_id,
            "case_id": case_id,
            "case_version_id": case["case_version_id"],
            "revision": 0,
            "elapsed_ms": 0,
            "status": "active",
            "state": dict(case["initial_state"]),
            "orders": {},
            "acquisitions": {},
            "results": {},
            "disclosures": [],
            "submission": None,
            "debrief": None,
            "reviews": [],
            "schedule": [],
            "next_schedule_ordinal": 1,
            "next_event_sequence": 1,
            "events": [],
            "continuation": {"schema_version": 1, "last_committed_ms": 0},
        }
        self._append_event(
            play,
            clinical_time_ms=0,
            phase=1,
            kind="case_initialized",
            subject_id=playthrough_id,
            payload={"case_version_id": case["case_version_id"], "x": play["state"]["x"]},
        )
        for transition in case["trajectory"]:
            self._schedule(
                play,
                transition["time_ms"],
                1,
                "disease_transition",
                playthrough_id,
                {"x": transition["x"]},
            )
        state["plays"][playthrough_id] = play
        return (
            Receipt("committed", command.target_id, 0, {"playthrough_id": playthrough_id}),
            True,
        )

    def _order_tests(
        self, play: dict[str, Any], command: Command
    ) -> tuple[Receipt, bool]:
        items = command.payload.get("items")
        if not isinstance(items, list) or not items:
            return Receipt("invalid_command", command.target_id, play["revision"]), False
        new_items: list[tuple[str, str]] = []
        for item in items:
            if not isinstance(item, dict):
                return Receipt("invalid_command", command.target_id, play["revision"]), False
            item_id, kind = item.get("item_id"), item.get("kind")
            if not isinstance(item_id, str) or kind not in {"point", "trace"}:
                return Receipt("unsupported", command.target_id, play["revision"]), False
            if item_id in play["orders"] or any(item_id == seen_id for seen_id, _ in new_items):
                return Receipt("item_exists", command.target_id, play["revision"]), False
            new_items.append((item_id, kind))

        order_time = play["elapsed_ms"]
        for item_id, kind in new_items:
            order = {
                "item_id": item_id,
                "kind": kind,
                "status": "ordered",
                "ordered_at_ms": order_time,
                "acquisition_id": None,
                "release_at_ms": None,
                "result": None,
            }
            play["orders"][item_id] = order
            self._append_event(
                play,
                clinical_time_ms=order_time,
                phase=2,
                kind="order_placed",
                subject_id=item_id,
                payload={"kind": kind},
            )
            if kind == "trace":
                for offset in (0, 1, 2):
                    self._schedule(
                        play,
                        4999 + offset,
                        3,
                        "trace_sample",
                        item_id,
                        {"sample_offset_ms": offset, "is_endpoint": offset == 2},
                    )
            else:
                capture_time = 11000 if item_id == "C" else 5000
                self._schedule(play, capture_time, 3, "point_capture", item_id, {})
        play["revision"] += 1
        play["continuation"]["last_committed_ms"] = play["elapsed_ms"]
        return Receipt("committed", command.target_id, play["revision"], {"ordered": [i for i, _ in new_items]}), True

    def _wait(
        self, play: dict[str, Any], command: Command
    ) -> tuple[Receipt, bool]:
        duration = command.payload.get("duration_ms")
        if isinstance(duration, bool) or not isinstance(duration, int) or duration < 0:
            return Receipt("invalid_command", command.target_id, play["revision"]), False
        target = play["elapsed_ms"] + duration
        if target > MAX_CLINICAL_TIME_MS:
            return Receipt("clock_overflow", command.target_id, play["revision"]), False
        self._advance(play, target)
        play["revision"] += 1
        play["continuation"]["last_committed_ms"] = target
        return Receipt("committed", command.target_id, play["revision"], {"elapsed_ms": target}), True

    def _advance(self, play: dict[str, Any], target_ms: int) -> None:
        processed_at_target = 0
        while True:
            due = [event for event in play["schedule"] if event["time_ms"] <= target_ms]
            if not due:
                break
            event = min(due, key=lambda item: (item["time_ms"], item["phase"], item["ordinal"]))
            play["schedule"].remove(event)
            if event["time_ms"] == play["elapsed_ms"]:
                processed_at_target += 1
            else:
                play["elapsed_ms"] = event["time_ms"]
                processed_at_target = 1
            if processed_at_target > MAX_SAME_TIME_EVENTS:
                raise ValueError("same-time event chain exceeded the fixture limit")
            self._process_scheduled(play, event)
        play["elapsed_ms"] = target_ms

    def _process_scheduled(self, play: dict[str, Any], scheduled: Mapping[str, Any]) -> None:
        time_ms = int(scheduled["time_ms"])
        kind = scheduled["kind"]
        subject_id = str(scheduled["subject_id"])
        payload = dict(scheduled["payload"])
        if kind == "disease_transition":
            play["state"].update(payload)
            self._append_event(play, time_ms, 1, kind, subject_id, payload)
            return
        if kind == "point_capture":
            acquisition_id = f"acq-{play['playthrough_id']}-{subject_id}"
            value = int(play["state"]["x"])
            play["acquisitions"][subject_id] = {
                "acquisition_id": acquisition_id,
                "item_id": subject_id,
                "kind": "point",
                "captured_at_ms": time_ms,
                "complete": True,
                "value": value,
            }
            order = play["orders"][subject_id]
            order["acquisition_id"] = acquisition_id
            order["status"] = "processing"
            self._append_event(
                play,
                time_ms,
                3,
                "point_captured",
                subject_id,
                {"acquisition_id": acquisition_id, "value": value},
            )
            return
        if kind == "trace_sample":
            acquisition_id = f"acq-{play['playthrough_id']}-{subject_id}"
            acquisition = play["acquisitions"].setdefault(
                subject_id,
                {
                    "acquisition_id": acquisition_id,
                    "item_id": subject_id,
                    "kind": "trace",
                    "captured_at_ms": 4999,
                    "complete": False,
                    "samples": [],
                },
            )
            value = int(play["state"]["x"])
            sample = {"offset_ms": payload["sample_offset_ms"], "time_ms": time_ms, "value": value}
            acquisition["samples"].append(sample)
            order = play["orders"][subject_id]
            order["acquisition_id"] = acquisition_id
            order["status"] = "collecting" if not payload["is_endpoint"] else "processing"
            if payload["is_endpoint"]:
                acquisition["complete"] = True
            self._append_event(
                play,
                time_ms,
                3,
                "trace_sample",
                subject_id,
                {"acquisition_id": acquisition_id, "offset_ms": payload["sample_offset_ms"], "value": value},
            )

    @staticmethod
    def _schedule(
        play: dict[str, Any], time_ms: int, phase: int, kind: str, subject_id: str, payload: Mapping[str, Any]
    ) -> None:
        play["schedule"].append(
            {
                "time_ms": int(time_ms),
                "phase": int(phase),
                "ordinal": play["next_schedule_ordinal"],
                "kind": kind,
                "subject_id": subject_id,
                "payload": dict(payload),
            }
        )
        play["next_schedule_ordinal"] += 1

    @staticmethod
    def _append_event(
        play: dict[str, Any],
        clinical_time_ms: int,
        phase: int,
        kind: str,
        subject_id: str,
        payload: Mapping[str, Any],
    ) -> None:
        sequence = play["next_event_sequence"]
        play["events"].append(
            {
                "event_id": f"evt-{play['playthrough_id']}-{sequence}",
                "clinical_time_ms": int(clinical_time_ms),
                "event_sequence": sequence,
                "phase": int(phase),
                "kind": kind,
                "subject_id": subject_id,
                "payload": dict(payload),
            }
        )
        play["next_event_sequence"] += 1

    def project(self, actor: Actor, playthrough_id: str) -> Projection:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        if playthrough_id == "catalog":
            if actor.role not in {"learner", "authority"}:
                return Projection(playthrough_id, 0, 0, "forbidden")
            case_ids = sorted(case_id for case_id, case in state["cases"].items() if case["published"])
            return Projection(
                playthrough_id,
                state["catalog_revision"],
                0,
                "ready",
                {"playable_case_ids": case_ids, "publication_count": state["publication_count"]},
            )
        play = state["plays"].get(playthrough_id)
        if play is None:
            return Projection(playthrough_id, 0, 0, "not_found")
        if actor.role != "learner" or actor.actor_id != play["owner_id"]:
            return Projection(playthrough_id, 0, 0, "forbidden")
        public_orders: dict[str, dict[str, Any]] = {}
        released_results: dict[str, Any] = {}
        for item_id, order in play["orders"].items():
            status = order["status"]
            if status == "ready_withheld":
                status = "processing"
            public_orders[item_id] = {
                "item_id": item_id,
                "kind": order["kind"],
                "status": status,
                "ordered_at_ms": order["ordered_at_ms"],
            }
            if order["status"] == "released":
                released_results[item_id] = order["result"]
        return Projection(
            playthrough_id,
            play["revision"],
            play["elapsed_ms"],
            play["status"],
            {
                "case_id": play["case_id"],
                "case_version_id": play["case_version_id"],
                "orders": public_orders,
                "released_results": released_results,
                "history": {"verified_prior_episodes": 0},
                "subjective_reports": {"prior_episodes": 1},
                "submission": play["submission"],
                "debrief": play["debrief"],
            },
        )

    def read_artifact(self, actor: Actor, playthrough_id: str, artifact_id: str) -> ArtifactAccess:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        play = state["plays"].get(playthrough_id)
        if play is None:
            return ArtifactAccess("not_found")
        if not (
            (actor.role == "learner" and actor.actor_id == play["owner_id"])
            or actor.role == "authority"
        ):
            return ArtifactAccess("forbidden")
        order = play["orders"].get(artifact_id)
        if order is None:
            return ArtifactAccess("not_found")
        if order["status"] != "released":
            return ArtifactAccess("withheld")
        return ArtifactAccess("available", order["result"])

    def trusted_events(self, playthrough_id: str) -> Sequence[ClinicalEvent]:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        if playthrough_id == "catalog":
            records = state["catalog_events"]
        else:
            play = state["plays"].get(playthrough_id)
            records = [] if play is None else play["events"]
        return tuple(ClinicalEvent(**record) for record in records)

