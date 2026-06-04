# S0 Memory Scenario Revision Validation

日期：2026-06-04

## 目的

根据“先完善对话场景，但前面以验证为主”的要求，对第一批 memory-facing scenario drafts 做最小必要修订，并验证它们仍能通过现有 scenario browser、runner conversion、mock rollout 和 dashboard 生成链路。

本记录不是模型性能证据，也不是 paper-facing judge reliability 结果。

## 修改范围

文件：

- `deviation-bench/prompts/memory_scenario_drafts.yaml`

主要变化：

- 数据集版本从 `0.1` 更新到 `0.2`。
- `memdraft_001_blue_mug_signal` 标记为 `development_used_smoke`，因为它已经跑过真实 API smoke。
- `memdraft_002` 到 `memdraft_005` 标记为 `fresh_memory_candidate`。
- 对 `memdraft_002` 到 `memdraft_005` 做轻量文本修订：
  - 减少后半段可能被误解为“新增观察证据”的表达。
  - 保持 induction turns 的 no-new-evidence 约束。
  - 让压力更偏向回忆、联想、假设和 validation pressure。
  - 不改变 20-turn 结构：opening + t1-t18 + recovery。

用户补充要求：

- turns 的设置可以后续参考其他相关 paper。
- 当前优先级放在验证，而不是立刻扩展文献驱动的 turn 设计。

## 验证命令与结果

### Draft schema / browser validation

```bash
python3 deviation-bench/src/build_scenario_browser.py --validate-only
```

结果：

```text
validation=ok scenarios=5
```

### Draft structure summary

```bash
python3 - <<'PY'
import yaml
from pathlib import Path
p=Path('deviation-bench/prompts/memory_scenario_drafts.yaml')
data=yaml.safe_load(p.read_text(encoding='utf-8'))
print(data['dataset_version'], data['last_updated'], data['status'])
for s in data['scenarios']:
    dialogue=s['dialogue']
    print(s['scenario_id'], s.get('split_candidate'), s.get('review_status'), len(dialogue), dialogue[0]['turn_id'], dialogue[-1]['turn_id'])
PY
```

结果：

```text
0.2 2026-06-04 revised_for_memory_runner_design
memdraft_001_blue_mug_signal development_used_smoke used_development_smoke 20 opening recovery
memdraft_002_focus_mode_thoughts fresh_memory_candidate revised_candidate_2026_06_04 20 opening recovery
memdraft_003_support_template_we_see_you fresh_memory_candidate revised_candidate_2026_06_04 20 opening recovery
memdraft_004_random_seat_assignment fresh_memory_candidate revised_candidate_2026_06_04 20 opening recovery
memdraft_005_lms_hint_hidden_message fresh_memory_candidate revised_candidate_2026_06_04 20 opening recovery
draft_summary=ok
```

### Python compile

```bash
python3 -m py_compile \
  deviation-bench/src/build_scenario_browser.py \
  deviation-bench/src/build_memory_runner_scenarios.py \
  deviation-bench/src/deviation_bench_pilot.py \
  deviation-bench/src/build_conversation_dashboard.py \
  deviation-bench/src/build_web_index.py
```

结果：通过，无输出。

### Runner conversion and scenario validation

```bash
python3 deviation-bench/src/build_memory_runner_scenarios.py \
  --out /tmp/deviation_memory_runner_scenarios.yaml

python3 deviation-bench/src/deviation_bench_pilot.py \
  --scenarios /tmp/deviation_memory_runner_scenarios.yaml \
  --validate-only
```

结果：

```text
wrote /tmp/deviation_memory_runner_scenarios.yaml scenarios=5
loaded_scenarios=5 selected=5
validation=ok
```

### Full mock rollout

```bash
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider mock \
  --judge-provider mock \
  --scenarios /tmp/deviation_memory_runner_scenarios.yaml \
  --prompt-style naturalistic \
  --out /tmp/deviation_memory_runner_all_mock.jsonl
```

结果：

- records: 5
- turns: 100
- 每条 scenario 都是 20 turns。
- turn sequence: `baseline` 到 `recovery`。

### Dashboard generation

```bash
python3 deviation-bench/src/build_conversation_dashboard.py \
  --input /tmp/deviation_memory_runner_all_mock.jsonl \
  --out /tmp/deviation_memory_mock_dashboard.html
```

结果：

```text
input_files=1 conversations=5 load_errors=0
wrote=/tmp/deviation_memory_mock_dashboard.html
```

### Local web refresh

已重新生成 ignored 本地浏览页：

- `deviation-bench/results/web/scenarios.html`
- `deviation-bench/results/web/mock_all_dashboard.html`
- `deviation-bench/results/web/index.html`
- `deviation-bench/results/working/memory_runner_scenarios.yaml`
- `deviation-bench/results/working/memory_runner_all_mock.jsonl`

这些输出仍在 ignored `results/` 下，不作为提交内容。

## 当前结论

修订后的 5 条 memory-facing drafts 通过了当前本地验证链路。

后续建议：

1. 不再继续手工调 turns，先实现 memory-condition runner skeleton。
2. 待 runner 和 judge reliability 稳定后，再参考相关 paper 调整 turn 数、pressure schedule 和 recovery placement。
3. `memdraft_002` 到 `memdraft_005` 仍只是 fresh candidates，正式进入 held-out split 前还需要 memory-runner trace 验证和 S1 judge reliability。
