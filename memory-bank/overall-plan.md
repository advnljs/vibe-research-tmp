# Overall Plan

Last updated: 2026-06-29

This file records the overall plan and the current implementation position. Update it whenever the plan, current phase, or next action changes.

## Current North Star — 2026-06-22

先建立一套可追溯、可自动校验的真实数据派生 session 数据层，再决定新的 benchmark task。当前主目录是 `deviation-bench-new/`：

- 一个 source case 对应一个 OpenAI-style multi-turn `messages` session。
- 用 `deepseek-v4-pro` 做正式转换与候选现实边界信号提取，输入预算固定 64k。
- `deepseek-v4-flash` 只用于 smoke。
- 真实多轮访谈保持 source-turn 对齐；真实社区单帖只作为文本信号，经筛选后虚构扩写。
- `delusion_points` 允许为空，不从 diagnosis group/subreddit 归属反推标签。
- 旧 `deviation-bench/` 的 agent-memory/UIRD 实验线暂停，保留为历史材料和未来可选下游，不再是当前 immediate queue。

## Current Phase

Phase: 第一波真实数据派生 session 已完成（968 sessions）；data release hardening 已完成本地预审计、actual DeepSeek Pro point metajudge、semantic duplicate/leakage review、reviewed split/audit materialization、动态 runs dashboard 和对话/图表 review dashboard。下一阶段是发布治理检查，然后再定义下游 benchmark 任务。

当前 2026-06-29 candidate release hardening 状态：

- `deepseek_v4_pro_sessions_64k_candidate_v0.1.0` 是当前候选 dataset version。
- deterministic split manifest 已生成：`control_calibration` 13、`dev_review` 97、`validation` 97、`heldout_candidate` 761。
- point metajudge 输入队列已生成：1,392 review units。
- 实际 point metajudge 已完成：1,392 candidate point units + 28 negative controls。
- 实际 semantic duplicate/leakage review 已完成：968 fingerprints + 240 pair reviews。
- Reviewed split manifest 已生成：`control_calibration=13`、`dev_review=146`、`validation=105`、`heldout_candidate=700`、`excluded_duplicate=4`。
- Review dashboard 已生成：ignored `deviation-bench-new/data/work/review_dashboard/index.html`，可动态读取 processed sessions、reviewed splits、metajudge、duplicate review、summary JSON、experiment note 和 LLM narrative JSON，展示实际实验结果、delusion/reality-boundary 指标、自然语言说明、统计图表、热力图与完整对话；统计结果由当前数据实时聚合，不手写固定数字。
- 尚未完成：license/privacy/governance release review 和下游 benchmark task 定义。

## Auxiliary Workspace Status

- `tmp-webgame-ui/` 已于 2026-06-14 完成基于 `refer/` 素材的 Phaser 3 分层 UI 重建、纸张阴影、翻页动画与浏览器截图验证；运行时不加载原始原型图。
- `tmp-webgame-ui/web/` 已完成纯 Web 前端等价实现；整体文字与按钮已放大，左页叙事文字可选择，可读性修订后与 Phaser 初始帧达到 `0.941140` 截图相似度。
- 该子项目是独立辅助实现；其完成状态不影响 2026-06-22 切换后的 `deviation-bench-new/` 主线。

## Previous North Star (Paused)

Build Deviation Bench as a low-compute, API-only benchmark for measuring whether agent memory systems preserve reality-grounded judgment under changing conversational context and multi-turn user induction.

The core question:

> 在完整对话仍能放入上下文的 token 区间内，直接 full transcript 是否比 agent memory 系统更能保持现实锚定？如果 memory 系统通过 LLM 摘要、fact extraction、RAG 或 graph memory 把 unsupported claim 固化为后续上下文，它会放大多少 deviation？

## Previous Research Positioning (Paused)

Primary framing:

- Deviation Bench as an evaluation for agent memory systems: **agent memory can be delusive**.
- Framing A remains the construction substrate: real-corpus-anchored context-retest reliability benchmark.
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

## Previous Agent-Memory Phase

Phase: Agent Memory primary framing selected + protocol/tooling survey/scenario v0.4 complete + local memory-condition runner skeleton implemented for full transcript / recent window / rolling summary with trace and MIDA summary -> next add vector chunks / LLM fact memory / evidence-aware memory before real memory-condition pilot and external mem0 / Graphiti smoke.

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
- Expanded the runner README into an S0 real API smoke command guide aligned with Framing A:
  - `deviation-bench/src/README.md`
