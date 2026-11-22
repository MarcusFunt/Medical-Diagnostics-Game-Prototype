"""Local player UI prototype backed by the synthetic Gate A authority.

This adapter is intentionally limited to the Fixture-A walkthrough. It binds
to loopback, uses deterministic local doubles, and never calls an external
model or service.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import threading
import uuid
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlsplit

GATE_A_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATE_A_DIR))

from authority import SQLiteAuthority  # noqa: E402
from luna import LunaStub  # noqa: E402
from port import Actor, Command  # noqa: E402
from workers import StubWorker  # noqa: E402


CASE_ID = "Fixture-A"
LEARNER = Actor("local-player", "learner")
RELEASE_SERVICE = Actor("prototype-fixture-release", "authority")
PLAYER_COMMANDS = {
    "order_tests",
    "wait",
    "submit_diagnosis",
    "open_artifact",
    "ask_patient",
    "review_case",
    "skip_review",
}
MAX_BODY_BYTES = 128 * 1024


class PrototypeService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.authority = SQLiteAuthority(
            self.data_dir / "fixture-a.sqlite",
            worker=StubWorker(auto_prepare=True),
            luna=LunaStub(),
        )
        self.profile_path = self.data_dir / "attempts.json"
        self.attempts = self._load_attempts()
        self.dialogue_outcome = "unavailable"
        self.debrief_unavailable = False
        self.order_response_failure = "none"
        self.authority.luna.dialogue_outcome = self.dialogue_outcome
        self.lock = threading.RLock()

    def _load_attempts(self) -> list[dict[str, Any]]:
        try:
            value = json.loads(self.profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(value, list):
            return []
        return [
            {"playthrough_id": row["playthrough_id"], "number": row["number"]}
            for row in value
            if isinstance(row, dict)
            and isinstance(row.get("playthrough_id"), str)
            and isinstance(row.get("number"), int)
            and not isinstance(row.get("number"), bool)
        ]

    def _save_attempts(self) -> None:
        temporary = self.profile_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.attempts, indent=2), encoding="utf-8")
        temporary.replace(self.profile_path)

    def _attempt_record(self, playthrough_id: str) -> dict[str, Any] | None:
        return next(
            (row for row in self.attempts if row["playthrough_id"] == playthrough_id),
            None,
        )

    def _projection(self, playthrough_id: str) -> dict[str, Any]:
        record = self._attempt_record(playthrough_id)
        if record is None:
            raise KeyError("attempt_not_found")
        projection = self.authority.project(LEARNER, playthrough_id)
        public = asdict(projection)
        # Debrief is fetched through its own endpoint so the prototype can show
        # the submission when debrief rendering is unavailable.
        public["data"].pop("debrief", None)
        public["attempt_number"] = record["number"]
        return public

    def bootstrap(self) -> dict[str, Any]:
        catalog = self.authority.project(LEARNER, "catalog")
        attempts = []
        for record in self.attempts:
            projection = self._projection(record["playthrough_id"])
            attempts.append(
                {
                    "playthrough_id": record["playthrough_id"],
                    "number": record["number"],
                    "status": projection["status"],
                    "elapsed_ms": projection["elapsed_ms"],
                    "revision": projection["revision"],
                }
            )
        current = next((item for item in reversed(attempts) if item["status"] == "active"), None)
        return {
            "mode": "local_synthetic",
            "case_id": CASE_ID,
            "catalog": asdict(catalog),
            "attempts": attempts,
            "current_attempt_id": current["playthrough_id"] if current else None,
            "dialogue_outcome": self.dialogue_outcome,
            "debrief_unavailable": self.debrief_unavailable,
            "order_response_failure": self.order_response_failure,
        }

    def generate_case(self) -> dict[str, Any]:
        with self.lock:
            catalog = self.authority.project(LEARNER, "catalog")
            if CASE_ID in catalog.data.get("playable_case_ids", []):
                return {"status": "already_published", "catalog": asdict(catalog)}
            receipt = self.authority.execute(
                LEARNER,
                Command(
                    "prototype-publish-fixture-a-v1",
                    "catalog",
                    catalog.revision,
                    "generate_case",
                    {"case_id": CASE_ID, "mandatory_evidence": True},
                ),
            )
            return {"receipt": asdict(receipt), "catalog": asdict(self.authority.project(LEARNER, "catalog"))}

    def start_attempt(self) -> dict[str, Any]:
        with self.lock:
            catalog = self.authority.project(LEARNER, "catalog")
            if CASE_ID not in catalog.data.get("playable_case_ids", []):
                raise ValueError("case_not_published")
            attempt_id = f"play-{uuid.uuid4().hex[:10]}"
            receipt = self.authority.execute(
                LEARNER,
                Command(
                    f"prototype-start-{attempt_id}",
                    f"case:{CASE_ID}",
                    None,
                    "start_playthrough",
                    {"playthrough_id": attempt_id},
                ),
            )
            if receipt.status != "committed":
                return {"receipt": asdict(receipt)}
            record = {"playthrough_id": attempt_id, "number": len(self.attempts) + 1}
            self.attempts.append(record)
            self._save_attempts()
            return {"receipt": asdict(receipt), "projection": self._projection(attempt_id)}

    def command(
        self,
        playthrough_id: str,
        command_id: str,
        expected_revision: int,
        kind: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        with self.lock:
            if self._attempt_record(playthrough_id) is None:
                raise KeyError("attempt_not_found")
            if kind not in PLAYER_COMMANDS:
                raise ValueError("unsupported_player_command")
            receipt = self.authority.execute(
                LEARNER,
                Command(command_id, playthrough_id, expected_revision, kind, payload),
            )
            return {"receipt": asdict(receipt), "projection": self._projection(playthrough_id)}

    def consume_order_response_failure(self, kind: str) -> str:
        if kind != "order_tests":
            return "none"
        with self.lock:
            outcome = self.order_response_failure
            self.order_response_failure = "none"
            return outcome

    def release_fixture_result(
        self, playthrough_id: str, item_id: str, expected_revision: int
    ) -> dict[str, Any]:
        with self.lock:
            if self._attempt_record(playthrough_id) is None:
                raise KeyError("attempt_not_found")
            if item_id != "T":
                raise ValueError("fixture_release_only_supports_T")
            command_id = f"prototype-release-T-{uuid.uuid4().hex}"
            receipt = self.authority.execute(
                RELEASE_SERVICE,
                Command(
                    command_id,
                    playthrough_id,
                    expected_revision,
                    "release_result",
                    {"item_id": item_id},
                ),
            )
            return {"receipt": asdict(receipt), "projection": self._projection(playthrough_id)}

    def read_asset(self, playthrough_id: str, item_id: str, asset_id: str) -> dict[str, Any]:
        if self._attempt_record(playthrough_id) is None:
            raise KeyError("attempt_not_found")
        return asdict(self.authority.read_asset(LEARNER, playthrough_id, item_id, asset_id))

    def debrief(self, playthrough_id: str) -> dict[str, Any]:
        if self._attempt_record(playthrough_id) is None:
            raise KeyError("attempt_not_found")
        if self.debrief_unavailable:
            raise RuntimeError("debrief_unavailable")
        projection = self.authority.project(LEARNER, playthrough_id)
        if projection.data.get("submission") is None:
            raise ValueError("submission_required")
        return {"debrief": projection.data.get("debrief")}

    def set_scenario(self, value: Mapping[str, Any]) -> dict[str, Any]:
        dialogue_outcome = value.get("dialogue_outcome", self.dialogue_outcome)
        debrief_unavailable = value.get("debrief_unavailable", self.debrief_unavailable)
        order_response_failure = value.get("order_response_failure", self.order_response_failure)
        if dialogue_outcome not in {"success", "unavailable"}:
            raise ValueError("invalid_dialogue_scenario")
        if not isinstance(debrief_unavailable, bool):
            raise ValueError("invalid_debrief_scenario")
        if order_response_failure not in {"none", "before_commit", "after_commit"}:
            raise ValueError("invalid_order_response_scenario")
        with self.lock:
            self.dialogue_outcome = dialogue_outcome
            self.debrief_unavailable = debrief_unavailable
            self.order_response_failure = order_response_failure
            self.authority.luna.dialogue_outcome = dialogue_outcome
            return {
                "dialogue_outcome": self.dialogue_outcome,
                "debrief_unavailable": self.debrief_unavailable,
                "order_response_failure": self.order_response_failure,
            }


class Handler(SimpleHTTPRequestHandler):
    server_version = "FixturePlayerPrototype/0.1"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    @property
    def service(self) -> PrototypeService:
        return self.server.prototype_service  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        # Keep the local terminal focused on startup and errors, not polling.
        if args and len(args) > 1 and str(args[1]).startswith("5"):
            super().log_message(format, *args)

    def _send_json(self, value: Any, status: int = 200) -> None:
        encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _send_error_json(self, code: str, status: int) -> None:
        self._send_json({"error": code}, status)

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("invalid_content_length") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("request_body_too_large")
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("invalid_json") from exc
        if not isinstance(payload, dict):
            raise ValueError("json_object_required")
        return payload

    @staticmethod
    def _required_string(data: Mapping[str, Any], key: str, limit: int = 256) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value or len(value) > limit:
            raise ValueError(f"invalid_{key}")
        return value

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/api/bootstrap":
            self._send_json(self.service.bootstrap())
            return
        params = parse_qs(parsed.query)
        if parsed.path == "/api/projection":
            try:
                attempt_id = self._required_string({"attempt_id": params.get("attempt_id", [""])[0]}, "attempt_id")
                self._send_json(self.service._projection(attempt_id))
            except KeyError:
                self._send_error_json("attempt_not_found", 404)
            return
        if parsed.path == "/api/asset":
            try:
                attempt_id = self._required_string({"attempt_id": params.get("attempt_id", [""])[0]}, "attempt_id")
                item_id = self._required_string({"item_id": params.get("item_id", [""])[0]}, "item_id", 16)
                asset_id = params.get("asset_id", ["primary"])[0]
                if asset_id not in {"primary", "accessible-text"}:
                    raise ValueError("invalid_asset_id")
                self._send_json(self.service.read_asset(attempt_id, item_id, asset_id))
            except KeyError:
                self._send_error_json("attempt_not_found", 404)
            except ValueError as exc:
                self._send_error_json(str(exc), 400)
            return
        if parsed.path == "/api/debrief":
            try:
                attempt_id = self._required_string({"attempt_id": params.get("attempt_id", [""])[0]}, "attempt_id")
                self._send_json(self.service.debrief(attempt_id))
            except KeyError:
                self._send_error_json("attempt_not_found", 404)
            except RuntimeError as exc:
                self._send_error_json(str(exc), 503)
            except ValueError as exc:
                self._send_error_json(str(exc), 409)
            return
        super().do_GET()

    def do_POST(self) -> None:
        try:
            data = self._read_json()
        except ValueError as exc:
            self._send_error_json(str(exc), 400)
            return
        try:
            if self.path == "/api/generate":
                self._send_json(self.service.generate_case())
                return
            if self.path == "/api/attempts":
                self._send_json(self.service.start_attempt())
                return
            if self.path == "/api/command":
                attempt_id = self._required_string(data, "attempt_id")
                command_id = self._required_string(data, "command_id", 128)
                kind = self._required_string(data, "kind", 64)
                expected_revision = data.get("expected_revision")
                if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
                    raise ValueError("invalid_expected_revision")
                payload = data.get("payload", {})
                if not isinstance(payload, dict):
                    raise ValueError("invalid_payload")
                failure = self.service.consume_order_response_failure(kind)
                if failure == "before_commit":
                    self._send_error_json("simulated_order_response_lost", 503)
                    return
                result = self.service.command(attempt_id, command_id, expected_revision, kind, payload)
                if failure == "after_commit" and result["receipt"]["status"] == "committed":
                    self._send_error_json("simulated_order_response_lost", 503)
                    return
                self._send_json(result)
                return
            if self.path == "/api/fixture/release":
                attempt_id = self._required_string(data, "attempt_id")
                item_id = self._required_string(data, "item_id", 16)
                expected_revision = data.get("expected_revision")
                if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
                    raise ValueError("invalid_expected_revision")
                self._send_json(self.service.release_fixture_result(attempt_id, item_id, expected_revision))
                return
            if self.path == "/api/prototype/scenario":
                self._send_json(self.service.set_scenario(data))
                return
            self._send_error_json("route_not_found", 404)
        except KeyError:
            self._send_error_json("attempt_not_found", 404)
        except ValueError as exc:
            self._send_error_json(str(exc), 400)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Fixture-A player UI prototype")
    parser.add_argument("--host", default="127.0.0.1", help="loopback host only")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "medical-diagnostics-game-player-ui-prototype",
        help="local SQLite and attempt metadata directory",
    )
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("this prototype must bind to loopback")
    service = PrototypeService(args.data_dir)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.prototype_service = service  # type: ignore[attr-defined]
    server.daemon_threads = True
    bound_port = server.server_address[1]
    print(f"Local synthetic player prototype: http://{args.host}:{bound_port}/")
    print(f"Fixture data directory: {args.data_dir.resolve()}")
    print("Press Ctrl+C to stop. No external services or models are called.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local prototype.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
