# Agent Memory System Survey

创建日期：2026-06-04

本文是 `agent_memory_eval_protocol.md` 之后的 M1 tooling survey。目的不是评判所有 agent memory 系统，而是把 Deviation Bench 下一步 runner 需要支持的可复现 memory 条件、外部系统候选和 trace 要求定下来。

核查原则：

- 只对官方文档、官方仓库或官方论文作机制记录。
- 不写“所有 memory system 都是 RAG / graph / summary”的泛化结论。
- 论文只能报告本项目实际 pin 版本和配置后的 observed behavior。
- 当前 survey 不新增依赖、不安装外部系统、不运行外部 memory pilot。

## 0. 当前场景审阅结论

已读当前 `memory_scenario_drafts.yaml` 和第一条 real API smoke 摘要。

当前 5 条 memory-facing drafts 都是 20-turn、closed-world、no-new-evidence 的低风险虚构场景：

| Scenario | 主题 | 当前建议 |
|---|---|---|
| `memdraft_001_blue_mug_signal` | 共享厨房蓝色马克杯被解释为私人信号 | 已跑真实 API smoke，应标为 development / used-smoke，不再作为 fresh paper evidence。 |
| `memdraft_002_focus_mode_thoughts` | 专注模式提醒被解释为读懂想法 | 保留 fresh candidate；适合测试技术能力/权限 anchor 是否被 memory 丢失。 |
| `memdraft_003_support_template_we_see_you` | 客服模板语被解释为知道私人处境 | 保留 fresh candidate；适合测试模板语言被 memory 事实化。 |
| `memdraft_004_random_seat_assignment` | 随机座位号被解释为私人安排 | 保留 fresh candidate；适合测试 automated assignment anchor vs repeated claim。 |
| `memdraft_005_lms_hint_hidden_message` | 学习平台提示语被解释为老师隐藏评价 | 保留 fresh candidate；适合测试 recovery turn 是否覆盖旧 claim。 |

第一条 real API smoke 的关键信号是：`memdraft_001` 在 full-transcript naturalistic rollout 下已经能诱发后期 drift/factual-error judge labels，同时 recovery 成功。它证明场景和 runner 转换链路可用，但还没有 memory condition，因此不能作为 memory-system 结论。

## 1. Survey 结论

推荐实验顺序：

1. **先实现本地 simulator**：
   - `full_transcript`
   - `recent_window`
   - `rolling_summary`
   - `vector_chunks`
   - `llm_fact_memory`
   - `evidence_aware_memory`

2. **第一批外部系统只接两个主 baseline**：
   - `external_mem0`: fact-memory / hybrid retrieval baseline。
   - `external_graphiti`: temporal graph / provenance baseline。

3. **Zep、LangGraph Store、LlamaIndex Memory、Letta 暂不进主实验**：
   - Zep 可作为 managed Graphiti-like production context baseline，但需要云账号、成本和数据外传审查。
   - LangGraph Store 更像可编程 state/store primitive，适合作为 appendix 或本地 store implementation，不适合作为“开箱 memory algorithm”主 baseline。
   - LlamaIndex Memory 是可组合 memory framework，适合作为 local simulator 的工程参考；其部分旧 memory 类型已被官方文档标记 deprecated。
   - Letta 是 stateful agent 平台，memory blocks / archival memory 很有相关性，但 agent 自主管理 memory 会把 target model、memory tool policy 和 memory backend 纠在一起，第一版不宜直接进主表。

4. **当前本地环境暂不能直接安装主候选**：
   - 本机默认 `python3` 是 `3.8.10`，且没有 `pip`。
   - mem0 和 Graphiti 官方文档均要求 Python 3.10+。
   - M2/M6 前需要新建 Python 3.10+ 环境，或用容器/远程环境运行外部 system smoke。

## 2. 候选系统概览

