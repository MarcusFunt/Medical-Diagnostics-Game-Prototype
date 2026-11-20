import importlib
import importlib.util
import inspect
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier


class GateAPortContractTests(unittest.TestCase):
    def test_public_port_exports_adapter_boundary_types(self):
        spec = importlib.util.find_spec("port")
        self.assertIsNotNone(spec, "Gate A public port module is not implemented")
        module = importlib.import_module("port")
        for name in (
            "Actor",
            "Command",
            "Receipt",
            "Projection",
            "ArtifactAccess",
            "ClinicalEvent",
            "GateAPort",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(module, name), f"missing public type: {name}")
        self.assertTrue(hasattr(module.GateAPort, "artifact_metadata"))
        self.assertTrue(hasattr(module.GateAPort, "read_asset"))

    def test_sqlite_authority_is_available(self):
        spec = importlib.util.find_spec("authority")
        self.assertIsNotNone(spec, "SQLite authority module is not implemented")
        module = importlib.import_module("authority")
        self.assertTrue(hasattr(module, "SQLiteAuthority"))
        for name in ("execute", "project", "read_artifact", "trusted_events"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(module.SQLiteAuthority, name), f"missing port operation: {name}")


    def test_worker_stub_exposes_bound_candidate_types(self):
        spec = importlib.util.find_spec("workers")
        self.assertIsNotNone(spec, "Gate A worker stub module is not implemented")
        module = importlib.import_module("workers")
        for name in ("WorkerCandidate", "StubWorker"):
            with self.subTest(name=name):
                self.assertTrue(hasattr(module, name), f"missing worker type: {name}")

    def test_authority_and_fixture_accept_worker_injection(self):
        authority = importlib.import_module("authority")
        fixture = importlib.import_module("fixture")
        self.assertIn("worker", inspect.signature(authority.SQLiteAuthority.__init__).parameters)
        self.assertIn("worker", inspect.signature(fixture.make_fixture).parameters)

    def test_luna_stub_is_injected_without_provider_substitution(self):
        spec = importlib.util.find_spec("luna")
        self.assertIsNotNone(spec, "Gate A Luna stub is not implemented")
        luna = importlib.import_module("luna")
        self.assertTrue(hasattr(luna, "LunaStub"))
        authority = importlib.import_module("authority")
        fixture = importlib.import_module("fixture")
        self.assertIn("luna", inspect.signature(authority.SQLiteAuthority.__init__).parameters)
        self.assertIn("luna", inspect.signature(fixture.make_fixture).parameters)
    def test_fixture_factory_is_available(self):
        spec = importlib.util.find_spec("fixture")
        self.assertIsNotNone(spec, "Fixture-A factory is not implemented")
        module = importlib.import_module("fixture")
        self.assertTrue(hasattr(module, "make_fixture"))
        parameters = inspect.signature(module.make_fixture).parameters
        self.assertIn("db_path", parameters)
        self.assertIn("initialize", parameters)


from fixture import make_fixture
from port import Actor, Command


