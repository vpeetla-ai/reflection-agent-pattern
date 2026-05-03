from dataclasses import dataclass, field
from time import time
from typing import Any
from uuid import uuid4

from .models import Critic, Critique, Generator
from .policy import QualityPolicy


@dataclass(frozen=True)
class ReflectionAttempt:
    draft: str
    critique: Critique


@dataclass(frozen=True)
class ReflectionResult:
    answer: str
    attempts: list[ReflectionAttempt]
    request_id: str = field(default_factory=lambda: str(uuid4()))
    completed_at: float = field(default_factory=time)


class ReflectionAgent:
    def __init__(
        self,
        generator: Generator,
        critic: Critic,
        policy: QualityPolicy | None = None,
    ) -> None:
        self.generator = generator
        self.critic = critic
        self.policy = policy or QualityPolicy()

    def run(self, task: str) -> ReflectionResult:
        draft = self.generator.draft(task)
        attempts: list[ReflectionAttempt] = []

        for _ in range(self.policy.max_revisions + 1):
            critique = self.critic.review(task, draft)
            attempts.append(ReflectionAttempt(draft=draft, critique=critique))
            if critique.approved and self.policy.accepts(critique.score):
                return ReflectionResult(answer=draft, attempts=attempts)
            draft = self.generator.revise(task, draft, critique)

        return ReflectionResult(answer=draft, attempts=attempts)

