# 已搜集资料与迁移导航

更新日期：2026-07-07

这个文件说明 `deviation-bench-restart-pack/` 里有什么、从哪里来、下一个 agent 应该按什么顺序读。

## 1. 推荐阅读顺序

1. `README.md`
   - 迁移包用途、边界、密钥和原始数据处理方式。
2. `01_initial_motivation_and_goals.md`
   - Deviation Bench 最初问题：UIRD、context-retest reliability、reality grounding。
3. `research_docs/00_core_motivation/Deviation Bench 现象定义与量化框架.md`
   - 原始核心定义和指标细节。
4. `research_docs/00_core_motivation/Deviation Bench 可执行优化版.md`
   - API-only、低 GPU、pilot/v1 规模和 benchmark scope。
5. `data_sources/下载清单与访问状态.md`
   - 已下载数据、许可、用途和隐私边界。
6. `research_docs/01_data_generation/数据生成方式与心理精神病学数据源清单.md`
   - Bloom-like 生成、Controlled Injection、真实语料使用边界。
7. `prompts/scenario_schema.yaml`、`prompts/judge_rubric.md`、`prompts/pilot_scenarios.yaml`
   - 旧 pilot 可直接复用的 schema / judge / scenario。
8. `src/README.md`、`src/deviation_bench_pilot.py`
   - 旧 API-only runner 入口。

## 2. 迁移包目录

### `research_docs/00_core_motivation/`

旧路线的核心概念文件：

- `Deviation Bench 现象定义与量化框架.md`
  - 定义 UIRD、episode 结构、Track A/B/C、RDS/IS/RDER/URR/RR 等指标。
- `Deviation Bench 可执行优化版.md`
  - 说明研究初心是挑战 situational consistency，并将项目收缩为 API-only benchmark。
- `目标收缩-工作流深思考.md`
  - 早期对多个 framing 的系统比较；注意其中人审建议已被后续 LLM-only 方案取代。
- `数据现状评估与下一步方案.md`
  - 早期对数据现状和下一步路线的判断。
- `后续优先级路线图.md`
  - 旧路线的阶段顺序，适合参考但不应机械照搬。

### `research_docs/01_data_generation/`

数据和合成路线：

- `数据生成方式与心理精神病学数据源清单.md`
  - 真实精神病学/心理学数据源、Bloom-like 自动生成、Controlled Injection、安全化合成方案。
- `Datasets for a Deviation Bench on Reality-Boundary Language.md`
  - 用户之前列出的候选数据源与 reality-boundary language 相关性。
- `LLM数据合成方案与API成本预估.md`
  - S0/S1/S2 合成和评测成本估算。

### `research_docs/02_evaluation_and_paper/`

评测、文献和论文结构：

- `Deviation Bench 相关研究深度综述.md`
  - 相关研究地图。
- `Benchmark 对比与研究缺口分析.md`
  - benchmark gap / Table 1 草稿。
- `LLM-only评测与验证方案.md`
  - 后续用户明确要求：论文不依赖人类标注，使用 LLM judge、metajudge、judge variance、gold-control 和 schema/rule validation。
- `标注规范草案.md`
  - 历史开发文档，只能作 debugging 参考，不是 paper-facing annotation source。
- `paper/table1_benchmark_comparison.md`
  - 论文对比表草稿。

### `research_docs/03_later_agent_memory_optional/`

后期可选路线，不是最初问题的起点：

- `Agent Memory系统评测新视角.md`
- `agent_memory_eval_protocol.md`
- `agent_memory_system_survey.md`

这些文件记录了“agent memory can be delusive”的后期主张和协议。如果新 agent 重新启动时仍想接 agent memory，先把 UIRD / evidence-anchor benchmark 做小做稳，再决定是否接入。

## 3. 数据资料

### `data_sources/下载清单与访问状态.md`

这是最重要的数据导航文件。它记录了每个数据源的：

- 本地路径。
- 来源 URL / DOI。
- 数据类型。
- 访问状态。
- 许可状态。
- 关键文件。
- 推荐用途。
- 禁止或谨慎事项。

### 已下载资料概览

- DAIS-C：schizophrenia / control 自然语言访谈，CC BY-SA 4.0。
- First-Episode Psychosis Friendship：first-episode psychosis 访谈转录，CC BY 4.0。
- AnnoMI：motivational interviewing 对话与专家标注，不是 psychosis 主数据。
- MentalChat16K：mental health assistance 问答/对话，含合成与改写材料。
- CounselChat：公开心理咨询问答，单轮为主。
- MDD-5k：合成诊断对话，适合作管线参考。
- Reddit Mental Health Dataset r/schizophrenia subset：社区文本信号，不是临床诊断。
- RedditMentalhealth sample：社区语料 sample。
- PDCH metadata：只有公开 metadata / code，不是完整数据。
- EATD-Corpus pointer：只有 Git LFS pointer，不是完整数据。
- Bloom / Bloom experiments branch：生成、rollout、judge 方法参考，不是临床数据。
- Weval configs：评测 blueprint / rubric 参考，不是真实临床数据。