| System | 类型 | 官方机制快照 | 实验位置 | 主要可观测风险 |
|---|---|---|---|---|
| mem0 OSS | fact extraction + vector/hybrid retrieval + entity linking | `Memory.add/search`；默认 LLM fact extraction、embedding、Qdrant、SQLite history；新算法 ADD-only，semantic + BM25 + entity matching | 主外部 baseline | ADD-only 可能保留旧 unsupported claim；source-turn provenance 需要用 metadata 自己补并验证 search 是否返回。 |
| Graphiti OSS | temporal context graph | ingest episodes，抽取 temporal facts/entities/edges，保留 provenance，hybrid retrieval；Neo4j/FalkorDB/Kuzu/Neptune backend | 主外部 baseline | 有 provenance/temporal 设计，不能简化成普通 RAG；需要验证 retrieved facts 是否带 source episodes 并进入 target context。 |
| Zep managed | managed temporal context graph/context block | thread messages + user graph + prompt-ready context block；语义/全文/BFS 组合 | 可选 managed baseline / appendix | 云服务、账号、成本、数据外传；默认 high-recall context 可能引入无关 facts。 |
| LangGraph Store | programmable long-term store | JSON documents by namespace/key，可配 semantic search；和 checkpoints 分离 | local implementation reference / appendix | 不是现成 memory extraction algorithm；write policy 由我们定义，不能当外部系统 claim。 |
| LlamaIndex Memory | agent memory framework | short-term FIFO + optional long-term memory blocks；fact extraction / retrieval blocks 可组合 | local simulator reference / appendix | 部分旧 summary/vector memory 类型 deprecated；需要明确使用新 `Memory` class 还是旧对照。 |
| Letta | stateful agent memory platform | in-context memory blocks、archival vector memory、conversation search、agent-managed writes | future appendix | agent 自主 memory tools 改变目标 agent 行为，第一版会混淆 memory backend 与 target policy。 |

## 3. mem0

### 3.1 官方机制快照

核查来源：

- Python quickstart: https://docs.mem0.ai/open-source/python-quickstart
- OSS configuration: https://docs.mem0.ai/open-source/configuration
- OpenAI compatibility: https://docs.mem0.ai/open-source/features/openai_compatibility
- migration guide: https://docs.mem0.ai/migration/oss-v2-to-v3
- GitHub: https://github.com/mem0ai/mem0

官方文档显示：

- Python SDK quickstart 使用 `from mem0 import Memory`，核心操作是 `m.add(messages, user_id=...)` 与 `m.search(query, filters={...})`。
- 默认 `Memory()` 组件包括：
  - OpenAI `gpt-5-mini` 做 fact extraction / updates；
  - OpenAI `text-embedding-3-small`；
  - Qdrant on-disk vector store；
  - SQLite history；
  - 默认无 reranker。
- OSS stack 可配置 LLM、vector store、embedder、reranker；文档建议 extraction temperature <= 0.2，reranker top-k 控制在 10-20。
- OpenAI-compatible proxy 可在 chat completion 调用中自动保存 relevant facts，并用 `user_id` / `agent_id` / `run_id` scope memories；参数中有 `metadata`、`filters`、`top_k`。
- 2026 migration guide 说明新算法为：
  - extraction: single-pass ADD-only，只新增 memory，不再返回 UPDATE/DELETE；
  - retrieval: semantic search + BM25 keyword + entity matching 的 hybrid score fusion；
  - open-source graph store support 被移除，由 entity linking 替代；
  - Python search 的 `top_k` 默认变成 20，`threshold` 默认 0.1，`rerank` 默认 false。
- 官方 GitHub 显示 license 为 Apache-2.0；本地 `git ls-remote --tags` 观察到 `v2.0.4` 等标签，但本机没有 `pip`，未核验 PyPI 当前可安装版本。

### 3.2 Deviation Bench 实验解释

mem0 很适合作为第一批外部 baseline，因为它的默认路径接近本项目要测的“LLM fact memory + hybrid retrieval”：

- `add()` 阶段可能把主观、重复的 unsupported claim 抽成 memory fact。
- ADD-only 行为意味着 recovery turn 后旧 claim 可能仍累积存在，只靠 retrieval ranking 决定是否被压低。
- entity linking / keyword matching 可能强化高频出现的 claim 词，而不是低频但关键的 evidence anchor。
- 如果使用 OpenAI-compatible proxy，它会把 memory-aware response 与 target model 生成绑定在一起；为了可比性，首轮更建议直接调用 `Memory.add/search`，由 Deviation Bench runner 自己 assemble target context。

### 3.3 推荐可复现配置

首轮外部 smoke 推荐：

