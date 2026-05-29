# Deviation Bench LLM 数据合成方案与 API 预算预估

创建日期：2026-05-29

目的：回答“如果需要 API key 进行 LLM 数据合成，应该怎么做、需要多少 token、多少 session、每个 session 几轮对话”。本文给出可执行的低 GPU / API-only 合成路线，并保持项目安全边界：不上传原始敏感转录或社区帖子，只使用已经抽象好的 seed patterns。

## 1. 结论摘要

需要 API key 的地方分三类：

1. **数据合成**：用 LLM 把 `seed_pattern_bank.jsonl` 中的抽象模式扩写成虚构、低风险、带 evidence anchor 的 benchmark item。
2. **数据质检**：用较强 LLM judge 检查是否复制原文、是否有真实人物/地点、是否引入高风险行动、是否符合 schema。
3. **真实 API pilot / benchmark 运行**：让 target model 跑生成好的 scenarios，再让 judge model 标注 stance / drift / recovery。

推荐先做小规模、可回滚的三阶段：

| 阶段 | 目标 | 是否需要 API key | 建议先做 |
|---|---|---|---|
| S0 Smoke | 1-2 个现有 scenario 真实 API 跑通 | 是 | 先做，验证 runner 和 judge |
| S1 Pilot synthesis | 合成 50 single-turn stems + 对齐现有 20 multi-turn scripts | 是 | 第二步，补齐 paraphrase/control |
| S2 v1 synthesis | 扩到 200-300 single-turn stems + 40-60 multi-turn scripts | 是 | pilot 有信号后再做 |

不建议直接跳到 S2。原因是目前还没有真实 API pilot 结果，也没有 judge-human agreement audit。

## 2. API key 使用方式

推荐只通过环境变量传 key，不写入仓库文件：

```bash
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="generation-model"
export JUDGE_MODEL="judge-model"
```

如果使用 OpenAI-compatible 的第三方服务，也保持同样结构，只改 `OPENAI_BASE_URL`、`OPENAI_MODEL`、`JUDGE_MODEL`。

本仓库已把本地 key 文件模式加入 `.gitignore`，例如 `.env`、`.env.*`、`*_key.txt`、`*key*.txt`。不要把 API key 放进 committed markdown、YAML、JSONL 或结果文件。

## 3. 输入与输出

### 3.1 输入

当前可直接用于合成的输入：

- `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl`
  - 60 条 abstracted patterns。
  - 不含原始转录或社区帖原文。
  - 每条含 `signal_type`、`risk_level`、`abstracted_template`、`scenario_use`。

- `deviation-bench/prompts/utterance_schema.yaml`
  - 统一 source / utterance / pattern schema。
  - 定义从 pattern bank 到 scenario seed 的规范化字段。

- `deviation-bench/prompts/scenario_schema.yaml`
  - 已有 pilot scenario schema。
  - 定义 evidence anchor、unsupported claim、induction turns、recovery turn、metrics。

### 3.2 输出

建议下一轮合成输出分三份：

| 文件 | 内容 | 是否公开 prompt 级别 |
|---|---|---|
| `deviation-bench/prompts/context_swap_stems.yaml` | single-turn stems，每个 stem 有 neutral + 3 context variants + 2 neutral paraphrases | 是，必须虚构低风险 |
| `deviation-bench/prompts/multiturn_scenarios_generated.yaml` | 新增或重写的 multi-turn scripts | 是，必须虚构低风险 |
| `deviation-bench/prompts/synthesis_qc_report.md` | LLM judge / 人审质检摘要 | 是，不含原文 |

已有 20 条 multi-turn pilot 可以保留，但应被统一 schema 和 neutral paraphrase control 补齐。

## 4. Session 定义

本文使用两个不同的 session 概念：

| 名称 | 定义 | 例子 |
|---|---|---|
| Synthesis API session | 一次 LLM API request/response，用于批量生成、修复或质检若干数据项 | 一次调用生成 5 个 single-turn stems |
| Evaluation session | 一个 target model 对一个 scenario 在一个 seed 下完成的测试 episode | 一个模型跑完某个 multi-turn scenario 的 baseline + induction + recovery |

对话轮数定义：

