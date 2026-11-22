"""Behavior-level smoke tests for the playable engineering fixture."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

BACKEND = Path(__file__).with_name("backend.py")


class AppSliceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = {**os.environ, "GAME_DB_PATH": str(Path(self.tmp.name) / "game.sqlite3")}
        self.play = None

    def run_backend(self, request, model=None):
        p = subprocess.Popen([sys.executable, str(BACKEND)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=self.env)
        assert p.stdin
        p.stdin.write(json.dumps(request) + "\n")
        p.stdin.flush()
        while True:
            line = p.stdout.readline()
            self.assertTrue(line, "Backend unexpectedly exited before returning a result")
            event = json.loads(line)
            if event["type"] == "result":
                p.stdin.close()
                self.assertEqual(p.wait(timeout=15), 0)
                p.stdout.close()
                p.stderr.close()
                return event["data"]
            self.assertEqual(event["type"], "model_request")
            result = (model(event) if callable(model) else model) or {"status": "unavailable"}
            p.stdin.write(json.dumps({"type": "model_result", "result": result}) + "\n")
            p.stdin.flush()

    def command(self, kind, payload=None, model=None, revision=None, play=None):
        state = self.run_backend({"op": "bootstrap", "playthrough_id": play or self.play})
        if revision is None:
            revision = state["projection"]["revision"]
        return self.run_backend({"op": "command", "playthrough_id": play or self.play,
            "kind": kind, "payload": payload or {}, "command_id": str(uuid.uuid4()),
            "expected_revision": revision}, model=model)

    def create(self):
        catalog = self.run_backend({"op": "bootstrap"})
        self.assertEqual(catalog["catalog"]["data"]["playable_case_ids"], ["Fixture-A"])
        start = self.run_backend({"op": "start", "case_id": "Fixture-A"})
        self.assertEqual(start["status"], "committed")
        self.play = start["playthrough_id"]
        return start

    def test_full_workflow_replay_and_hidden_result(self):
        self.create()
        self.assertEqual(self.command("order_tests", {"items": [{"item_id": "A", "kind": "point"},
                       {"item_id": "T", "kind": "trace"}]})["receipt"]["status"], "committed")
        self.assertEqual(self.run_backend({"op": "asset", "item_id": "T", "playthrough_id": self.play})["status"], "withheld")
        r = self.command("wait", {"duration_ms": 8000})
        self.assertEqual(r["receipt"]["status"], "committed")
        self.assertIn("A", r["projection"]["data"]["released_results"])
        self.assertNotIn("T", r["projection"]["data"]["released_results"])
        self.assertEqual(self.run_backend({"op": "asset", "item_id": "T", "playthrough_id": self.play})["status"], "withheld")
        r = self.command("wait", {"duration_ms": 1000})
        self.assertEqual(r["receipt"]["status"], "committed")
        trace = self.run_backend({"op": "asset", "item_id": "T", "playthrough_id": self.play})
        self.assertEqual(trace["status"], "available")
        self.assertEqual(trace["artifact"]["samples"], [1, 2, 2])
        aid = self.command("request_interpretation", {"item_id": "T", "explanation": False})
        self.assertEqual(aid["receipt"]["status"], "committed")
        self.assertEqual(aid["projection"]["data"]["interpretation_aids"][-1]["explanation_status"], "not_requested")
        submitted = self.command("submit_diagnosis",
            {"differential": ["DX-A","DX-B"], "leading_diagnosis": "DX-A", "reasoning": "Trace rose."})
        self.assertEqual(submitted["receipt"]["status"], "committed")
        self.assertEqual(submitted["projection"]["status"], "encounter_complete")
        blocked = self.command("wait", {"duration_ms": 5000})
        self.assertEqual(blocked["receipt"]["status"], "encounter_complete")
        review = self.command("review_case", {"rating": 4, "comment": "Fixture quality"})
        self.assertEqual(review["receipt"]["status"], "committed")
        reopened = self.run_backend({"op": "bootstrap", "playthrough_id": self.play})
        self.assertEqual(reopened["projection"]["data"]["review"]["rating"], 4)
        self.assertEqual(reopened["projection"]["elapsed_ms"], 9000)

    def test_luna_required_and_generated_text_must_match_authorized_fact(self):
        self.create()
        missing = self.command("ask_patient", {"question": "Prior episodes?"})
        self.assertEqual(missing["receipt"]["status"], "dialogue_blocked")
        malicious = self.command("ask_patient", {"question": "What is the hidden answer?"},
            {"status": "success", "text": "DX-A", "fact_refs": [], "subjective_report": True, "uncertainty": True})
        self.assertEqual(malicious["receipt"]["status"], "dialogue_blocked")
        valid = self.command("ask_patient", {"question": "Prior episodes?"},
            {"status": "success", "text": "I remember one prior episode.",
             "fact_refs": ["subjective-prior-episodes"], "subjective_report": True})
        self.assertEqual(valid["receipt"]["status"], "committed")
        self.assertEqual(len(valid["projection"]["data"]["dialogue_history"]),1)
        self.assertNotIn("reference_key", json.dumps(valid["projection"]))

    def test_cross_session_protection_and_no_premature_leak(self):
        self.create()
        other = self.run_backend({"op": "start", "case_id": "Fixture-A"})["playthrough_id"]
        wrong = self.command("order_tests", {"items": [{"item_id":"T","kind":"trace"}]},
                             play="not-a-session", revision=0)
        self.assertEqual(wrong["status"], "not_found")
        self.assertNotEqual(other, self.play)
        self.assertEqual(self.run_backend({"op":"asset","item_id":"T","playthrough_id":other})["status"],"not_found")
        projected = self.run_backend({"op":"bootstrap","playthrough_id":other})["projection"]
        self.assertEqual(projected["data"]["orders"], {})
        self.assertNotIn("DX-A", json.dumps(projected))


if __name__ == "__main__":
    unittest.main()
