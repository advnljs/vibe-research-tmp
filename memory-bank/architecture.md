# Architecture

Last updated: 2026-06-04

This is a compact architecture memory file. Detailed research state lives in `memory-bank/overall-plan.md`, `memory-bank/next-step.md`, and `研究导航.md`.

## System Boundary

Deviation Bench is a low-GPU, API-only research workspace for evaluating reality-grounded judgment under multi-turn pressure. The current primary framing is agent-memory evaluation: compare direct full transcript context with memory-conditioned generation on fictional, evidence-bound scenarios.

The project does not train models, read activations, scrape new sensitive data by default, or use human annotation as paper evidence.

## Main Components

- Research docs: `deviation-bench/*.md`
- Scenario specs: `deviation-bench/prompts/*.yaml` and rewrite/judge prompts.
- Runner: `deviation-bench/src/deviation_bench_pilot.py`
- Scenario tooling: `build_scenario_browser.py`, `build_memory_runner_scenarios.py`
- Judge reliability tooling: `build_judge_consensus.py`
- Dashboard/web tooling: `build_conversation_dashboard.py`, `build_web_index.py`, `scripts/start_research_web.sh`
- Data/source notes: `deviation-bench/data_sources/`
- Project memory: `memory-bank/`

## Data Flow

1. Real clinical/community/reference sources are converted only into abstract patterns or fictional scenario drafts.
2. Scenario YAML defines scenario descriptions, mainlines, related facts, real-data anchors, evidence anchors, unsupported claims, no-new-evidence induction turns, and recovery turns.
3. Runner sends target-visible naturalistic user turns to target model and hidden evidence anchors to the judge.
4. Judge outputs structured labels and metrics.
5. Consensus/metajudge tooling rechecks priority turns for paper-facing LLM-only validation.
6. Future memory runner will add memory write/retrieval/context traces before target generation.

## Key Technical Decisions

- Use OpenAI-compatible chat completions for target and judge APIs.
- Keep generated raw results under ignored `deviation-bench/results/`.
- Do not use human annotation as paper-facing labels.
- Treat mem0 and Graphiti as first external memory-system baselines only after version/config pinning.
- Implement local memory simulator before external systems.

## Important Constraints

- Use fictional low-risk scenarios; do not copy raw patient/community text into prompts.
- Do not turn the work into jailbreak/safety-bypass research.
- External memory systems need traceable provenance, memory write policy, retrieval policy, token counts, and per-turn context records.
- Current environment has Python 3.8.10 and no `pip`; external mem0/Graphiti smoke needs Python 3.10+ environment.

## Architecture Change History

- 2026-05-21 to 2026-05-30: UIRD benchmark runner, judge, dashboard, LLM-only validation route.
- 2026-05-31: Main paper framing upgraded to agent-memory evaluation; protocol and memory-facing scenarios added.
- 2026-06-04: M1 memory-system tooling survey completed; next architecture change should be memory-condition runner support.
- 2026-06-04: Memory-facing scenario drafts expanded to v0.4 with 9 longform 30-turn drafts and explicit source-pattern metadata; browser and runner conversion now preserve/display those fields.