### `data_sources/downloaded/`

本地迁移包里复制了已下载原始资料，但该目录被 `.gitignore` 排除，避免在 restart pack 中二次提交大量真实/第三方数据。

如果要迁移到另一个 agent：

- 本地复制整个 `deviation-bench-restart-pack/` 目录即可带走这些数据。
- 公开分享或 push 前必须确认不包含 `data_sources/downloaded/` 和 `ds_key.txt`。
- 新 agent 应先读 `data_sources/下载清单与访问状态.md`，再决定哪些数据能进入公开研究输出。

### `data_sources/notes/`

已整理的数据使用说明：

- `社区语料获取与妄想相关性判定方案.md`
  - Reddit / Zhihu-like 社区文本只作为 text signals，不诊断发帖者。
- `数据许可与引用.md`
  - 数据许可、引用和治理提醒。
- `真实语料到场景设计映射.md`
  - 真实资料如何映射成虚构场景家族。
- `真实数据贴近度与半真实评测方案.md`
  - Tier 0/1/2/3/4 数据贴近度路线。

### `data_sources/patterns/`

- `seed_pattern_bank.jsonl`
  - 60 条抽象模式记录，来源包括 DAIS-C、FEP friendship interviews 和 Reddit。
  - `source_text_copied=false`，不包含原始转录或社区帖原文。
- `README.md`
  - 模式库说明。

### `data_sources/restricted_or_apply/`

- `申请清单.md`
  - PsychosisBank、DAIC-WOZ、PDCH full dataset 等受限/申请制数据源。

## 4. Prompt / schema / runner

### `prompts/`

关键文件：

- `scenario_schema.yaml`
- `pilot_scenarios.yaml`
- `judge_rubric.md`
- `metajudge_rubric.md`
- `gold_control_scenarios.yaml`
- `real_to_dialogue_rewrite_prompt.md`
- `utterance_schema.yaml`
- `memory_scenario_drafts.yaml`

重启建议：

- 先从 `scenario_schema.yaml`、`judge_rubric.md` 和 `pilot_scenarios.yaml` 恢复小规模 S0。
- `memory_scenario_drafts.yaml` 属于后期 agent-memory 分支，不建议作为第一入口。

### `src/`

关键文件：

- `deviation_bench_pilot.py`
  - 旧 pilot 主 runner。
- `build_judge_consensus.py`
  - metajudge / judge-consensus 工具。
- `rewrite_real_to_dialogue.py`
  - 真实资料到虚构 dialogue 的改写工具。
- `build_conversation_dashboard.py`
  - 对话结果浏览页面生成。
- `build_scenario_browser.py`
  - scenario browser。
- `build_memory_runner_scenarios.py`、`summarize_memory_runs.py`
  - 后期 memory 分支工具。

## 5. 已有实验记录

`experiments/` 包含旧路线已经写好的 S0 和 mock 记录：

- DeepSeek smoke。
- naturalistic 20-turn calibration。
- standard held-out mini pilot。
- judge contract hardening。
- judge spot check。
- memory draft mock rollout。
- memory real API smoke。
- memory scenario revision/expansion validation。
- memory-condition runner skeleton validation。

这些记录可用于理解哪些尝试有效、哪些只是 development calibration。不要把 smoke/calibration fragment 混成正式 held-out 证据。

## 6. 密钥文件

根目录 `ds_key.txt` 已复制到迁移包中，但不会提交。新 agent 使用时：

- 只在本地读。
- 不打印内容。
- 不写入日志。
- 不提交。
- 如果要迁移到在线环境，优先改成环境变量或密钥管理，而不是继续用明文文件。

## 7. 新 agent 的最小重启任务

建议从一个很小、可验证的循环开始：

1. 读 `01_initial_motivation_and_goals.md` 和核心文档。
2. 挑 5 个 low-risk fictional evidence-anchor scenarios。
3. 运行 `src/deviation_bench_pilot.py` 的 mock / API smoke。
4. 用 `prompts/judge_rubric.md` + `prompts/metajudge_rubric.md` 做 turn-level 判定。
5. 只报告 RDS / URR / RR 三个主指标。
6. 通过 gold controls 检查 judge 是否稳定。
7. 再扩到 20-50 个场景，而不是先做新的大规模数据整理。
