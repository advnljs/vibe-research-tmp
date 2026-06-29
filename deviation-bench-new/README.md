# Deviation Bench New

`deviation-bench-new/` 是一条与旧 `deviation-bench/` 隔离的数据准备线。它不再先构造压力诱导 benchmark，而是先把已有真实访谈语料整理成可直接用于 LLM 实验的 session 数据。

当前目标：

1. 一个真实访谈案例对应一个 JSONL session。
2. 保留访谈多轮结构，映射为 OpenAI-style `messages`：参与者是 `user`，访谈者是 `assistant`。
3. 用 `deepseek-v4-pro` 做语义保真的去标识化改写，不直接复制敏感原句。
4. 对每个案例提取结构化 `delusion_points`；允许空列表，禁止为了“每例都有标签”而臆造。
5. 模型输出只是候选文本信号，不是临床诊断或患者级 ground truth。
6. 转换请求的上下文窗口固定为 64k tokens（`65,536`）；默认为输出预留 `8,192`，每次调用前对 prompt + payload 做输入预算检查。
7. 结构化转换/筛选默认向兼容 endpoint 发送 `thinking: {"type": "disabled"}`，并在 provenance 记录。这不改变模型名，只避免把输出预算消耗在不需要的长推理上。

## 当前纳入的真实数据

| Source | Case boundary | Role mapping | License / boundary |
|---|---|---|---|
| DAIS-C clinical/control interactional transcripts | 每个访谈文件一个 case | participant -> `user`, interviewer -> `assistant` | CC BY-SA 4.0；输出仍按每条来源记录归属和 ShareAlike 边界 |
| First-Episode Psychosis Friendship interviews | `Participant 1`-`14` 各一个 case | participant -> `user`, interviewer `CH` -> `assistant` | CC BY 4.0；不是 delusion-only corpus |

数量边界：

- 原生多轮访谈共 42 例：DAIS-C clinical 15、DAIS-C control 13、FEP 14。
- 其中 psychosis-related 访谈是 29 例，但都不是 delusion-specific corpus，不保证每例有妄想表现。
- 13 个 DAIS-C control 只进入单独 calibration split，不与妄想相关数据混合计数。
- Reddit `r/schizophrenia` 上游共 8,712 rows，去重后 7,685 个帖子；本地安全/PII/宽松词汇 probe 后 2,541 个进入 LLM 语义筛选。这些都不是临床 ground truth。

`42` 只是“原生多轮真实访谈”的 case 数，不是最终派生 session 总数。2026-06-22 完成的正式数据如下：

| Split | Sessions | Messages | Candidate points | Sessions with points |
|---|---:|---:|---:|---:|
| DAIS-C clinical | 15 | 2,618 | 23 | 6 |
| FEP friendship | 14 | 1,472 | 17 | 8 |
| DAIS-C control calibration | 13 | 1,206 | 0 | 0 |
| Reddit fictionalized text-signal sessions | 926 | 11,112 | 1,352 | 926 |
| **Total** | **968** | **16,408** | **1,392** | **940** |

因此，29 个 psychosis-related 访谈里只有 14 个被模型提取出候选点；这正是不能把 DAIS/FEP 组别直接当作 delusion 标签的原因。

本轮不纳入主 case 路线：

- AnnoMI / CounselChat：不是 psychosis / delusion 语料。
- MentalChat16K / MDD-5k：主要是合成或二次改写数据，不符合这一阶段“真实案例”的优先级。

Reddit 不作为真实对话直接纳入，而走单独派生路线：真实帖子 -> 本地排除/去重 -> LLM 文本信号筛选 -> 虚构去标识化 12-message session。输出不保留原文、作者或真实事件链。

正式成品：

- `data/processed/deepseek_v4_pro_interview_sessions_64k.jsonl`
- `data/processed/deepseek_v4_pro_control_sessions_64k.jsonl`
- `data/screened/deepseek_v4_pro_reddit_screening_64k.jsonl`
- `data/processed/deepseek_v4_pro_reddit_sessions_64k.jsonl`
- `experiments/real_data_session_preparation_2026-06-22.md`

## 输出 schema

每行一个 session，核心字段：

```json
{
  "schema_version": "0.1.0",
  "session_id": "dais_c_cl_001",
  "messages": [
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "message_provenance": [
    {"message_index": 0, "source_turn_ids": ["st0001"], "transform": "llm_semantic_paraphrase"}
  ],
  "delusion_points": [],
  "metadata": {},
  "provenance": {},
  "quality": {}
}
```

完整约束见 `schemas/session.schema.json`。

## 流水线

### 1. 解析原始访谈

```bash
python3 deviation-bench-new/src/prepare_cases.py
```

输出：

- 可提交 manifest：`data/manifests/source_cases.jsonl`
- 忽略的规范化原文：`data/work/prepared_cases/*.json`

