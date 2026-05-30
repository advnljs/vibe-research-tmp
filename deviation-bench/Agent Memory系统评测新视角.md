# Agent Memory 系统评测新视角

创建日期：2026-05-30

## 一句话想法

把 Deviation Bench 从“测模型在多轮诱导下是否 reality drift”进一步转成一种 **测 agent memory 系统是否保持现实锚定记忆** 的 benchmark：在同一个 Deviation Bench episode 中，比对完整上下文记录、不同 agent memory 系统和检索式摘要记忆，观察它们是否因为信息丢失、检索偏差或记忆重写而更容易放大 unsupported claim。

## 核心论文视角

当前更有区分度的切入点：

> Agent memory 系统声称能让长程交互更稳定、更个性化、更高效，但在 reality-boundary 场景中，压缩式 / RAG 式记忆可能丢掉关键反证、保留高频主观 claim，甚至把用户反复表达的妄想式解释固化为“事实记忆”。Deviation Bench 可以测量这种 memory-induced reality drift。

这个视角比单纯比较 target LLM 更绑定真实 agent 场景：

- 真实 agent 常常不把完整对话放入上下文，而依赖 memory extraction、vector retrieval、graph memory 或 summary memory。
- 这些系统本质上会选择、压缩、重排、持久化信息。
- Deviation Bench 的关键恰好是区分：
  - evidence anchor
  - unsupported claim
  - 用户情绪 / 重复表达
  - 无新证据的诱导
  - recovery re-anchoring
- 因此它天然适合测 memory 系统是否把“用户说过很多次”误变成“应该被 agent 记住并相信的事实”。

## 主假设

### H1: 在指定上下文 token 区间内，完整记录优于 agent memory 系统

在上下文窗口仍能容纳完整交互记录的 token 区间内，直接给模型完整 transcript 应该比 memory 系统更准。

原因：

- 完整记录保留了原始 evidence anchor、缺失证据和 recovery turn。
- memory 系统需要抽取 / 压缩 / 检索，会引入选择性丢失。
- 对 reality-boundary 判断而言，少量被丢失的反证或限定语就可能显著改变最终判断。

需要实验确定的关键变量：

- full transcript token budget 上限是多少。
- 在什么 turn 数 / token 区间内 full transcript 仍可行。
- 超过该区间后，memory 系统是否开始有优势，还是继续在 grounding 上劣化。

### H2: 当前主流 agent memory 基本是广义 RAG，可能丢失信息并放大妄想

待测系统包括用户点名的：

- mem0
- Graphiti

也可在后续 literature / tooling check 后加入其他常见 agent memory route。

这里的“广义 RAG”指：

- 从历史交互中抽取 memory item。
- 用 embedding / graph / metadata / summary 检索相关记忆。
- 将检索结果重新注入当前上下文。

潜在失败模式：

- **反证丢失**：系统记住“用户觉得广告在暗示他”，但忘记 evidence anchor 说广告是公共模板。
- **重复 claim 加权过高**：用户越反复表达 unsupported claim，memory retrieval 越可能把它当成重要事实。
- **压缩误写**：从“用户担心 X 是暗示”压缩成“X 是暗示用户的事件”。
- **检索错配**：取回高情绪、高相似度的 claim，而不是取回低频但关键的 grounded correction。
- **图结构固化**：graph memory 把用户、事件、claim 建成边，后续回答把边当作事实关系。
- **恢复失败**：recovery turn 要求回到初始事实，但 memory 注入的 prior claim 继续污染判断。

### H3: Deviation Bench 可以定义 Memory-Induced Drift Amplification

可定义一个新的比较量：

```text
MIDA = Drift(memory_system) - Drift(full_transcript)
```

其中 Drift 可以用现有 Deviation Bench 指标：

- reality_drift_event_rate
- factual_error_rate
- rds_auc
- confabulatory_elaboration_rate
- recovery_reliability
- residual_drift

如果 `MIDA > 0`，说明 memory 系统相对 full transcript 放大 reality drift。

## 实验设计草案

### 条件设置

同一批 Deviation Bench episodes，在同一 target model 上比较：

1. **Full Transcript**
   - 把完整对话历史直接放入上下文。
   - 作为上下文窗口可容纳时的上界基线。

2. **Summary Memory**
   - 周期性摘要对话历史。
   - 当前 turn 只给 summary + 最近若干轮。

3. **Vector Memory / RAG Memory**
   - 把历史拆成 memory chunks。
   - 每轮检索 top-k 相关内容注入上下文。

4. **Graph Memory**
   - 将用户、事件、claim、情绪、证据关系写成图。
   - 每轮查询相关节点 / 边。

5. **Hybrid Memory**
   - summary + vector / graph 检索。

后续实测系统可以包括 mem0、Graphiti，以及其他确认后可复现实验的 agent memory framework。

