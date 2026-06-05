# S0 Memory-Condition Runner Skeleton Validation

日期：2026-06-05

## 目的

完成 M2 的第一阶段本地 memory-condition runner skeleton，使同一 Deviation Bench episode 能显式比较
`full_transcript`、`recent_window` 和 `rolling_summary`，并生成逐轮 memory/context trace 与 MIDA 汇总。

本记录只验证工程 contract、trace 和汇总逻辑。Mock target/judge/summary 的结果不是模型性能证据。

## 修改范围

- `deviation-bench/src/deviation_bench_pilot.py`
  - 新增统一 context assembly 层。
  - 新增 `--memory-condition`、`--token-window`、`--recent-turns`、`--memory-trace-out` 和独立
    `--memory-*` provider/model 配置。
  - 每个 target turn 记录 full-transcript / condition-context 近似 tokens、compression ratio、memory
    writes、retrieval/context items、source turns、provenance、verification status、evidence relation、
    distortion flags 和 trimming flags。
  - `full_transcript` 在显式 token window 超限时失败；`recent_window` 和 `rolling_summary` 会按窗口裁剪。
- `deviation-bench/src/build_memory_runner_scenarios.py`
  - runner conversion 现在透传 `memory_test_design` 和每轮 `memory_probe_tags`。
- `deviation-bench/src/summarize_memory_runs.py`
  - 新增 matched full-transcript 对照和 MIDA 汇总。
  - 汇总 context token/compression、rule-derived evidence/unsupported-claim retention、provenance、
    distortion 和 relation-evaluation coverage。
- `deviation-bench/src/build_conversation_dashboard.py`
  - 优先使用 runner 记录的动态 expected turn count，并展示 memory condition；30-turn memory episodes 不再被
    旧的 20-turn 默认值误判。
- `deviation-bench/scripts/start_research_web.sh` / `deviation-bench/src/build_web_index.py`
  - 本地 web workspace 现在会生成并链接 memory-condition mock dashboard。
- `deviation-bench/src/README.md`
  - 新增本地 memory conditions、trace 和 MIDA 命令说明。

## 关键边界

- Token 计数使用无新依赖的 `utf8_bytes_div_4_v1` 近似，只用于本地 context assembly，不是 provider
  billing token。
- Mock `rolling_summary` 使用 deterministic engineering summary；real run 可使用独立 OpenAI-compatible
  memory model。
- Summary 的语义 evidence relation / distortion 当前标记为 `not_evaluated`，不能把 source provenance
  误当成 summary 真正保留了某个事实。
- 当前 episode 在 recovery 后结束，因此 `recovery_anchor_retention` 保持 `null`；需要未来 post-recovery
  probe 才能测量。

## 验证命令与结果

### Compile / conversion / schema

```bash
python3 -m py_compile \
  deviation-bench/src/deviation_bench_pilot.py \
  deviation-bench/src/build_memory_runner_scenarios.py \
  deviation-bench/src/summarize_memory_runs.py

python3 deviation-bench/src/build_memory_runner_scenarios.py \
  --out /tmp/memory_runner_scenarios.yaml

python3 deviation-bench/src/deviation_bench_pilot.py \
  --scenarios /tmp/memory_runner_scenarios.yaml \
  --validate-only
```

结果：

```text
wrote /tmp/memory_runner_scenarios.yaml scenarios=9
loaded_scenarios=9 selected=9
validation=ok
```

### Matched three-condition mock

在 development-only `memdraft_001_blue_mug_signal` 上，以相同 mock target/judge、naturalistic prompt、
`token_window=16000`、`recent_turns=4` 分别运行三个条件。

结果：

```text
full_transcript: turns=30, trace_records=30, summary_writes=0
recent_window: turns=30, trace_records=30, summary_writes=0
rolling_summary: turns=30, trace_records=30, summary_writes=26
```

最后一轮近似 context tokens：

```text
full_transcript=3011
recent_window=376
rolling_summary=1412
```

最后一轮 source-turn 范围：

```text
full_transcript: baseline ... recovery
recent_window: t26, t27, t28, recovery
rolling_summary: summary provenance baseline ... t25 + raw t26 ... recovery
```

### Token-window boundary

`rolling_summary` 使用 `token_window=700` 跑完同一 30-turn episode：

```text
max_condition_context_tokens=700
trace flags observed:
- oldest_context_turn_pair_trimmed
- summary_truncated_for_token_window
```

显式把 `full_transcript` 限制到 `token_window=700` 时，runner 在近似 full history 达到 742 tokens 后按预期
失败，而不是静默截断 baseline。

### Full draft-set contract run

对 9 条 v0.4 memory-facing drafts 分别运行三个条件：

```text
full_transcript: records=9, turns=270, traces=270, writes=0
recent_window: records=9, turns=270, traces=270, writes=0
rolling_summary: records=9, turns=270, traces=270, writes=234
total: records=27, turns=810, traces=810
```

每条记录的 `expected_turn_count=30`，与实际 turn count 一致。

### MIDA summary

```bash
python3 deviation-bench/src/summarize_memory_runs.py \
  --input 'deviation-bench/results/working/memory_condition_*_mock.jsonl' \
  --out deviation-bench/results/working/memory_condition_mida_summary.json
```

结果：

```text
runs=27
comparisons=27
```

Mock 三个条件的 drift metrics 相同，因此 MIDA 为 0；该结果只证明 matched comparison 与汇总 contract
可运行，不代表不同 memory condition 实际等价。

### Dashboard / local web

```bash
python3 deviation-bench/src/build_conversation_dashboard.py \
  --input 'deviation-bench/results/working/memory_condition_*_mock.jsonl' \
  --out deviation-bench/results/web/memory_conditions_mock_dashboard.html
```

结果：

```text
input_files=3 conversations=27 load_errors=0
```

本地 `deviation-bench/results/web/index.html` 已链接该 dashboard；27 条 conversation 均按动态
`expected_turn_count=30` 标为 full。

## 当前结论

M2 第一阶段 skeleton 已完成：runner 现在能显式区分 direct full history、recent truncation 和 rolling
summary，并输出可审计 trace 与 matched MIDA summary。

下一步应在同一接口上增加 `vector_chunks`、`llm_fact_memory` 和 `evidence_aware_memory`，然后再进入真实
memory-condition pilot 和外部 mem0 / Graphiti 接入。