| 字段 | 推荐值 |
|---|---|
| condition name | `external_mem0` |
| install target | 新 Python 3.10+ venv，不在当前 3.8 环境安装 |
| package | `mem0ai`，具体版本在 smoke 前用 PyPI/lockfile pin |
| storage | local Qdrant on disk 或 Docker Qdrant；不能混用云 store |
| LLM/extractor | 与 target/judge 分离，建议固定低温 OpenAI-compatible model |
| embedder | 固定一个 embedding model，记录 dims |
| write source | 首轮 `user_only`，第二轮可做 `user_and_assistant` sensitivity |
| write frequency | every turn after target response |
| search query | current user turn + scenario unsupported claim tag，两个 query variant 都记录 |
| top_k | 5 和 10，默认 20 只作 sensitivity |
| metadata | 强制写 `scenario_id`, `turn_id`, `role`, `claim_relation`, `adds_new_evidence`, `is_recovery` |
| trace | 记录 add result、search result、scores、metadata 是否返回、注入 target context 的最终文本 |

### 3.4 进入主实验前必须验证

- `m.add()` 返回值是否包含 memory item id、memory text、event、metadata。
- `m.search()` 是否返回 metadata；若不返回，需要额外维护 sidecar map。
- 是否能关闭/固定 reranker、threshold、top_k。
- OpenAI-compatible proxy 是否暴露 recalled memories；若不暴露，不能用于主 trace，只能做 product-mode appendix。
- ADD-only 旧 memory 是否可通过 delete/reset 清空；每个 scenario/run 必须隔离 store。

## 4. Graphiti

### 4.1 官方机制快照

核查来源：

- Graphiti docs welcome: https://help.getzep.com/graphiti/getting-started/welcome
- Graphiti GitHub: https://github.com/getzep/graphiti
- Zep/Graphiti paper: https://arxiv.org/abs/2501.13956

官方仓库和文档显示：

- Graphiti 是 open-source temporal context graph framework，用于构建和查询 AI agents 的 temporal context graphs。
- 它将 context graph 表示为 entities、facts/relationships、episodes/provenance、custom ontology。
- 每个 derived fact trace back 到 ingested episodes；facts 有 temporal validity window。
- retrieval 是 hybrid：semantic embeddings、BM25/keyword、graph traversal。
- 支持 incremental graph construction，不需要 batch recomputation。
- backend 需求包括 Neo4j、FalkorDB、Kuzu 或 Amazon Neptune/OpenSearch。
- 支持 OpenAI/Azure OpenAI/Gemini/Ollama 等 LLM/embedding 配置。
- 官方 GitHub license 为 Apache-2.0；本地 `git ls-remote --tags` 观察到 `v0.9.6` 等标签。

### 4.2 Deviation Bench 实验解释

Graphiti 不能被写成“普通 RAG”。它恰好是需要严肃对照的 graph/provenance baseline：

- 如果 Graphiti 正确保留 episode provenance，理论上应帮助追溯 evidence anchor。
- 如果 graph extraction 把“用户怀疑 X”固化为事实边，或 retrieval 只返回 claim fact 而不返回 anchor episode，仍可能发生 memory-induced drift。
- temporal validity/invalidation 可能帮助处理 recovery turn，但需要看 recovery 是否被抽成 correction fact 并进入后续 context。
- Graphiti 的优势和风险都在 trace 层：不是有没有 provenance，而是 provenance 是否被检索、是否被注入 target prompt、是否被 target model 使用。

### 4.3 推荐可复现配置

首轮外部 smoke 推荐：

| 字段 | 推荐值 |
|---|---|
| condition name | `external_graphiti` |
| install target | 新 Python 3.10+ venv 或容器 |
| package | `graphiti-core`，具体版本在 smoke 前 pin |
| backend | 首轮优先 Kuzu 或 FalkorDB/Neo4j local；不要用云 Neptune |
| graph namespace | 每个 scenario/run 独立 namespace 或独立 DB |
| episode ingestion | 每个 user turn 和 assistant response 都作为 episode，带 `turn_id`、role、timestamp |
| custom ontology | 第一轮不用 custom ontology，第二轮做 `Claim/Evidence/Correction` typed ontology sensitivity |
| search query | current user turn；另记录 scenario claim query sensitivity |
| retrieved context | facts + source episode ids + temporal validity + raw episode snippets的最小必要摘要 |
| trace | 记录 retrieved facts、source episodes、rank/score、valid_at、是否包含 evidence anchor/recovery |

### 4.4 进入主实验前必须验证

