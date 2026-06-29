# Memory Bank Navigation

Last updated: 2026-06-29

Canonical project navigation is `研究导航.md`. This file is a compact memory-bank-local index.

## Core Memory Files

- `overall-progress.md`: completed work and current state.
- `overall-plan.md`: phase, milestones, decision log, implementation position.
- `next-step.md`: current action queue and handoff instructions.
- `todo.md`: compact task table.
- `architecture.md`: compact system architecture.
- `specs.md`: persistent user requirements and constraints.
- `module-agent-memory-eval.md`: paused historical agent-memory module notes.
- `module-deviation-bench-new.md`: current primary real-data session pipeline and data contract.
- `module-webgame-ui.md`: Phaser UI replica module notes.

## Current High-Value Project Files

- `deviation-bench-new/README.md`: current primary route, counts, commands and interpretation boundary.
- `deviation-bench-new/experiments/real_data_session_preparation_2026-06-22.md`: 968-session preparation and validation report.
- `deviation-bench-new/src/`: parsers, DeepSeek builders, QC validator and local browser.
- `deviation-bench-new/src/audit_release.py`: release hardening pre-audit, candidate split/version manifest and point-review unit builder.
- `deviation-bench-new/data/processed/`: three finished session JSONL files and summaries.
- `deviation-bench-new/data/screened/deepseek_v4_pro_reddit_screening_64k.jsonl`: tracked no-raw-text Reddit screen results.
- `deviation-bench-new/data/manifests/`: no-raw-text source and run manifests.
- `deviation-bench-new/data/manifests/deepseek_v4_pro_release_splits_64k.jsonl`: 968-row candidate split/version manifest.
- `deviation-bench-new/data/manifests/deepseek_v4_pro_release_audit_64k.json`: deterministic pre-audit summary.
- `deviation-bench-new/data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl`: 1,392-row second-pass/metajudge review queue.
- `deviation-bench-new/data/manifests/deepseek_v4_pro_release_splits_reviewed_64k.jsonl`: reviewed split manifest after actual LLM reviews.
- `deviation-bench-new/data/manifests/deepseek_v4_pro_release_audit_reviewed_64k.json`: reviewed audit combining pre-audit, metajudge and semantic duplicate review.
- `deviation-bench-new/data/reviews/`: tracked LLM review summaries/results without raw API responses.
- `deviation-bench-new/prompts/point_metajudge.md`: independent candidate-point review prompt.
- `deviation-bench-new/experiments/session_release_hardening_pre_audit_2026-06-29.md`: pre-audit experiment note.
- `deviation-bench-new/experiments/session_release_hardening_actual_flow_2026-06-29.md`: actual release-hardening flow note.
- `deviation-bench-new/data/work/runs_dashboard/index.html`: ignored dynamic local page that fetches run/result files.
- `deviation-bench-new/src/build_review_dashboard.py`: generator for the richer local review dashboard.
- `deviation-bench-new/data/work/review_dashboard/index.html`: ignored dynamic local page with actual experiment results, status icons, charts, filters, conversations, metajudge rationales and duplicate/leakage review.
- The files below belong to the paused historical agent-memory route:
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
- `tmp-webgame-ui/web/styles.css`: DOM visual layers, shared-asset styling, responsive scaling, readable controls, selectable left-page text, and page-turn animation.
- `tmp-webgame-ui/web/app.js`: pure JavaScript scene composition, centralized text-size scaling, and interactions.
- `tmp-webgame-ui/refer/`: user-supplied source material sheets.
- `tmp-webgame-ui/assets/generated/`: deterministic transparent sprites generated from `refer/`.
- `tmp-webgame-ui/scripts/build-assets.sh`: source-sheet crop and transparency build pipeline.
- `tmp-webgame-ui/scripts/capture-and-compare.sh`: Chrome screenshot and pixel comparison entrypoint.
- `tmp-webgame-ui/scripts/capture-web-and-compare.sh`: Phaser-to-Web screenshot comparison.

## Common Commands

```bash
python3 deviation-bench-new/src/prepare_cases.py
python3 deviation-bench-new/src/prepare_reddit_cases.py
python3 deviation-bench-new/src/validate_sessions.py deviation-bench-new/data/processed/*_64k.jsonl
python3 deviation-bench-new/src/audit_release.py
python3 deviation-bench-new/src/run_point_metajudge.py --provider openai --include-negative-controls --resume --overwrite
python3 deviation-bench-new/src/run_semantic_duplicate_audit.py --provider openai --resume --overwrite
python3 deviation-bench-new/src/finalize_release_hardening.py
python3 deviation-bench-new/src/build_runs_dashboard.py
python3 deviation-bench-new/src/build_review_dashboard.py
python3 -m unittest discover -s deviation-bench-new/tests -v
python3 deviation-bench-new/src/build_dataset_browser.py --input 'deviation-bench-new/data/processed/*_64k.jsonl'
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
