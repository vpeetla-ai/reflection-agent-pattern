# Reflection Agent Pattern


<!-- vpeetla-tech-stack:start -->
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square)]() [![Curriculum stub](https://img.shields.io/badge/Curriculum-stub-0EA5E9?style=flat-square)]() [![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square)]() [![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square)]()
<!-- vpeetla-tech-stack:end -->
**Curriculum teaching stub for Reflection loops** — critique-and-revise before delivery. Pattern used in **VAP Research + Architecture**.

[▶ Live demo](https://reflection-agent-pattern.vercel.app) · [Architecture](docs/ARCHITECTURE.md) · [Portfolio](https://venkat-ai.com/work) · [VAP case study](https://github.com/vpeetla-ai/ai-architecture-portfolio/blob/main/case-studies/venkat-ai-platform.md)

## What this is

Self-critique loops improve draft quality before ship — bounded reflection with trace viewer for teaching.

## How we solve it

Critic agent revises generator output with stop conditions and structured traces — composable into VAP pipelines.

## Case study & tradeoffs

[venkat-ai.com/work](https://venkat-ai.com/work) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

Org skills: [vpeetla-ai-skills](https://github.com/vpeetla-ai/vpeetla-ai-skills). This repo includes `.cursor/skills/`, `AGENTS.md`, and `CONTEXT.md`.

```bash
git clone https://github.com/vpeetla-ai/vpeetla-ai-skills.git
./vpeetla-ai-skills/scripts/install.sh --cursor --codex --project .
```

---


> **Scope:** Curriculum stub with deterministic tests and a live trace viewer — not a production agent fleet. Compose into [Venkat AI Platform](https://github.com/vpeetla-ai/venkat-ai-platform) for governed graphs.

## Implementation status

| Component | Status | Notes |
|-----------|--------|-------|
| Pattern demo + trace UI | ✅ | Live Vercel demo |
| Core agent loop | ✅ | Reference implementation |
| LangGraph production graph | 🟡 | Teaching scope — compose into VAP for fleet use |
| MCP tool bridge | ❌ | See LoopForge / VAP MCP docs |
| AegisAI gateway | ❌ | No side effects in pattern demo |
| Pytest regression | ✅ | `pytest -q` in repo |


[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://reflection-agent-pattern.vercel.app)
[![Part of Curriculum Agent Patterns](https://img.shields.io/badge/series-Curriculum%20Agent%20Patterns-purple)](https://github.com/vpeetla-ai/reflection-agent-pattern)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Part 2 of 5** in the [Curriculum Agent Patterns](https://github.com/vpeetla-ai/react-agent-pattern) series.

Curriculum teaching stub (compose into VAP for production graphs) of the **Reflection** pattern for accuracy-critical generation, code review, content validation, and complex reasoning workflows.

| # | Pattern | Repository | Use when |
|---|---------|------------|----------|
| 1 | ReAct | [react-agent-pattern](https://github.com/vpeetla-ai/react-agent-pattern) | Tool use + reasoning loops |
| 2 | **Reflection** | **this repo** | Self-critique and improve output |
| 3 | Plan-Execute | [plan-execute-agent-pattern](https://github.com/vpeetla-ai/plan-execute-agent-pattern) | Decompose goals into steps |
| 4 | Multi-Agent | [multi-agent-system-pattern](https://github.com/vpeetla-ai/multi-agent-system-pattern) | Specialized role delegation |
| 5 | Swarm | [swarm-agent-pattern](https://github.com/vpeetla-ai/swarm-agent-pattern) | Parallel autonomous agents |

[▶ Live demo](https://reflection-agent-pattern.vercel.app) · [📖 Full series roadmap](https://github.com/vpeetla-ai/ai-content-factory/blob/main/docs/agent-patterns/ROADMAP.md) · [Compose in production — AI Content Factory (separate repo)](https://ai-content-factory-iota.vercel.app)

---

## What you'll learn

- **Draft → critique → improve → finalize** loop
- Quality gates with score thresholds and retry limits
- Independent generator and critic interfaces
- Structured review findings for logging, UI, and evaluation

## What this repo demonstrates

- Draft, critique, improve, and finalize loop
- Quality gates with score thresholds and retry limits
- Independent generator and critic interfaces
- Structured review findings that can be logged, displayed, or used for evaluation

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m reflection_agent_pattern
pytest
```

Runs without API keys using deterministic generator and critic stubs.

```bash
cp .env.example .env
```

See [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) for production setup.

## Repo layout

```text
src/reflection_agent_pattern/
  __main__.py
  reflection.py
  models.py
  policy.py
docs/ARCHITECTURE.md
tests/test_reflection.py
```

## Interview map

**Business function:** Minimal LangGraph teaching stub for one agent pattern (compose into VAP for production).

Staff+ prep crosswalk — [playbook](https://github.com/vpeetla-ai/ai-architect-interview-playbook) · [study UI](https://ai-architect-interview-playbook-9xs.vercel.app) · [Practice Arena](https://ai-architect-practice-arena.vercel.app) · [org matrix](https://github.com/vpeetla-ai/ai-architecture-portfolio/blob/main/docs/REPO_INTERVIEW_MAP.md). Only entries this repo honestly exercises.

| Category | Entry | Fit |
|----------|-------|-----|
| System design | [Agent tool-use / orchestration](https://ai-architect-interview-playbook-9xs.vercel.app/q/ai-system-design/03-agent-tool-use-orchestration-platform) ([md](https://github.com/vpeetla-ai/ai-architect-interview-playbook/blob/main/ai-system-design/03-agent-tool-use-orchestration-platform.md)) | Pattern slice only — not a full platform |
| Coding | [Clone a graph (cycle-safe)](https://ai-architect-interview-playbook-9xs.vercel.app/q/coding/07-graph-clone-and-cycle-safe) ([md](https://github.com/vpeetla-ai/ai-architect-interview-playbook/blob/main/coding/07-graph-clone-and-cycle-safe.md)) | Light — graph structure intuition for LangGraph |

## Related

- **Previous:** [ReAct Agent Pattern](https://github.com/vpeetla-ai/react-agent-pattern)
- **Next:** [Plan-Execute Agent Pattern](https://github.com/vpeetla-ai/plan-execute-agent-pattern)
- **Full pipeline:** [AI Content Factory](https://github.com/vpeetla-ai/ai-content-factory)

⭐ Star the repo if this pattern helps your work.
