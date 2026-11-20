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


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