- **Single-turn evaluation session**：1 轮用户输入 + 1 轮模型输出。
- **Multi-turn evaluation session**：默认 5 个模型输出轮：
  1. baseline question
  2. induction turn 1
  3. induction turn 2
  4. induction turn 3
  5. recovery / re-anchoring turn

如果后续要测“恢复后稳定性”，可加第 6 轮 `post_recovery_check`，但首版不建议默认加，避免 token 翻倍。

## 5. 推荐合成流程

### S0: Real API smoke

目标：先验证 runner、target 输出 contract、judge JSON 和 metrics 是否可用。

建议规模：

| 项 | 数量 |
|---|---:|
| scenarios | 1-2 |
| target models | 1 |
| judge models | 1 |
| seeds | 1 |
| evaluation sessions | 1-2 |
| turns per multi-turn session | 5 |

预估 token：

| 组件 | 粗估 token |
|---|---:|
| target model outputs + growing context | 5k-8k / scenario |
| judge calls | 5k-8k / scenario |
| total | 10k-16k / scenario |

S0 总量：约 **20k-35k tokens**。

### S1: Pilot synthesis

目标：补齐当前 pilot 的单轮对照和 paraphrase noise，避免 reviewer 说 drift 只是普通 prompt sensitivity。

建议产物：

| 数据类型 | 数量 | 说明 |
|---|---:|---|
| single-turn stems | 50 | 每个 stem 有明确 evidence anchor |
| context variants | 50 x 3 = 150 | role / authority / social-consensus 或 emotional framing |
| neutral paraphrases | 50 x 2 = 100 | 用作 neutral paraphrase noise |
| multi-turn scripts | 20 | 可复用并修订已有 20 条 pilot |
| total prompt instances | 50 neutral + 150 variants + 100 paraphrases + 20 scripts | scripts 不是单轮 prompt |

Synthesis API sessions：

| 任务 | batch 策略 | API sessions | token/session 粗估 | 小计 |
|---|---:|---:|---:|---:|
| 生成 50 single-turn stems + variants | 5 stems / call | 10 | 5k-7k | 50k-70k |
| 生成 100 neutral paraphrases | 10 stems / call | 5 | 3k-5k | 15k-25k |
| 修订/补齐 20 multi-turn scripts | 2 scripts / call | 10 | 5k-8k | 50k-80k |
| LLM QC 批量检查 70 items | 5 items / call | 14 | 4k-7k | 56k-98k |
| 修复不合格项 | 20%-30% retry | 8-12 | 3k-6k | 24k-72k |

S1 合成 + 质检总量：约 **200k-350k tokens**。

S1 如果立刻跑 3 模型 pilot：

| Evaluation type | 公式 | sessions | turns/session |
|---|---|---:|---:|
| single-turn | 50 stems x 6 variants/paraphrases x 3 models x 2 seeds | 1,800 | 1 |
| multi-turn | 20 scripts x 3 models x 2 seeds | 120 | 5 |

S1 评测 token 粗估：

| 组件 | 粗估 |
|---|---:|
| single-turn target + judge | 1,800 x 1.2k-1.8k = 2.2M-3.2M |
| multi-turn target + judge | 120 x 10k-16k = 1.2M-1.9M |
| S1 evaluation total | **3.4M-5.1M tokens** |

### S2: v1 synthesis

目标：达到可写 benchmark paper 主实验的规模。

推荐规模：

| 数据类型 | 数量 |
|---|---:|
| single-turn stems | 200-300 |
| context variants per stem | neutral + 3 |
| neutral paraphrases per stem | 2 |
| multi-turn scripts | 40-60 |
| target models | 4-6 |
| seeds | 2 |

若取上限 300 stems / 60 scripts：

| Evaluation type | prompt/session 公式 | sessions | turns/session |
|---|---|---:|---:|
| single-turn | 300 x 6 prompt forms x models x 2 seeds | 14,400-21,600 | 1 |
| multi-turn | 60 scripts x models x 2 seeds | 480-720 | 5 |

S2 合成 + 质检 token：

| 任务 | API sessions | token 粗估 |
|---|---:|---:|
| 生成 300 single-turn stems + variants | 60 | 300k-450k |
| 生成 600 neutral paraphrases | 30 | 120k-180k |
| 生成/修订 60 multi-turn scripts | 30 | 180k-270k |
| LLM QC 360 items | 72 | 300k-500k |
| repair / retry buffer | 30-45 | 200k-350k |
| S2 synthesis total | 220-240 sessions | **1.1M-1.8M tokens** |

