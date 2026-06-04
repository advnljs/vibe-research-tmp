# Todo

Last updated: 2026-06-04

This file mirrors the actionable queue in `memory-bank/next-step.md`. The detailed handoff source remains `next-step.md`; this file exists to satisfy the global memory-bank workflow with a compact task index.

## Active Tasks

| Task | Priority | Status | Blocker | Next step |
|---|---|---|---|---|
| Implement local memory-condition runner skeleton | P0 | pending | none for local mock/full transcript/recent window/rolling summary | Add CLI flags, trace schema, and mock validation without external dependencies. |
| Add local retrieval/fact/evidence-aware memory conditions | P1 | pending | runner skeleton first | Implement `vector_chunks`, `llm_fact_memory`, `evidence_aware_memory`; use development items only. |
| Prepare external memory environment | P1 | blocked | current `python3` is 3.8.10 and no `pip`; mem0/Graphiti require Python 3.10+ | Create venv/container or alternate environment before installing `mem0ai` / `graphiti-core`. |
| Run S1 judge reliability pass | P1 | pending | should follow runner design or run in parallel if API budget exists | Use `build_judge_consensus.py` with real metajudge and gold controls. |
| Fresh memory-facing scenario split | P2 | pending | runner and judge reliability should stabilize first | Keep `memdraft_002` to `memdraft_005` as candidates; `memdraft_001` is used smoke/development. |
| External mem0 / Graphiti smoke | P2 | blocked | needs Python 3.10+ env and version pins | Run 1 scenario x 1 target x 1 external system; record exact config. |

## Completed Recently

- 2026-06-04: Completed `deviation-bench/agent_memory_system_survey.md`.
- 2026-05-31: Completed Agent Memory protocol, memory-facing drafts/browser, first memory real API smoke, and local web workspace.