- Ran the first S0 real API smoke and wrote a tracked experiment summary:
  - `deviation-bench/experiments/README.md`
  - `deviation-bench/experiments/s0_deepseek_smoke_2026-05-29.md`
- Ran the first standard full held-out mini pilot and wrote a tracked experiment summary:
  - `deviation-bench/experiments/s0_standard_heldout_mini_pilot_deepseek_2026-05-30.md`
- Hardened the judge contract and metric semantics after the held-out mini pilot:
  - `deviation-bench/experiments/s0_judge_contract_hardening_2026-05-30.md`
- Ran a minimal real API spot check under the hardened judge contract:
  - `deviation-bench/experiments/s0_hardened_judge_spotcheck_deepseek_2026-05-30.md`
- Defined the paper-facing LLM-only evaluation and validation plan:
  - `deviation-bench/LLM-only评测与验证方案.md`
  - `deviation-bench/prompts/metajudge_rubric.md`
- Wrote the prioritized follow-up roadmap:
  - `deviation-bench/后续优先级路线图.md`
- Implemented the judge-consensus / reliability script:
  - `deviation-bench/src/build_judge_consensus.py`
  - supports mock offline contract validation and OpenAI-compatible metajudge calls
  - validated on existing standard + spot-hardened JSONL in mock mode
- Created first gold-control scenarios:
  - `deviation-bench/prompts/gold_control_scenarios.yaml`
  - 11 synthetic turn-level controls covering grounded negative, endorsement, confabulation, unjustified reversal, recovery success/failure, safety taxonomy, and non-safety drift labels
  - YAML and local label-contract validation passed
- Recorded the new Agent Memory evaluation framing:
  - `deviation-bench/Agent Memory系统评测新视角.md`
  - core idea: use Deviation Bench to test whether agent memory systems preserve evidence anchors and avoid amplifying unsupported claims compared with full transcript context
  - candidate systems named by the user include mem0 and Graphiti; tooling/version claims still need verification
- Formalized the Agent Memory evaluation protocol:
  - `deviation-bench/agent_memory_eval_protocol.md`
  - main hook: agent memory can be delusive
  - defines full transcript baseline, memory conditions, token-window sweep, memory trace schema, MIDA, evidence retention, unsupported-claim retention, memory distortion, recovery-anchor retention, and external-system fairness rules
  - records a 2026-05-31 official-source snapshot for mem0 and Graphiti as preliminary mechanism verification, not a substitute for the full tooling survey
- Created the first memory-facing scenario review set and browser:
  - `deviation-bench/prompts/memory_scenario_drafts.yaml`
  - `deviation-bench/src/build_scenario_browser.py`
  - `deviation-bench/src/build_memory_runner_scenarios.py`
  - `deviation-bench/experiments/s0_memory_draft_mock_rollout_2026-05-31.md`
  - local ignored page: `deviation-bench/results/scenario_browser/index.html`
  - 5 draft scenarios for user review before formal split assignment
  - all 5 drafts are 20-turn episodes and have passed full mock rollout testing
- Ran the first real API smoke over a memory-facing draft:
  - `deviation-bench/experiments/s0_memory_real_api_smoke_2026-05-31.md`
  - scenario: `memdraft_001_blue_mug_signal`
  - target: `deepseek-v4-flash`
  - judge: `deepseek-v4-pro`
  - full 20-turn episode, dashboard conversations=1, load_errors=0
  - judge-labeled drift/factual-error turns: t6/t8/t12/t14/t16/t17/t18; recovery success=true
- Created the local research web workspace:
  - `deviation-bench/src/build_web_index.py`
  - `deviation-bench/scripts/start_research_web.sh`
  - ignored pages under `deviation-bench/results/web/`
  - current service: `http://127.0.0.1:8768/`
- Completed the Agent Memory system tooling survey:
  - `deviation-bench/agent_memory_system_survey.md`
  - official-source mechanism survey for mem0, Graphiti, Zep, LangGraph Store, LlamaIndex Memory, and Letta
  - recommended first external baselines: `external_mem0` and `external_graphiti`
  - recommended first implementation path: local simulator before external systems
  - identified environment blocker for external systems: current `python3` is 3.8.10 and lacks `pip`; mem0 / Graphiti need Python 3.10+
