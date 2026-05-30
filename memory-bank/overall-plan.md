# Overall Plan

Last updated: 2026-05-30

This file records the overall plan and the current implementation position. Update it whenever the plan, current phase, or next action changes.

## North Star

Build Deviation Bench as a low-compute, API-only benchmark for measuring whether LLMs maintain reality-grounded judgments under changing conversational context and multi-turn user induction.

The core question:

> 同一模型、同一问题，在不同上下文和多轮用户诱导下，是否会系统性偏离现实锚定判断？这种偏离有多大、如何量化、能否被纠正？

## Research Positioning

Primary framing:

- Framing A: real-corpus-anchored context-retest reliability benchmark
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

Phase: Framing A selected + standard held-out mini pilot completed + judge contract spot-checked + LLM-only evaluation design selected -> metajudge / judge-consensus implementation, Tier 2 real-to-dialogue drafts, and fresh held-out scenario expansion.

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
- Next implementation unit is an LLM-only metajudge / judge-consensus pass over the 2026-05-30 standard run plus the hardened spot-check rerun, then automatic QC and generation of 1-2 Tier 2 real-to-dialogue held-out drafts.
- Follow-up priority is now explicit:
  - Priority 1 judge-consensus / reliability script,
  - Priority 2 gold-control scenarios,
  - Priority 3 S1 judge reliability pass,
  - Priority 4 Tier 2 drafts,
  - Priority 5 fresh held-out naturalistic scenarios,
  - Priority 6 S1 fresh held-out mini pilot,
  - Priority 7 Section 2 Task and Design Goals,
  - Priority 8 S2 / v1 scaling.

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

Status: development calibration signal and first held-out mini-pilot signal observed; judge contract hardened and spot-checked; user selected no-human-annotation paper route; next blocked on metajudge / judge-consensus validation and fresh held-out scenario construction before benchmark claims.

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

Phase shift 2026-05-30：用户已选择 Framing A，并明确论文不使用人类标注。当前主路径是“LLM-only metajudge / judge-consensus + Tier 2 real-to-dialogue 数据构造 + fresh held-out scenario expansion”。

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
   - 下一步：写 judge-consensus 脚本，对 2026-05-30 标准 run / hardened spot check 做 LLM-only 复核。
   - 下一步：从 DAIS-C / first-episode friendship 去标识化片段或 seed patterns 生成 1-2 个 Tier 2 对话草稿，并通过自动 QC / metajudge。
   - 写 Section 2 §Task and Design Goals 草稿（覆盖 G1-G4，复用 `paper/table1_benchmark_comparison.md` 和 `Benchmark 对比与研究缺口分析.md`）。
3. LLM-only judge reliability 和 judge hardening 稳定后再回到：新增 1-3 fresh held-out scenarios → 20-scenario pilot → v1 scale-up。

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
