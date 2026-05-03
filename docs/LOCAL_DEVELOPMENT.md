# Local Development Guide

## Current Runtime Behavior

This repo runs locally without any LLM API key. It uses deterministic generator and critic stubs:

- `ScriptedGenerator` creates the first draft.
- `ScriptedCritic` scores the draft and returns findings.
- `ReflectionAgent` revises until the quality policy passes or the revision budget is exhausted.

This lets you test the Reflection architecture before adding real model calls.

## 1. Setup

```bash
cd /Users/lakshmipraveenabodempudi/reflection-agent-pattern
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Run Locally

```bash
python -m reflection_agent_pattern
```

No-key smoke run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m reflection_agent_pattern
```

Expected behavior:

- Initial draft is generated.
- Critic rejects the first draft with findings.
- Generator revises the answer.
- Critic approves the revised output.

## 3. Run Tests

```bash
pytest
```

## 4. Environment Variables

Create your local environment file:

```bash
cp .env.example .env
```

Important variables:

| Variable | Purpose |
| --- | --- |
| `AGENT_RUNTIME_MODE` | `local_stub` or `llm` |
| `OPENAI_API_KEY` | OpenAI API key |
| `GENERATOR_MODEL` | Model used for draft and revision |
| `CRITIC_MODEL` | Model used for critique |
| `REFLECTION_MIN_SCORE` | Quality score required to finalize |
| `REFLECTION_MAX_REVISIONS` | Maximum self-correction attempts |
| `DATABASE_URL` | Store drafts, critiques, scores, and approvals |
| `ENABLE_HUMAN_REVIEW` | Escalate low-confidence outputs |

## 5. Where To Add Real LLM Support

Add provider-backed implementations in:

```text
src/reflection_agent_pattern/models.py
```

Create classes that implement:

- `Generator`
- `Critic`

Recommended adapters:

```python
class OpenAIGenerator:
    def draft(self, task: str) -> str:
        ...

    def revise(self, task: str, draft: str, critique: Critique) -> str:
        ...

class OpenAICritic:
    def review(self, task: str, draft: str) -> Critique:
        ...
```

The critic should return structured data, not free-form prose. Persist the score, findings, model version, rubric version, and final approval decision.

## 6. Where To Add Database Support

Recommended persisted entities:

- `reflection_requests`
- `reflection_attempts`
- `critique_findings`
- `quality_scores`
- `human_review_decisions`

Store every attempt because revision lineage is essential for auditability and quality analysis.

## 7. Production Readiness Checks

- Critic scores correlate with human review.
- Rubrics are versioned.
- Revision count is capped.
- Low-quality outputs escalate safely.
- Cost is tracked across generator and critic calls.
- Sensitive draft data is redacted before logging.