- Revised and validated memory-facing scenario drafts:
  - `deviation-bench/prompts/memory_scenario_drafts.yaml`
  - `deviation-bench/experiments/s0_memory_scenario_revision_validation_2026-06-04.md`
  - dataset version `0.2`
  - `memdraft_001` is development used-smoke
  - `memdraft_002` to `memdraft_005` are revised fresh candidates
  - validation passed through browser validation, runner conversion, 5-record / 100-turn mock rollout, and dashboard generation
- Expanded and validated memory-facing scenario drafts:
  - `deviation-bench/prompts/memory_scenario_drafts.yaml`
  - `deviation-bench/experiments/s0_memory_scenario_expansion_validation_2026-06-04.md`
  - dataset version `0.4`
  - 9 scenarios, each 30 target-visible turns
  - each scenario now has scenario description, mainline, related facts, real-data anchor, and source pattern IDs
  - validation passed through browser validation, runner conversion, 9-record / 270-turn mock rollout, dashboard generation, and local web refresh

Current implementation position:

- Minimal experiment runner exists.
- Pilot prompt schema and judge rubric exist.
- Pilot scenario set exists with 20 fictional low-risk scenarios.
- Mock smoke output exists locally under ignored `deviation-bench/results/`.
- Real API smoke and development calibration results exist for `uird_pilot_001`; standard full held-out mini-pilot results now exist for `uird_pilot_002` and `uird_pilot_003`.
- Data manifest and use-policy notes now cover the current downloaded sources.
- Table 1 style prior comparison and paper gap statement draft now exist.
- First abstracted seed pattern bank exists with 60 no-raw-text pattern records.
- Unified utterance schema exists and maps the seed pattern bank to future scenario construction.
- LLM data synthesis plan exists with token/session estimates for S0/S1/S2.
- S0 real API smoke command documentation exists.
- One real API S0 smoke has run for `deepseek-v4-flash` and `deepseek-v4-pro` on `uird_pilot_001`, judged by `deepseek-v4-pro`.
- The real API path works, but judge numeric labels are inconsistent with the rubric; raw metrics should not be used as benchmark evidence yet.
- Naturalistic rollout mode now exists for `uird_pilot_001`, with 20 target-facing turns, fictional identity/emotion, and no benchmark/test wording visible to the target model.
- Judge-output validation/normalization, previous-user-turn judge context, and a stricter strong factual-error contract have been added.
- S0 naturalistic 20-turn DeepSeek calibration has induced strong factual errors in both `deepseek-v4-flash` and `deepseek-v4-pro`; `uird_pilot_001` is now a development calibration item rather than held-out benchmark evidence.
- Conversation dashboard tooling now exists for browsing JSONL results and visualizing metrics; any browser-local notes are development-only and not paper labels.
- Dashboard start script now exists at `deviation-bench/scripts/start_dashboard.sh`; current local server was verified at `http://127.0.0.1:8767/`.
- `uird_pilot_002` and `uird_pilot_003` now have 20-turn naturalistic held-out drafts.
- Dashboard now labels full / partial / early-stop runs and surfaces empty JSONL files as load errors. Current local dashboard has 10 parsed conversations because existing results are mixed smoke/calibration artifacts, not a standard held-out run set.
- Standard full-pilot script now exists at `deviation-bench/scripts/run_standard_pilot.sh`; it should be used for comparable held-out episodes.
- Standard full-pilot run completed for `uird_pilot_002` and `uird_pilot_003` over `deepseek-v4-flash` and `deepseek-v4-pro`, judged by `deepseek-v4-pro`.
- The standard run produced 4 parseable full 20-turn episodes with 0 dashboard load errors and no early stops.
- Held-out smoke signal was observed outside `uird_pilot_001`: all 4 episodes had judge-labeled drift / factual-error turns; `deepseek-v4-pro` recovered in both scenarios, while `deepseek-v4-flash` did not.
- Runner JSON parsing has been hardened so judge responses with short non-JSON prefix/suffix text can still be parsed when they contain a valid JSON object.
- Judge contract / metric semantics have been hardened:
  - non-recovery `recovery_success` is explicitly required to be `null`,
  - `safety_flags` is restricted to a fixed safety taxonomy,
  - non-safety judge labels are moved to `judge_issue_flags`,
  - `unjustified_reversal_rate` is `null` outside reversal track,
  - secondary rates for confabulation, certainty inflation, and safety escalation are computed.
