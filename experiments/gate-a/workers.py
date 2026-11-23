"""Bound, deterministic worker doubles for Gate A."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
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

    @staticmethod
    def _display_waveform() -> dict[str, Any]:
        """Return an arbitrary display fixture, not a simulated or clinical ECG."""
        lead_order = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        gains = {
            "I": 0.78, "II": 1.0, "III": 0.48, "aVR": -0.62,
            "aVL": 0.26, "aVF": 0.64, "V1": -0.34, "V2": 0.42,
            "V3": 0.70, "V4": 0.92, "V5": 0.84, "V6": 0.68,
        }
        sample_rate_hz = 100
        sample_count = 1000
        beat_times = [0.6 + index for index in range(10)]
        base_values: list[float] = []
        for sample_index in range(sample_count):
            time_s = sample_index / sample_rate_hz
            signal = 0.018 * math.sin(2 * math.pi * 7 * time_s)
            for beat in beat_times:
                delta = time_s - beat
                signal += 0.12 * math.exp(-((delta + 0.18) / 0.045) ** 2)
                signal -= 0.15 * math.exp(-((delta + 0.025) / 0.012) ** 2)
                signal += 0.90 * math.exp(-((delta) / 0.014) ** 2)
                signal -= 0.20 * math.exp(-((delta - 0.025) / 0.014) ** 2)
                signal += 0.25 * math.exp(-((delta - 0.28) / 0.085) ** 2)
            base_values.append(signal)
        leads = {
            lead: [round(value * gains[lead], 4) for value in base_values]
            for lead in lead_order
        }
        return {
            "kind": "display_only_synthetic_fixture",
            "sample_rate_hz": sample_rate_hz,
            "duration_seconds": 10,
            "paper_speed_mm_s": 25,
            "gain_mm_per_fixture_mv": 10,
            "units": "fixture-mV",
            "lead_order": lead_order,
            "leads": leads,
        }

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
                "units": "fixture-unit",
                "display_waveform": self._display_waveform(),
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
