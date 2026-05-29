# Overall Plan

Last updated: 2026-05-29

This file records the overall plan and the current implementation position. Update it whenever the plan, current phase, or next action changes.

## North Star

Build Deviation Bench as a low-compute, API-only benchmark for measuring whether LLMs maintain reality-grounded judgments under changing conversational context and multi-turn user induction.

The core question:

> 同一模型、同一问题，在不同上下文和多轮用户诱导下，是否会系统性偏离现实锚定判断？这种偏离有多大、如何量化、能否被纠正？

## Research Positioning

Primary framing:

- Context-induced deviation
- Social judgment deviation
- Context-retest reliability / situation-retest reliability
- User-Induced Reality Drift

Not primary framing:

- Traditional demographic bias benchmark
- General hallucination benchmark
- Jailbreak benchmark
- Clinical diagnosis tool

## Non-Negotiable Constraints

- Must be feasible with LLM APIs and ordinary local scripting.
- Must not require high GPU usage.
- Must not require model finetuning or activation access.
- Must preserve the original research motivation: questioning the situational consistency assumption in AI evaluation.
- Must define and quantify the phenomenon before expanding the benchmark.
- Must keep induction safe: test reality-grounding failure without creating harmful real-world escalation.

## Current Phase

Phase: API-only runner smoke-tested + benchmark gap comparison drafted + seed pattern bank + utterance schema created -> real API smoke preparation.

Completed:

- Installed research skills.
- Defined the phenomenon as User-Induced Reality Drift.
- Drafted executable benchmark direction.
- Drafted data generation and data source strategy.
- Downloaded first wave of open real interview/dialogue data and reference evaluation configs.
- Created workspace navigation.
- Started memory bank and agent instructions.
- Prepared git tracking with raw downloaded data excluded from commits.
- Initialized local git repository and pushed the initial workspace commit to `git@github.com:advnljs/vibe-research-tmp.git`.
- Added downloaded data to git at the user's request, with a manifest and restricted-source application list.
- Reviewed the user-added `Datasets for a Deviation Bench on Reality-Boundary Language.md`.
- Downloaded additional public / legally accessible sources:
  - AnnoMI
  - MentalChat16K
  - CounselChat
  - MDD-5k
  - PDCH public metadata only
  - EATD-Corpus pointer only
  - Reddit Mental Health Dataset r/schizophrenia subset
  - RedditMentalhealth sample
- Wrote the community-data route for Reddit / Zhihu-like sources:
  - do not diagnose real users,
  - use existing public datasets before live scraping,
  - label text signals,
  - abstract into fictional benchmark scenarios.
- Created the first real-data-to-scenario mapping bridge:
  - `deviation-bench/data_sources/notes/真实语料到场景设计映射.md`
- Created the first executable pilot specification:
  - `deviation-bench/prompts/scenario_schema.yaml`
  - `deviation-bench/prompts/judge_rubric.md`
  - `deviation-bench/prompts/pilot_scenarios.yaml`
  - `deviation-bench/annotations/标注规范草案.md`
- Implemented the first minimal runner:
  - `deviation-bench/src/deviation_bench_pilot.py`
  - `deviation-bench/src/README.md`
  - `deviation-bench/requirements.txt`
- Offline validation and mock smoke test passed.
- Drafted the Table 1 style benchmark gap / prior comparison:
  - `deviation-bench/Benchmark 对比与研究缺口分析.md`
- Created the first abstracted seed pattern bank:
  - `deviation-bench/data_sources/patterns/README.md`
  - `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl`
- Created the unified utterance/source schema and LLM synthesis budget plan:
  - `deviation-bench/prompts/utterance_schema.yaml`
  - `deviation-bench/LLM数据合成方案与API成本预估.md`

Current implementation position:

- Minimal experiment runner exists.
- Pilot prompt schema and judge rubric exist.
- Pilot scenario set exists with 20 fictional low-risk scenarios.
- Mock smoke output exists locally under ignored `deviation-bench/results/`.
- No real API pilot result yet.
- Data manifest and use-policy notes now cover the current downloaded sources.
- Table 1 style prior comparison and paper gap statement draft now exist.
- First abstracted seed pattern bank exists with 60 no-raw-text pattern records.
- Unified utterance schema exists and maps the seed pattern bank to future scenario construction.
- LLM data synthesis plan exists with token/session estimates for S0/S1/S2.
- Next implementation unit is a real API smoke test, followed by synthesis script implementation if smoke passes.

## Milestone Plan

### Milestone 1: Project Memory and Data Hygiene

Status: completed for the current data wave; keep updated for future additions.

Deliverables:

