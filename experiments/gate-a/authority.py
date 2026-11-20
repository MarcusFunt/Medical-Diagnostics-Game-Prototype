"""SQLite-backed synthetic case authority used only by the Gate A fixture."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Mapping, Sequence

from port import Actor, ArtifactAccess, ClinicalEvent, Command, Projection, Receipt
from luna import LunaStub
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
        "kind": command.kind,
        "payload": dict(command.payload),
    }
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


class SQLiteAuthority:
    """Small, transactional implementation of the public GateAPort."""

    def __init__(
        self,
        db_path: str | Path,
        worker: StubWorker | None = None,
        luna: LunaStub | None = None,
    ):
        self.db_path = Path(db_path)
        self.worker = worker or StubWorker()
        self.luna = luna or LunaStub()
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
                "actor_id TEXT NOT NULL, scope TEXT NOT NULL, command_id TEXT NOT NULL, "
                "fingerprint TEXT NOT NULL, receipt TEXT NOT NULL, "
                "PRIMARY KEY (actor_id, scope, command_id))"
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
            scope = command.target_id
            existing = connection.execute(
                "SELECT fingerprint, receipt FROM command_receipts "
                "WHERE actor_id = ? AND scope = ? AND command_id = ?",
                (actor.actor_id, scope, command.command_id),
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
                    "INSERT INTO command_receipts(actor_id, scope, command_id, fingerprint, receipt) "
                    "VALUES(?, ?, ?, ?, ?)",
                    (
                        actor.actor_id,
                        scope,
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
        review_commands = {"review_case", "skip_review"}
        if play["status"] != "active" and command.kind not in review_commands:
            return Receipt("encounter_complete", command.target_id, play["revision"]), False
        if play["status"] == "active" and command.kind in review_commands:
            return Receipt("review_not_available", command.target_id, play["revision"]), False
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
        if command.kind == "open_artifact":
            return self._open_artifact(play, command)
        if command.kind == "request_interpretation":
            return self._request_interpretation(play, command)
        if command.kind == "ask_patient":
            return self._ask_patient(play, state["cases"][play["case_id"]], command)
        if command.kind == "review_case":
            return self._review_case(play, command)
        if command.kind == "skip_review":
            return self._skip_review(play, command)
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
            "reference_differential": ["DX-A", "DX-B"],
            "valid_alternatives": ["DX-B"],
            "dialogue_mode": "luna_required",
            "dialogue_facts": [
                {
                    "fact_id": "subjective-prior-episodes",
                    "text": "The patient recalls one prior fictional episode.",
                    "source": "subjective_report",
                }
            ],
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
        if state["cases"][case_id].get("dialogue_mode", "luna_required") == "canned_only":
            return Receipt("legacy_case_not_playable", command.target_id), False
        if playthrough_id in state["plays"]:
            return Receipt("playthrough_exists", command.target_id), False
        case = state["cases"][case_id]
        play = {
            "playthrough_id": playthrough_id,
            "owner_id": actor.actor_id,
            "case_id": case_id,
            "case_version_id": case["case_version_id"],
            "_private_case": dict(case),
            "revision": 0,
            "elapsed_ms": 0,
            "status": "active",
            "state": dict(case["initial_state"]),
            "orders": {},
            "acquisitions": {},
            "results": {},
            "disclosures": [],
            "dialogue_history": [],
            "interpretation_aids": [],
            "artifact_views": [],
            "submission": None,
            "debrief": None,
            "review": None,
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
        new_items: list[tuple[str, str, str]] = []
        for item in items:
            if not isinstance(item, dict):
                return Receipt("invalid_command", command.target_id, play["revision"]), False
            item_id, kind = item.get("item_id"), item.get("kind")
            capability = item.get("capability", "supported")
            if not isinstance(item_id, str) or kind not in {"point", "trace"}:
                return Receipt("unsupported", command.target_id, play["revision"]), False
            if capability not in {"supported", "unsupported", "unavailable"}:
                return Receipt("invalid_command", command.target_id, play["revision"]), False
            if item_id in play["orders"] or any(item_id == seen_id for seen_id, _, _ in new_items):
                return Receipt("item_exists", command.target_id, play["revision"]), False
            new_items.append((item_id, kind, capability))

        order_time = play["elapsed_ms"]
        for item_id, kind, capability in new_items:
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
            if capability in {"unsupported", "unavailable"}:
                order["status"] = capability
                order["failure_cause"] = (
                    "no_registered_capability"
                    if capability == "unsupported"
                    else "unavailable_in_context"
                )
            play["orders"][item_id] = order
            self._append_event(
                play,
                clinical_time_ms=order_time,
                phase=2,
                kind="order_placed",
                subject_id=item_id,
                payload={"kind": kind, "investigation_version": order["investigation_version"]},
            )
            if capability in {"unsupported", "unavailable"}:
                self._append_event(
                    play,
                    order_time,
                    4,
                    "item_disposition_recorded",
                    item_id,
                    {"status": capability, "cause": order["failure_cause"]},
                )
                continue
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
        return Receipt("committed", command.target_id, play["revision"], {"ordered": [i for i, _, _ in new_items]}), True

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
            candidate_result = dict(candidate.result)
            if acquisition["kind"] == "point":
                validated_payload = {"value": candidate_result["value"], "units": "fixture-unit"}
            else:
                validated_payload = {
                    "samples": list(candidate_result["samples"]),
                    "interpretation": candidate_result["interpretation"],
                    "units": "fixture-unit",
                    "media_available": candidate_result.get("media_available", True),
                }
                if validation["outcome"] == "limited":
                    validated_payload["sample_offsets"] = list(candidate_result["sample_offsets"])
            result = {
                **validated_payload,
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
            if acquisition["kind"] == "trace":
                result["primary_media_available"] = bool(candidate.result.get("media_available", True))
                if "sample_offsets" in candidate.result:
                    result["sample_offsets"] = list(candidate.result["sample_offsets"])
                if not result["primary_media_available"]:
                    offsets = result.get("sample_offsets", [0, 1, 2][: len(result["samples"])])
                    result["accessible_text"] = (
                        "Trace samples: "
                        + ", ".join(
                            f"offset {offset} ms = {value} fixture-units"
                            for offset, value in zip(offsets, result["samples"])
                        )
                        + "."
                    )
            if subject_id == "T":
                if validation["outcome"] == "pass":
                    result["validated_assessment"] = {
                        "status": "available",
                        "study_id": acquisition["acquisition_id"],
                        "supported_assertions": ["DX-A is supported by the trace step under Fixture-A rules"],
                        "evidence": ["trace samples at offsets 0, 1, and 2 ms"],
                        "uncertainty": "limited to the fictional fixture rubric",
                    }
                else:
                    result["validated_assessment"] = {"status": "unavailable", "study_id": acquisition["acquisition_id"]}
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
        if acquisition["kind"] == "point" and (
            isinstance(result.get("value"), bool)
            or not isinstance(result.get("value"), int)
            or result.get("value") != acquisition["value"]
        ):
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "unsupported_value"}
        quality = result.get("quality", "valid")
        if quality not in {"valid", "limited"}:
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "invalid_quality"}
        if acquisition["kind"] == "trace":
            expected = [sample["value"] for sample in acquisition["samples"]]
            sample_values = result.get("samples")
            if not isinstance(sample_values, list) or not isinstance(result.get("interpretation"), str):
                return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "trace_binding_mismatch"}
            expected_interpretation = "supports DX-A" if quality == "valid" else "partial trace only"
            if result["interpretation"] != expected_interpretation:
                return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "unsupported_interpretation"}
            if quality == "valid":
                if (
                    sample_values != expected
                    or any(isinstance(value, bool) or not isinstance(value, int) for value in sample_values)
                ):
                    return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "trace_binding_mismatch"}
            else:
                offsets = result.get("sample_offsets")
                if (
                    not isinstance(offsets, list)
                    or len(offsets) != len(sample_values)
                    or not offsets
                    or any(isinstance(offset, bool) or not isinstance(offset, int) or offset not in range(len(expected)) for offset in offsets)
                    or offsets != sorted(offsets)
                    or len(offsets) != len(set(offsets))
                    or any(isinstance(value, bool) or not isinstance(value, int) for value in sample_values)
                    or any(sample_values[index] != expected[offset] for index, offset in enumerate(offsets))
                ):
                    return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "limited_trace_binding_mismatch"}
        if "media_available" in result and not isinstance(result["media_available"], bool):
            return {"policy_version": order["validation_policy_version"], "outcome": "reject", "reason": "invalid_media_status"}
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
        cutoff_sequence = play["next_event_sequence"] - 1
        differential = command.payload.get("differential", [])
        if not isinstance(differential, list) or not all(isinstance(item, str) for item in differential):
            return Receipt("invalid_command", command.target_id, play["revision"]), False
        accessible_evidence = {
            item_id: {
                "acquisition_id": order["acquisition_id"],
                "input_hash": order["result"].get("provenance", {}).get("input_hash"),
                "released_at_ms": order["result"].get("released_at_ms"),
                "result": dict(order["result"]),
                "versions": {
                    name: order[name]
                    for name in ("investigation_version", "adapter_version", "validation_policy_version")
                },
            }
            for item_id, order in play["orders"].items()
            if order["status"] == "released"
            and order["result"].get("released_at_ms", submitted_at + 1) <= submitted_at
        }
        submission = {
            "submitted_at_ms": submitted_at,
            "leading_diagnosis": command.payload.get("leading_diagnosis"),
            "differential": list(differential),
            "reasoning": command.payload.get("reasoning"),
            "evidence_cutoff_ms": submitted_at,
            "event_sequence_cutoff": cutoff_sequence,
            "accessible_evidence": {
                item_id: {
                    "acquisition_id": evidence["acquisition_id"],
                    "input_hash": evidence["input_hash"],
                    "released_at_ms": evidence["released_at_ms"],
                    "versions": dict(evidence["versions"]),
                }
                for item_id, evidence in accessible_evidence.items()
            },
            "artifact_views": [dict(view) for view in play["artifact_views"] if view["at_ms"] <= submitted_at],
            "interpretation_aids": [dict(aid) for aid in play["interpretation_aids"] if aid["delivered_at_ms"] <= submitted_at],
        }

        # Freeze adjudication inputs before changing any outstanding order states.
        case = self._case_for_play(play)
        play["submission"] = submission
        play["debrief"] = self._build_debrief(play, case, submission, accessible_evidence)
        for item_id, order in play["orders"].items():
            if order["status"] in {"ordered", "collecting", "processing", "ready_withheld"}:
                previous = order["status"]
                order["pre_close_state"] = previous
                order["closure_reason"] = "diagnosis_submission"
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
        play["status"] = "encounter_complete"
        play["review"] = {"status": "prompted"}
        self._append_event(
            play,
            submitted_at,
            6,
            "diagnosis_submitted",
            play["playthrough_id"],
            {"evidence_cutoff_ms": submitted_at, "event_sequence_cutoff": cutoff_sequence},
        )
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"submitted_at_ms": submitted_at}), True

    @staticmethod
    def _case_for_play(play: Mapping[str, Any]) -> dict[str, Any]:
        # The case record is attached privately at play creation for offline adjudication.
        return dict(play["_private_case"])

    @staticmethod
    def _build_debrief(
        play: Mapping[str, Any],
        case: Mapping[str, Any],
        submission: Mapping[str, Any],
        accessible_evidence: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, Any]:
        leading = submission["leading_diagnosis"]
        differential = submission["differential"]
        reasoning = submission["reasoning"]
        required = {"A", "T"}
        selected = set(play["orders"])
        redundant = sorted(item_id for item_id in selected if item_id == "C")
        text = reasoning.strip().lower() if isinstance(reasoning, str) else ""
        evidence_link = (
            "present"
            if "point sample was 2" in text and "trace rose from 1 to 2" in text
            else "absent" if text else "unassessed"
        )
        uncertainty = "present" if any(word in text for word in ("uncertain", "uncertainty", "might", "possibly")) else "absent" if text else "unassessed"
        point = accessible_evidence.get("A", {}).get("result", {}).get("value")
        trace = accessible_evidence.get("T", {}).get("result", {}).get("samples")
        interpretation_supported = (
            point == 2
            and trace == [1, 2, 2]
            and evidence_link == "present"
        )
        key_evidence = []
        if "A" in accessible_evidence:
            key_evidence.append({"item_id": "A", "observation": "point sample = 2", "acquisition_id": accessible_evidence["A"]["acquisition_id"]})
        if "T" in accessible_evidence:
            key_evidence.append({"item_id": "T", "observation": "trace samples = [1, 2, 2]", "acquisition_id": accessible_evidence["T"]["acquisition_id"]})
        return {
            "rubric_version": "fixture-rubric-v1",
            "submitted_at_ms": submission["submitted_at_ms"],
            "event_sequence_cutoff": submission["event_sequence_cutoff"],
            "dimensions": {
                "diagnostic_accuracy": {"status": "correct" if leading in case.get("reference_key", []) else "incorrect", "leading_diagnosis": leading},
                "differential_quality": {"status": "reference_ranked" if differential == case.get("reference_differential", []) else "partial" if leading in case.get("reference_key", []) else "incorrect", "reference_order": list(case.get("reference_differential", []))},
                "test_selection": {"status": "required_tests_selected" if required.issubset(selected) else "missing_required_tests", "required": sorted(required), "selected": sorted(selected)},
                "unnecessary_testing": {"status": "redundant_test" if redundant else "none", "items": redundant},
                "interpretation": {"status": "supported" if interpretation_supported else "unassessed" if not text else "unsupported", "evidence_link": evidence_link},
                "explanation": {"status": "unassessed" if not text else "assessed"},
                "reasoning": {"evidence_link": evidence_link, "uncertainty": uncertainty},
            },
            "key_evidence": key_evidence,
            "valid_alternative_reasoning": ["DX-B was retained as a valid alternative under the fixture rubric."],
            "uncertainty": {"reasoning_discussed": uncertainty == "present", "reference_limit": "fictional fixture rubric"},
            "interpretation_aids": [dict(aid) for aid in submission["interpretation_aids"]],
        }

    def _open_artifact(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        item_id = str(command.payload.get("item_id", ""))
        order = play["orders"].get(item_id)
        if order is None:
            return Receipt("not_found", command.target_id, play["revision"]), False
        if order["status"] != "released":
            return Receipt(order["status"] if order["status"] in {"unsupported", "unavailable", "failed", "cancelled"} else "withheld", command.target_id, play["revision"]), False
        view = {"item_id": item_id, "at_ms": play["elapsed_ms"], "acquisition_id": order["acquisition_id"]}
        play["artifact_views"].append(view)
        self._append_event(play, play["elapsed_ms"], 5, "artifact_opened", item_id, view)
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], view), True

    def _request_interpretation(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        item_id = str(command.payload.get("item_id", ""))
        order = play["orders"].get(item_id)
        if order is None:
            return Receipt("not_found", command.target_id, play["revision"]), False
        if order["status"] != "released":
            return Receipt("withheld", command.target_id, play["revision"]), False
        assessment = order["result"].get("validated_assessment", {"status": "unavailable"})
        if assessment.get("status") != "available":
            return Receipt("assessment_unavailable", command.target_id, play["revision"], {"assessment": dict(assessment)}), False
        explanation_status = "not_requested"
        explanation_text = None
        if command.payload.get("explanation", False):
            response = self.luna.complete(
                "explanation",
                {"study_id": assessment["study_id"], "assessment": dict(assessment), "observation": dict(order["result"])},
            )
            explanation_status = response.get("status", "error")
            if explanation_status == "success" and isinstance(response.get("text"), str):
                explanation_text = response["text"]
            elif explanation_status == "success":
                explanation_status = "error"
        aid = {
            "item_id": item_id,
            "assessment": dict(assessment),
            "explanation_status": explanation_status,
            "explanation": explanation_text,
            "delivered_at_ms": play["elapsed_ms"],
            "acquisition_id": order["acquisition_id"],
        }
        play["interpretation_aids"].append(aid)
        self._append_event(
            play,
            play["elapsed_ms"],
            5,
            "interpretation_delivered",
            item_id,
            {"acquisition_id": order["acquisition_id"], "explanation_status": explanation_status},
        )
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"assessment": dict(assessment), "explanation_status": explanation_status}), True

    def _ask_patient(
        self,
        play: dict[str, Any],
        case: Mapping[str, Any],
        command: Command,
    ) -> tuple[Receipt, bool]:
        question = command.payload.get("question")
        if not isinstance(question, str) or not question.strip():
            return Receipt("invalid_command", command.target_id, play["revision"]), False
        allowed_facts = list(case.get("dialogue_facts", []))
        response = self.luna.complete(
            "dialogue",
            {"question": question, "facts": allowed_facts, "role": "patient"},
        )
        if response.get("status") != "success":
            return Receipt("dialogue_blocked", command.target_id, play["revision"], {"cause": response.get("status", "error")}), False
        text = response.get("text")
        fact_refs = response.get("fact_refs", [])
        allowed_ids = {fact["fact_id"] for fact in allowed_facts}
        if (
            not isinstance(text, str)
            or not text.strip()
            or not isinstance(fact_refs, list)
            or any(not isinstance(ref, str) for ref in fact_refs)
            or any(ref not in allowed_ids for ref in fact_refs)
            or (not fact_refs and response.get("uncertainty") is not True)
            or response.get("subjective_report") is not True
        ):
            return Receipt("dialogue_blocked", command.target_id, play["revision"], {"cause": "response_not_grounded"}), False
        utterance = {
            "question": question,
            "answer": text,
            "fact_refs": list(fact_refs),
            "subjective_report": True,
            "at_ms": play["elapsed_ms"],
        }
        play["dialogue_history"].append(utterance)
        self._append_event(play, play["elapsed_ms"], 2, "patient_utterance_committed", "patient", utterance)
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], {"utterance": utterance}), True

    def _review_case(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        if play.get("review", {}).get("status") != "prompted":
            return Receipt("review_already_recorded", command.target_id, play["revision"]), False
        rating = command.payload.get("rating")
        if isinstance(rating, bool) or not isinstance(rating, int) or rating not in range(1, 6):
            return Receipt("invalid_command", command.target_id, play["revision"]), False
        review = {"status": "submitted", "rating": rating, "comment": str(command.payload.get("comment", "")), "at_ms": play["elapsed_ms"]}
        play["review"] = review
        self._append_event(play, play["elapsed_ms"], 6, "case_review_submitted", play["playthrough_id"], review)
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], review), True

    def _skip_review(self, play: dict[str, Any], command: Command) -> tuple[Receipt, bool]:
        if play.get("review", {}).get("status") != "prompted":
            return Receipt("review_already_recorded", command.target_id, play["revision"]), False
        review = {"status": "skipped", "at_ms": play["elapsed_ms"]}
        play["review"] = review
        self._append_event(play, play["elapsed_ms"], 6, "case_review_skipped", play["playthrough_id"], review)
        play["revision"] += 1
        return Receipt("committed", command.target_id, play["revision"], review), True

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
                "dialogue_history": [dict(utterance) for utterance in play["dialogue_history"]],
                "interpretation_aids": [dict(aid) for aid in play["interpretation_aids"]],
                "submission": play["submission"],
                "debrief": play["debrief"],
                "review": play.get("review") or ({"status": "prompted"} if play["status"] == "encounter_complete" else None),
            },
        )

    def read_artifact(self, actor: Actor, playthrough_id: str, artifact_id: str) -> ArtifactAccess:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        play = state["plays"].get(playthrough_id)
        status, order = self._artifact_order_access(actor, play, artifact_id)
        if status != "available":
            return ArtifactAccess(status)
        return ArtifactAccess("available", dict(order["result"]))

    def artifact_metadata(self, actor: Actor, playthrough_id: str, artifact_id: str) -> ArtifactAccess:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        play = state["plays"].get(playthrough_id)
        status, order = self._artifact_order_access(actor, play, artifact_id)
        if status != "available":
            return ArtifactAccess(status)
        result = order["result"]
        return ArtifactAccess(
            "available",
            {
                "item_id": artifact_id,
                "kind": order["kind"],
                "acquisition_id": order["acquisition_id"],
                "collected_at_ms": result["collected_at_ms"],
                "released_at_ms": result["released_at_ms"],
                "units": result.get("units"),
                "quality": result["quality"],
                "primary_media_status": "available" if result.get("primary_media_available", True) else "unavailable",
                "accessible_text_available": order["kind"] == "trace" or "value" in result,
            },
        )

    def read_asset(
        self,
        actor: Actor,
        playthrough_id: str,
        artifact_id: str,
        asset_id: str = "primary",
    ) -> ArtifactAccess:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        play = state["plays"].get(playthrough_id)
        status, order = self._artifact_order_access(actor, play, artifact_id)
        if status != "available":
            return ArtifactAccess(status)
        result = order["result"]
        if asset_id == "primary":
            if not result.get("primary_media_available", True):
                return ArtifactAccess("unavailable")
            if order["kind"] == "trace":
                return ArtifactAccess(
                    "available",
                    {"asset_id": "primary", "representation": "synthetic-trace", "samples": list(result["samples"]), "units": result["units"]},
                )
            return ArtifactAccess("available", {"asset_id": "primary", "representation": "synthetic-scalar", "value": result["value"], "units": result["units"]})
        if asset_id == "accessible-text":
            if order["kind"] == "trace":
                offsets = result.get("sample_offsets", [0, 1, 2][: len(result["samples"])])
                return ArtifactAccess(
                    "available",
                    {
                        "asset_id": "accessible-text",
                        "text": result.get("accessible_text") or "Trace samples: " + ", ".join(map(str, result["samples"])) + f" {result['units']}.",
                        "samples": list(result["samples"]),
                        "sample_offsets": list(offsets),
                        "units": result["units"],
                    },
                )
            return ArtifactAccess(
                "available",
                {"asset_id": "accessible-text", "text": f"Measured value: {result['value']} {result['units']}.", "value": result["value"], "units": result["units"]},
            )
        return ArtifactAccess("asset_not_found")

    @staticmethod
    def _artifact_order_access(
        actor: Actor,
        play: Mapping[str, Any] | None,
        artifact_id: str,
    ) -> tuple[str, Mapping[str, Any] | None]:
        if play is None:
            return "not_found", None
        if not (
            (actor.role == "learner" and actor.actor_id == play["owner_id"])
            or actor.role == "authority"
        ):
            return "forbidden", None
        order = play["orders"].get(artifact_id)
        if order is None:
            return "not_found", None
        status = order["status"]
        if status == "released":
            return "available", order
        if status == "closed_at_submission":
            return "withheld", None
        if status in {"failed", "cancelled", "unsupported", "unavailable"}:
            return status, None
        return "withheld", None

    def trusted_events(self, playthrough_id: str) -> Sequence[ClinicalEvent]:
        with closing(self._connect()) as connection:
            state = self._load_state(connection)
        if playthrough_id == "catalog":
            records = state["catalog_events"]
        else:
            play = state["plays"].get(playthrough_id)
            records = [] if play is None else play["events"]
        return tuple(ClinicalEvent(**record) for record in records)
