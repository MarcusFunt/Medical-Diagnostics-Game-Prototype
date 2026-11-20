"""Fixture-A construction helpers for tests and adapter comparisons."""

from dataclasses import dataclass
from pathlib import Path

from authority import SQLiteAuthority
from port import Actor, Command
from workers import StubWorker


@dataclass
class FixtureRig:
    authority: SQLiteAuthority
    learner: Actor
    other_learner: Actor
    release_actor: Actor
    patient: Actor
    case_id: str
    playthrough_id: str
    worker: StubWorker


def make_fixture(
    db_path: str | Path,
    initialize: bool = True,
    playthrough_id: str = "play-1",
    worker: StubWorker | None = None,
) -> FixtureRig:
    selected_worker = worker or StubWorker()
    rig = FixtureRig(
        authority=SQLiteAuthority(db_path, worker=selected_worker),
        learner=Actor("learner-1", "learner"),
        other_learner=Actor("learner-2", "learner"),
        release_actor=Actor("release-service", "authority"),
        patient=Actor("patient-npc", "patient"),
        case_id="Fixture-A",
        playthrough_id=playthrough_id,
        worker=selected_worker,
    )
    if initialize:
        generated = rig.authority.execute(
            rig.learner,
            Command(
                f"generate-{rig.case_id}",
                "catalog",
                0,
                "generate_case",
                {"case_id": rig.case_id, "mandatory_evidence": True},
            ),
        )
        if generated.status != "committed":
            raise RuntimeError(f"Fixture-A generation failed: {generated.status}")
        started = rig.authority.execute(
            rig.learner,
            Command(
                f"start-{playthrough_id}",
                f"case:{rig.case_id}",
                None,
                "start_playthrough",
                {"playthrough_id": playthrough_id},
            ),
        )
        if started.status != "committed":
            raise RuntimeError(f"Fixture-A playthrough failed: {started.status}")
    return rig
