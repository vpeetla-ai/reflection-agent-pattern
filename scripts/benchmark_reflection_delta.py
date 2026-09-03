"""Real, executed benchmark: does the reflection (critique-and-revise) loop
actually improve the critic's own score, and what does it cost in revisions?

This does NOT measure real LLM output quality — `Generator`/`Critic` here are
deterministic stubs, exactly like this repo's `ScriptedGenerator` /
`ScriptedCritic` (see src/reflection_agent_pattern/models.py and the README's
"Curriculum stub" framing). What IS real: every task below is run through the
actual `ReflectionAgent.run()` control-flow loop (src/reflection_agent_pattern
/reflection.py) with the actual `QualityPolicy` stop conditions, and every
number in the receipt is read back from the `ReflectionResult` that loop
produces — not hand-typed.

The thing under test is the *mechanism*: does routing a draft through
critique-and-revise, scored by the same critic the agent uses to decide when
to stop, move the score versus taking the first draft as-is? And what happens
when the generator structurally cannot satisfy one of the critic's
requirements (e.g. it names something outside the generator's own action
space, like an external sign-off) — does the loop correctly report a spent,
un-approved budget instead of silently pretending success?

Usage:
    python scripts/benchmark_reflection_delta.py
        Runs the full suite and writes docs/receipts/benchmark.md.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from reflection_agent_pattern.models import Critique  # noqa: E402
from reflection_agent_pattern.policy import QualityPolicy  # noqa: E402
from reflection_agent_pattern.reflection import ReflectionAgent  # noqa: E402


# ---------------------------------------------------------------------------
# Deterministic fixtures (benchmark-local, mirroring models.ScriptedGenerator
# / ScriptedCritic's style: no network, no API key, fully reproducible).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RequiredMarkersCritic:
    """Scores a draft by how many required substrings it contains.

    This is the SAME critic instance the agent uses to decide whether to
    stop — so `attempts[0].critique.score` is genuinely "what draft-only
    would have scored" under this benchmark's own rubric, not a separate
    metric bolted on afterward.
    """

    required_markers: tuple[str, ...]
    floor_score: float = 0.55
    ceiling_score: float = 0.97

    def review(self, task: str, draft: str) -> Critique:
        text = draft.lower()
        present = [m for m in self.required_markers if m.lower() in text]
        missing = [m for m in self.required_markers if m.lower() not in text]
        fraction = len(present) / len(self.required_markers) if self.required_markers else 1.0
        score = round(self.floor_score + (self.ceiling_score - self.floor_score) * fraction, 4)
        approved = not missing
        findings = [f"Add explicit coverage for: {m}." for m in missing]
        return Critique(score=score, findings=findings, approved=approved)


@dataclass(frozen=True)
class IncrementalGenerator:
    """Drafts a task, then fixes exactly one missing (addressable) required
    marker per `revise()` call, in `required_markers` order — matching how a
    real editing pass tends to land one fix at a time rather than rewriting
    everything at once.

    `unaddressable_markers` models a generator that structurally cannot
    satisfy some requirement on its own (e.g. it names an external sign-off
    a generator has no way to produce) — those are always skipped, so the
    reflection loop can genuinely exhaust its revision budget without ever
    approving, which is the honest, disclosed outcome for those tasks.
    """

    required_markers: tuple[str, ...]
    start_markers: tuple[str, ...] = ()
    unaddressable_markers: frozenset[str] = field(default_factory=frozenset)

    def draft(self, task: str) -> str:
        lines = [f"Draft response for: {task}."]
        lines.extend(f"Includes: {marker}." for marker in self.start_markers)
        return "\n".join(lines)

    def revise(self, task: str, draft: str, critique: Critique) -> str:
        text = draft.lower()
        for marker in self.required_markers:
            if marker.lower() in text:
                continue
            if marker in self.unaddressable_markers:
                continue
            return f"{draft}\nAddressed: {marker}."
        # Nothing this generator knows how to add is left missing.
        return draft


@dataclass(frozen=True)
class TaskScenario:
    name: str
    group: str  # "already-passing" | "one-revision" | "two-revision" | "adversarial-exhausted"
    task: str
    required_markers: tuple[str, ...]
    start_markers: tuple[str, ...] = ()
    unaddressable_markers: frozenset[str] = field(default_factory=frozenset)

    def build_agent(self, policy: QualityPolicy) -> ReflectionAgent:
        generator = IncrementalGenerator(
            required_markers=self.required_markers,
            start_markers=self.start_markers,
            unaddressable_markers=self.unaddressable_markers,
        )
        critic = RequiredMarkersCritic(required_markers=self.required_markers)
        return ReflectionAgent(generator, critic, policy)


# 11 tasks: 3 already pass on the first draft (honest ~0 delta), 3 need
# exactly one revision, 3 need exactly two revisions (the full default
# budget), and 2 are adversarial — the generator can never supply one of the
# critic's requirements, so the loop must exhaust its revision budget
# without approving.
TASK_SCENARIOS: tuple[TaskScenario, ...] = (
    TaskScenario(
        name="q3-revenue-summary",
        group="already-passing",
        task="Summarize Q3 revenue trends for the board",
        required_markers=("quarter-over-quarter comparison",),
        start_markers=("quarter-over-quarter comparison",),
    ),
    TaskScenario(
        name="changelog-entry",
        group="already-passing",
        task="Write a one-line changelog entry for the bugfix",
        required_markers=("issue reference",),
        start_markers=("issue reference",),
    ),
    TaskScenario(
        name="standup-status",
        group="already-passing",
        task="Draft a status update for the weekly standup",
        required_markers=("blockers",),
        start_markers=("blockers",),
    ),
    TaskScenario(
        name="pricing-calculator-tests",
        group="one-revision",
        task="Write unit tests for the new pricing calculator",
        required_markers=("edge case coverage",),
    ),
    TaskScenario(
        name="incident-postmortem",
        group="one-revision",
        task="Draft an incident postmortem for the outage",
        required_markers=("root cause analysis",),
    ),
    TaskScenario(
        name="orders-api-docs",
        group="one-revision",
        task="Write API documentation for the /orders endpoint",
        required_markers=("error code reference",),
    ),
    TaskScenario(
        name="db-migration-plan",
        group="two-revision",
        task="Design a database migration plan for the orders table",
        required_markers=("rollback plan", "data validation checks"),
    ),
    TaskScenario(
        name="auth-security-review",
        group="two-revision",
        task="Write a security review for the new auth flow",
        required_markers=("threat model", "mitigation owner"),
    ),
    TaskScenario(
        name="payment-rollback-plan",
        group="two-revision",
        task="Draft a rollback plan for the payment service deploy",
        required_markers=("monitoring plan", "kill switch"),
    ),
    TaskScenario(
        name="soc2-attestation",
        group="adversarial-exhausted",
        task="Write a compliance attestation for SOC2 audit evidence",
        required_markers=("control test results", "independent verification signature"),
        unaddressable_markers=frozenset({"independent verification signature"}),
    ),
    TaskScenario(
        name="dpa-clause",
        group="adversarial-exhausted",
        task="Produce a legally binding data processing agreement clause",
        required_markers=("data subject rights clause", "counsel sign-off"),
        unaddressable_markers=frozenset({"counsel sign-off"}),
    ),
)


@dataclass(frozen=True)
class TaskOutcome:
    scenario: TaskScenario
    attempts: int
    revisions_used: int
    first_score: float
    final_score: float
    approved_within_budget: bool

    @property
    def score_delta(self) -> float:
        return round(self.final_score - self.first_score, 4)


def run_scenario(scenario: TaskScenario, policy: QualityPolicy) -> TaskOutcome:
    agent = scenario.build_agent(policy)
    result = agent.run(scenario.task)
    first = result.attempts[0].critique
    final = result.attempts[-1].critique
    return TaskOutcome(
        scenario=scenario,
        attempts=len(result.attempts),
        revisions_used=len(result.attempts) - 1,
        first_score=first.score,
        final_score=final.score,
        approved_within_budget=final.approved,
    )


@dataclass(frozen=True)
class BenchmarkSummary:
    outcomes: tuple[TaskOutcome, ...]

    @property
    def mean_score_delta(self) -> float:
        return round(mean(o.score_delta for o in self.outcomes), 4)

    @property
    def improved_count(self) -> int:
        return sum(1 for o in self.outcomes if o.score_delta > 0)

    @property
    def improved_pct(self) -> float:
        return round(100 * self.improved_count / len(self.outcomes), 1)

    @property
    def approved_count(self) -> int:
        return sum(1 for o in self.outcomes if o.approved_within_budget)

    @property
    def approved_pct(self) -> float:
        return round(100 * self.approved_count / len(self.outcomes), 1)

    @property
    def exhausted_count(self) -> int:
        return len(self.outcomes) - self.approved_count

    @property
    def exhausted_pct(self) -> float:
        return round(100 * self.exhausted_count / len(self.outcomes), 1)


def run_benchmark(policy: QualityPolicy | None = None) -> BenchmarkSummary:
    policy = policy or QualityPolicy()
    outcomes = tuple(run_scenario(scenario, policy) for scenario in TASK_SCENARIOS)
    return BenchmarkSummary(outcomes=outcomes)


# ---------------------------------------------------------------------------
# Receipt rendering
# ---------------------------------------------------------------------------


def render_receipt(summary: BenchmarkSummary, policy: QualityPolicy) -> str:
    lines: list[str] = []
    lines.append("# Benchmark receipt: reflection critique-delta")
    lines.append("")
    lines.append(
        "Generated by `scripts/benchmark_reflection_delta.py`. Every number below "
        "was read from a real `ReflectionAgent.run()` call — see "
        "`tests/test_benchmark_reflection_delta.py` for the pytest that re-runs "
        "this suite and asserts the invariants it depends on."
    )
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append(
        "- `Generator`/`Critic` are deterministic stubs (`IncrementalGenerator` / "
        "`RequiredMarkersCritic`, defined in the benchmark script itself), matching "
        "this repo's existing `ScriptedGenerator`/`ScriptedCritic` convention — "
        "**no external LLM call, no API key**. This measures the reflection loop's "
        "mechanical control flow, not real LLM output quality."
    )
    lines.append(
        "- Each task runs through the real `ReflectionAgent(generator, critic, "
        f"policy).run(task)` with the repo's default `QualityPolicy(min_score="
        f"{policy.min_score}, max_revisions={policy.max_revisions})`."
    )
    lines.append(
        "- The SAME `RequiredMarkersCritic.review()` call the agent uses to decide "
        "when to stop is what scores every attempt — `first_score` is literally "
        "`attempts[0].critique.score` (what draft-only would have scored) and "
        "`final_score` is `attempts[-1].critique.score` (what the loop actually "
        "shipped)."
    )
    lines.append(
        "- `IncrementalGenerator` fixes one missing, addressable required marker "
        "per `revise()` call — modeling a real one-fix-per-pass editing loop, not "
        "an instant full rewrite."
    )
    lines.append(
        "- Two tasks are adversarial by construction: one required marker is in "
        "`unaddressable_markers`, so the generator can never supply it (it models "
        "a requirement outside the generator's own action space, such as an "
        "external sign-off). These tasks are expected to exhaust the revision "
        "budget without approval — that is reported as a real outcome, not hidden "
        "or excluded from the aggregate."
    )
    lines.append("")
    lines.append("## Per-task results")
    lines.append("")
    lines.append(
        "| Task | Group | Attempts | Revisions used | First score | Final score | "
        "Δ score | Approved within budget |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for outcome in summary.outcomes:
        s = outcome.scenario
        lines.append(
            f"| {s.task} | {s.group} | {outcome.attempts} | {outcome.revisions_used} | "
            f"{outcome.first_score:.4f} | {outcome.final_score:.4f} | "
            f"{outcome.score_delta:+.4f} | {'yes' if outcome.approved_within_budget else 'NO (exhausted)'} |"
        )
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- Tasks: {len(summary.outcomes)}")
    lines.append(f"- Mean score delta (final − first): **{summary.mean_score_delta:+.4f}**")
    lines.append(
        f"- Tasks where reflection improved the score: **{summary.improved_count}/"
        f"{len(summary.outcomes)} ({summary.improved_pct}%)**"
    )
    lines.append(
        f"- Tasks approved within the revision budget: **{summary.approved_count}/"
        f"{len(summary.outcomes)} ({summary.approved_pct}%)**"
    )
    lines.append(
        f"- Tasks that exhausted the revision budget without approval: "
        f"**{summary.exhausted_count}/{len(summary.outcomes)} ({summary.exhausted_pct}%)**"
    )
    lines.append("")
    lines.append("## Honest reading")
    lines.append("")
    lines.append(
        "- The 3 `already-passing` tasks correctly show a `+0.0000` delta and 0 "
        "revisions — the loop does not manufacture improvement where the first "
        "draft already clears the bar. That is included in the aggregate, not "
        "discarded as a non-result."
    )
    lines.append(
        "- The 2 `adversarial-exhausted` tasks correctly show `Approved within "
        "budget = NO` after spending the full revision budget — the loop reports "
        "budget exhaustion rather than silently approving a draft that still "
        "fails a requirement. This is the benchmark's evidence that the pattern's "
        "stop condition (`critique.approved and policy.accepts(score)`) is real: "
        "it does not rubber-stamp on timeout."
    )
    lines.append(
        "- This receipt says nothing about whether reflection improves *real* LLM "
        "output — it demonstrates that, given a scoring function, the "
        "draft → critique → revise → re-critique control flow in "
        "`reflection.py` mechanically moves the score toward the critic's bar "
        "when the generator can address the critique, and honestly fails to when "
        "it can't."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    policy = QualityPolicy()
    summary = run_benchmark(policy)
    receipt = render_receipt(summary, policy)
    out_path = REPO_ROOT / "docs" / "receipts" / "benchmark.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(receipt, encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"mean_score_delta={summary.mean_score_delta:+.4f}")
    print(f"improved={summary.improved_count}/{len(summary.outcomes)} ({summary.improved_pct}%)")
    print(f"approved_within_budget={summary.approved_count}/{len(summary.outcomes)} ({summary.approved_pct}%)")
    print(f"exhausted={summary.exhausted_count}/{len(summary.outcomes)} ({summary.exhausted_pct}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