class GateA01To03Tests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.db_path = Path(self.tempdir.name) / "gate-a.sqlite"
        self.rig = make_fixture(self.db_path, initialize=False)
        self.authority = self.rig.authority
        self.learner = self.rig.learner

    def generate(self, command_id="generate-1", mandatory_evidence=True, expected_revision=0):
        return self.authority.execute(
            self.learner,
            Command(
                command_id=command_id,
                target_id="catalog",
                expected_revision=expected_revision,
                kind="generate_case",
                payload={
                    "case_id": "Fixture-A",
                    "mandatory_evidence": mandatory_evidence,
                },
            ),
        )

    def start(self, playthrough_id):
        return self.authority.execute(
            self.learner,
            Command(
                command_id=f"start-{playthrough_id}",
                target_id="case:Fixture-A",
                expected_revision=None,
                kind="start_playthrough",
                payload={"playthrough_id": playthrough_id},
            ),
        )

    def execute_play(self, command_id, kind, payload, expected_revision=None, actor=None, playthrough_id=None):
        target = playthrough_id or self.rig.playthrough_id
        if expected_revision is None:
            expected_revision = self.authority.project(self.learner, target).revision
        return self.authority.execute(
            actor or self.learner,
            Command(
                command_id=command_id,
                target_id=target,
                expected_revision=expected_revision,
                kind=kind,
                payload=payload,
            ),
        )

    def seed_play(self, playthrough_id="play-1"):
        generated = self.generate()
        self.assertEqual(generated.status, "committed")
        started = self.start(playthrough_id)
        self.assertEqual(started.status, "committed")
        return playthrough_id

    @staticmethod
    def orders_payload(*items):
        return {"items": [{"item_id": item_id, "kind": kind} for item_id, kind in items]}

    def test_a01_generation_retry_publishes_once_and_playthroughs_are_independent(self):
        first = self.generate()
        self.assertEqual(first.status, "committed")
        retry = self.generate()
        self.assertTrue(retry.replayed)
        self.assertEqual(retry.data["case_version_id"], first.data["case_version_id"])

        first_play = self.start("play-1")
        second_play = self.start("play-2")
        self.assertEqual(first_play.status, "committed")
        self.assertEqual(second_play.status, "committed")
        for playthrough_id in ("play-1", "play-2"):
            projection = self.authority.project(self.learner, playthrough_id)
            self.assertEqual(projection.elapsed_ms, 0)
            initial = [event for event in self.authority.trusted_events(playthrough_id) if event.kind == "case_initialized"]
            self.assertEqual(len(initial), 1)
            self.assertEqual(initial[0].payload["x"], 1)

        rejected = self.generate("generate-missing-evidence", mandatory_evidence=False, expected_revision=1)
        self.assertEqual(rejected.status, "generation_failed")
        catalog = self.authority.project(self.learner, "catalog")
        self.assertEqual(catalog.data["playable_case_ids"], ["Fixture-A"])
        self.assertEqual(catalog.data["publication_count"], 1)

    def test_a02_retries_stale_commands_and_receipts_obey_authority(self):
        self.seed_play()
        original = Command(
            "order-a",
            "play-1",
            0,
            "order_tests",
            self.orders_payload(("A", "point")),
        )
        first = self.authority.execute(self.learner, original)
        self.assertEqual(first.status, "committed")

        other_orders = self.execute_play(
            "order-bt",
            "order_tests",
            self.orders_payload(("B", "point"), ("T", "trace")),
        )
        self.assertEqual(other_orders.status, "committed")

        retry = self.authority.execute(self.learner, original)
        self.assertTrue(retry.replayed)
        self.assertEqual(retry.data, first.data)
        refreshed_precondition_retry = self.authority.execute(
            self.learner,
            Command("order-a", "play-1", 999, "order_tests", original.payload),
        )
        self.assertTrue(refreshed_precondition_retry.replayed)
        self.assertEqual(refreshed_precondition_retry.data, first.data)

        modified = Command(
            "order-a",
            "play-1",
            0,
            "order_tests",
            self.orders_payload(("A", "point"), ("X", "point")),
        )
        self.assertEqual(self.authority.execute(self.learner, modified).status, "idempotency_conflict")

        stale = Command(
            "new-stale-command",
            "play-1",
            0,
            "order_tests",
            self.orders_payload(("C", "point")),
        )
        self.assertEqual(self.authority.execute(self.learner, stale).status, "revision_conflict")

        unauthorized = self.authority.execute(
            self.rig.other_learner,
            Command("order-a", "play-1", 0, "order_tests", original.payload),
        )
        self.assertEqual(unauthorized.status, "forbidden")
        projection = self.authority.project(self.learner, "play-1")
        self.assertEqual(set(projection.data["orders"]), {"A", "B", "T"})

    def test_a02_concurrent_duplicate_commands_have_one_canonical_effect(self):
        self.seed_play()
        other_connection = type(self.authority)(self.db_path)
        duplicate = Command(
            "concurrent-order",
            "play-1",
            0,
            "order_tests",
            self.orders_payload(("A", "point")),
        )
        barrier = Barrier(2)

        def submit(authority):
            barrier.wait()
            return authority.execute(self.learner, duplicate)

        with ThreadPoolExecutor(max_workers=2) as pool:
            receipts = list(pool.map(submit, (self.authority, other_connection)))

        self.assertEqual(sum(not receipt.replayed for receipt in receipts), 1)
        self.assertEqual(sum(receipt.replayed for receipt in receipts), 1)
        projection = self.authority.project(self.learner, "play-1")
        self.assertEqual(list(projection.data["orders"]), ["A"])

    def test_a02_idempotency_keys_are_scoped_to_the_target(self):
        self.seed_play("play-1")
        self.assertEqual(self.start("play-2").status, "committed")
        first = self.authority.execute(
            self.learner,
            Command("same-key", "play-1", 0, "order_tests", self.orders_payload(("A", "point"))),
        )
        second = self.authority.execute(
            self.learner,
            Command("same-key", "play-2", 0, "order_tests", self.orders_payload(("B", "point"))),
        )
        self.assertEqual((first.status, second.status), ("committed", "committed"))
        self.assertEqual(set(self.authority.project(self.learner, "play-1").data["orders"]), {"A"})
        self.assertEqual(set(self.authority.project(self.learner, "play-2").data["orders"]), {"B"})


    def test_database_handle_is_released_after_query_boundaries(self):
        self.seed_play()
        self.authority.project(self.learner, "play-1")
        self.authority.read_artifact(self.learner, "play-1", "missing")
        self.authority.trusted_events("play-1")
        try:
            self.db_path.unlink()
        except PermissionError as error:
            self.fail(f"SQLite query left a live file handle: {error}")
    def test_a03_partitioned_advances_preserve_transition_and_acquisitions(self):
        def run_path(path_name, durations, observe=False):
            db_path = Path(self.tempdir.name) / f"{path_name}.sqlite"
            rig = make_fixture(db_path, initialize=True, playthrough_id="play-1")
            port = rig.authority
            orders_receipt = port.execute(
                rig.learner,
                Command(
                    f"orders-{path_name}",
                    "play-1",
                    0,
                    "order_tests",
                    self.orders_payload(("A", "point"), ("B", "point"), ("T", "trace")),
                ),
            )
            self.assertEqual(orders_receipt.status, "committed")
            if observe:
                before = port.project(rig.learner, "play-1")
                port.project(rig.learner, "play-1")
                port.read_artifact(rig.learner, "play-1", "T")
                after = port.project(rig.learner, "play-1")
                self.assertEqual(before.elapsed_ms, 0)
                self.assertEqual(after.elapsed_ms, 0)
                zero_wait = port.execute(
                    rig.learner,
                    Command(
                        f"zero-wait-{path_name}",
                        "play-1",
                        after.revision,
                        "wait",
                        {"duration_ms": 0},
                    ),
                )
                self.assertEqual(zero_wait.status, "committed")
                self.assertEqual(port.project(rig.learner, "play-1").elapsed_ms, 0)
            for index, duration in enumerate(durations):
                current = port.project(rig.learner, "play-1")
                receipt = port.execute(
                    rig.learner,
                    Command(
                        f"wait-{path_name}-{index}",
                        "play-1",
                        current.revision,
                        "wait",
                        {"duration_ms": duration},
                    ),
                )
                self.assertEqual(receipt.status, "committed")
            current = port.project(rig.learner, "play-1")
            self.assertEqual(current.elapsed_ms, 5500)
            events = list(port.trusted_events("play-1"))
            transition = [event for event in events if event.kind == "disease_transition" and event.clinical_time_ms == 5000]
            point = [event for event in events if event.kind == "point_captured" and event.clinical_time_ms == 5000]
            trace = [event for event in events if event.kind == "trace_sample" and event.subject_id == "T"]
            self.assertEqual(len(transition), 1)
            self.assertEqual(transition[0].payload["x"], 2)
            self.assertEqual({event.subject_id: event.payload["value"] for event in point}, {"A": 2, "B": 2})
            samples = [(event.clinical_time_ms, event.payload["value"]) for event in trace]
            self.assertEqual(samples, [(4999, 1), (5000, 2), (5001, 2)])
            at_five = [event for event in events if event.clinical_time_ms == 5000]
            transition_sequence = transition[0].event_sequence
            self.assertLess(transition_sequence, min(event.event_sequence for event in at_five if event.kind in ("point_captured", "trace_sample")))
            return [(event.clinical_time_ms, event.kind, event.subject_id, dict(event.payload)) for event in events]

        single = run_path("single", [5000, 500], observe=True)
        partitioned = run_path("partitioned", [2500, 2500, 500])
        self.assertEqual(single, partitioned)



