"""Fixture-A construction and injectable test controls for adapter comparisons."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from authority import SQLiteAuthority
from luna import LunaStub
from port import Actor, Command, GateAPort
from workers import StubWorker


class FixtureTestControls(Protocol):
    """Narrow test-only seams; scenarios still assert through GateAPort."""

    def set_continuation_dependency(self, playthrough_id: str, name: str, value: str) -> None: ...

    def tamper_play_field(self, playthrough_id: str, section: str, item_id: str, field: str, value: Any) -> None: ...

    def set_dialogue_mode(self, case_id: str, mode: str) -> None: ...

    def fail_next_persist(self) -> None: ...

    def restore_persistence(self) -> None: ...


class SQLiteFixtureControls:
    """SQLite-specific fault/input injection kept outside behavioral assertions."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def _update_state(self, change: Callable[[dict[str, Any]], None]) -> None:
        connection = sqlite3.connect(self.db_path)
        try:
            row = connection.execute("SELECT payload FROM authority_state WHERE singleton=1").fetchone()
            state = json.loads(row[0])
            change(state)
            connection.execute("UPDATE authority_state SET payload=? WHERE singleton=1", (json.dumps(state),))
            connection.commit()
        finally:
            connection.close()

    def set_continuation_dependency(self, playthrough_id: str, name: str, value: str) -> None:
        self._update_state(lambda state: state["plays"][playthrough_id]["continuation"].__setitem__(name, value))

    def tamper_play_field(self, playthrough_id: str, section: str, item_id: str, field: str, value: Any) -> None:
        def change(state: dict[str, Any]) -> None:
            play = state["plays"][playthrough_id]
            if section in {"", "__play__"}:
                play[field] = value
            elif item_id:
                play[section][item_id][field] = value
            else:
                play[section][field] = value

        self._update_state(change)

    def set_dialogue_mode(self, case_id: str, mode: str) -> None:
        self._update_state(lambda state: state["cases"][case_id].__setitem__("dialogue_mode", mode))

    def fail_next_persist(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS fail_authority_update BEFORE UPDATE ON authority_state "
                "BEGIN SELECT RAISE(ABORT, 'injected write failure'); END"
            )
            connection.commit()

    def restore_persistence(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("DROP TRIGGER IF EXISTS fail_authority_update")
            connection.commit()


AuthorityFactory = Callable[..., GateAPort]
ControlsFactory = Callable[[str | Path], FixtureTestControls]


@dataclass
class FixtureRig:
    authority: GateAPort
    learner: Actor
    other_learner: Actor
    release_actor: Actor
    patient: Actor
    case_id: str
    playthrough_id: str
    worker: StubWorker
    luna: LunaStub
    db_path: Path
    authority_factory: AuthorityFactory
    controls: FixtureTestControls

    def reopen_authority(self, worker: StubWorker | None = None, luna: LunaStub | None = None) -> GateAPort:
        return self.authority_factory(
            self.db_path,
            worker=worker or self.worker,
            luna=luna or self.luna,
        )


def make_fixture(
    db_path: str | Path,
    initialize: bool = True,
    playthrough_id: str = "play-1",
    worker: StubWorker | None = None,
    luna: LunaStub | None = None,
    authority_factory: AuthorityFactory = SQLiteAuthority,
    controls_factory: ControlsFactory = SQLiteFixtureControls,
) -> FixtureRig:
    selected_worker = worker or StubWorker()
    selected_luna = luna or LunaStub()
    selected_path = Path(db_path)
    rig = FixtureRig(
        authority=authority_factory(selected_path, worker=selected_worker, luna=selected_luna),
        learner=Actor("learner-1", "learner"),
        other_learner=Actor("learner-2", "learner"),
        release_actor=Actor("release-service", "authority"),
        patient=Actor("patient-npc", "patient"),
        case_id="Fixture-A",
        playthrough_id=playthrough_id,
        worker=selected_worker,
        luna=selected_luna,
        db_path=selected_path,
        authority_factory=authority_factory,
        controls=controls_factory(selected_path),
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
