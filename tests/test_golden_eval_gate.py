"""Real merge gate: runs the shared `reflection_agent.critique_delta_v1`
suite from vpeetla-ai/golden-eval-registry against this repo's own
`scripts/benchmark_reflection_delta.py` — the same 11 tasks, run for real
through the actual `ReflectionAgent` (see docs/receipts/benchmark.md for the
methodology and the numbers this suite's `expect` thresholds were derived
from).

Follows the convention established in
vpeetla-ai/aegisloop-agentops-workbench's
`services/api/tests/test_golden_eval_gate.py`: skip locally when the sibling
registry repo isn't checked out (set `GOLDEN_EVAL_REGISTRY_PATH` to run it
by hand), always check it out and run it in CI (see
.github/workflows/ci.yml).
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from scripts.benchmark_reflection_delta import run_benchmark

try:
    from golden_eval_registry.runner import score_suite
    from golden_eval_registry.schema import parse_manifest
    from golden_eval_registry.validate import load_jsonl

    GOLDEN_EVAL_REGISTRY_AVAILABLE = True
except ImportError:
    GOLDEN_EVAL_REGISTRY_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = Path(
    os.getenv("GOLDEN_EVAL_REGISTRY_PATH", str(REPO_ROOT / "golden-eval-registry"))
).resolve()
SUITE_DIR = REGISTRY_PATH / "suites" / "reflection_agent_critique_delta_v1"


@unittest.skipUnless(
    GOLDEN_EVAL_REGISTRY_AVAILABLE and SUITE_DIR.exists(),
    "golden-eval-registry not available — set GOLDEN_EVAL_REGISTRY_PATH or run in CI",
)
class GoldenEvalGateTests(unittest.TestCase):
    def test_reflection_agent_critique_delta_v1_suite_passes(self) -> None:
        manifest = parse_manifest(SUITE_DIR / "manifest.json")
        cases = load_jsonl(manifest.cases_path)

        summary = run_benchmark()
        outcomes_by_task_name = {outcome.scenario.name: outcome for outcome in summary.outcomes}

        actual_by_id: dict[str, dict] = {}
        for case in cases:
            task_name = case["input"]["task_name"]
            outcome = outcomes_by_task_name[task_name]
            actual_by_id[str(case["id"])] = {
                "score_delta": outcome.score_delta,
                "approved_within_budget": outcome.approved_within_budget,
                "revisions_used": outcome.revisions_used,
                "final_score": outcome.final_score,
            }

        result = score_suite(manifest, cases, actual_by_id)
        failures = "\n".join(f"{failure.case_id}: {failure.detail}" for failure in result.failures)
        self.assertTrue(result.passed, f"golden eval regressions:\n{failures}")

        # Suite-level aggregate thresholds declared on the manifest itself.
        mean_delta_min = manifest.thresholds.get("mean_score_delta_min")
        if mean_delta_min is not None:
            self.assertGreaterEqual(
                summary.mean_score_delta,
                mean_delta_min,
                f"mean_score_delta {summary.mean_score_delta} below suite threshold {mean_delta_min}",
            )

        approved_rate_min = manifest.thresholds.get("approved_within_budget_rate_min")
        if approved_rate_min is not None:
            approved_rate = summary.approved_count / len(summary.outcomes)
            self.assertGreaterEqual(
                approved_rate,
                approved_rate_min,
                f"approved_within_budget rate {approved_rate} below suite threshold {approved_rate_min}",
            )


if __name__ == "__main__":
    unittest.main()