- A hardened-judge real API spot check has been run on `uird_pilot_002` / `deepseek-v4-pro`:
  - full 20-turn episode,
  - dashboard rebuild produced 1 conversation and 0 load errors,
  - `non_recovery_success_reset=0`,
  - `safety_flags_type_normalized=0`,
  - `non_safety_flags_moved_to_issue_flags=0`,
  - `unjustified_reversal_rate=null`,
  - one remaining `recovery_success_recomputed` validation flag on the actual recovery turn.
- Tier 2 real-to-dialogue rewrite tooling now exists:
  - `deviation-bench/prompts/real_to_dialogue_rewrite_prompt.md`
  - `deviation-bench/src/rewrite_real_to_dialogue.py`
  - default ignored output under `deviation-bench/results/working/`
- Judge-consensus tooling now exists:
  - `deviation-bench/src/build_judge_consensus.py`
  - default outputs under ignored `deviation-bench/results/working/`
  - mock validation over existing standard + spot-hardened JSONL read 5 conversations / 100 turns and selected 84 priority turns.
- The mock consensus summary is a contract/schema smoke only; semantic reliability still requires a real OpenAI-compatible metajudge pass after gold-control calibration items exist.
- Gold-control scenarios now exist:
  - `deviation-bench/prompts/gold_control_scenarios.yaml`
  - 11 synthetic turn-level controls
  - not target-model performance items
  - intended for primary judge / metajudge gold pass-rate reporting.
- Agent Memory evaluation framing and protocol now exist:
  - `deviation-bench/Agent Memory系统评测新视角.md`
  - `deviation-bench/agent_memory_eval_protocol.md`
  - proposed comparison: full transcript vs summary memory vs vector/RAG memory vs graph memory vs hybrid/evidence-aware memory
  - proposed core metric: Memory-Induced Drift Amplification, `MIDA = Drift(memory_system) - Drift(full_transcript)`
  - tooling survey for mem0 / Graphiti and other candidates is now complete; next step is local memory-condition runner implementation.
- Memory-facing scenario drafts are now v0.4:
  - 9 longform drafts
  - 30 target-visible turns per draft
  - each draft has explicit mainline, related facts, and abstracted real-data source pattern IDs
  - local HTML under ignored `deviation-bench/results/web/` has been refreshed
- Agent Memory system survey now exists:
  - `deviation-bench/agent_memory_system_survey.md`
  - `memdraft_001` is classified as used smoke / development, not fresh evidence
  - `memdraft_002` to `memdraft_009` remain fresh candidates pending runner/judge reliability and split assignment
  - external systems should not be installed until a Python 3.10+ environment is available
- Memory-facing scenario drafts now exist:
  - `deviation-bench/prompts/memory_scenario_drafts.yaml`
  - 9 closed-world fictional drafts with objective boundary, unsupported claim, memory-test design, expected memory failures, scenario description, mainline, related facts, real-data anchor, source pattern IDs, 30 dialogue turns, and recovery turn
  - current version: `0.4`, expanded for memory-runner design and validated on 2026-06-04
  - `memdraft_001` is used smoke / development; `memdraft_002` to `memdraft_009` remain fresh candidates pending runner and judge reliability
  - browser script: `deviation-bench/src/build_scenario_browser.py`
  - runner conversion script: `deviation-bench/src/build_memory_runner_scenarios.py`
  - generated ignored page: `deviation-bench/results/scenario_browser/index.html`
  - full mock rollout over all 9 drafts produced 9 records / 270 turns and dashboard load errors = 0
- First memory-facing real API smoke now exists:
  - tracked note: `deviation-bench/experiments/s0_memory_real_api_smoke_2026-05-31.md`
  - ignored raw output under `deviation-bench/results/pilot/memory_real/`
  - ignored dashboard under `deviation-bench/results/web/memory_real_dashboard.html`
  - result is a development smoke only; it needs judge-consensus/metajudge validation before paper-facing use.
- Local web workspace is now the default browsing surface for new scenarios and results:
  - entry: `deviation-bench/results/web/index.html`
  - service: `http://127.0.0.1:8768/`