- `研究导航.md`
- `memory-bank/overall-progress.md`
- `memory-bank/overall-plan.md`
- `memory-bank/next-step.md`
- `AGENTS.md`
- `.gitignore`
- Git remote `origin/main`
- `deviation-bench/data_sources/下载清单与访问状态.md`
- `deviation-bench/data_sources/restricted_or_apply/申请清单.md`
- `deviation-bench/data_sources/notes/数据许可与引用.md`
- `deviation-bench/data_sources/notes/社区语料获取与妄想相关性判定方案.md`
- `deviation-bench/data_sources/notes/真实语料到场景设计映射.md`

Exit condition:

- Any future agent can understand what exists, what is real data, what is synthetic/reference config, and what access restrictions apply.
- Any future agent can identify the next actionable task and longer roadmap from the three memory-bank files before reading the full research corpus.

### Milestone 2: Pilot Benchmark Specification

Status: first draft completed.

Deliverables:

- `deviation-bench/prompts/`
  - baseline prompts
  - induction prompts
  - recovery prompts
  - judge prompts

- `deviation-bench/annotations/标注规范草案.md`
  - stance labels
  - examples
  - edge cases
  - safety exclusions

- `deviation-bench/data_sources/notes/真实语料到场景设计映射.md`
  - how DAIS-C and first-episode psychosis interviews inform fictional benchmark scenarios without copying sensitive content.

Exit condition:

- 20 to 30 pilot scenarios are specified and can be run through LLM APIs.

Current status:

- 20 pilot scenarios exist in `deviation-bench/prompts/pilot_scenarios.yaml`.
- YAML parse check passed.
- Scenario schema, judge rubric, and human annotation draft exist.

### Milestone 3: Pilot Runner

Status: first draft completed with mock smoke test.

Deliverables:

- `deviation-bench/src/`
  - API client wrapper
  - conversation rollout runner
  - judge runner
  - metric calculator

- `deviation-bench/results/pilot/`
  - raw model outputs
  - judge outputs
  - metrics table
  - short analysis note

Exit condition:

- At least 2 to 3 models are evaluated on the pilot.
- Metrics include RDS, IS, RDER, URR, RR, and RD.

Current status:

- Scenario loading and validation implemented.
- Mock target model and mock judge implemented for offline tests.
- OpenAI-compatible chat completions path implemented.
- Metrics are computed per scenario.
- Real API run has not been executed yet.

### Milestone 4: Validate Signal

Status: next after real API smoke test.

Deliverables:

- Model comparison table.
- Repetition variance analysis.
- Human spot-check of judge labels.
- Failure-case taxonomy.

Exit condition:

- The benchmark shows measurable differences between models or conditions, without relying on high-risk prompts.

### Milestone 5: Paper Skeleton

Status: started with Table 1 / related-work asset.

Deliverables:

- `deviation-bench/paper/table1_benchmark_comparison.md`
- `deviation-bench/paper/outline.md`
- `deviation-bench/paper/introduction.md`
- `deviation-bench/paper/method.md`
- `deviation-bench/paper/related-work.md`
- first figures:
  - benchmark pipeline
  - drift curve
  - recovery curve
  - model comparison panel

Exit condition:

- A coherent benchmark paper draft can be assembled from pilot results.

## Immediate Next Actions

Phase shift 2026-05-29：framing 决策仍未由用户最终拍板；与 framing 无关的 Table 1 / gap comparison、seed pattern bank、utterance schema 和 LLM 合成预算方案已完成，主路径继续保持在“real API smoke + 可并行准备工作”。

Detailed handoff queue:

- `memory-bank/next-step.md`

1. **阻塞中**：等用户回答 `deviation-bench/目标收缩-工作流深思考.md` §7 的 6 个开放问题（A/B/C framing、venue、companion method 是否做、语种、原文使用阈值、deadline）。
2. 与 framing 无关、可并行（来自同文 §6）：
   - 已完成：写 Table 1 Benchmark Comparison Table 草稿（weval / Stanford HAI / ELEPHANT 等 prior 横向对比）。
   - 已完成：写 Benchmark gap / prior comparison addendum，补充 gap statement、RQ、G1-G4 与 reviewer 风险防守。
   - 已完成：抽 60 条 abstracted pattern 到 `data_sources/patterns/seed_pattern_bank.jsonl`。
   - 已完成：写统一 utterance schema `prompts/utterance_schema.yaml`。
   - 已完成：写 LLM 数据合成方案与 API token/session 预估。
   - 跑 real-API smoke test（1 target + 1 judge × 1-2 scenario）。
   - 写 Section 2 §Task and Design Goals 草稿（覆盖 G1-G4，复用 `paper/table1_benchmark_comparison.md` 和 `Benchmark 对比与研究缺口分析.md`）。
