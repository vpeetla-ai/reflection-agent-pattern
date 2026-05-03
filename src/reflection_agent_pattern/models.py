from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Critique:
    score: float
    findings: list[str]
    approved: bool


class Generator(Protocol):
    def draft(self, task: str) -> str:
        """Create an initial answer."""

    def revise(self, task: str, draft: str, critique: Critique) -> str:
        """Improve an answer using critique."""


class Critic(Protocol):
    def review(self, task: str, draft: str) -> Critique:
        """Evaluate an answer against quality criteria."""


class ScriptedGenerator:
    def draft(self, task: str) -> str:
        return f"Draft response for: {task}"

    def revise(self, task: str, draft: str, critique: Critique) -> str:
        missing = "; ".join(critique.findings)
        return f"{draft}\nImproved with validation details addressing: {missing}"


class ScriptedCritic:
    def review(self, task: str, draft: str) -> Critique:
        has_validation = "validation details" in draft.lower()
        if has_validation:
            return Critique(score=0.93, findings=[], approved=True)
        return Critique(
            score=0.62,
            findings=[
                "Add explicit validation criteria.",
                "Ground the answer in observable success conditions.",
            ],
            approved=False,
        )