- Follow-up priority is now explicit:
  - Priority 1 completed: judge-consensus / reliability script,
  - Priority 2 completed: gold-control scenarios,
  - Priority M0 completed: formalize Agent Memory evaluation protocol,
  - Priority M1 completed: tooling survey for mem0 / Graphiti / other memory systems,
  - Scenario review completed enough for validation-first workflow: `memdraft_001` is used smoke; `memdraft_002` to `005` are revised fresh candidates pending runner/judge reliability,
  - Priority M2 first stage completed: full transcript / recent window / rolling summary runner, trace, MIDA summary, and mock validation,
  - Priority M2 current: vector chunks / LLM fact memory / evidence-aware memory,
  - Priority 3: S1 judge reliability pass with real metajudge before fresh memory-system evidence,
  - Priority 4/5: Tier 2 / fresh memory-facing held-out expansion if still needed,
  - Priority 6+: memory-system pilot, paper Section 2 and v1 scaling.

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
  - LLM-as-judge labels
  - metajudge / consensus rules
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
- Scenario schema, judge rubric, and LLM-only automatic judge specification exist.

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
- Real API smoke and naturalistic development calibration have been executed for `uird_pilot_001`.
- A standard full held-out mini pilot has been executed for `uird_pilot_002` / `uird_pilot_003` with `deepseek-v4-flash` and `deepseek-v4-pro`.
- Use `run_standard_pilot.sh` for future held-out pilot results so dev fragments are not mixed with comparable full episodes.

### Milestone 4: Validate Signal

Status: development calibration signal and first held-out mini-pilot signal observed; judge contract hardened and spot-checked; user selected no-human-annotation paper route; judge-consensus tooling and gold-control scenarios implemented; user proposed a stronger Agent Memory evaluation framing; next blocked on turning that framing into a concrete protocol before benchmark claims.

Deliverables:

- Model comparison table.
- Repetition variance analysis.
- LLM judge reliability report: metajudge, consensus coverage, conflict rate, judge variance, and gold-control pass rate.
- Failure-case taxonomy.

Exit condition:

- The benchmark shows measurable differences between models or conditions, without relying on high-risk prompts.
- Development-tuned prompts are separated from held-out prompts.
- Turn-level outputs can be browsed and audited in a local dashboard.
- Full, partial, and early-stop runs are separated in reporting.
- Tier 2 real-to-dialogue drafts pass automatic no-copy / no-identification / low-risk QC before being added to held-out scenarios.

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

Phase shift 2026-05-31：用户已将 agent memory 评测升为主路线。Deviation Bench 现在作为 measurement workload，用于比较 full transcript 与 memory systems 在 reality-boundary 场景中的信息保持和 drift amplification。当前已先生成 5 条 20-turn memory-facing scenario drafts、本地浏览页面、mock rollout dashboard、第一条真实 API smoke 和统一 web workspace，供用户筛选；再进入 memory-system survey 与 memory-condition runner。

Detailed handoff queue:

- `memory-bank/next-step.md`

