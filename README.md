# Reflection Agent Pattern

Production-grade reference implementation of the Reflection pattern for accuracy-critical generation, code review, content validation, and complex reasoning workflows.

## What This Repo Demonstrates

- Draft, critique, improve, and finalize loop.
- Quality gates with score thresholds and retry limits.
- Independent generator and critic interfaces.
- Structured review findings that can be logged, displayed, or used for evaluation.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m reflection_agent_pattern
pytest
```

## Repo Layout

```text
src/reflection_agent_pattern/
  __main__.py
  reflection.py
  models.py
  policy.py
docs/ARCHITECTURE.md
tests/test_reflection.py
```

