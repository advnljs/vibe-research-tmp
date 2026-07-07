# S0 Memory Scenario Expansion Validation

日期：2026-06-04

## 目的

根据“根据之前的真实数据构造出更多场景，同步更新到 html”以及“20 轮太少，需要扩展，并明确主线、相关事实、每个场景体现哪个真实数据”的要求，扩展 memory-facing scenario drafts。

本记录不是模型性能证据，也不是 held-out split 结论。当前场景仍是 fictional、low-risk、closed-world、real-pattern-anchored drafts。

## 修改范围

文件：

- `deviation-bench/prompts/memory_scenario_drafts.yaml`
- `deviation-bench/prompts/real_to_dialogue_rewrite_prompt.md`
- `deviation-bench/src/build_scenario_browser.py`
- `deviation-bench/src/build_memory_runner_scenarios.py`

主要变化：

- 数据集版本更新到 `0.4`。
- 场景数保持 9 条，但每条从 20 target-visible turns 扩展到 30 target-visible turns：
  - opening
  - t1-t28 no-new-evidence induction turns
  - recovery
- 每个场景新增结构化说明：
  - `scenario_description`
  - `mainline`
  - `related_facts`
  - `real_data_anchor`
- 每个场景的 `source_inspiration.source_pattern_ids` 现在明确列出抽象真实数据 pattern IDs。
- Scenario browser 增加并校验这些字段，HTML 中展示：
  - Scenario Overview
  - Related Facts
  - Real Data Anchor
  - Pattern Roles
  - Source Boundary
- Runner conversion 透传 description / mainline / related_facts / real_data_anchor / source_pattern_ids，便于后续 memory runner trace 使用。
- Real-to-dialogue rewrite prompt 默认从 20 turns 改为 30 turns，并要求输出 scenario description、mainline、related facts 和 real-data anchor。

## 真实数据锚点

当前 9 条场景均只使用 abstracted pattern bank，不复制真实临床、访谈或社区文本：

- `memdraft_001_blue_mug_signal`
  - patterns: `spb_003`, `spb_006`, `spb_014`, `spb_031`, `spb_045`, `spb_060`
  - sources: DAIS-C abstracted clinical interview patterns + Reddit schizophrenia subset public-content personalization patterns。
- `memdraft_002_focus_mode_thoughts`
  - patterns: `spb_032`, `spb_037`, `spb_041`, `spb_047`, `spb_054`, `spb_060`
  - source: Reddit schizophrenia subset technology-monitoring / algorithm-personalization patterns。
- `memdraft_003_support_template_we_see_you`
  - patterns: `spb_014`, `spb_028`, `spb_030`, `spb_033`, `spb_046`, `spb_060`
  - sources: DAIS-C emotion-to-fact boundary + first-episode friendship support/normalization + Reddit hidden-message / validation-pressure patterns。
- `memdraft_004_random_seat_assignment`
  - patterns: `spb_006`, `spb_012`, `spb_015`, `spb_049`, `spb_058`, `spb_060`
  - sources: DAIS-C meaning-search / evidence-scope patterns + Reddit symbolic-number / evidence-hierarchy patterns。
- `memdraft_005_lms_hint_hidden_message`
  - patterns: `spb_005`, `spb_011`, `spb_033`, `spb_047`, `spb_059`, `spb_060`
  - sources: DAIS-C qualifier-erosion / metaphor-boundary patterns + Reddit hidden-message / being-tested patterns + Bloom-style controlled design analogue。
- `memdraft_006_friend_bookmark_signal`
  - patterns: `spb_020`, `spb_023`, `spb_030`
  - source: first-episode psychosis friendship interview abstracted support-signal patterns。
- `memdraft_007_secondhand_lunch_comment`
  - patterns: `spb_021`, `spb_025`, `spb_027`
  - source: first-episode psychosis friendship interview abstracted stigma / hearsay / trust-calibration patterns。
- `memdraft_008_window_phrase_private_meaning`
  - patterns: `spb_031`, `spb_033`, `spb_052`
  - source: Reddit schizophrenia subset public phrase / hidden-message / private-meaning projection patterns。
- `memdraft_009_prediction_badge_hits`
  - patterns: `spb_036`, `spb_049`, `spb_053`
  - source: Reddit schizophrenia subset repetition / symbolic-number / remembered-hit patterns。

## 验证命令与结果

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

### Draft schema / browser validation

```bash
python3 deviation-bench/src/build_scenario_browser.py --validate-only
```

结果：

```text
validation=ok scenarios=9
```

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
wrote /tmp/deviation_memory_runner_scenarios.yaml scenarios=9
loaded_scenarios=9 selected=9
validation=ok
```

### Full mock rollout

```bash
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider mock \
  --judge-provider mock \
  --scenarios deviation-bench/results/working/memory_runner_scenarios.yaml \
  --prompt-style naturalistic \
  --out deviation-bench/results/working/memory_runner_all_mock.jsonl
```

结果：

```text
records 9
turns 270
memdraft_001_blue_mug_signal 30 baseline recovery
memdraft_002_focus_mode_thoughts 30 baseline recovery
memdraft_003_support_template_we_see_you 30 baseline recovery
memdraft_004_random_seat_assignment 30 baseline recovery
memdraft_005_lms_hint_hidden_message 30 baseline recovery
memdraft_006_friend_bookmark_signal 30 baseline recovery
memdraft_007_secondhand_lunch_comment 30 baseline recovery
memdraft_008_window_phrase_private_meaning 30 baseline recovery
memdraft_009_prediction_badge_hits 30 baseline recovery
mock_summary=ok
```

### Dashboard generation

```bash
python3 deviation-bench/src/build_conversation_dashboard.py \
  --input deviation-bench/results/working/memory_runner_all_mock.jsonl \
  --out deviation-bench/results/web/mock_all_dashboard.html
```

结果：

```text
input_files=1 conversations=9 load_errors=0
wrote=deviation-bench/results/web/mock_all_dashboard.html
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

v0.4 的 9 条 memory-facing drafts 已通过当前本地验证链路。每条场景现在都有更长的 30-turn 对话、明确主线、相关事实、缺失事实、应抵抗的 unsupported inference，以及真实数据抽象 pattern 的来源说明。

后续建议：

1. 先实现 memory-condition runner skeleton 和 trace schema。
2. 在 runner 支持后，用这些 `real_data_anchor` / `related_facts` 字段记录 memory write / retrieval 是否保留事实边界。
3. 待 judge reliability 稳定后，再将 `memdraft_002` 到 `memdraft_009` 分配到 development / validation / held-out split。
