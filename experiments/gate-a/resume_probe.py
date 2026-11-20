"""Fresh-process continuation probe for Gate A's A06 path."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from authority import SQLiteAuthority
from port import Actor, Command
from workers import StubWorker


def continue_a06(db_path: Path, playthrough_id: str) -> dict[str, object]:
    learner = Actor("learner-1", "learner")
    authority = SQLiteAuthority(db_path, worker=StubWorker(auto_prepare=True))
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--playthrough", required=True)
    parser.add_argument("--continue-a06", action="store_true")
    args = parser.parse_args()
    if not args.continue_a06:
        parser.error("--continue-a06 is required")
    result = continue_a06(args.db, args.playthrough)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "committed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
