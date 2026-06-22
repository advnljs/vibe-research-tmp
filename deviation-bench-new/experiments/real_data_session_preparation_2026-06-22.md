# Real-data-derived session preparation — 2026-06-22

## 目标

把当前本地、许可状态已记录且与 psychosis / reality-boundary 方向相关的真实数据，统一转换成“一例一个 session”的 OpenAI-style `messages`，并提取 case-level `delusion_points` 候选信号。

- 正式模型：`deepseek-v4-pro`
- 冒烟模型：`deepseek-v4-flash`
- 本地上下文预算：`65,536` tokens
- 单次最大输出预留：`8,192` tokens
- thinking mode：`disabled`
- 标签解释：`llm_extracted_candidate_not_diagnosis`

## Source accounting

| Source / split | Source boundary | Sessions | Messages | Candidate points | Sessions with points |
|---|---|---:|---:|---:|---:|
| DAIS-C clinical | 真实多轮访谈，每个文件一例 | 15 | 2,618 | 23 | 6 |
| FEP friendship | 真实多轮访谈，每位 participant 一例 | 14 | 1,472 | 17 | 8 |
| DAIS-C control | 真实多轮访谈，对照校准 split | 13 | 1,206 | 0 | 0 |
| Reddit `r/schizophrenia` | 真实单帖信号，经筛选后虚构扩写 | 926 | 11,112 | 1,352 | 926 |
| **Total** |  | **968** | **16,408** | **1,392** | **940** |

`42` 是原生多轮访谈数；它由 DAIS-C clinical 15、DAIS-C control 13、FEP 14 组成。最终 session 总数还包括 926 个 Reddit 派生 session。

## Reddit screening funnel

- 上游 CSV rows：8,712
- exact-hash 去重后：7,685
- 本地长度、高风险、PII/link、宽松 reality-boundary probe 后：2,541
- DeepSeek Pro 语义筛选通过：926
- 正式生成成功：926
- 生成失败：0
- eligible 中 `contains_identifying_detail=true`：0
- eligible 中 `diagnosis_inferred=true`：0
- tracked screening JSONL 包含原帖文本：false
- tracked screening 的 rejection reasons：仅类别码；模型自由文本理由只留在 ignored checkpoint

社区归属不是诊断，Reddit session 是从筛选后的文本信号虚构扩写的对话，不是真实对话。

## Candidate point distribution

真实访谈 40 个候选点：

- persecutory 15
- referential 11
- other_reality_boundary 6
- grandiose 5
- control_or_influence 1
- religious 1
- somatic 1

Reddit 派生 session 1,352 个候选点：

- persecutory 494
- other_reality_boundary 243
- referential 193
- control_or_influence 157
- thought_interference 86
- grandiose 70
- religious 46
- somatic 30
- nihilistic 26
- jealous 7

29 个 psychosis-related 真实访谈中，15 个没有提取到候选点。DAIS/FEP 因此不能被描述为 delusion-only corpus，也不能把研究组别当作逐例妄想标签。

## Automatic QC

- 统一 session contract：968/968 passed
- 跨文件唯一 session IDs：968/968
- regex PII scan hits：0
- context window provenance：全部为 65,536
- transform model provenance：全部为 `deepseek-v4-pro`
- thinking mode provenance：全部为 `disabled`
- 真实访谈最大连续来源词重叠：31，失败阈值 `>=32`
- Reddit 最大连续来源词重叠：11，失败阈值 `>=12`
- processed data 中原始 source/API response：false
- DAIS control `dais_c_co_010` 的上游 interviewer 内容为空；保留 36 个 participant turns，并在 provenance 标记 `missing_interviewer_role`，未伪造 interviewer 内容。

自动 regex/结构校验不能证明绝对匿名，也不能替代发布前的许可、隐私和治理检查。浏览器人工查看只用于开发/治理检查，不作为论文标注证据。

## Smoke and formal run status

- `deepseek-v4-flash` interview smoke：端到端结构/QC 通过。
- `deepseek-v4-flash` Reddit smoke：screen + fictional session generation 通过。
- `deepseek-v4-pro` interview/control：42/42 完成。
- `deepseek-v4-pro` Reddit screen：2,541/2,541 完成。
- `deepseek-v4-pro` Reddit generation：926/926 完成。

## Validation evidence

```text
interview: sessions=29 messages=4090 delusion_points=40 errors=0
control:   sessions=13 messages=1206 delusion_points=0 errors=0
reddit:    sessions=926 messages=11112 delusion_points=1352 errors=0
combined:  sessions=968 messages=16408 delusion_points=1392 errors=0
tests:     Ran 11 tests — OK
browser:   sessions=968
```

## Outputs

- `data/processed/deepseek_v4_pro_interview_sessions_64k.jsonl`
- `data/processed/deepseek_v4_pro_control_sessions_64k.jsonl`
- `data/screened/deepseek_v4_pro_reddit_screening_64k.jsonl`
- `data/processed/deepseek_v4_pro_reddit_sessions_64k.jsonl`
- summaries alongside each processed JSONL
- local ignored browser: `data/work/web/index.html`
