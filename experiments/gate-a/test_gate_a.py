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


if __name__ == "__main__":
    unittest.main()