from workers import StubWorker, WorkerCandidate


class GateA04To06And11Tests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def rig(self, name, worker=None):
        return make_fixture(
            Path(self.tempdir.name) / f"{name}.sqlite",
            initialize=True,
            playthrough_id="play-1",
            worker=worker,
        )

    @staticmethod
    def execute(rig, command_id, kind, payload, actor=None, expected_revision=None):
        authority = rig.authority
        learner = rig.learner
        if expected_revision is None:
            expected_revision = authority.project(learner, rig.playthrough_id).revision
        return authority.execute(
            actor or learner,
            Command(command_id, rig.playthrough_id, expected_revision, kind, payload),
        )

    def order(self, rig, *items):
        return self.execute(
            rig,
            "orders-initial" if not rig.authority.project(rig.learner, rig.playthrough_id).data["orders"] else f"orders-{len(rig.authority.project(rig.learner, rig.playthrough_id).data['orders'])}",
            "order_tests",
            {"items": [{"item_id": item_id, "kind": kind} for item_id, kind in items]},
        )

    def advance(self, rig, duration_ms, command_id):
        return self.execute(rig, command_id, "wait", {"duration_ms": duration_ms})

    def capture_event(self, rig, item_id):
        events = list(rig.authority.trusted_events(rig.playthrough_id))
        if item_id == "T":
            matches = [event for event in events if event.kind == "trace_sample" and event.subject_id == item_id and event.payload.get("offset_ms") == 2]
        else:
            matches = [event for event in events if event.kind == "point_captured" and event.subject_id == item_id]
        self.assertEqual(len(matches), 1)
        event = matches[0]
        for field in ("acquisition_id", "input_hash", "investigation_version", "adapter_version", "validation_policy_version"):
            self.assertIn(field, event.payload)
        return event

    def candidate(self, rig, item_id, outcome="ready", failure_cause=None):
        event = self.capture_event(rig, item_id)
        payload = event.payload
        if item_id == "T":
            samples = [
                sample.payload["value"]
                for sample in rig.authority.trusted_events(rig.playthrough_id)
                if sample.kind == "trace_sample" and sample.subject_id == "T"
            ]
            result = {"samples": samples, "interpretation": "supports DX-A", "units": "fixture-unit"}
        else:
            result = {"value": payload["value"], "units": "fixture-unit"}
        if outcome == "failed":
            result = {}
        return WorkerCandidate(
            playthrough_id=rig.playthrough_id,
            item_id=item_id,
            acquisition_id=payload["acquisition_id"],
            input_hash=payload["input_hash"],
            investigation_version=payload["investigation_version"],
            adapter_version=payload["adapter_version"],
            validation_policy_version=payload["validation_policy_version"],
            outcome=outcome,
            result=result,
            failure_cause=failure_cause,
        )

    def prepare_initial_orders(self, rig, *items):
        self.assertEqual(self.order(rig, *items).status, "committed")
        self.assertEqual(self.advance(rig, 5500, "wait-to-5500").status, "committed")

    def test_a04_worker_results_stay_bound_across_revisions_and_cancelled_b_is_discarded(self):
        for index, arrive_before_revision in enumerate((True, False)):
            with self.subTest(arrive_before_revision=arrive_before_revision):
                rig = self.rig(f"a04-{index}")
                self.prepare_initial_orders(rig, ("A", "point"), ("B", "point"), ("T", "trace"))
                candidates = {item: self.candidate(rig, item) for item in ("A", "B", "T")}
                if arrive_before_revision:
                    rig.worker.offer(candidates["A"])
                    rig.worker.offer(candidates["T"])
                self.assertEqual(self.advance(rig, 0, f"intervening-{index}").status, "committed")
                if not arrive_before_revision:
                    rig.worker.offer(candidates["A"])
                    rig.worker.offer(candidates["T"])

                cancelled = self.execute(rig, f"cancel-B-{index}", "cancel_order", {"item_id": "B"})
                self.assertEqual(cancelled.status, "committed")
                rig.worker.offer(candidates["B"])
                self.assertEqual(self.advance(rig, 500, f"wait-to-6000-{index}").status, "committed")
                self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "A").status, "withheld")
                self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").status, "withheld")
                self.assertEqual(rig.authority.project(rig.learner, rig.playthrough_id).data["orders"]["B"]["status"], "cancelled")

                self.assertEqual(self.advance(rig, 2000, f"wait-to-8000-{index}").status, "committed")
                point = rig.authority.read_artifact(rig.learner, rig.playthrough_id, "A")
                self.assertEqual(point.status, "available")
                self.assertEqual(point.artifact["value"], 2)
                self.assertEqual(point.artifact["collected_at_ms"], 5000)
                self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").status, "withheld")
                self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "B").status, "cancelled")

    def test_a04_cancellation_at_processing_cutoff_is_rejected_and_b_releases(self):
        rig = self.rig("a04-cutoff")
        self.prepare_initial_orders(rig, ("A", "point"), ("B", "point"), ("T", "trace"))
        for item_id in ("A", "B", "T"):
            rig.worker.offer(self.candidate(rig, item_id))
        self.assertEqual(self.advance(rig, 500, "wait-to-6000").status, "committed")
        rejected = self.execute(rig, "cancel-B-at-cutoff", "cancel_order", {"item_id": "B"})
        self.assertEqual(rejected.status, "cancellation_closed")
        self.assertEqual(self.advance(rig, 2000, "wait-to-8000").status, "committed")
        result = rig.authority.read_artifact(rig.learner, rig.playthrough_id, "B")
        self.assertEqual(result.status, "available")
        self.assertEqual(result.artifact["value"], 2)

    def test_a05_processing_block_is_atomic_and_retry_commits_once(self):
        rig = self.rig("a05-retry")
        self.prepare_initial_orders(rig, ("A", "point"))
        before = rig.authority.project(rig.learner, rig.playthrough_id)
        due = Command("wait-to-6000", rig.playthrough_id, before.revision, "wait", {"duration_ms": 500})
        blocked = rig.authority.execute(rig.learner, due)
        self.assertEqual(blocked.status, "processing_blocked")
        after_block = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertEqual((after_block.elapsed_ms, after_block.revision), (before.elapsed_ms, before.revision))

        rig.worker.offer(self.candidate(rig, "A"))
        retried = rig.authority.execute(rig.learner, due)
        self.assertEqual(retried.status, "committed")
        self.assertEqual(rig.authority.project(rig.learner, rig.playthrough_id).elapsed_ms, 6000)
        self.assertEqual(rig.authority.execute(rig.learner, due).replayed, True)

    def test_a05_terminal_worker_failure_has_cause_and_no_measurement(self):
        rig = self.rig("a05-terminal")
        self.prepare_initial_orders(rig, ("A", "point"))
        rig.worker.offer(self.candidate(rig, "A", outcome="failed", failure_cause="solver_timeout"))
        self.assertEqual(self.advance(rig, 500, "terminal-wait").status, "committed")
        order = rig.authority.project(rig.learner, rig.playthrough_id).data["orders"]["A"]
        self.assertEqual(order["status"], "failed")
        self.assertEqual(order["failure_cause"], "solver_timeout")
        self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "A").status, "failed")

    def _save_at_cancelled_b_boundary(self, name, auto_prepare):
        rig = self.rig(name, worker=StubWorker(auto_prepare=auto_prepare))
        self.prepare_initial_orders(rig, ("A", "point"), ("B", "point"), ("T", "trace"))
        self.assertEqual(self.execute(rig, "cancel-B", "cancel_order", {"item_id": "B"}).status, "committed")
        return rig

    def _continue_uninterrupted(self, rig):
        self.assertEqual(self.advance(rig, 3500, "wait-to-9000").status, "committed")
        self.assertEqual(self.order(rig, ("C", "point")).status, "committed")
        self.assertEqual(self.advance(rig, 4000, "wait-to-13000").status, "committed")
        return {
            "projection": rig.authority.project(rig.learner, rig.playthrough_id),
            "events": rig.authority.trusted_events(rig.playthrough_id),
        }

    def test_a06_fresh_process_resume_matches_uninterrupted_next_acquisition(self):
        uninterrupted = self._continue_uninterrupted(self._save_at_cancelled_b_boundary("a06-live", True))
        resumed_rig = self._save_at_cancelled_b_boundary("a06-resume", False)
        probe = Path(__file__).with_name("resume_probe.py")
        completed = __import__("subprocess").run(
            [
                __import__("sys").executable,
                str(probe),
                "--db",
                str(resumed_rig.authority.db_path),
                "--playthrough",
                resumed_rig.playthrough_id,
                "--continue-a06",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        resumed = __import__("json").loads(completed.stdout)
        live_projection = uninterrupted["projection"]
        events = resumed_rig.authority.trusted_events(resumed_rig.playthrough_id)
        c_capture = [event for event in events if event.kind == "point_captured" and event.subject_id == "C"]
        self.assertEqual(len(c_capture), 1)
        self.assertEqual((c_capture[0].clinical_time_ms, c_capture[0].payload["value"]), (11000, 3))
        projection = resumed["projection"]
        self.assertEqual(projection["elapsed_ms"], 13000)
        self.assertEqual(projection["data"]["released_results"]["C"]["released_at_ms"], 13000)
        self.assertEqual(projection["data"]["released_results"]["A"]["value"], 2)
        self.assertEqual(projection, __import__("dataclasses").asdict(live_projection))
        self.assertEqual(resumed["events"], [__import__("dataclasses").asdict(event) for event in uninterrupted["events"]])

    def test_a06_missing_continuation_dependency_blocks_without_changing_history(self):
        rig = self._save_at_cancelled_b_boundary("a06-missing", False)
        before = rig.authority.project(rig.learner, rig.playthrough_id)
        import json
        import sqlite3

        connection = sqlite3.connect(rig.authority.db_path)
        try:
            payload = json.loads(connection.execute("SELECT payload FROM authority_state WHERE singleton=1").fetchone()[0])
            payload["plays"][rig.playthrough_id]["continuation"]["adapter_version"] = "missing-adapter-v99"
            connection.execute("UPDATE authority_state SET payload=? WHERE singleton=1", (json.dumps(payload),))
            connection.commit()
        finally:
            connection.close()

        restored = type(rig.authority)(rig.authority.db_path, worker=StubWorker(auto_prepare=True))
        blocked = restored.execute(
            rig.learner,
            Command("blocked-restore", rig.playthrough_id, before.revision, "wait", {"duration_ms": 1}),
        )
        after = restored.project(rig.learner, rig.playthrough_id)
        self.assertEqual(blocked.status, "restore_blocked")
        self.assertEqual((after.elapsed_ms, after.revision), (before.elapsed_ms, before.revision))

    def test_a11_submission_cutoff_preserves_same_boundary_release_and_rejects_late_work(self):
        rig = self.rig("a11-release", worker=StubWorker(auto_prepare=True))
        self.order(rig, ("A", "point"), ("T", "trace"))
        self.assertEqual(self.advance(rig, 8000, "wait-to-8000").status, "committed")
        self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "A").status, "available")
        self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").status, "withheld")
        late = self.candidate(rig, "T")
        self.assertEqual(self.execute(rig, "submit-at-8000", "submit_diagnosis", {"leading_diagnosis": "DX-A"}).status, "committed")
        completed = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertEqual(completed.elapsed_ms, 8000)
        self.assertEqual(completed.data["orders"]["T"]["status"], "closed_at_submission")
        self.assertEqual(completed.data["orders"]["A"]["status"], "released")
        rig.worker.offer(late)
        self.assertEqual(self.advance(rig, 5000, "late-wait").status, "encounter_complete")
        self.assertEqual(rig.authority.project(rig.learner, rig.playthrough_id).elapsed_ms, 8000)
        self.assertEqual(rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").status, "withheld")
        self.assertFalse(any(event.kind == "result_released" and event.subject_id == "T" for event in rig.authority.trusted_events(rig.playthrough_id)))

    def test_a11_submission_closes_collecting_and_processing_items(self):
        collecting = self.rig("a11-collecting")
        self.order(collecting, ("T", "trace"))
        self.assertEqual(self.advance(collecting, 5000, "collecting-wait").status, "committed")
        self.assertEqual(collecting.authority.project(collecting.learner, collecting.playthrough_id).data["orders"]["T"]["status"], "collecting")
        self.assertEqual(self.execute(collecting, "collecting-submit", "submit_diagnosis", {}).status, "committed")
        closed = collecting.authority.project(collecting.learner, collecting.playthrough_id)
        self.assertEqual(closed.data["orders"]["T"]["status"], "closed_at_submission")
        self.assertEqual(closed.data["orders"]["T"]["pre_close_state"], "collecting")
        self.assertEqual(self.advance(collecting, 1000, "collecting-late-wait").status, "encounter_complete")
        self.assertFalse(any(event.kind == "trace_sample" and event.clinical_time_ms == 5001 for event in collecting.authority.trusted_events(collecting.playthrough_id)))

        processing = self.rig("a11-processing")
        self.order(processing, ("A", "point"))
        self.assertEqual(self.advance(processing, 5500, "processing-wait").status, "committed")
        self.assertEqual(processing.authority.project(processing.learner, processing.playthrough_id).data["orders"]["A"]["status"], "processing")
        late = self.candidate(processing, "A")
        self.assertEqual(self.execute(processing, "processing-submit", "submit_diagnosis", {}).status, "committed")
        processing.worker.offer(late)
        self.assertEqual(self.advance(processing, 1000, "processing-late-wait").status, "encounter_complete")
        closed = processing.authority.project(processing.learner, processing.playthrough_id)
        self.assertEqual(closed.data["orders"]["A"]["status"], "closed_at_submission")
        self.assertEqual(closed.data["orders"]["A"]["pre_close_state"], "processing")
        self.assertFalse(any(event.kind == "result_released" and event.subject_id == "A" for event in processing.authority.trusted_events(processing.playthrough_id)))


class GateA07To10Tests(unittest.TestCase):
    FIXED_REASONING = "The point sample was 2 and the trace rose from 1 to 2."

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def rig(self, name, worker=None, luna=None):
        return make_fixture(
            Path(self.tempdir.name) / f"{name}.sqlite",
            initialize=True,
            worker=worker,
            luna=luna,
        )

    @staticmethod
    def execute(rig, command_id, kind, payload, actor=None, expected_revision=None):
        authority = rig.authority
        learner = rig.learner
        if expected_revision is None:
            expected_revision = authority.project(learner, rig.playthrough_id).revision
        return authority.execute(
            actor or learner,
            Command(command_id, rig.playthrough_id, expected_revision, kind, payload),
        )

    def order(self, rig, *items):
        return self.execute(
            rig,
            f"orders-{rig.authority.project(rig.learner, rig.playthrough_id).revision}",
            "order_tests",
            {"items": [{"item_id": item_id, "kind": kind} for item_id, kind in items]},
        )

    def wait(self, rig, duration, command_id):
        return self.execute(rig, command_id, "wait", {"duration_ms": duration})

    def candidate(self, rig, item_id, *, result=None):
        events = rig.authority.trusted_events(rig.playthrough_id)
        if item_id == "T":
            event = next(event for event in events if event.kind == "trace_sample" and event.subject_id == item_id and event.payload.get("offset_ms") == 2)
            samples = [event.payload["value"] for event in events if event.kind == "trace_sample" and event.subject_id == item_id]
            default = {"samples": samples, "interpretation": "supports DX-A", "units": "fixture-unit"}
        else:
            event = next(event for event in events if event.kind == "point_captured" and event.subject_id == item_id)
            default = {"value": event.payload["value"], "units": "fixture-unit"}
        return WorkerCandidate(
            playthrough_id=rig.playthrough_id,
            item_id=item_id,
            acquisition_id=event.payload["acquisition_id"],
            input_hash=event.payload["input_hash"],
            investigation_version=event.payload["investigation_version"],
            adapter_version=event.payload["adapter_version"],
            validation_policy_version=event.payload["validation_policy_version"],
            outcome="ready",
            result=default if result is None else result,
        )

    def release_trace_at_nine(self, rig, *, include_point=False):
        items = [("T", "trace")]
        if include_point:
            items.insert(0, ("A", "point"))
        self.assertEqual(self.order(rig, *items).status, "committed")
        self.assertEqual(self.wait(rig, 5500, "wait-to-5500").status, "committed")
        rig.worker.offer(self.candidate(rig, "T"))
        if include_point:
            rig.worker.offer(self.candidate(rig, "A"))
        self.assertEqual(self.wait(rig, 500, "wait-to-6000").status, "committed")
        self.assertEqual(self.wait(rig, 3000, "wait-to-9000").status, "committed")
        return self.execute(rig, "release-T", "release_result", {"item_id": "T"}, actor=rig.release_actor)

    def test_a07_metadata_assets_and_patient_role_share_release_boundary(self):
        rig = self.rig("a07")
        self.assertEqual(self.order(rig, ("T", "trace")).status, "committed")
        self.assertEqual(self.wait(rig, 5500, "wait-to-5500").status, "committed")
        rig.worker.offer(
            self.candidate(
                rig,
                "T",
                result={
                    "samples": [1, 2, 2],
                    "interpretation": "supports DX-A",
                    "units": "fixture-unit",
                    "reference_key": ["DX-B"],
                    "private_annotation": "must not reach learner",
                },
            )
        )
        self.assertEqual(self.wait(rig, 500, "wait-to-6000").status, "committed")

        before = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertNotIn("T", before.data["released_results"])
        self.assertNotIn("reference_key", before.data)
        withheld_metadata = rig.authority.artifact_metadata(rig.learner, rig.playthrough_id, "T")
        self.assertEqual(withheld_metadata.status, "withheld")
        self.assertIsNone(withheld_metadata.artifact)
        self.assertEqual(rig.authority.read_asset(rig.learner, rig.playthrough_id, "T").status, "withheld")
        self.assertEqual(rig.authority.read_asset(rig.learner, rig.playthrough_id, "T", "accessible-text").status, "withheld")
        self.assertEqual(rig.authority.read_artifact(rig.patient, rig.playthrough_id, "T").status, "forbidden")
        self.assertEqual(rig.authority.artifact_metadata(rig.other_learner, rig.playthrough_id, "T").status, "forbidden")

        self.assertEqual(self.wait(rig, 3000, "wait-to-9000").status, "committed")
        self.assertEqual(self.execute(rig, "unauthorized-release", "release_result", {"item_id": "T"}, actor=rig.other_learner).status, "forbidden")
        self.assertEqual(self.execute(rig, "release-T", "release_result", {"item_id": "T"}, actor=rig.release_actor).status, "committed")
        opened = self.execute(rig, "open-T", "open_artifact", {"item_id": "T"})
        self.assertEqual(opened.status, "committed")
        metadata = rig.authority.artifact_metadata(rig.learner, rig.playthrough_id, "T")
        self.assertEqual(metadata.status, "available")
        self.assertTrue(metadata.artifact["accessible_text_available"])
        primary = rig.authority.read_asset(rig.learner, rig.playthrough_id, "T", "primary")
        text_alternative = rig.authority.read_asset(rig.learner, rig.playthrough_id, "T", "accessible-text")
        self.assertEqual(primary.status, "available")
        self.assertEqual(text_alternative.artifact["samples"], [1, 2, 2])
        released_artifact = rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").artifact
        self.assertNotIn("reference_key", released_artifact)
        self.assertNotIn("private_annotation", released_artifact)
        self.assertEqual(rig.authority.read_asset(rig.patient, rig.playthrough_id, "T", "accessible-text").status, "forbidden")

        time_before = rig.authority.project(rig.learner, rig.playthrough_id).elapsed_ms
        aid = self.execute(rig, "interpret-T", "request_interpretation", {"item_id": "T", "explanation": False})
        self.assertEqual(aid.status, "committed")
        projection = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertNotIn("reference_key", projection.data)
        self.assertEqual(projection.elapsed_ms, time_before)
        self.assertEqual(projection.data["history"], {"verified_prior_episodes": 0})
        self.assertEqual(projection.data["subjective_reports"], {"prior_episodes": 1})
        assessment = projection.data["interpretation_aids"][0]["assessment"]
        self.assertEqual(assessment, rig.authority.read_artifact(rig.learner, rig.playthrough_id, "T").artifact["validated_assessment"])
        self.assertEqual(assessment["study_id"], "acq-play-1-T")
        self.assertIn("DX-A", assessment["supported_assertions"][0])
        self.assertNotIn("reference_key", projection.data)

    def test_a08_submission_freezes_dimensioned_debrief_and_review_is_separate(self):
        for index, reasoning in enumerate((self.FIXED_REASONING, None)):
            with self.subTest(reasoning_present=reasoning is not None):
                rig = self.rig(f"a08-{index}", worker=StubWorker(auto_prepare=True))
                self.assertEqual(self.order(rig, ("A", "point"), ("T", "trace")).status, "committed")
                self.assertEqual(self.wait(rig, 8000, f"wait-to-8000-{index}").status, "committed")
                self.assertEqual(self.wait(rig, 1000, f"wait-to-9000-{index}").status, "committed")
                self.assertEqual(self.execute(rig, f"release-T-{index}", "release_result", {"item_id": "T"}, actor=rig.release_actor).status, "committed")
                self.assertEqual(self.execute(rig, f"open-A-{index}", "open_artifact", {"item_id": "A"}).status, "committed")
                self.assertEqual(self.execute(rig, f"open-T-{index}", "open_artifact", {"item_id": "T"}).status, "committed")
                self.assertEqual(self.execute(rig, f"aid-T-{index}", "request_interpretation", {"item_id": "T", "explanation": False}).status, "committed")
                self.assertEqual(self.order(rig, ("C", "point")).status, "committed")
                submitted_at_revision = rig.authority.project(rig.learner, rig.playthrough_id).revision
                payload = {
                    "leading_diagnosis": "DX-A",
                    "differential": ["DX-A", "DX-B"],
                    "reasoning": reasoning,
                }
                submitted = self.execute(rig, f"submit-{index}", "submit_diagnosis", payload, expected_revision=submitted_at_revision)
                self.assertEqual(submitted.status, "committed")
                completed = rig.authority.project(rig.learner, rig.playthrough_id)
                self.assertEqual(completed.elapsed_ms, 9000)
                self.assertEqual(completed.data["orders"]["C"]["status"], "closed_at_submission")
                self.assertEqual(completed.data["orders"]["C"]["pre_close_state"], "ordered")
                for item_id in ("A", "T"):
                    snapshot = completed.data["submission"]["accessible_evidence"][item_id]
                    self.assertEqual(set(snapshot["versions"]), {"investigation_version", "adapter_version", "validation_policy_version"})
                self.assertFalse(any(event.subject_id == "C" and event.kind in {"point_captured", "result_released"} for event in rig.authority.trusted_events(rig.playthrough_id)))
                debrief = completed.data["debrief"]
                self.assertEqual(debrief["dimensions"]["diagnostic_accuracy"]["status"], "correct")
                self.assertEqual(debrief["dimensions"]["differential_quality"]["status"], "reference_ranked")
                self.assertEqual(debrief["dimensions"]["test_selection"]["status"], "required_tests_selected")
                self.assertEqual(debrief["dimensions"]["unnecessary_testing"]["items"], ["C"])
                self.assertEqual(debrief["dimensions"]["interpretation"]["status"], "supported" if reasoning else "unassessed")
                self.assertEqual(len(debrief["interpretation_aids"]), 1)
                if reasoning is None:
                    self.assertEqual(debrief["dimensions"]["explanation"]["status"], "unassessed")
                else:
                    self.assertEqual(debrief["dimensions"]["reasoning"]["evidence_link"], "present")
                    self.assertEqual(debrief["dimensions"]["reasoning"]["uncertainty"], "absent")

                # The same logical retry remains authorized after later revisions and ignores its stale precondition.
                retry = self.execute(rig, f"submit-{index}", "submit_diagnosis", payload, expected_revision=0)
                self.assertTrue(retry.replayed)
                self.assertEqual(retry.data, submitted.data)
                after_review_baseline = rig.authority.project(rig.learner, rig.playthrough_id)
                if index == 0:
                    review = self.execute(rig, f"review-{index}", "review_case", {"rating": 4, "comment": "Clear evidence."})
                    expected_review_status = "submitted"
                else:
                    review = self.execute(rig, f"review-{index}", "skip_review", {})
                    expected_review_status = "skipped"
                self.assertEqual(review.status, "committed")
                after_review = rig.authority.project(rig.learner, rig.playthrough_id)
                self.assertEqual(after_review.data["debrief"], after_review_baseline.data["debrief"])
                self.assertEqual(after_review.data["review"]["status"], expected_review_status)
                reopened = type(rig.authority)(rig.authority.db_path, worker=rig.worker, luna=rig.luna)
                self.assertEqual(reopened.project(rig.learner, rig.playthrough_id).data["debrief"], after_review.data["debrief"])
                self.assertEqual(reopened.project(rig.learner, rig.playthrough_id).data["review"], after_review.data["review"])
                self.assertEqual(rig.authority.project(rig.learner, "catalog").data["publication_count"], 1)
                self.assertEqual(self.wait(rig, 4000, f"post-case-wait-{index}").status, "encounter_complete")

    def test_a09_fallback_limited_unsupported_validation_and_storage_outcomes(self):
        fallback = self.rig("a09-fallback")
        self.assertEqual(self.order(fallback, ("T", "trace")).status, "committed")
        self.assertEqual(self.wait(fallback, 5500, "fallback-to-5500").status, "committed")
        fallback.worker.offer(self.candidate(fallback, "T", result={"samples": [1, 2, 2], "interpretation": "supports DX-A", "units": "fixture-unit", "media_available": False}))
        self.assertEqual(self.wait(fallback, 500, "fallback-to-6000").status, "committed")
        self.assertEqual(self.wait(fallback, 3000, "fallback-to-9000").status, "committed")
        self.assertEqual(self.execute(fallback, "fallback-release", "release_result", {"item_id": "T"}, actor=fallback.release_actor).status, "committed")
        self.assertEqual(fallback.authority.read_asset(fallback.learner, fallback.playthrough_id, "T", "primary").status, "unavailable")
        fallback_text = fallback.authority.read_asset(fallback.learner, fallback.playthrough_id, "T", "accessible-text")
        self.assertEqual(fallback_text.status, "available")
        self.assertEqual(fallback_text.artifact["samples"], [1, 2, 2])

        unsupported = self.rig("a09-unsupported")
        unsupported_receipt = self.execute(unsupported, "unsupported-order", "order_tests", {"items": [{"item_id": "U", "kind": "point", "capability": "unsupported"}]})
        self.assertEqual(unsupported_receipt.status, "committed")
        self.assertEqual(unsupported.authority.project(unsupported.learner, unsupported.playthrough_id).data["orders"]["U"]["status"], "unsupported")
        self.assertEqual(unsupported.authority.read_artifact(unsupported.learner, unsupported.playthrough_id, "U").status, "unsupported")
        unavailable_receipt = self.execute(unsupported, "unavailable-order", "order_tests", {"items": [{"item_id": "N", "kind": "point", "capability": "unavailable"}]})
        self.assertEqual(unavailable_receipt.status, "committed")
        self.assertEqual(unsupported.authority.project(unsupported.learner, unsupported.playthrough_id).data["orders"]["N"]["status"], "unavailable")
        self.assertEqual(unsupported.authority.read_artifact(unsupported.learner, unsupported.playthrough_id, "N").status, "unavailable")

        limited = self.rig("a09-limited")
        self.assertEqual(self.order(limited, ("T", "trace")).status, "committed")
        self.assertEqual(self.wait(limited, 5500, "limited-to-5500").status, "committed")
        limited.worker.offer(self.candidate(limited, "T", result={"samples": [1, 2], "sample_offsets": [0, 1], "quality": "limited", "interpretation": "partial trace only", "units": "fixture-unit"}))
        self.assertEqual(self.wait(limited, 500, "limited-to-6000").status, "committed")
        self.assertEqual(self.wait(limited, 3000, "limited-to-9000").status, "committed")
        self.assertEqual(self.execute(limited, "limited-release", "release_result", {"item_id": "T"}, actor=limited.release_actor).status, "committed")
        limited_result = limited.authority.read_artifact(limited.learner, limited.playthrough_id, "T").artifact
        self.assertEqual(limited_result["quality"], "limited")
        self.assertEqual(limited_result["samples"], [1, 2])
        self.assertEqual(limited_result["validated_assessment"]["status"], "unavailable")

        rejected = self.rig("a09-invalid-units")
        self.assertEqual(self.order(rejected, ("A", "point")).status, "committed")
        self.assertEqual(self.wait(rejected, 5500, "invalid-to-5500").status, "committed")
        rejected.worker.offer(self.candidate(rejected, "A", result={"value": 2, "units": "wrong-unit"}))
        self.assertEqual(self.wait(rejected, 500, "invalid-to-6000").status, "committed")
        self.assertEqual(rejected.authority.project(rejected.learner, rejected.playthrough_id).data["orders"]["A"]["status"], "failed")
        self.assertEqual(rejected.authority.read_artifact(rejected.learner, rejected.playthrough_id, "A").status, "failed")
        self.assertNotIn("value", (rejected.authority.read_artifact(rejected.learner, rejected.playthrough_id, "A").artifact or {}))

    def test_a09_storage_failure_rolls_back_clock_revision_and_receipt(self):
        import sqlite3

        rig = self.rig("a09-storage")
        before = rig.authority.project(rig.learner, rig.playthrough_id)
        connection = sqlite3.connect(rig.authority.db_path)
        try:
            connection.execute("CREATE TRIGGER fail_authority_update BEFORE UPDATE ON authority_state BEGIN SELECT RAISE(ABORT, 'injected write failure'); END")
        finally:
            connection.close()
        failed = self.execute(rig, "storage-failure", "wait", {"duration_ms": 250})
        self.assertEqual(failed.status, "storage_failed")
        after = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertEqual((after.elapsed_ms, after.revision), (before.elapsed_ms, before.revision))
        connection = sqlite3.connect(rig.authority.db_path)
        try:
            connection.execute("DROP TRIGGER fail_authority_update")
            connection.commit()
        finally:
            connection.close()
        retried = self.execute(rig, "storage-failure", "wait", {"duration_ms": 250})
        self.assertEqual(retried.status, "committed")
        self.assertEqual(rig.authority.project(rig.learner, rig.playthrough_id).elapsed_ms, 250)

    def test_a10_dialogue_requires_luna_and_saved_turns_survive_provider_outage(self):
        luna_module = importlib.import_module("luna")
        LunaStub = luna_module.LunaStub
        for index, outcome in enumerate(("denied", "unavailable", "error")):
            with self.subTest(outcome=outcome):
                luna = LunaStub(dialogue_outcome=outcome)
                rig = self.rig(f"a10-blocked-{index}", luna=luna)
                before = rig.authority.project(rig.learner, rig.playthrough_id)
                events_before = rig.authority.trusted_events(rig.playthrough_id)
                blocked = self.execute(rig, "ask-patient", "ask_patient", {"question": "How many episodes do you recall?"})
                after = rig.authority.project(rig.learner, rig.playthrough_id)
                self.assertEqual(blocked.status, "dialogue_blocked")
                self.assertEqual((after.elapsed_ms, after.revision), (before.elapsed_ms, before.revision))
                self.assertEqual(rig.authority.trusted_events(rig.playthrough_id), events_before)
                self.assertEqual(after.data["dialogue_history"], [])
                self.assertNotIn("DX-A", str(luna.requests[-1]["context"]))
                if outcome == "error":
                    luna.dialogue_outcome = "success"
                    retried = self.execute(rig, "ask-patient", "ask_patient", {"question": "How many episodes do you recall?"})
                    self.assertEqual(retried.status, "committed")

        luna = LunaStub()
        rig = self.rig("a10-history", luna=luna)
        accepted = self.execute(rig, "ask-patient", "ask_patient", {"question": "How many episodes do you recall?"})
        self.assertEqual(accepted.status, "committed")
        saved = rig.authority.project(rig.learner, rig.playthrough_id)
        self.assertEqual(len(saved.data["dialogue_history"]), 1)
        unavailable = LunaStub(dialogue_outcome="unavailable", explanation_outcome="unavailable")
        reopened = type(rig.authority)(rig.authority.db_path, worker=rig.worker, luna=unavailable)
        replay = reopened.project(rig.learner, rig.playthrough_id)
        self.assertEqual(replay.data["dialogue_history"], saved.data["dialogue_history"])
        later = reopened.execute(rig.learner, Command("new-question", rig.playthrough_id, replay.revision, "ask_patient", {"question": "Anything else?"}))
        self.assertEqual(later.status, "dialogue_blocked")

        # A failed explanation cannot replace the already validated reference assessment.
        self.assertEqual(self.release_trace_at_nine(rig, include_point=True).status, "committed")
        explanation = reopened.execute(rig.learner, Command("explain-T", rig.playthrough_id, reopened.project(rig.learner, rig.playthrough_id).revision, "request_interpretation", {"item_id": "T", "explanation": True}))
        self.assertEqual(explanation.status, "committed")
        aid = reopened.project(rig.learner, rig.playthrough_id).data["interpretation_aids"][-1]
        self.assertEqual(aid["assessment"]["status"], "available")
        self.assertEqual(aid["explanation_status"], "unavailable")

        import json
        import sqlite3

        connection = sqlite3.connect(rig.authority.db_path)
        try:
            payload = json.loads(connection.execute("SELECT payload FROM authority_state WHERE singleton=1").fetchone()[0])
            payload["cases"]["Fixture-A"]["dialogue_mode"] = "canned_only"
            connection.execute("UPDATE authority_state SET payload=? WHERE singleton=1", (json.dumps(payload),))
            connection.commit()
        finally:
            connection.close()
        legacy = reopened.execute(rig.learner, Command("start-legacy", "case:Fixture-A", None, "start_playthrough", {"playthrough_id": "legacy-play"}))
        self.assertEqual(legacy.status, "legacy_case_not_playable")


class GateASchedulerBoundaryTests(unittest.TestCase):
    def test_scheduler_rejects_backwards_time_phase_and_overlong_chain(self):
        import importlib

        module = importlib.import_module("scheduler")
        with self.assertRaises(module.ScheduleError):
            module.EventScheduler.validate_new_event(5000, 4, 4999, 5)
        with self.assertRaises(module.ScheduleError):
            module.EventScheduler.validate_new_event(5000, 6, 5000, 1)
        with self.assertRaises(module.ScheduleError):
            module.EventScheduler(max_same_time_events=2).check_chain(3)

    def test_clock_overflow_rejects_without_advancing_or_revising(self):
        from authority import MAX_CLINICAL_TIME_MS

        with tempfile.TemporaryDirectory() as directory:
            rig = make_fixture(Path(directory) / "clock-overflow.sqlite", initialize=True)
            at_limit = rig.authority.execute(
                rig.learner,
                Command("to-clock-limit", rig.playthrough_id, 0, "wait", {"duration_ms": MAX_CLINICAL_TIME_MS}),
            )
            self.assertEqual(at_limit.status, "committed")
            before = rig.authority.project(rig.learner, rig.playthrough_id)
            overflow = rig.authority.execute(
                rig.learner,
                Command("past-clock-limit", rig.playthrough_id, before.revision, "wait", {"duration_ms": 1}),
            )
            after = rig.authority.project(rig.learner, rig.playthrough_id)
            self.assertEqual(overflow.status, "clock_overflow")
            self.assertEqual((after.elapsed_ms, after.revision), (before.elapsed_ms, before.revision))


if __name__ == "__main__":
    unittest.main()