### 2. 离线 mock 端到端检查

```bash
python3 deviation-bench-new/src/build_sessions.py \
  --provider mock \
  --limit 2 \
  --output /tmp/deviation_bench_new_mock.jsonl \
  --summary /tmp/deviation_bench_new_mock.md
```

### 3. DeepSeek 转换

API key 从 `OPENAI_API_KEY` 或已忽略的 workspace `ds_key.txt` 读取，不会写入输出：

```bash
python3 deviation-bench-new/src/build_sessions.py \
  --provider openai \
  --model deepseek-v4-pro \
  --base-url https://api.deepseek.com \
  --context-window-tokens 65536 \
  --case-ids dais_c_cl_001,dais_c_cl_002 \
  --run-id deepseek_v4_pro_batch_001 \
  --output deviation-bench-new/data/processed/deepseek_v4_pro_batch_001.jsonl \
  --summary deviation-bench-new/data/processed/deepseek_v4_pro_batch_001_summary.md
```

脚本会把访谈分块改写，再用同一模型在完整改写 session 上合并/复核 `delusion_points`。API checkpoint 在 `data/work/runs/<run-id>/`，可用 `--resume` 续跑，不进入 Git。

冒烟测试可用 `deepseek-v4-flash`；正式全量转换仍固定用用户指定的 `deepseek-v4-pro`。`context_window_tokens` 是本地预算约束，不会向不同 provider 发送一个非标准 `context_window` 字段。

### 4. 校验

```bash
python3 deviation-bench-new/src/validate_sessions.py \
  deviation-bench-new/data/processed/deepseek_v4_pro_batch_001.jsonl
```

三类正式输出可一次校验；该命令也检查跨文件 `session_id` 重复：

```bash
python3 deviation-bench-new/src/validate_sessions.py \
  deviation-bench-new/data/processed/deepseek_v4_pro_interview_sessions_64k.jsonl \
  deviation-bench-new/data/processed/deepseek_v4_pro_control_sessions_64k.jsonl \
  deviation-bench-new/data/processed/deepseek_v4_pro_reddit_sessions_64k.jsonl
```

### 5. Reddit 真实文本信号衍生数据

```bash
python3 deviation-bench-new/src/prepare_reddit_cases.py

python3 deviation-bench-new/src/build_reddit_sessions.py \
  --provider openai \
  --stage screen \
  --screen-model deepseek-v4-pro \
  --context-window-tokens 65536 \
  --workers 3 \
  --resume

python3 deviation-bench-new/src/build_reddit_sessions.py \
  --provider openai \
  --stage generate \
  --generate-model deepseek-v4-pro \
  --context-window-tokens 65536 \
  --workers 3 \
  --resume
```

`deepseek-v4-flash` 只用于小样本 smoke。全量 screening 和 session generation 使用 `deepseek-v4-pro`。

### 6. 本地浏览

```bash
python3 deviation-bench-new/src/build_dataset_browser.py \
  --input deviation-bench-new/data/processed/deepseek_v4_pro_interview_sessions_64k.jsonl \
  --input deviation-bench-new/data/processed/deepseek_v4_pro_control_sessions_64k.jsonl \
  --input deviation-bench-new/data/processed/deepseek_v4_pro_reddit_sessions_64k.jsonl \
  --out deviation-bench-new/data/work/web/index.html
```

浏览页只生成到 Git 忽略的 `data/work/`，用于开发质检，不构成人工标注。

### 7. 发布硬化本地预审计

```bash
python3 deviation-bench-new/src/audit_release.py
```

输出：

- `data/manifests/deepseek_v4_pro_release_audit_64k.json`
- `data/manifests/deepseek_v4_pro_release_splits_64k.jsonl`
- `data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl`
- `experiments/session_release_hardening_pre_audit_2026-06-29.md`

该步骤冻结候选 `dataset_version` 和 deterministic split manifest，生成 1,392 个 candidate point 的 second-pass/metajudge review units，并做本地 contract/PII、精确重复和 lexical near-duplicate 预审计。它不调用新模型；LLM second-pass/metajudge 和 embedding/LLM 语义重复检查仍是后续发布硬化步骤。

## 关键边界

- 不把“精神病性障碍访谈”等同于“每例都有妄想”。
- `delusion_points` 是 LLM 从文本中提取的候选现实边界信号，不是对人的诊断。
- 公开输出不保留真实姓名、地点、机构、联系方式和稀有事件链；使用类型化占位符。
- 真实访谈是语义保真规范化，可能保留通用短语；每例报告最大连续源词重叠，`>=32` 则失败。Reddit 虚构扩写使用更严格的 `>=12` 失败阈值。
- 混合数据集不宣告一个新的统一许可；每个 session 保留来源许可、归属和源文件 hash。