### Token 区间实验

需要系统扫描 token 区间：

- short context: 完整记录明显可放入。
- medium context: 完整记录仍可放入，但接近成本 / latency 临界。
- long context: 完整记录开始不可行，需要 memory 或截断。

核心论文问题：

> 在 full transcript 仍可放入上下文的区间内，是否存在任何 memory 系统能在 Deviation Bench 上超过 full transcript？如果不能，agent memory 的价值边界在哪里？

### Memory 写入策略控制

为公平比较，需要固定或记录：

- 何时写 memory：每轮写、每 k 轮写、episode 结束写。
- 写什么：raw chunk、summary、entity-relation、claim-state。
- 检索 top-k。
- 是否允许 memory 删除 / 更新。
- 是否允许 recovery turn 覆盖旧 memory。
- 是否存储“unsupported / unverified”状态。

关键对照：

- naive memory：不区分 claim 是否 verified。
- evidence-aware memory：显式存储 claim 的证据状态。
- full transcript：不做抽取，直接保留原始对话。

## Deviation Bench 如何适配

现有 Deviation Bench 已有关键结构：

- evidence anchor
- unsupported claim
- induction turns
- recovery turn
- judge / metajudge / consensus
- gold controls

需要新增 memory-facing 字段：

- memory_condition
- memory_backend
- memory_write_policy
- memory_retrieval_policy
- retrieved_memory_items
- memory_item_source_turns
- memory_item_verified_status
- memory_context_tokens
- full_transcript_tokens
- compression_ratio

新增可观测量：

- evidence_retention_rate：memory 是否保留关键 evidence anchor。
- unsupported_claim_retention_rate：memory 是否保留用户 unsupported claim。
- claim_verification_status_accuracy：memory 是否正确标记 claim 为 unverified。
- recovery_anchor_retention：recovery 后 memory 是否保留 / 提升 grounded correction。
- retrieval_grounding_ratio：检索结果中 evidence anchor vs unsupported claim 的比例。
- memory_distortion_rate：memory item 是否把主观表达改写成事实。
- MIDA：memory 相对 full transcript 的 drift 增量。

## 论文贡献可能改写为

原始版本：

- Deviation Bench measures whether LLMs maintain reality-grounded judgment under user pressure.

新版本：

- Deviation Bench measures whether **agent memory systems** preserve reality-grounded judgment under long-running user pressure.
- It challenges the assumption that compressing interaction history into memory improves agent reliability.
- It shows that, within certain context-token regimes, full transcript can be more reliable than popular memory systems for reality-boundary tasks.
- It diagnoses memory-induced drift through evidence retention, unsupported-claim amplification, and recovery failure.

## 为什么这个方向更精妙

这个 framing 把 Deviation Bench 绑定到一个更具体、更现实的系统问题：

- Agent memory 是真实产品和框架正在解决的问题。
- “更长记忆”通常被默认视为能力提升，但这里可以提出反直觉结论：不恰当记忆会伤害现实锚定。
- Deviation Bench 的多轮结构不只是 prompt stress test，而是 memory system stress test。
- 论文可以避免只做又一个 model safety benchmark，而变成 agent infrastructure evaluation。

## 需要避免的误区

- 不要把结论写成“所有 memory 系统都不好”。
- 不要只测一种 naive memory；至少要有 full transcript、summary、RAG、graph、evidence-aware memory 的对照。
- 不要只看最终回答；要记录 memory 写入和检索过程。
- 不要把用户反复表达的 unsupported claim 当作真实 user preference。
- 不要让 memory 系统存储真实患者或社区原文；仍使用虚构 / 抽象 scenario。
- 不要做真实妄想诱导或危险行动升级。

## 下一步建议

1. 写一个正式实验设计文档：
   - `deviation-bench/agent_memory_eval_protocol.md`

2. 先做小型本地 memory simulator：
   - full transcript
   - rolling summary
   - simple vector retrieval over turn chunks
   - evidence-aware retrieval

3. 再接入真实系统：
   - mem0
   - Graphiti
   - 其他需要经过版本和 API 调研确认的 memory framework

4. 改造 runner：
   - 支持 `--memory-condition full_transcript|summary|vector|graph|external`
   - 输出 memory write / retrieval trace。

5. 新增 metrics：
   - evidence retention
   - memory distortion
   - unsupported-claim amplification
   - MIDA

6. 做 token-window sweep：
   - 确定 full transcript 在不同上下文长度下的可行边界。

## 当前状态

这是 2026-05-30 用户提出的新主视角。尚未做文献 / 工具版本核验，也尚未确认 mem0、Graphiti 的具体 API、默认写入策略和可复现实验配置。后续在写论文 claim 前需要单独做 tooling survey 和公平性设置。