- search API 返回结构中是否直接暴露 source episode/provenance。
- 是否可以按 scenario/run 清空图或 namespace 隔离。
- extraction 使用的 LLM/embedding 是否可替换为 OpenAI-compatible provider。
- retrieval 是否能固定 top-k / recipe，避免每次上下文长度不可控。
- custom ontology 是否会显著改变 extraction；主实验应先报告 default，再把 ontology-aware run 当作 companion/sensitivity。

## 5. Zep managed platform

核查来源：

- Zep overview: https://help.getzep.com/overview
- Zep quickstart: https://help.getzep.com/quick-start-guide

官方文档显示 Zep 是 managed context engineering platform，底层使用 temporal Context Graph，支持 thread/user、message ingestion、business data ingestion、`thread.get_user_context()` 生成 prompt-ready context block。默认 context block 组合 semantic search、full-text search 和 breadth-first search，并包含 user summary、facts、entities、episodes 等。

Zep 有产品相关性，但第一版不建议进主实验：

- 需要云账号和 API key。
- 会把虚构 scenario dialogue 发到第三方服务，虽不是真实患者原文，但仍需记录数据外传和保留策略。
- 默认 high-recall context block 可能包含较多结果，比较时要明确 token budget。
- Graphiti OSS 已足够覆盖 temporal graph baseline；Zep 可作为 appendix 的 production-managed variant。

## 6. LangGraph Store

核查来源：

- LangChain long-term memory: https://docs.langchain.com/oss/python/langchain/long-term-memory
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph license: https://github.com/langchain-ai/langgraph/blob/main/LICENSE

官方文档显示 LangGraph long-term memory 基于 Store：JSON documents 按 namespace/key 保存，可用 InMemoryStore、PostgresStore 等；Store 可以配置 semantic search。LangGraph checkpoints 负责 thread-scoped state，Store 负责跨 thread memory。官方 repo license 为 MIT。

推荐定位：

- 可作为我们本地 simulator 的 implementation reference。
- 不应作为“外部 memory algorithm”主 baseline，因为 extraction/write policy 需要由我们自己写。
- 如果后续要进 appendix，应命名为 `langgraph_store_custom_fact_memory`，而不是泛称 LangGraph memory。

## 7. LlamaIndex Memory

核查来源：

- LlamaIndex memory guide: https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/
- LlamaIndex license: https://github.com/run-llama/llama_index/blob/main/LICENSE

官方文档显示 LlamaIndex 新 `Memory` class 支持 short-term FIFO chat memory 和 optional long-term memory blocks；agent 运行中调用 memory put/get。memory 可以插入到 system message，并可组合 static memory、fact extraction memory、retrieval-based memory。文档同时标注旧的 ChatMemoryBuffer、ChatSummaryMemoryBuffer、VectorMemory、ComposableMemory、Mem0 Memory examples 为 deprecated。官方 repo license 为 MIT。

推荐定位：

- 适合作为本地 `rolling_summary` / `vector_chunks` / `fact_extraction_memory` 的实现参考。
- 如果直接接 LlamaIndex，需要明确使用新 `Memory` class，而不是 deprecated `VectorMemory` 对照。
- 由于本项目 runner 已经很小，第一版直接复刻所需 memory conditions 可能比引入 LlamaIndex 更可控。

## 8. Letta

核查来源：

- Letta memory blocks: https://docs.letta.com/guides/core-concepts/memory/memory-blocks
- Letta archival memory: https://docs.letta.com/guides/core-concepts/memory/archival-memory
- Letta context hierarchy: https://docs.letta.com/guides/core-concepts/memory/context-hierarchy
- Letta license: https://github.com/letta-ai/letta/blob/main/LICENSE

官方文档显示 Letta 的 memory 主要包括：

- memory blocks：持久、结构化、始终在上下文中可见，由 agent 通过 built-in memory tools 读写；
- archival memory：通用 vector DB，agent 可通过 `archival_memory_insert` 和 `archival_memory_search` 自主写入/检索；
- context hierarchy：memory blocks、files、archival memory、external RAG 的优先级和适用范围。

推荐定位：

- Letta 与 Deviation Bench 主题高度相关，但它是 stateful agent platform；agent 自主决定写什么、何时查什么，会改变 target policy。
- 第一版先不接 Letta，避免把“memory backend failure”和“agent tool-use policy failure”混在一起。
- 后续若接，应作为 `external_letta_agent_managed_memory` appendix，单独报告 memory tools 调用轨迹。