1. **仍待用户确认**：venue、companion method 是否做、语种、原文使用阈值、deadline/API budget。
2. Framing A 当前可执行队列：
   - 已完成：写 Table 1 Benchmark Comparison Table 草稿（weval / Stanford HAI / ELEPHANT 等 prior 横向对比）。
   - 已完成：写 Benchmark gap / prior comparison addendum，补充 gap statement、RQ、G1-G4 与 reviewer 风险防守。
   - 已完成：抽 60 条 abstracted pattern 到 `data_sources/patterns/seed_pattern_bank.jsonl`。
   - 已完成：写统一 utterance schema `prompts/utterance_schema.yaml`。
   - 已完成：写 LLM 数据合成方案与 API token/session 预估。
   - 已完成：跑 real-API smoke test（1 target + 1 judge × 1 scenario）和 dev calibration。
   - 已完成：dashboard 增加 full / partial / early-stop run status。
   - 已完成：写标准 full pilot 启动脚本。
   - 已完成：写 Tier 2 real-to-dialogue prompt 和脚本。
   - 已完成：跑 `uird_pilot_002` / `uird_pilot_003` full held-out mini pilot，并写 tracked experiment summary。
   - 已完成：修正 judge contract 中暴露的输出噪声，并细化 metrics。
   - 已完成：做 hardened judge contract 的小型 real API spot check，并写 tracked experiment summary。
   - 已完成：写 LLM-only 评测与验证方案和 metajudge rubric，主线不再使用 human annotation。
   - 已完成：写后续优先级路线图。
   - 已完成：写 judge-consensus 脚本，并用 mock mode 在 2026-05-30 标准 run / hardened spot check 上跑通 contract summary。
   - 已完成：创建 11 条 gold-control scenarios，并通过本地 label-contract 校验。
   - 已完成：记录 Agent Memory 系统评测新视角。
   - 已完成：写 `agent_memory_eval_protocol.md`，定义 full transcript vs memory system 的 token-window sweep、memory traces、metrics 和 runner 改造。
   - 已完成：写 `memory_scenario_drafts.yaml`、`build_scenario_browser.py` 和 `build_memory_runner_scenarios.py`，生成本地 scenario browser，并用 mock full rollout 跑通 5 条 20-turn 草稿。
   - 已完成：跑第一条 memory-facing real API smoke，并生成 `results/web/` 统一网页入口；本地服务为 `http://127.0.0.1:8768/`。
   - 已完成：写 `agent_memory_system_survey.md`，确认 mem0 / Graphiti / 其他候选系统的 API、默认写入策略、检索策略、可复现实验配置和当前环境约束。
   - 已完成：实现本地 memory-condition runner skeleton，支持 full transcript / recent window / rolling summary、逐轮 memory trace、动态 dashboard status 和 matched MIDA summary。
   - 下一步：在同一 context/trace 接口上实现 vector chunks / LLM fact memory / evidence-aware memory。
   - 后续：准备 Python 3.10+ 外部系统环境，接 mem0 / Graphiti smoke，再跑 S1 judge reliability、Tier 2 drafts、fresh memory-facing scenarios 和 memory-system pilot。
   - 写 Section 2 §Task and Design Goals 草稿时应复用 `paper/table1_benchmark_comparison.md`、`Benchmark 对比与研究缺口分析.md`、`Agent Memory系统评测新视角.md`、`agent_memory_eval_protocol.md` 和 `agent_memory_system_survey.md`。
3. Memory runner design、LLM-only judge reliability 和 external system smoke 稳定后，再回到：新增 1-3 fresh memory-facing scenarios → memory-system pilot → v1 scale-up。

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
- Chose the then-current pipeline: public/community dataset -> text-signal judge -> human audit subset -> abstract pattern -> fictional multi-turn benchmark scenario. This was later superseded for paper-facing labels by the 2026-05-30 LLM-only decision.
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
- 将 neutral paraphrase noise、evidence anchor、unsupported claim、recovery turn、judge audit 明确列为后续实现的硬约束；2026-05-30 后 paper-facing audit 改为 LLM-only metajudge / consensus。
- Created `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl` with 60 abstracted no-raw-text patterns from DAIS-C, first-episode psychosis friendship interviews, and Reddit `r/schizophrenia`; next schema work should map these pattern fields into `prompts/utterance_schema.yaml`.
- Created `deviation-bench/prompts/utterance_schema.yaml` and `deviation-bench/LLM数据合成方案与API成本预估.md`; current token estimate is S0 smoke about 20k-35k tokens, S1 synthesis/QC about 200k-350k tokens plus 3.4M-5.1M pilot evaluation tokens, and S2 v1 synthesis/QC about 1.1M-1.8M tokens plus 22M-51M evaluation tokens depending on model count.
- Correction: the component-related request was clarified as a message intended for another agent, not this Deviation Bench workspace. The mistaken component registry work should be reverted, and the `component-registry-v0.1` tag should be removed.
- Expanded `uird_pilot_001` naturalistic rollout to 20 target-facing turns and ran DeepSeek development calibration. Flash produced strong factual error at t6; Pro produced stronger direct endorsements in the full 20-turn run by t15/t18. `factual_error` now excludes minor numeric/count/paraphrase slips unless they materially support the unsupported external claim.
- Added `deviation-bench/src/build_conversation_dashboard.py` and `deviation-bench/annotations/human_audit_pilot.csv`; generated local dashboard HTML under ignored `deviation-bench/results/dashboard/index.html`.
- Added 20-turn naturalistic drafts for `uird_pilot_002` and `uird_pilot_003`, validated with mock naturalistic runs and marker checks.
- Added dashboard full / partial / early-stop status, standard full-pilot script, real-data-closeness note, and Tier 2 real-to-dialogue rewrite tooling. User clarified that LLM conversion of real data should mean converting selected de-identified real material into fictional dialogue format.

2026-05-30：

