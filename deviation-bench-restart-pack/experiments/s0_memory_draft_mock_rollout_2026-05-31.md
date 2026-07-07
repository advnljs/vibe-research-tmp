# S0 Memory Draft Mock Rollout

日期：2026-05-31

## 目的

响应用户要求，将第一批 agent-memory-facing scenario drafts 从 12 轮扩展到标准 20 轮，并确认它们能进入现有 Deviation Bench rollout / dashboard 流水线。

这些结果是工程 smoke，不是 paper-facing benchmark evidence，也不是模型性能结论。

## 输入

- Draft scenarios: `deviation-bench/prompts/memory_scenario_drafts.yaml`
- Draft count: 5
- Turn structure: `opening` + `t1`-`t18` + `recovery`
- Runner conversion script: `deviation-bench/src/build_memory_runner_scenarios.py`
- Generated runner YAML: `deviation-bench/results/working/memory_runner_scenarios.yaml` (ignored)
- Mock output: `deviation-bench/results/working/memory_runner_all_mock.jsonl` (ignored)
- Mock dashboard: `deviation-bench/results/scenario_browser/mock_all_dashboard.html` (ignored)

## Scenario Count Check

All five drafts now have `draft_turn_count=20` and exactly 20 dialogue turns:

| Scenario | Turns | First | Last |
|---|---:|---|---|
| `memdraft_001_blue_mug_signal` | 20 | opening | recovery |
| `memdraft_002_focus_mode_thoughts` | 20 | opening | recovery |
| `memdraft_003_support_template_we_see_you` | 20 | opening | recovery |
| `memdraft_004_random_seat_assignment` | 20 | opening | recovery |
| `memdraft_005_lms_hint_hidden_message` | 20 | opening | recovery |

## Validation Commands

```bash
python3 deviation-bench/src/build_scenario_browser.py --validate-only
python3 -m py_compile deviation-bench/src/build_scenario_browser.py deviation-bench/src/build_memory_runner_scenarios.py
python3 deviation-bench/src/build_scenario_browser.py --out deviation-bench/results/scenario_browser/index.html
python3 deviation-bench/src/build_memory_runner_scenarios.py --out deviation-bench/results/working/memory_runner_scenarios.yaml
python3 deviation-bench/src/deviation_bench_pilot.py --scenarios deviation-bench/results/working/memory_runner_scenarios.yaml --validate-only
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider mock \
  --judge-provider mock \
  --scenarios deviation-bench/results/working/memory_runner_scenarios.yaml \
  --prompt-style naturalistic \
  --out deviation-bench/results/working/memory_runner_all_mock.jsonl
python3 deviation-bench/src/build_conversation_dashboard.py \
  --input deviation-bench/results/working/memory_runner_all_mock.jsonl \
  --out deviation-bench/results/scenario_browser/mock_all_dashboard.html
```

## Results

- Scenario browser validation: `validation=ok scenarios=5`
- Runner YAML validation: `loaded_scenarios=5 selected=5`, `validation=ok`
- Mock rollout:
  - records: 5
  - total turns: 100
  - per-record turns: 20
  - first turn: `baseline`
  - last turn: `recovery`
- Mock dashboard:
  - conversations: 5
  - load errors: 0
- Scenario browser page size: about 71KB
- Mock dashboard page size: about 129KB

## Real API Status

Real API rollout was not run in this stage because the shell environment did not contain:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `JUDGE_MODEL`

Next real test should use the generated runner YAML or regenerate it, then run one scenario first before running all five.

Suggested one-scenario command once API variables are set:

```bash
python3 deviation-bench/src/build_memory_runner_scenarios.py \
  --scenario-id memdraft_001_blue_mug_signal \
  --out deviation-bench/results/working/memory_runner_smoke.yaml

python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider openai \
  --judge-provider openai \
  --scenarios deviation-bench/results/working/memory_runner_smoke.yaml \
  --scenario-id memdraft_001_blue_mug_signal \
  --prompt-style naturalistic \
  --model "$OPENAI_MODEL" \
  --judge-model "$JUDGE_MODEL" \
  --base-url "$OPENAI_BASE_URL" \
  --out deviation-bench/results/working/memory_runner_real_smoke.jsonl \
  --timeout 180 \
  --sleep 0.5
```

## Interpretation

The new drafts are now long enough for memory-pressure testing and can be exercised by the existing target/judge runner after conversion. They still need user review for naturalness, objective boundary clarity, and whether each item should enter a formal held-out split.
