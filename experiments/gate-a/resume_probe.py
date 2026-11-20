"""Fresh-process continuation probe for Gate A's A06 path."""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import asdict
from pathlib import Path

from port import Actor, Command, GateAPort
from workers import StubWorker, WorkerCandidate


def load_authority_factory(specification: str):
    module_name, separator, qualified_name = specification.partition(":")
    if not separator or not module_name or not qualified_name:
        raise ValueError("authority factory must use module:callable syntax")
    selected: object = importlib.import_module(module_name)
    for name in qualified_name.split("."):
        selected = getattr(selected, name)
    if not callable(selected):
        raise TypeError("authority factory is not callable")
    return selected


def continue_a06(
    db_path: Path,
    playthrough_id: str,
    authority_factory_spec: str = "authority:SQLiteAuthority",
) -> dict[str, object]:
    learner = Actor("learner-1", "learner")
    authority_factory = load_authority_factory(authority_factory_spec)
    authority: GateAPort = authority_factory(db_path, worker=StubWorker(auto_prepare=True))
    projection = authority.project(learner, playthrough_id)
    if projection.status != "active":
        return {"status": projection.status, "projection": asdict(projection), "events": []}

    if projection.elapsed_ms < 9000:
        wait_to_nine = authority.execute(
            learner,
            Command(
                "wait-to-9000",
                playthrough_id,
                projection.revision,
                "wait",
                {"duration_ms": 9000 - projection.elapsed_ms},
            ),
        )
        if wait_to_nine.status != "committed":
            return {"status": wait_to_nine.status, "projection": asdict(authority.project(learner, playthrough_id)), "events": []}

    projection = authority.project(learner, playthrough_id)
    order_c = authority.execute(
        learner,
        Command(
            "orders-3",
            playthrough_id,
            projection.revision,
            "order_tests",
            {"items": [{"item_id": "C", "kind": "point"}]},
        ),
    )
    if order_c.status != "committed":
        return {"status": order_c.status, "projection": asdict(authority.project(learner, playthrough_id)), "events": []}

    projection = authority.project(learner, playthrough_id)
    finish = authority.execute(
        learner,
        Command(
            "wait-to-13000",
            playthrough_id,
            projection.revision,
            "wait",
            {"duration_ms": 13000 - projection.elapsed_ms},
        ),
    )
    final = authority.project(learner, playthrough_id)
    return {
        "status": finish.status,
        "projection": asdict(final),
        "events": [asdict(event) for event in authority.trusted_events(playthrough_id)],
    }


def check_closeout(
    db_path: Path,
    playthrough_id: str,
    authority_factory_spec: str,
    late_item_id: str | None,
    release_item_id: str,
) -> dict[str, object]:
    learner = Actor("learner-1", "learner")
    release_actor = Actor("release-service", "authority")
    worker = StubWorker(auto_prepare=True)
    authority_factory = load_authority_factory(authority_factory_spec)
    authority: GateAPort = authority_factory(db_path, worker=worker)
    before = authority.project(learner, playthrough_id)
    events_before = tuple(authority.trusted_events(playthrough_id))
    if before.status != "encounter_complete":
        return {"status": "not_closed", "projection": asdict(before)}
    if late_item_id:
        events = events_before
        if late_item_id == "T":
            acquisition_event = next((event for event in reversed(events) if event.kind == "trace_sample" and event.subject_id == late_item_id and "input_hash" in event.payload), None)
            if acquisition_event is not None:
                samples = [event.payload["value"] for event in events if event.kind == "trace_sample" and event.subject_id == late_item_id]
                worker.offer(WorkerCandidate(
                    playthrough_id, late_item_id, acquisition_event.payload["acquisition_id"], acquisition_event.payload["input_hash"],
                    acquisition_event.payload["investigation_version"], acquisition_event.payload["adapter_version"], acquisition_event.payload["validation_policy_version"],
                    result={"samples": samples, "interpretation": "supports DX-A", "units": "fixture-unit"},
                ))
        else:
            acquisition_event = next((event for event in reversed(events) if event.kind == "point_captured" and event.subject_id == late_item_id), None)
            if acquisition_event is not None:
                worker.offer(WorkerCandidate(
                    playthrough_id, late_item_id, acquisition_event.payload["acquisition_id"], acquisition_event.payload["input_hash"],
                    acquisition_event.payload["investigation_version"], acquisition_event.payload["adapter_version"], acquisition_event.payload["validation_policy_version"],
                    result={"value": acquisition_event.payload["value"], "units": "fixture-unit"},
                ))
    wait = authority.execute(learner, Command("post-closeout-wait", playthrough_id, before.revision, "wait", {"duration_ms": 1000}))
    release = authority.execute(release_actor, Command("post-closeout-release", playthrough_id, before.revision, "release_result", {"item_id": release_item_id}))
    after = authority.project(learner, playthrough_id)
    events_after = tuple(authority.trusted_events(playthrough_id))
    return {
        "status": "committed" if wait.status == "encounter_complete" and release.status == "encounter_complete" and after == before and events_after == events_before else "failed",
        "wait_status": wait.status,
        "release_status": release.status,
        "projection": asdict(after),
        "events": [asdict(event) for event in events_after],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--playthrough", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--continue-a06", action="store_true")
    mode.add_argument("--check-closeout", action="store_true")
    parser.add_argument("--authority-factory", default="authority:SQLiteAuthority")
    parser.add_argument("--late-item")
    parser.add_argument("--release-item", default="T")
    args = parser.parse_args()
    if args.continue_a06:
        result = continue_a06(args.db, args.playthrough, args.authority_factory)
    else:
        result = check_closeout(args.db, args.playthrough, args.authority_factory, args.late_item, args.release_item)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "committed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
