# Module: Agent Memory Evaluation

Last updated: 2026-06-05

## Responsibility

This module covers the current main Deviation Bench framing: evaluating whether agent memory systems preserve evidence anchors or amplify unsupported claims compared with full transcript context.

## Entry Files

- Protocol: `deviation-bench/agent_memory_eval_protocol.md`
- System survey: `deviation-bench/agent_memory_system_survey.md`
- Scenario drafts: `deviation-bench/prompts/memory_scenario_drafts.yaml`
- Scenario validation note: `deviation-bench/experiments/s0_memory_scenario_revision_validation_2026-06-04.md`
- Scenario expansion validation note: `deviation-bench/experiments/s0_memory_scenario_expansion_validation_2026-06-04.md`
- Runner conversion: `deviation-bench/src/build_memory_runner_scenarios.py`
- Main runner: `deviation-bench/src/deviation_bench_pilot.py`
- Memory summary: `deviation-bench/src/summarize_memory_runs.py`
- Runner validation note: `deviation-bench/experiments/s0_memory_condition_runner_skeleton_validation_2026-06-05.md`

## Key Interfaces

Current runner CLI:

```bash
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider mock \
  --judge-provider mock \
  --prompt-style naturalistic \
  --scenarios deviation-bench/results/working/memory_runner_scenarios.yaml \
  --memory-condition rolling_summary \
  --token-window 16000 \
  --memory-trace-out deviation-bench/results/working/memory_trace.jsonl
```

Implemented conditions:

```text
full_transcript
recent_window
rolling_summary
```

Next conditions: `vector_chunks`, `llm_fact_memory`, `evidence_aware_memory`.

## Internal Dependencies

- Scenario schema and judge rubric in `deviation-bench/prompts/`
- Dashboard and web builders under `deviation-bench/src/`
- LLM-only consensus script `build_judge_consensus.py`

## External Dependencies

- Current implemented runner: `PyYAML`, Python standard library, OpenAI-compatible HTTP API.
- Future external baselines:
  - mem0 OSS (`mem0ai`) for fact-memory / hybrid retrieval.
  - Graphiti OSS (`graphiti-core`) for temporal graph / provenance.

## Notes

- Current local Python is 3.8.10 and lacks `pip`; external memory-system testing needs Python 3.10+ environment.
- `memdraft_001_blue_mug_signal` is already used in real smoke and should be development-only.
- `memory_scenario_drafts.yaml` v0.4 contains 9 longform 30-turn drafts with scenario description, mainline, related facts, real-data anchor, and source pattern IDs.
- v0.4 passed browser validation, runner conversion, 9-record / 270-turn mock rollout, dashboard generation, and local HTML refresh.
- The local runner skeleton and trace schema passed 27-record / 810-turn mock validation.
- Summary semantic evidence relation/distortion is deliberately `not_evaluated` until metajudge support exists.
- The next implementation should not install mem0/Graphiti yet; extend the local simulator with vector/fact/evidence-aware conditions first.
