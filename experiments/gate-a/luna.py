"""Offline deterministic Luna double for synthetic Gate A orchestration tests."""

from __future__ import annotations

from typing import Any, Mapping


class LunaStub:
    """Configurable local double; it never calls a model or handles credentials."""

    def __init__(
        self,
        dialogue_outcome: str = "success",
        explanation_outcome: str = "success",
        dialogue_text: str = "I remember one prior episode.",
        explanation_text: str = "The trace rises from 1 to 2 and supports DX-A under Fixture-A rules; the conclusion is limited to this fictional rubric.",
    ):
        self.dialogue_outcome = dialogue_outcome
        self.explanation_outcome = explanation_outcome
        self.dialogue_text = dialogue_text
        self.explanation_text = explanation_text
        self.requests: list[dict[str, Any]] = []

    def complete(self, purpose: str, context: Mapping[str, Any]) -> dict[str, Any]:
        """Return the configured outcome and retain only this in-memory test trace."""
        safe_context = dict(context)
        self.requests.append({"purpose": purpose, "context": safe_context})
        outcome = self.dialogue_outcome if purpose == "dialogue" else self.explanation_outcome
        if outcome != "success":
            return {"status": outcome}
        if purpose == "dialogue":
            facts = safe_context.get("facts", [])
            question = str(safe_context.get("question", "")).lower()
            if not any(word in question for word in ("episode", "history", "remember", "prior")):
                return {
                    "status": "success",
                    "text": "I'm not sure about that.",
                    "fact_refs": [],
                    "subjective_report": True,
                    "uncertainty": True,
                }
            return {
                "status": "success",
                "text": self.dialogue_text,
                "fact_refs": [fact["fact_id"] for fact in facts],
                "subjective_report": True,
            }
        if purpose == "explanation":
            return {"status": "success", "text": self.explanation_text}
        return {"status": "error"}
