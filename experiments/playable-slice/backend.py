"""Local CLI adapter to the existing Gate A authority. Fictional engineering fixture only.

Protocol: JSON lines over stdin/stdout. During model calls the backend emits a
model_request and awaits a model_result from the trusted Node server.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "gate-a"))
from authority import SQLiteAuthority
from port import Actor, Command
from workers import StubWorker

DB = Path(os.environ.get("GAME_DB_PATH", str(HERE / "local-demo.sqlite3")))
LEARNER = Actor("local-learner", "learner")
AUTHORITY = Actor("internal-release-service", "authority")


def emit(payload):
    print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), flush=True)


class LunaPipe:
    def complete(self, purpose, context):
        # Fixture-A's internal reference assessment contains its scoring target.
        # Do not send that diagnosis-bearing payload to a pre-submission model.
        if purpose == "explanation":
            return {"status": "unavailable"}
        emit({"type": "model_request", "purpose": purpose, "context": context})
        raw = sys.stdin.readline()
        if not raw:
            return {"status": "unavailable"}
        try:
            answer = json.loads(raw)
            if answer.get("type") != "model_result" or not isinstance(answer.get("result"), dict):
                return {"status": "error"}
            return answer["result"]
        except (ValueError, TypeError):
            return {"status": "error"}


def sessions_table():
    DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB)
    try:
        connection.execute("CREATE TABLE IF NOT EXISTS local_sessions (playthrough_id TEXT PRIMARY KEY, case_id TEXT NOT NULL)")
        connection.commit()
    finally:
        connection.close()


def session_ids():
    with sqlite3.connect(DB) as con:
        return list(con.execute("SELECT playthrough_id, case_id FROM local_sessions ORDER BY rowid DESC"))


def known_session(playthrough_id):
    return isinstance(playthrough_id, str) and any(row[0] == playthrough_id for row in session_ids())


def to_dict(obj):
    return asdict(obj)


def player_assessment(_assessment):
    return {
        "status": "unavailable",
        "summary": "This synthetic software fixture has no clinical reference interpretation.",
        "limitations": "The displayed values are fictional and have no diagnostic meaning.",
    }


def player_projection(projection):
    value = to_dict(projection)
    data = value.get("data")
    if not isinstance(data, dict):
        return value
    for result in data.get("released_results", {}).values():
        if isinstance(result, dict):
            for key in ("interpretation", "reference_key", "reference_differential", "supported_assertions"):
                result.pop(key, None)
    for aid in data.get("interpretation_aids", []):
        if isinstance(aid, dict):
            aid["assessment"] = player_assessment(aid.get("assessment"))
            aid["explanation"] = None
            aid["explanation_status"] = "unavailable"
    return value


def player_receipt(receipt):
    value = to_dict(receipt)
    data = value.get("data")
    if isinstance(data, dict) and "assessment" in data:
        data["assessment"] = player_assessment(data["assessment"])
        data.pop("explanation", None)
    return value


def ensure_fixture(authority):
    catalog = authority.project(LEARNER, "catalog")
    if "Fixture-A" not in catalog.data.get("playable_case_ids", []):
        result = authority.execute(LEARNER, Command(
            "demo-fixture-create", "catalog", None, "generate_case",
            {"case_id": "Fixture-A", "mandatory_evidence": True},
        ))
        if result.status not in ("committed", "case_exists"):
            raise RuntimeError("fixture_creation_failed_" + result.status)


def release_due(authority, play_id):
    """Trusted demonstration service, not a browser-facing release command."""
    with sqlite3.connect(DB) as con:
        row = con.execute("SELECT payload FROM authority_state WHERE singleton=1").fetchone()
        if not row:
            return
        private = json.loads(row[0]).get("plays", {}).get(play_id)
    if not private or private["status"] != "active" or private["elapsed_ms"] < 9000:
        return
    order = private.get("orders", {}).get("T")
    if not order or order.get("status") != "ready_withheld":
        return
    command = Command(f"demo-release-T-{play_id}", play_id, private["revision"], "release_result", {"item_id": "T"})
    result = authority.execute(AUTHORITY, command)
    if result.status != "committed":
        raise RuntimeError("trusted_release_failed_" + result.status)


def handle(request):
    op = request.get("op")
    if op not in {"bootstrap", "start", "command", "asset", "metadata"}:
        return {"status": "unsupported_operation"}
    sessions_table()
    authority = SQLiteAuthority(DB, worker=StubWorker(auto_prepare=True), luna=LunaPipe())
    ensure_fixture(authority)
    if op == "bootstrap":
        cases = authority.project(LEARNER, "catalog")
        entries = []
        for play_id, case_id in session_ids():
            release_due(authority, play_id)
            p = authority.project(LEARNER, play_id)
            if p.status != "not_found":
                entries.append({"playthrough_id": play_id, "case_id": case_id,
                                "status": p.status, "elapsed_ms": p.elapsed_ms})
        selected = request.get("playthrough_id")
        projection = (player_projection(authority.project(LEARNER, selected))
                      if known_session(selected) else None)
        return {"status": "ok", "catalog": to_dict(cases), "sessions": entries,
                "projection": projection}
    if op == "start":
        if request.get("case_id") != "Fixture-A":
            return {"status": "case_not_found"}
        play_id = "demo-" + uuid.uuid4().hex
        result = authority.execute(LEARNER, Command(
            "start-" + play_id, "case:Fixture-A", None,
            "start_playthrough", {"playthrough_id": play_id},
        ))
        if result.status != "committed":
            return player_receipt(result)
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO local_sessions VALUES (?, ?)", (play_id, "Fixture-A"))
            con.commit()
        return {"status": "committed", "playthrough_id": play_id,
                "projection": player_projection(authority.project(LEARNER, play_id))}
    play_id = request.get("playthrough_id")
    if not known_session(play_id):
        return {"status": "not_found"}
    if op in {"asset", "metadata"}:
        item = request.get("item_id")
        if item not in {"A", "T"}:
            return {"status": "not_found"}
        result = (authority.read_asset(LEARNER, play_id, item,
                                      "accessible-text" if request.get("text") else "primary")
                  if op == "asset" else authority.artifact_metadata(LEARNER, play_id, item))
        return to_dict(result)
    kind = request.get("kind")
    allowed = {"order_tests", "wait", "ask_patient", "open_artifact",
               "request_interpretation", "submit_diagnosis", "review_case", "skip_review"}
    if kind not in allowed:
        return {"status": "unsupported_command"}
    data = request.get("payload", {})
    if not isinstance(data, dict):
        return {"status": "invalid_command"}
    # Validation, authorization, and command idempotency remain inside the Case Authority.
    command_id = request.get("command_id")
    revision = request.get("expected_revision")
    if not isinstance(command_id, str) or not (0 < len(command_id) <= 128):
        return {"status": "invalid_command"}
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        return {"status": "invalid_command"}
    result = authority.execute(LEARNER, Command(command_id, play_id, revision, kind, data))
    if kind == "wait" and result.status == "committed":
        release_due(authority, play_id)
    return {"receipt": player_receipt(result),
            "projection": player_projection(authority.project(LEARNER, play_id))}


def main():
    request = sys.stdin.readline()
    try:
        if not request or len(request) > 65536:
            raise ValueError("invalid_request")
        response = handle(json.loads(request))
    except (ValueError, TypeError, KeyError) as exc:
        response = {"status": "invalid_request"}
    except Exception as exc:
        print("backend_failure: " + type(exc).__name__, file=sys.stderr)
        response = {"status": "internal_error"}
    emit({"type": "result", "data": response})


if __name__ == "__main__":
    main()