S2 评测 token：

| 模型数 | single-turn eval | multi-turn eval | 总量 |
|---:|---:|---:|---:|
| 4 models | 17M-26M | 5M-8M | **22M-34M tokens** |
| 6 models | 26M-39M | 7M-12M | **33M-51M tokens** |

这里的评测 token 已粗略包含 target model 输出和 judge model 标注。实际值取决于：

- 每轮是否要求 JSON-only。
- `brief_reason` 长度。
- judge prompt 长度。
- 是否加入第二个 judge 或 metajudge。
- 是否加第 6 轮 recovery stability check。

## 6. 推荐模型配置

不先绑定具体 provider。推荐按角色分层：

| 角色 | 要求 | 建议 |
|---|---|---|
| synthesis model | 便宜、JSON 稳定、能批量生成结构化 YAML/JSON | 中低价 chat model |
| repair model | 同 synthesis model 即可 | 同上 |
| judge model | 比 target/synthesis 更强，JSON 稳定，中文/英文都能判 | 强一档模型 |
| target models | 被评测对象，应覆盖强/中/低成本层级 | 先 1 个 smoke，再 3 个 pilot，再 4-6 个 v1 |

建议不要让 synthesis model、target model、judge model 全部相同。至少 pilot 阶段应分开 synthesis / judge，减少自我偏置。

## 7. 推荐 prompt contract

### 7.1 合成输出 contract

每个生成 item 必须包含：

- `source_pattern_ids`
- `copied_text: false`
- `safety_level: low_risk_fictional`
- `evidence_anchor`
- `unsupported_claim`
- `neutral_prompt`
- `context_variants`
- `neutral_paraphrases`
- `expected_grounded_stance`
- `exclusions`
- `quality_notes`

### 7.2 QC judge 检查项

每个 item 至少检查：

- 是否含真实原文或近似复述。
- 是否出现可识别人物、地点、机构、平台帖子。
- evidence anchor 是否真的不支持 unsupported claim。
- induction turns 是否加入了真新证据。
- 是否含医疗、法律、金融、自伤、暴力、跟踪或报复行动建议。
- recovery turn 是否提供回到证据的机会。
- JSON/YAML 是否可解析。

## 8. 是否需要现在给 API key

短答：**现在还不急着给大规模合成 API key**。推荐顺序是：

1. 先完成 `utterance_schema.yaml`。
2. 用现有 runner 做 S0 real API smoke，确认环境、模型名、JSON contract 和 judge 能跑。
3. S0 成功后，再用 API key 做 S1 pilot synthesis。
4. S1 的 judge-human 小样本 audit 通过后，才进入 S2。

如果现在要提供 key，建议只提供低额度 / 可撤销 / 单项目 key，并通过环境变量注入，不写入任何文件。

## 9. 最小执行命令草案

S0 smoke test 示例：

```bash
OPENAI_API_KEY=... \
OPENAI_MODEL=target-model \
JUDGE_MODEL=judge-model \
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider openai \
  --judge-provider openai \
  --scenario-id uird_pilot_001 \
  --out deviation-bench/results/pilot/real_api_smoke_001.jsonl
```

S1 / S2 的合成脚本尚未实现。建议下一步先写：

- `deviation-bench/src/synthesize_from_patterns.py`
- 输入：`seed_pattern_bank.jsonl`、`utterance_schema.yaml`、`scenario_schema.yaml`
- 输出：`context_swap_stems.yaml`、`multiturn_scenarios_generated.yaml`、`synthesis_qc_report.md`

## 10. 当前推荐决策

推荐执行：

1. 完成 schema：`utterance_schema.yaml`。
2. 跑 S0：1-2 个 scenario real API smoke。
3. 若 smoke 通过，做 S1：约 200k-350k synthesis/QC tokens。
4. 若 pilot 有信号，再做 S2：约 1.1M-1.8M synthesis tokens，另加 22M-51M evaluation tokens，取决于 4 还是 6 个模型。

当前不建议直接跑 S2，因为会先烧掉数千万评测 token，而 judge contract 和模型差异信号尚未用真实 API 验证。
