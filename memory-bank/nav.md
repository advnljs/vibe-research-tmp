# Memory Bank Navigation

Last updated: 2026-06-04

Canonical project navigation is `研究导航.md`. This file is a compact memory-bank-local index.

## Core Memory Files

- `overall-progress.md`: completed work and current state.
- `overall-plan.md`: phase, milestones, decision log, implementation position.
- `next-step.md`: current action queue and handoff instructions.
- `todo.md`: compact task table.
- `architecture.md`: compact system architecture.
- `specs.md`: persistent user requirements and constraints.
- `module-agent-memory-eval.md`: current main module notes.

## Current High-Value Project Files

- `deviation-bench/agent_memory_eval_protocol.md`: formal agent-memory evaluation protocol.
- `deviation-bench/agent_memory_system_survey.md`: current M1 tooling survey and external-system selection.
- `deviation-bench/prompts/memory_scenario_drafts.yaml`: first memory-facing 20-turn drafts.
- `deviation-bench/src/deviation_bench_pilot.py`: current API-only runner.
- `deviation-bench/src/build_judge_consensus.py`: LLM-only metajudge/consensus tooling.
- `deviation-bench/后续优先级路线图.md`: priority ordering.

## Common Commands

```bash
python3 deviation-bench/src/deviation_bench_pilot.py --validate-only
python3 deviation-bench/src/build_scenario_browser.py --validate-only
python3 -m py_compile deviation-bench/src/deviation_bench_pilot.py
python3 -m py_compile deviation-bench/src/build_judge_consensus.py
```
