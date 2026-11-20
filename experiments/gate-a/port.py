"""Candidate-independent public boundaries for the Gate A fixture."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class Actor:
    actor_id: str
    role: str = "learner"


@dataclass(frozen=True)
class Command:
    command_id: str
    target_id: str
    expected_revision: int | None
    kind: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Receipt:
    status: str
    target_id: str
    revision: int | None = None
    data: Mapping[str, Any] = field(default_factory=dict)
    replayed: bool = False


@dataclass(frozen=True)
class Projection:
    target_id: str
    revision: int
    elapsed_ms: int
    status: str
    data: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ArtifactAccess:
    status: str
    artifact: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ClinicalEvent:
    event_id: str
    clinical_time_ms: int
    event_sequence: int
    phase: int
    kind: str
    subject_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)


class GateAPort(Protocol):
    """The same boundary a future candidate adapter must satisfy."""

    def execute(self, actor: Actor, command: Command) -> Receipt: ...

    def project(self, actor: Actor, playthrough_id: str) -> Projection: ...

    def read_artifact(
        self, actor: Actor, playthrough_id: str, artifact_id: str
    ) -> ArtifactAccess: ...

    def trusted_events(self, playthrough_id: str) -> Sequence[ClinicalEvent]: ...