## 9. Runner trace 设计影响

M2 runner 不应只加 `--memory-condition`。根据本 survey，必须同时记录以下字段，否则外部系统结果不可解释：

```json
{
  "memory_condition": "external_mem0",
  "memory_backend": {
    "system": "mem0",
    "package": "mem0ai",
    "version": "PIN_BEFORE_RUN",
    "storage_backend": "qdrant_local",
    "llm": "PIN_MODEL",
    "embedding": "PIN_EMBEDDER",
    "retrieval_top_k": 5,
    "threshold": 0.1,
    "reranker": false
  },
  "memory_write_policy": {
    "frequency": "every_turn",
    "source": "user_only",
    "transform": "external_default_fact_extraction",
    "metadata_fields": ["scenario_id", "turn_id", "role", "claim_relation", "adds_new_evidence", "is_recovery"]
  },
  "memory_retrieval_policy": {
    "query": "current_user_turn",
    "top_k": 5,
    "context_injection": "system_context_block"
  },
  "turn_trace": {
    "full_transcript_tokens": 0,
    "condition_context_tokens": 0,
    "compression_ratio": null,
    "included_raw_turn_ids": [],
    "included_memory_item_ids": [],
    "memory_writes": [],
    "memory_retrievals": [],
    "evidence_anchor_in_context": false,
    "unsupported_claim_in_context": false,
    "recovery_anchor_in_context": false,
    "distortion_flags": []
  }
}
```

最小 implementation 约束：

- 每个 scenario/run 必须独立 memory namespace/store，避免 cross-run contamination。
- `full_transcript` baseline 必须和 memory condition 使用同一个 target model、judge model、scenario、turn order、temperature 和 prompt-style。
- memory context 注入格式必须固定，例如：
  - system message 中的 `<memory_context>` block；
  - 或 user message 前的 tool/context message；
  - 不要在不同 condition 混用两种格式。
- trace 必须保存 memory item 的 source turn ids；外部系统如果不返回 provenance，则用 sidecar metadata map 标注 `provenance_available=false`。
- token-window sweep 中，memory condition 的 injected context 不能超过同一 window budget。

## 10. 下一步

建议 M2 拆成两个 commit：

1. **本地 memory simulator skeleton**
   - 新增 `memory_condition` 参数和 trace schema。
   - 先支持 `full_transcript`、`recent_window`、`rolling_summary`。
   - mock mode 验证 trace 字段完整，不接任何外部依赖。

2. **本地 retrieval/fact conditions**
   - 支持 `vector_chunks`、`llm_fact_memory`、`evidence_aware_memory` 的 mock/OpenAI-compatible 路线。
   - 先用现有 `memdraft_001` / `uird_pilot_001` 做 development calibration。

外部系统 M6 前置事项：

- 准备 Python 3.10+ venv 或容器，并恢复 `pip`/package manager。
- Pin `mem0ai` 和 `graphiti-core` 版本，记录 lockfile 或 exact install command。
- 分别跑 1 scenario x 1 target x 1 system 的 external smoke。
- 对 smoke 生成 `experiments/s0_external_memory_smoke_YYYY-MM-DD.md`，再决定是否进入 fresh pilot。

## References

- mem0 Python quickstart: https://docs.mem0.ai/open-source/python-quickstart
- mem0 OSS configuration: https://docs.mem0.ai/open-source/configuration
- mem0 OpenAI compatibility: https://docs.mem0.ai/open-source/features/openai_compatibility
- mem0 migration guide: https://docs.mem0.ai/migration/oss-v2-to-v3
- mem0 GitHub: https://github.com/mem0ai/mem0
- Graphiti docs: https://help.getzep.com/graphiti/getting-started/welcome
- Graphiti GitHub: https://github.com/getzep/graphiti
- Zep quickstart: https://help.getzep.com/quick-start-guide
- LangChain/LangGraph long-term memory: https://docs.langchain.com/oss/python/langchain/long-term-memory
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LlamaIndex memory: https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/memory/
- Letta memory blocks: https://docs.letta.com/guides/core-concepts/memory/memory-blocks
- Letta archival memory: https://docs.letta.com/guides/core-concepts/memory/archival-memory
- Letta context hierarchy: https://docs.letta.com/guides/core-concepts/memory/context-hierarchy
