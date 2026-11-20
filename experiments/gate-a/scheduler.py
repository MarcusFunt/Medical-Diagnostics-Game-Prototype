"""Deterministic clinical-time queue ordering for Gate A."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


PHASES = {
    "disease_transition": 1,
    "action_effect": 2,
    "acquisition": 3,
    "processing": 4,
    "release": 5,
    "closeout": 6,
}


class ScheduleError(ValueError):
    pass


@dataclass(frozen=True)
class ScheduledEvent:
    time_ms: int
    phase: int
    ordinal: int
    kind: str
    subject_id: str
    payload: Mapping[str, Any]

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "ScheduledEvent":
        return cls(
            time_ms=int(record["time_ms"]),
            phase=int(record["phase"]),
            ordinal=int(record["ordinal"]),
            kind=str(record["kind"]),
            subject_id=str(record["subject_id"]),
            payload=dict(record["payload"]),
        )

    def as_record(self) -> dict[str, Any]:
        return {
            "time_ms": self.time_ms,
            "phase": self.phase,
            "ordinal": self.ordinal,
            "kind": self.kind,
            "subject_id": self.subject_id,
            "payload": dict(self.payload),
        }


class EventScheduler:
    def __init__(self, max_same_time_events: int = 1000):
        self.max_same_time_events = max_same_time_events

    @staticmethod
    def next_due(events: Sequence[Mapping[str, Any]], boundary_ms: int) -> dict[str, Any] | None:
        due = [event for event in events if int(event["time_ms"]) <= boundary_ms]
        if not due:
            return None
        return dict(min(due, key=lambda event: (event["time_ms"], event["phase"], event["ordinal"])))

    @staticmethod
    def validate_new_event(
        current_time_ms: int,
        current_phase: int | None,
        scheduled_time_ms: int,
        scheduled_phase: int,
    ) -> None:
        if scheduled_time_ms < current_time_ms:
            raise ScheduleError("event cannot be scheduled before the committed clinical time")
        if (
            scheduled_time_ms == current_time_ms
            and current_phase is not None
            and scheduled_phase < current_phase
        ):
            raise ScheduleError("same-time event depends on an earlier scheduler phase")
        if scheduled_phase not in range(1, 7):
            raise ScheduleError("scheduler phase must be between 1 and 6")

    def check_chain(self, count_at_timestamp: int) -> None:
        if count_at_timestamp > self.max_same_time_events:
            raise ScheduleError("same-time event chain exceeded the fixture limit")