3. framing 确定后再回到：选 target/judge 模型 → 跑 20-场景 pilot → 扩规模。

## Decision Log

2026-05-21:

- Chose User-Induced Reality Drift as the most feasible and faithful narrowed phenomenon.
- Chose API-only benchmark design due to the low-GPU constraint.
- Chose real dialogue/interview data as grounding reference, not as direct benchmark prompts by default.
- Chose Bloom / Weval as generation and evaluation structure references, not as real clinical data.
- Chose safety boundary: induce reality-grounding stress, not jailbreak or harmful escalation.
- Chose conservative git tracking: commit research/memory/navigation/skill files, but exclude raw downloaded datasets and extracted transcripts by default.
- Initialized and pushed the local repository to `git@github.com:advnljs/vibe-research-tmp.git` on branch `main`.
- User then requested data to be pushed as well. DAIS-C, first-episode psychosis transcripts, Bloom, Bloom experiments configs, and Weval configs were prepared for git tracking with license/access notes.
- Data push completed in commit `27d461b` on `origin/main`.

2026-05-22:

- Continued from `todo20260521.txt`.
- Treated community data as a signal source, not a source of clinical labels.
- Chose not to directly scrape Zhihu at this phase because platform terms, privacy, copyright, and redistribution risk are higher than using existing public datasets.
- Chose the pipeline: public/community dataset -> text-signal judge -> human audit subset -> abstract pattern -> fictional multi-turn benchmark scenario.
- Recorded PDCH full data as restricted; downloaded only public metadata/code.
- Recorded EATD full data as a large Git LFS item; downloaded only the pointer/README.
- Created `真实语料到场景设计映射.md` as the bridge from data sources to pilot scenario families.
- User added a persistent workflow requirement: after each stage-level result, update memory bank and commit to git.
- Created the pilot benchmark spec draft with scenario schema, judge rubric, 20 scenarios, and annotation guidelines.
- Implemented and smoke-tested the minimal API-only runner in mock mode.

2026-05-22 afternoon：

- Produced `deviation-bench/数据现状评估与下一步方案.md`，把 pilot/v1 数据充足性按"够 / 不够 / 缺什么"系统化；§6.5 增补"真实数据 + LLM 合成"专项方案。
- Produced `deviation-bench/目标收缩-工作流深思考.md`，以 `idea-evaluator` + `benchmark-paper-template` + `vibe-research-workflow` 为脚手架，给出三套 framing 候选 (A/B/C)，每套都走完 fatal-flaws / 5 维评分 / paradigm probe / feasibility / 5 pillars。
- 决定不替用户选 framing，让 §7 的 6 个开放问题由用户回答后再继续。
- 强化 `AGENTS.md` 工作流规则：每完成一个完整任务必须更新 memory-bank + 单独 commit；显式定义“完整任务”边界与 per-task closing checklist。
- 完成 `deviation-bench/paper/table1_benchmark_comparison.md`，作为 introduction / related work 的 benchmark comparison 资产；当前差异化主张收束为“reality-boundary judgment 的 context-retest reliability”。
- 创建 `memory-bank/next-step.md` 作为第三个必维护 memory-bank 文件，承接可执行队列、阻塞问题、A/B/C 后续路线和 future-agent starting procedure；同步更新 `AGENTS.md`，要求每个 agent 优先依赖和维护三个 memory-bank 文件。

2026-05-29：

- Produced `deviation-bench/Benchmark 对比与研究缺口分析.md`，将 Deviation Bench 与 Weval、Stanford HAI / FAccT、Bloom、ELEPHANT、Anthropic sycophancy、multi-turn reliability 和 hallucination probes 做 Table 1 式对比。
- 决定后续 introduction 的主防守点应是 context-retest reliability of reality-grounded judgment，而不是 AI psychosis、therapy safety、generic sycophancy 或 ordinary hallucination。
- 将 neutral paraphrase noise、evidence anchor、unsupported claim、recovery turn、人审 audit 明确列为后续实现的硬约束。
- Created `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl` with 60 abstracted no-raw-text patterns from DAIS-C, first-episode psychosis friendship interviews, and Reddit `r/schizophrenia`; next schema work should map these pattern fields into `prompts/utterance_schema.yaml`.
- Created `deviation-bench/prompts/utterance_schema.yaml` and `deviation-bench/LLM数据合成方案与API成本预估.md`; current token estimate is S0 smoke about 20k-35k tokens, S1 synthesis/QC about 200k-350k tokens plus 3.4M-5.1M pilot evaluation tokens, and S2 v1 synthesis/QC about 1.1M-1.8M tokens plus 22M-51M evaluation tokens depending on model count.