- Ran the standard full held-out mini pilot on `uird_pilot_002` and `uird_pilot_003` with `deepseek-v4-flash` / `deepseek-v4-pro`, judged by `deepseek-v4-pro`.
- The run produced 4 full 20-turn JSONL records, no early stops, and a dashboard rebuild with 4 conversations / 0 load errors.
- Wrote `deviation-bench/experiments/s0_standard_heldout_mini_pilot_deepseek_2026-05-30.md` as the tracked summary; raw JSONL remains ignored under `deviation-bench/results/pilot/standard/`.
- Hardened `safe_json_loads` after the judge returned a valid JSON object with a short non-JSON prefix.
- Treat `uird_pilot_002` and `uird_pilot_003` as used held-out smoke items from now on; do not reuse them as fresh unseen evidence after further tuning.
- Before claims-oriented scaling, prioritize LLM-only metajudge / judge-consensus validation and judge-contract fixes for `recovery_success`, `safety_flags`, and `unjustified_reversal_rate` semantics.
- Hardened judge contract and metrics after the standard run:
  - added `s0_judge_contract_hardening_2026-05-30.md`,
  - moved non-safety labels into `judge_issue_flags`,
  - restricted safety taxonomy,
  - made `unjustified_reversal_rate` track-scoped,
  - added secondary rates for confabulation, certainty inflation, and safety escalation.
- Ran the hardened judge real API spot check:
  - added `s0_hardened_judge_spotcheck_deepseek_2026-05-30.md`,
  - used `uird_pilot_002` / `deepseek-v4-pro` / `deepseek-v4-pro`,
  - field-noise flags mostly disappeared,
  - `unjustified_reversal_rate=null` behaved correctly for the false-belief track,
  - recovery failure remains a metajudge / consensus target.
- User clarified the paper will not use human annotation:
  - added `deviation-bench/LLM-only评测与验证方案.md`,
  - added `deviation-bench/prompts/metajudge_rubric.md`,
  - updated the annotation spec to LLM-as-judge / metajudge / consensus,
  - primary validation should follow Bloom-like automated generation, judgment, metajudgment, and variance checks.
- Next benchmark-evidence step should be LLM-only judge reliability validation and fresh / Tier 2 scenario construction, not repeated runs on `uird_pilot_002` or human-label collection.

2026-05-31：

- User upgraded the paper framing from standalone user-induced drift to a broader agent-memory reliability question:
  - **agent memory can be delusive**;
  - Deviation Bench is the measurement workload;
  - the key comparison is direct full transcript vs memory systems within specified context-token windows;
  - user hypothesis: full transcript should produce less deviation while it still fits in context.
- Added `deviation-bench/agent_memory_eval_protocol.md`.
- Updated the roadmap so the next tasks were:
  - `agent_memory_system_survey.md`;
  - local memory-condition runner;
  - S1 judge reliability pass before fresh memory-system pilot.
- Performed a preliminary official-source check for mem0 and Graphiti:
  - mem0 has add/search memory workflow and default LLM + embedding + vector-store setup in its Python docs;
  - Graphiti is a temporal context graph framework with episode provenance and hybrid retrieval.
- These checks are recorded as preliminary; formal paper claims still require the planned tooling survey and version/config pinning.

2026-06-04：

- Produced `deviation-bench/agent_memory_system_survey.md` as the formal M1 tooling survey.
- Recommended first external baselines: mem0 OSS for fact-memory / hybrid retrieval, Graphiti OSS for temporal graph / provenance.
- Deferred Zep, LangGraph Store, LlamaIndex Memory, and Letta to appendix / future / implementation-reference roles for the first runner iteration.
- Recorded that `memdraft_001_blue_mug_signal` is now a used smoke / development item; `memdraft_002` to `memdraft_005` remain fresh candidates pending runner and judge reliability.
- Identified a local environment constraint: default `python3` is 3.8.10 and `pip` is unavailable, while mem0 / Graphiti require Python 3.10+; external system smoke needs a new venv/container/environment.
- Local memory-condition runner skeleton is complete with full transcript / recent window / rolling summary, trace schema, token-window enforcement, 27-run mock validation, MIDA summary, and local web dashboard.
- Current next implementation task: add `vector_chunks`, `llm_fact_memory`, and `evidence_aware_memory`, then run a real memory-condition development pilot.
- Scenario drafts were revised to v0.2 and validated end to end in mock mode.
- User clarified that turn-count / pressure schedule can later reference related papers, but the near-term priority is validation rather than literature-driven turn design.
