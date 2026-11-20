"""Bound, deterministic worker doubles for Gate A."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class WorkerCandidate:
    playthrough_id: str
    item_id: str
    acquisition_id: str
    input_hash: str
    investigation_version: str
    adapter_version: str
    validation_policy_version: str
    outcome: str = "ready"
    result: Mapping[str, Any] = field(default_factory=dict)
    failure_cause: str | None = None


class StubWorker:
    """In-memory worker double; auto mode deterministically derives a result from its acquisition."""

    def __init__(self, auto_prepare: bool = False):
        self.auto_prepare = auto_prepare
        self._candidates: dict[tuple[str, str, str, str, str, str, str], WorkerCandidate] = {}

    @staticmethod
    def _candidate_key(candidate: WorkerCandidate) -> tuple[str, str, str, str, str, str, str]:
        return (
            candidate.playthrough_id,
            candidate.item_id,
            candidate.acquisition_id,
            candidate.input_hash,
            candidate.investigation_version,
            candidate.adapter_version,
            candidate.validation_policy_version,
        )

    def offer(self, candidate: WorkerCandidate) -> None:
        self._candidates[self._candidate_key(candidate)] = candidate

    def get_candidate(
        self,
        playthrough_id: str,
        item_id: str,
        acquisition: Mapping[str, Any],
        versions: Mapping[str, str],
    ) -> WorkerCandidate | None:
        key = (
            playthrough_id,
            item_id,
            str(acquisition["acquisition_id"]),
            str(acquisition["input_hash"]),
            versions["investigation_version"],
            versions["adapter_version"],
            versions["validation_policy_version"],
        )
        candidate = self._candidates.get(key)
        if candidate is not None or not self.auto_prepare:
            return candidate
        if acquisition["kind"] == "point":
            result = {"value": acquisition["value"], "units": "fixture-unit"}
        else:
            result = {
                "samples": [sample["value"] for sample in acquisition["samples"]],
                "interpretation": "supports DX-A",
                "units": "fixture-unit",
            }
        return WorkerCandidate(
            playthrough_id=playthrough_id,
            item_id=item_id,
            acquisition_id=acquisition["acquisition_id"],
            input_hash=acquisition["input_hash"],
            investigation_version=versions["investigation_version"],
            adapter_version=versions["adapter_version"],
            validation_policy_version=versions["validation_policy_version"],
            outcome="ready",
            result=result,
        )
