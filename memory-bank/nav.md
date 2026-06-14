# Memory Bank Navigation

Last updated: 2026-06-14

Canonical project navigation is `研究导航.md`. This file is a compact memory-bank-local index.

## Core Memory Files

- `overall-progress.md`: completed work and current state.
- `overall-plan.md`: phase, milestones, decision log, implementation position.
- `next-step.md`: current action queue and handoff instructions.
- `todo.md`: compact task table.
- `architecture.md`: compact system architecture.
- `specs.md`: persistent user requirements and constraints.
- `module-agent-memory-eval.md`: current main module notes.
- `module-webgame-ui.md`: Phaser UI replica module notes.

## Current High-Value Project Files

- `deviation-bench/agent_memory_eval_protocol.md`: formal agent-memory evaluation protocol.
- `deviation-bench/agent_memory_system_survey.md`: current M1 tooling survey and external-system selection.
- `deviation-bench/prompts/memory_scenario_drafts.yaml`: memory-facing 30-turn drafts, current version `0.4`.
- `deviation-bench/experiments/s0_memory_scenario_revision_validation_2026-06-04.md`: scenario v0.2 validation note.
- `deviation-bench/experiments/s0_memory_scenario_expansion_validation_2026-06-04.md`: scenario v0.4 expansion validation note.
- `deviation-bench/experiments/s0_memory_condition_runner_skeleton_validation_2026-06-05.md`: local memory runner/trace/MIDA validation.
- `deviation-bench/src/deviation_bench_pilot.py`: current API-only runner.
- `deviation-bench/src/summarize_memory_runs.py`: matched full-transcript MIDA and memory-trace summary.
- `deviation-bench/src/build_judge_consensus.py`: LLM-only metajudge/consensus tooling.
- `deviation-bench/后续优先级路线图.md`: priority ordering.
- `tmp-webgame-ui/src/game.js`: Phaser Scene, hotspots, and UI state feedback.
- `tmp-webgame-ui/web/index.html`: pure Web frontend entrypoint.
- `tmp-webgame-ui/web/styles.css`: DOM visual layers, shared-asset styling, responsive scaling, and page-turn animation.
- `tmp-webgame-ui/web/app.js`: pure JavaScript scene composition and interactions.
- `tmp-webgame-ui/refer/`: user-supplied source material sheets.
- `tmp-webgame-ui/assets/generated/`: deterministic transparent sprites generated from `refer/`.
- `tmp-webgame-ui/scripts/build-assets.sh`: source-sheet crop and transparency build pipeline.
- `tmp-webgame-ui/scripts/capture-and-compare.sh`: Chrome screenshot and pixel comparison entrypoint.
- `tmp-webgame-ui/scripts/capture-web-and-compare.sh`: Phaser-to-Web screenshot comparison.

## Common Commands

```bash
python3 deviation-bench/src/deviation_bench_pilot.py --validate-only
python3 deviation-bench/src/build_scenario_browser.py --validate-only
python3 deviation-bench/src/summarize_memory_runs.py --input 'deviation-bench/results/working/memory_condition_*_mock.jsonl'
python3 -m py_compile deviation-bench/src/deviation_bench_pilot.py
python3 -m py_compile deviation-bench/src/build_judge_consensus.py
cd tmp-webgame-ui && npm start
cd tmp-webgame-ui && npm run build:assets
cd tmp-webgame-ui && npm run verify:screenshot
cd tmp-webgame-ui && npm run verify:web
```
