# Data Governance

## 目的

本目录生成的是“去标识化、语义保真的访谈 session + 文本信号”，不是新的临床诊断数据库。

## 分层保存

1. 上游原文：位于 `deviation-bench/data_sources/downloaded/`，按旧项目的许可清单管理。
2. 规范化原文和 API 原始响应：位于 `deviation-bench-new/data/work/`，Git 忽略。
3. 可审核派生数据：位于 `deviation-bench-new/data/processed/`，只包含去标识化改写、候选信号、谱系和 QC 结果。

Reddit screening 的模型自由文本拒绝理由也只保留在 `data/work/` checkpoint；tracked screening JSONL 只发布类别码，避免拒绝理由间接复述帖子细节。

## 两种 session 类型

- `llm_semantic_paraphrase`：上游本身是真实多轮访谈，每个 source turn 一对一改写。
- `llm_fictional_expansion`：上游是单篇社区帖子，经 LLM 语义筛选后只保留抽象信念/不确定性，改写成虚构 12-message 访谈。这些不是真实对话。

DAIS-C clinical/FEP 仅表示上游研究组别，不表示每个 case 有妄想。Reddit subreddit 归属也不是诊断。

## 第三方 LLM 处理

- 用户指定 `deepseek-v4-pro` 作为转换模型。
- 发送前使用上游已公开/已去标识化的转录，并在 prompt 中要求二次去标识化和语义改写。
- 最终数据不保存 API key、原始 request、原始 response 或模型隐藏推理。
- 如上游许可、同意书或 API 条款后续显示不允许这种处理，对应来源必须停用并从发布集删除。

## `delusion_points` 的解释

`delusion_points` 只描述参与者在转录中表达的候选信念/现实边界信号。它必须：

- 指向改写后 `messages` 的索引和本地 `source_turn_ids`，不存 quote。
- 区分 `explicit` / `implicit` / `unclear`。
- 记录不确定性、反证或自我修正。
- 允许空列表，并记录 `no_delusion_point_reason`。
- 不从诊断组别、subreddit 归属或一般性焦虑反推妄想。

允许的候选类型：

- `persecutory`
- `referential`
- `grandiose`
- `somatic`
- `religious`
- `jealous`
- `nihilistic`
- `control_or_influence`
- `thought_interference`
- `other_reality_boundary`

## 发布前门槛

- 每个 source turn 在 provenance 中覆盖且只覆盖一次。
- 输出不得出现上游 case code、email、URL、电话或明显邮编。
- 自动检查输出与原文的长连续 token 重叠。
- `delusion_points` 必须能映射到现有 message/source turn。
- 输出中明确带 `llm_extracted_candidate_not_diagnosis`。
- 每个批次保存模型名、prompt hash、源文件 hash、时间和 QC 摘要。
- 冻结 deterministic split/version manifest，且 control、clinical/FEP、community-fictionalized 不混成统一 clinical corpus。
- 对 candidate points 运行独立 second-pass/metajudge；`data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl` 是该步骤的输入队列，不是复核结果。
- 对 Reddit 和跨 split 重复风险做 duplicate/leakage 审计；当前 `audit_release.py` 只完成标准库 lexical pre-audit，embedding/LLM 语义复核仍需后续执行。

重叠阈值按来源分层：

- 公开、假名化、有明确派生许可的 DAIS-C/FEP 真实访谈：失败阈值是 `>=32` 个连续 source words。这是语义保真规范化，不声称零原句重叠。
- Reddit 社区文本衍生的虚构 session：失败阈值仍为 `>=12`，且不保留真实事件链。
