"""SQLite-backed synthetic case authority used only by the Gate A fixture."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Mapping, Sequence

from port import Actor, ArtifactAccess, ClinicalEvent, Command, Projection, Receipt
from scheduler import EventScheduler, ScheduleError
from workers import StubWorker, WorkerCandidate

MAX_CLINICAL_TIME_MS = 2**31 - 1
MAX_SAME_TIME_EVENTS = 1000
SCHEMA_VERSION = 1
FIXTURE_VERSIONS = {
    "model_version": "fixture-scalar-model-v1",
    "adapter_version": "fixture-adapter-v1",
    "investigation_version": "fixture-investigation-v1",
    "validation_policy_version": "fixture-validation-v1",
}


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


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


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

    def __init__(self, db_path: str | Path, worker: StubWorker | None = None):
        self.db_path = Path(db_path)
        self.worker = worker or StubWorker()
        self.scheduler = EventScheduler(MAX_SAME_TIME_EVENTS)
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

            play = state["plays"].get(command.target_id)
            if (
                play is not None
                and play["status"] == "active"
                and not self._continuation_available(play)
            ):
                connection.rollback()
                return Receipt("restore_blocked", command.target_id, play["revision"])

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
            if changed and command.target_id in state["plays"]:
                self._update_continuation(state["plays"][command.target_id])
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
        except ScheduleError:
            if connection.in_transaction:
                connection.rollback()
            return Receipt("invalid_schedule", command.target_id)
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
        if command.kind == "cancel_order":
            return self._cancel_order(play, command)
        if command.kind == "release_result":
            return self._release_result(play, command)
        if command.kind == "submit_diagnosis":
            return self._submit_diagnosis(play, command)
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
            "continuation": {},
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
        self._update_continuation(play)
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
                "acquisition_ids": [],
                "eligible_at_ms": 8000 if item_id == "T" else None,
                "failure_cause": None,
                "release_at_ms": None,
                "result": None,
                **FIXTURE_VERSIONS,
            }
            play["orders"][item_id] = order
            self._append_event(
                play,
                clinical_time_ms=order_time,
                phase=2,
                kind="order_placed",
                subject_id=item_id,
                payload={"kind": kind, "investigation_version": order["investigation_version"]},
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
                processing_time = 6000
            else:
                capture_time = 11000 if item_id == "C" else 5000
                self._schedule(play, capture_time, 3, "point_capture", item_id, {})
                processing_time = 12000 if item_id == "C" else 6000
            self._schedule(play, processing_time, 4, "process_result", item_id, {})
        play["revision"] += 1
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
        previous_time = play["elapsed_ms"]
        if not self._advance(play, target):
            return Receipt(
                "processing_blocked",
                command.target_id,
                play["revision"],
                {"committed_time_ms": previous_time},
            ), False
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"elapsed_ms": target}), True

    def _advance(self, play: dict[str, Any], target_ms: int) -> bool:
        last_time: int | None = None
        count_at_timestamp = 0
        while True:
            scheduled = self.scheduler.next_due(play["schedule"], target_ms)
            if scheduled is None:
                break
            play["schedule"] = [
                event for event in play["schedule"] if event["ordinal"] != scheduled["ordinal"]
            ]
            if scheduled["time_ms"] == last_time:
                count_at_timestamp += 1
            else:
                last_time = scheduled["time_ms"]
                count_at_timestamp = 1
            self.scheduler.check_chain(count_at_timestamp)
            play["elapsed_ms"] = scheduled["time_ms"]
            play["_scheduler_cursor"] = {
                "time_ms": scheduled["time_ms"],
                "phase": scheduled["phase"],
            }
            try:
                processed = self._process_scheduled(play, scheduled)
            finally:
                play.pop("_scheduler_cursor", None)
            if not processed:
                return False
        play["elapsed_ms"] = target_ms
        return True

    def _process_scheduled(self, play: dict[str, Any], scheduled: Mapping[str, Any]) -> bool:
        time_ms = int(scheduled["time_ms"])
        kind = str(scheduled["kind"])
        subject_id = str(scheduled["subject_id"])
        payload = dict(scheduled["payload"])
        if kind == "disease_transition":
            play["state"].update(payload)
            self._append_event(play, time_ms, 1, kind, subject_id, payload)
            return True

        order = play["orders"].get(subject_id)
        if order is None or order["status"] in {"cancelled", "closed_at_submission"}:
            return True

        if kind == "point_capture":
            acquisition_id = f"acq-{play['playthrough_id']}-{subject_id}"
            acquisition = {
                "acquisition_id": acquisition_id,
                "item_id": subject_id,
                "kind": "point",
                "captured_at_ms": time_ms,
                "complete": True,
                "value": int(play["state"]["x"]),
                **{name: order[name] for name in ("investigation_version", "adapter_version", "validation_policy_version", "model_version")},
            }
            acquisition["input_hash"] = self._acquisition_hash(play, acquisition)
            play["acquisitions"][subject_id] = acquisition
            order["acquisition_id"] = acquisition_id
            order["acquisition_ids"] = [acquisition_id]
            order["status"] = "processing"
            self._append_event(
                play,
                time_ms,
                3,
                "point_captured",
                subject_id,
                {
                    "acquisition_id": acquisition_id,
                    "input_hash": acquisition["input_hash"],
                    "investigation_version": order["investigation_version"],
                    "adapter_version": order["adapter_version"],
                    "validation_policy_version": order["validation_policy_version"],
                    "value": acquisition["value"],
                },
            )
            return True

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
                    **{name: order[name] for name in ("investigation_version", "adapter_version", "validation_policy_version", "model_version")},
                },
            )
            value = int(play["state"]["x"])
            acquisition["samples"].append(
                {"offset_ms": payload["sample_offset_ms"], "time_ms": time_ms, "value": value}
            )
            order["acquisition_id"] = acquisition_id
            order["acquisition_ids"] = [acquisition_id]
            order["status"] = "collecting" if not payload["is_endpoint"] else "processing"
            event_payload: dict[str, Any] = {
                "acquisition_id": acquisition_id,
                "offset_ms": payload["sample_offset_ms"],
                "value": value,
            }
            if payload["is_endpoint"]:
                acquisition["complete"] = True
                acquisition["input_hash"] = self._acquisition_hash(play, acquisition)
                event_payload.update(
                    {
                        "input_hash": acquisition["input_hash"],
                        "investigation_version": order["investigation_version"],
                        "adapter_version": order["adapter_version"],
                        "validation_policy_version": order["validation_policy_version"],
                    }
                )
            self._append_event(play, time_ms, 3, "trace_sample", subject_id, event_payload)
            return True

        if kind == "process_result":
            acquisition = play["acquisitions"].get(subject_id)
            if acquisition is None or not acquisition.get("complete"):
                return False
            versions = {name: order[name] for name in ("investigation_version", "adapter_version", "validation_policy_version")}
            candidate = self.worker.get_candidate(play["playthrough_id"], subject_id, acquisition, versions)
            if candidate is None or not self._candidate_matches(candidate, play, order, acquisition):
                return False
            if candidate.outcome == "failed":
                order["status"] = "failed"
                order["failure_cause"] = candidate.failure_cause or "worker_failed"
                order["validation"] = {"policy_version": order["validation_policy_version"], "outcome": "not_run"}
                self._append_event(
                    play,
                    time_ms,
                    4,
                    "result_failed",
                    subject_id,
                    {"cause": order["failure_cause"], "acquisition_id": acquisition["acquisition_id"]},
                )
                return True
            if candidate.outcome != "ready":
                return False
            validation = self._validate_candidate(candidate, acquisition, order)
            if validation["outcome"] == "reject":
                order["status"] = "failed"
                order["failure_cause"] = "validation_rejected"
                order["validation"] = validation
                self._append_event(
                    play,
                    time_ms,
                    4,
                    "validation_rejected",
                    subject_id,
                    {"acquisition_id": acquisition["acquisition_id"], "reason": validation["reason"]},
                )
                return True
            eligible_at = 8000 if subject_id in {"A", "B", "T"} else 13000
            result = {
                **dict(candidate.result),
                "item_id": subject_id,
                "acquisition_id": acquisition["acquisition_id"],
                "collected_at_ms": acquisition["captured_at_ms"],
                "processed_at_ms": time_ms,
                "eligible_at_ms": eligible_at,
                "quality": "limited" if validation["outcome"] == "limited" else "valid",
                "validation": validation,
                "provenance": {
                    "investigation_version": order["investigation_version"],
                    "adapter_version": order["adapter_version"],
                    "input_hash": acquisition["input_hash"],
                },
            }
            if subject_id == "T":
                result["validated_assessment"] = {
                    "status": "available",
                    "study_id": acquisition["acquisition_id"],
                    "supported_assertions": ["DX-A is supported by the trace step under Fixture-A rules"],
                    "evidence": ["trace samples at offsets 0, 1, and 2 ms"],
                    "uncertainty": "limited to the fictional fixture rubric",
                }
            order["status"] = "ready_withheld"
            order["eligible_at_ms"] = eligible_at
            order["result"] = result
            self._append_event(
                play,
                time_ms,
                4,
                "result_validated",
                subject_id,
                {
                    "acquisition_id": acquisition["acquisition_id"],
                    "validation_outcome": validation["outcome"],
                    "quality": result["quality"],
                },
            )
            if subject_id in {"A", "B", "C"}:
                release_at = 13000 if subject_id == "C" else 8000
                order["release_at_ms"] = release_at
                self._schedule(play, release_at, 5, "automatic_release", subject_id, {})
            return True

        if kind == "automatic_release":
            if order["status"] == "ready_withheld":
                self._commit_release(play, order, time_ms)
            return True
        return True

    @staticmethod
    def _candidate_matches(
        candidate: WorkerCandidate,
        play: Mapping[str, Any],
        order: Mapping[str, Any],
        acquisition: Mapping[str, Any],
    ) -> bool:
        return (
            candidate.playthrough_id == play["playthrough_id"]
            and candidate.item_id == order["item_id"]
            and candidate.acquisition_id == acquisition["acquisition_id"]
            and candidate.input_hash == acquisition["input_hash"]
            and candidate.investigation_version == order["investigation_version"]
            and candidate.adapter_version == order["adapter_version"]
            and candidate.validation_policy_version == order["validation_policy_version"]
        )

    @staticmethod
    def _validate_candidate(
        candidate: WorkerCandidate,
        acquisition: Mapping[str, Any],
        order: Mapping[str, Any],
    ) -> dict[str, Any]:
        result = dict(candidate.result)
        if result.get("units") != "fixture-unit":
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "invalid_units"}
        if acquisition["kind"] == "point" and result.get("value") != acquisition["value"]:
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "unsupported_value"}
        if acquisition["kind"] == "trace":
            expected = [sample["value"] for sample in acquisition["samples"]]
            if result.get("samples") != expected or not isinstance(result.get("interpretation"), str):
                return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "trace_binding_mismatch"}
        quality = result.get("quality", "valid")
        if quality not in {"valid", "limited"}:
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "invalid_quality"}
        return {
            "policy_version": order["validation_policy_version"],
            "outcome": "limited" if quality == "limited" else "pass",
            "input_hash": acquisition["input_hash"],
        }

    @staticmethod
    def _acquisition_hash(play: Mapping[str, Any], acquisition: Mapping[str, Any]) -> str:
        keys = (
            "acquisition_id", "item_id", "kind", "captured_at_ms", "complete", "value", "samples",
            "investigation_version", "adapter_version", "validation_policy_version", "model_version",
        )
        content = {
            "playthrough_id": play["playthrough_id"],
            "case_version_id": play["case_version_id"],
            "acquisition": {key: acquisition[key] for key in keys if key in acquisition},
        }
        return _sha256(content)

    def _cancel_order(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        item_id = str(command.payload.get("item_id", ""))
        order = play["orders"].get(item_id)
        if order is None:
            return Receipt("not_found", command.target_id, play["revision"]), False
        if item_id != "B" or play["elapsed_ms"] >= 6000:
            return Receipt("cancellation_closed", command.target_id, play["revision"]), False
        if order["status"] in {"released", "cancelled", "failed", "closed_at_submission"}:
            return Receipt("cancellation_closed", command.target_id, play["revision"]), False
        order["status"] = "cancelled"
        order["cancelled_at_ms"] = play["elapsed_ms"]
        play["schedule"] = [event for event in play["schedule"] if event["subject_id"] != item_id]
        self._append_event(
            play,
            play["elapsed_ms"],
            2,
            "order_cancelled",
            item_id,
            {"acquisition_id": order.get("acquisition_id")},
        )
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"item_id": item_id}), True

    def _release_result(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        item_id = str(command.payload.get("item_id", ""))
        order = play["orders"].get(item_id)
        if order is None:
            return Receipt("not_found", command.target_id, play["revision"]), False
        if order["status"] != "ready_withheld" or play["elapsed_ms"] < order["eligible_at_ms"]:
            return Receipt("release_not_eligible", command.target_id, play["revision"]), False
        self._commit_release(play, order, play["elapsed_ms"])
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"item_id": item_id}), True

    def _commit_release(self, play: dict[str, Any], order: dict[str, Any], time_ms: int) -> None:
        order["status"] = "released"
        order["result"]["released_at_ms"] = time_ms
        self._append_event(
            play,
            time_ms,
            5,
            "result_released",
            order["item_id"],
            {"acquisition_id": order["acquisition_id"], "released_at_ms": time_ms},
        )

    def _submit_diagnosis(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        submitted_at = play["elapsed_ms"]
        for item_id, order in play["orders"].items():
            if order["status"] in {"ordered", "collecting", "processing", "ready_withheld"}:
                previous = order["status"]
                order["pre_close_state"] = previous
                order["status"] = "closed_at_submission"
                order["closed_at_ms"] = submitted_at
                play["schedule"] = [event for event in play["schedule"] if event["subject_id"] != item_id]
                self._append_event(
                    play,
                    submitted_at,
                    6,
                    "order_closed_at_submission",
                    item_id,
                    {"pre_close_state": previous, "acquisition_id": order.get("acquisition_id")},
                )
        play["submission"] = {
            "submitted_at_ms": submitted_at,
            "leading_diagnosis": command.payload.get("leading_diagnosis"),
            "differential": list(command.payload.get("differential", [])),
            "reasoning": command.payload.get("reasoning"),
            "evidence_cutoff_ms": submitted_at,
        }
        play["status"] = "encounter_complete"
        self._append_event(
            play,
            submitted_at,
            6,
            "diagnosis_submitted",
            play["playthrough_id"],
            {"evidence_cutoff_ms": submitted_at},
        )
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"submitted_at_ms": submitted_at}), True

    @staticmethod
    def _continuation_basis(play: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "case_version_id": play["case_version_id"],
            **FIXTURE_VERSIONS,
            "last_committed_ms": play["elapsed_ms"],
            "pending_schedule": list(play["schedule"]),
            "in_progress_acquisitions": {
                item_id: acquisition
                for item_id, acquisition in play["acquisitions"].items()
                if not acquisition.get("complete", False)
            },
            "random_stream_state": {"fixture": "Fixture-A:stable-v1"},
        }

    def _update_continuation(self, play: dict[str, Any]) -> None:
        basis = self._continuation_basis(play)
        play["continuation"] = {**basis, "integrity_sha256": _sha256(basis)}

    def _continuation_available(self, play: Mapping[str, Any]) -> bool:
        continuation = play.get("continuation", {})
        basis = self._continuation_basis(play)
        return (
            all(continuation.get(name) == value for name, value in FIXTURE_VERSIONS.items())
            and continuation.get("schema_version") == 1
            and continuation.get("case_version_id") == play["case_version_id"]
            and continuation.get("last_committed_ms") == play["elapsed_ms"]
            and continuation.get("pending_schedule") == play["schedule"]
            and continuation.get("in_progress_acquisitions") == basis["in_progress_acquisitions"]
            and continuation.get("random_stream_state") == basis["random_stream_state"]
            and continuation.get("integrity_sha256") == _sha256(basis)
        )

    @staticmethod
    def _schedule(
        play: dict[str, Any], time_ms: int, phase: int, kind: str, subject_id: str, payload: Mapping[str, Any]
    ) -> None:
        cursor = play.get("_scheduler_cursor")
        current_phase = None if cursor is None else int(cursor["phase"])
        EventScheduler.validate_new_event(
            int(play["elapsed_ms"]), current_phase, int(time_ms), int(phase)
        )
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
                **({"failure_cause": order["failure_cause"]} if order.get("failure_cause") else {}),
                **({"pre_close_state": order["pre_close_state"]} if order.get("pre_close_state") else {}),
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
        if order["status"] == "failed":
            return ArtifactAccess("failed")
        if order["status"] == "cancelled":
            return ArtifactAccess("cancelled")
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
