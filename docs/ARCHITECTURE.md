# Architecture Decision Record: Reflection Agent Pattern

## Context

Accuracy-critical AI workflows need more than a better prompt. Code generation, technical writing, policy analysis, regulated content, and executive reporting all benefit from an explicit review loop where one model output is critiqued against quality criteria before it is released.

## Decision

This repo implements Reflection as a generator-critic-reviser system:

1. `Generator.draft` creates the first answer.
2. `Critic.review` scores the answer and returns actionable findings.
3. `QualityPolicy` decides whether the answer is acceptable.
4. `Generator.revise` improves the answer using critique.
5. `ReflectionAgent` owns the loop limit and finalization behavior.

The critic is a separate interface from the generator. In production, the critic can be a stronger model, a cheaper model with strict rubrics, a rules engine, static analysis, retrieval-grounded verifier, human reviewer, or a blend of those.

## When To Use

Use Reflection when correctness and polish are more important than lowest latency:

- Code generation and code review.
- Content validation and editing.
- High-stakes reasoning.
- Requirements and architecture documents.
- Customer-facing communication that must be checked before delivery.

Avoid Reflection for simple tool lookup where a ReAct loop is cheaper and easier to observe.

## Runtime Flow

```text
Task
  -> initial draft
  -> critique with score and findings
  -> accept if threshold passes
  -> revise and review again until budget is exhausted
```

## State Model

Each attempt stores the draft and critique. Production systems should persist:

- Prompt and model metadata.
- Critique rubric version.
- Score, findings, and approval decision.
- Revision lineage.
- Human override decisions.

Do not persist hidden chain-of-thought. Persist summarized critique and explicit evidence instead.

## Guardrails

- Minimum score threshold.
- Maximum revision count.
- Structured critique object.
- Separate approval from score so policy can include hard-fail rules.

Recommended production additions:

- Rubric-specific evaluators.
- Regression suites with golden tasks.
- Static analyzers for generated code.
- Factuality checks against retrieval sources.
- Human review queue when scores remain low after retries.

## Failure Modes

- Critic leniency: the reviewer approves weak output. Mitigation: calibrate against human-labeled examples.
- Critic overfitting: the generator learns to satisfy rubric wording without solving the task. Mitigation: rotate rubrics and use task-specific evidence checks.
- Latency amplification: every revision adds model calls. Mitigation: use Reflection only on workflows where quality economics justify it.
- Infinite refinement pressure: models keep changing acceptable answers. Mitigation: threshold plus revision cap.

## Scaling Strategy

Run Reflection inline for short-form tasks. For heavier work, move critique and revision to asynchronous jobs with resumable state. Use score distributions and finding categories as product telemetry: they reveal where prompts, tools, or source data are weak.

## Success Metrics

- Pass rate after first draft.
- Pass rate after revision.
- Human acceptance rate.
- Defect escape rate.
- Average revisions per task.
- Cost per accepted answer.

