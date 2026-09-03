"""Real, fast pytest re-running the reflection critique-delta benchmark and
asserting invariants about the actual `ReflectionAgent` control flow — not
about real LLM output quality (the Generator/Critic here are deterministic
stubs; see scripts/benchmark_reflection_delta.py's module docstring).
"""

from __future__ import annotations

from reflection_agent_pattern.policy import QualityPolicy

from scripts.benchmark_reflection_delta import TASK_SCENARIOS, run_benchmark


def test_suite_has_at_least_ten_varied_tasks() -> None:
    assert len(TASK_SCENARIOS) >= 10
    groups = {scenario.group for scenario in TASK_SCENARIOS}
    assert {"already-passing", "one-revision", "two-revision", "adversarial-exhausted"} <= groups


def test_mean_score_delta_is_non_negative() -> None:
    summary = run_benchmark()
    assert summary.mean_score_delta >= 0


def test_already_passing_tasks_need_zero_revisions_and_zero_delta() -> None:
    summary = run_benchmark()
    already_passing = [o for o in summary.outcomes if o.scenario.group == "already-passing"]
    assert already_passing, "expected at least one already-passing scenario"
    for outcome in already_passing:
        assert outcome.revisions_used == 0
        assert outcome.score_delta == 0
        assert outcome.approved_within_budget is True


def test_budget_exhausted_tasks_are_reported_not_silently_dropped() -> None:
    """The adversarial tasks must show up in the results with
    approved_within_budget=False and a full revision spend — reflection.py's
    stop condition must not be papered over as a false approval."""
    summary = run_benchmark()
    adversarial = [o for o in summary.outcomes if o.scenario.group == "adversarial-exhausted"]
    assert adversarial, "expected at least one adversarial scenario"

    policy = QualityPolicy()
    for outcome in adversarial:
        assert outcome.approved_within_budget is False
        assert outcome.revisions_used == policy.max_revisions
        assert outcome.attempts == policy.max_revisions + 1

    # And they must be counted in the aggregate, not excluded from it.
    assert summary.exhausted_count == len(adversarial)
    assert summary.exhausted_count > 0
    assert summary.approved_count + summary.exhausted_count == len(summary.outcomes)


def test_revising_tasks_improve_and_eventually_get_approved() -> None:
    summary = run_benchmark()
    revising = [
        o for o in summary.outcomes if o.scenario.group in ("one-revision", "two-revision")
    ]
    assert revising, "expected at least one revising scenario"
    for outcome in revising:
        assert outcome.revisions_used >= 1
        assert outcome.score_delta > 0
        assert outcome.approved_within_budget is True


def test_two_revision_tasks_use_the_full_default_budget() -> None:
    summary = run_benchmark()
    policy = QualityPolicy()
    two_revision = [o for o in summary.outcomes if o.scenario.group == "two-revision"]
    assert two_revision, "expected at least one two-revision scenario"
    for outcome in two_revision:
        assert outcome.revisions_used == policy.max_revisions == 2


def test_aggregate_counts_are_internally_consistent() -> None:
    summary = run_benchmark()
    total = len(summary.outcomes)
    assert total == len(TASK_SCENARIOS)
    assert summary.improved_count <= total
    assert summary.approved_count + summary.exhausted_count == total
    assert 0 <= summary.improved_pct <= 100
    assert 0 <= summary.approved_pct <= 100
