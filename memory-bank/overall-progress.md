# Overall Progress

Last updated: 2026-05-22

This file records completed work and the current state of the Deviation Bench project. Update it after any meaningful research, data, implementation, or planning change.

## Current Project State

Deviation Bench has been narrowed from a broad context-induced deviation idea into a more feasible, API-only benchmark direction:

- Working phenomenon: User-Induced Reality Drift (UIRD), also described as user-induced reality-grounding drift.
- Core observation: in multi-turn interaction, an LLM may move from grounded, evidence-constrained responses toward unsupported delusional elaboration, inappropriate validation, or unjustified reversal of an earlier determination.
- Intended contribution: measure context-retest / situation-retest reliability for LLMs, analogous to test-retest reliability in psychology.
- Compute constraint: low GPU / API-only. The benchmark should not depend on model training, activation extraction, or high-cost inference infrastructure.
- Safety boundary: induction designs should test reality-grounding failure in controlled, fictional, low-risk settings. They should not be jailbreaks, safety bypasses, or prompts that escalate real-world harm.

## Completed 2026-05-21

### Skills Installed

Installed skills from `https://github.com/HKUSTDial/Supervisor-Skills` into the current workspace:

- `idea-evaluator/`
- `benchmark-paper-template/`
- `figure-designer/`
- `intro-drafter/`
- `pre-submission-reviewer/`
- `tech-paper-template/`
- `vibe-research-workflow/`

### Research Direction Optimized

Created and refined these Deviation Bench research documents:

- `deviation-bench/Deviation Bench 可执行优化版.md`
  - Converts the idea into an executable API-only benchmark direction.
  - Defines v1 scope, pilot scale, tracks, schema, metrics, and paper skeleton.

- `deviation-bench/Deviation Bench 现象定义与量化框架.md`
  - Defines UIRD precisely.
  - Establishes tracks: False-Belief Amplification, Unjustified Determination Reversal, Recovery and Re-anchoring.
  - Defines stance labels and metrics such as RDS, IS, RDER, URR, CI, CER, RR, and RD.
  - Adds safe induction patterns such as premise laundering, commitment erosion, pattern-seeking traps, emotional validation pressure, authority smuggling, and hypothetical-to-real slide.

- `deviation-bench/数据生成方式与心理精神病学数据源清单.md`
  - Records Bloom-style generation strategies and real clinical / psychiatric data sources.
  - Separates real dialogue/interview datasets from synthetic/evaluation configs.

Existing literature file:

- `deviation-bench/Deviation Bench 相关研究深度综述.md`
  - Contains the literature map and motivation sources.

### Data Found and Downloaded

Created data directories:

- `deviation-bench/data_sources/downloaded/`
- `deviation-bench/data_sources/restricted_or_apply/`
- `deviation-bench/data_sources/notes/`

Downloaded / prepared:

- DAIS-C: `deviation-bench/data_sources/downloaded/dais_c/`
  - Real schizophrenia / comparison interview corpus.
  - Contains clinical and comparison groups, interactional transcripts, speaker-only raw text, timestamped files, metadata, consent/info sheets, and paper PDF.
  - Clinical speaker-only raw files: 15 individual files plus one aggregate file.
  - Comparison speaker-only raw files: 13 files.

- First-episode psychosis friendship interview transcripts:
  - `deviation-bench/data_sources/downloaded/first_episode_psychosis_friendship/`
  - 14 real interview transcripts from PLOS/Figshare supporting data.
  - Original `.doc` files extracted and converted to `.txt`.
  - Converted text total: about 94,507 words.

- Bloom repository:
  - `deviation-bench/data_sources/downloaded/bloom/`
  - Used as a reference for Bloom-style generation and judgment pipeline.
  - Relevant file: `examples/sweeps/delusion-sycophancy.yaml`.

- Bloom experiments branch:
  - `deviation-bench/data_sources/downloaded/bloom_experiments_branch/`
  - Relevant configs include `experiments/benchmarks/delusion-sycophancy.yaml`, `experiments/judge/delusion-sycophancy.yaml`, `experiments/metajudge/delusion-sycophancy.yaml`, and variance configs.

- Weval configs:
  - `deviation-bench/data_sources/downloaded/weval_configs/`
  - Relevant blueprints include `ai-psychosis.yml`, `ai-spiral-safety.yml`, `mental-health.yml`, `stanford-hai-mental-health-safety-eval.yml`, `sycophancy-probe.yml`, `overpersonalization-anchor-bias.yml`, `polarization-confirmation-risk.yml`, and `hallucination-probe.yml`.

### Data Added to Git

At the user's request, the downloaded data directory is now tracked in git and pushed to `origin/main`:

- Updated `.gitignore` so `deviation-bench/data_sources/downloaded/` is no longer ignored.
- Added `deviation-bench/data_sources/下载清单与访问状态.md` with source URLs, licenses, checksums, counts, citations, and intended use.
- Added `deviation-bench/data_sources/restricted_or_apply/申请清单.md`.
- License/access checks recorded:
  - DAIS-C: open access, CC BY-SA 4.0 on ReShare.
  - PLOS/Figshare first-episode psychosis transcripts: CC BY 4.0.
  - Bloom: MIT License.
  - Weval configs: CC0 1.0.
  - Bloom / Weval cloned `.git` metadata is not tracked by the parent repository.
- GitHub push protection flagged Stripe-like example keys in Bloom sabotage examples; these placeholders were redacted in the local tracked copies before pushing.
- Data commit pushed: `27d461b` (`Add downloaded data sources`).
- Parent repository status after push: clean.
- Nested `.git` metadata for Bloom / Weval was temporarily moved while adding files, then restored locally; it is not tracked by the parent repository.

### Data Sources Identified but Not Downloaded

Restricted or application-based sources identified:

- PsychosisBank DISCOURSE-UWO
- PsychosisBank Tang Corpus
- AVATAR Therapy Dialogue Corpus
- DAIC-WOZ
- SMHD and related social-media datasets, marked as lower priority because they are not real clinical dialogue and are not delusion-specific.

These should be tracked in `deviation-bench/data_sources/restricted_or_apply/` before application work begins.

### Navigation Created

Created:

- `研究导航.md`

This file explains the workspace structure, reading order, installed skills, research documents, downloaded data directories, and recommended next data usage.

### Memory Bank Started

Created:

- `memory-bank/overall-progress.md`
- `memory-bank/overall-plan.md`

These files should be kept current as the project evolves.

### Agent Instructions Started

Created:

- `AGENTS.md`

It records the user’s current requirements, constraints, safety boundaries, and maintenance rules for future work in this workspace.

### Repository Setup

Completed repository setup for the workspace:

- Added `.gitignore`.
- Chose a conservative default: `deviation-bench/data_sources/downloaded/` is not committed because it contains raw downloaded datasets, extracted transcripts, archives, and cloned third-party repositories.
- Added `.gitkeep` files for:
  - `deviation-bench/data_sources/notes/`
  - `deviation-bench/data_sources/restricted_or_apply/`
- Initialized local git repository on branch `main`.
- Configured remote `origin`: `git@github.com:advnljs/vibe-research-tmp.git`.
- Initial commit pushed to `origin/main`: `bb86941` (`Initial Deviation Bench research workspace`).

## Completed 2026-05-22

Continued from `todo20260521.txt`.

### Remote Pull and Workflow Rule Update

Pulled latest remote state from `origin/main`:

- Command: `git pull --ff-only origin main`
- Result: fast-forwarded from `fc2bbbb` to `bdc42f2`.
- New remote documents pulled:
  - `deviation-bench/数据现状评估与下一步方案.md`
  - `deviation-bench/目标收缩-工作流深思考.md`

Updated `AGENTS.md` per the user's new persistent workflow requirement:

- Every completed task must now end with:
  - memory-bank updates,
  - a focused git commit,
  - push to `origin/main`.
- It is no longer enough to commit locally and defer remote push.

### New Data Source Review and Downloads

Inspected `deviation-bench/Datasets for a Deviation Bench on Reality-Boundary Language.md` and downloaded the legally accessible / public sources that were useful enough for the current phase.

New local data directories:

- `deviation-bench/data_sources/downloaded/annomi/`
  - AnnoMI expert-annotated motivational interviewing dialogues.
  - Files: `AnnoMI-full.csv`, `AnnoMI-simple.csv`, `README.md`.
  - Use: counseling dialogue structure and validation/reflection style control; not psychosis/delusion ground truth.

- `deviation-bench/data_sources/downloaded/mentalchat16k/`
  - MentalChat16K from Hugging Face, MIT license.
  - Files: `Interview_Data_6K.csv`, `Synthetic_Data_10K.csv`, `README.md`.
  - Use: mental-health assistance format and synthetic generation reference; not raw delusion dialogue.

- `deviation-bench/data_sources/downloaded/counselchat/`
  - CounselChat from Hugging Face.
  - Files: `counselchat-data.csv`, `README.md`.
  - Use: single-turn counseling QA style reference.

- `deviation-bench/data_sources/downloaded/mdd_5k/`
  - MDD-5k GitHub repository, MIT license.
  - File count: 1,892.
  - Use: synthetic diagnostic conversation generation pipeline reference; not real psychosis/delusion corpus.

- `deviation-bench/data_sources/downloaded/pdch_metadata/`
  - PDCH public metadata / code snapshot only.
  - Full ScienceDB dataset is restricted and was not downloaded.

- `deviation-bench/data_sources/downloaded/eatd_corpus_pointer/`
  - EATD-Corpus Git LFS pointer and README only.
  - Full zip is about 543MB and was not added to the repository.

- `deviation-bench/data_sources/downloaded/reddit_mental_health_zenodo/`
  - r/schizophrenia subset from Reddit Mental Health Dataset on Zenodo.
  - Includes 2018, 2019, pre, post feature/text CSVs plus Zenodo metadata.
  - Use: community reality-boundary language signal source; not clinical diagnosis data.

- `deviation-bench/data_sources/downloaded/reddit_mentalhealth_sample/`
  - Public sample from `dxlabskku/RedditMentalhealth`.
  - Use: parser / filtering smoke test only.

Downloaded data root is currently about 206MB. No file larger than 95MB was found in the downloaded tree.

### Data Documentation Updated

Updated:

- `deviation-bench/data_sources/下载清单与访问状态.md`
  - Added source URLs, access status, license notes, local paths, row/file counts, caveats, and recommended use for the new sources.

- `deviation-bench/data_sources/restricted_or_apply/申请清单.md`
  - Added PDCH full dataset, MODMA, D4, HOPE/MEMO, Psych8k, and TalkBank control corpora to the application/restricted list.

Created:

- `deviation-bench/data_sources/notes/数据许可与引用.md`
  - Summarizes citation and use boundaries.

- `deviation-bench/data_sources/notes/社区语料获取与妄想相关性判定方案.md`
  - Defines a safe route for Reddit / Zhihu-like community data:
    - use existing public datasets first,
    - label text signals instead of diagnosing people,
    - abstract patterns into fictional multi-turn scenarios,
    - exclude high-risk action/self-harm/stalking content.

- `deviation-bench/data_sources/notes/真实语料到场景设计映射.md`
  - Maps real/interview/community/counseling/synthetic sources to safe pilot scenario families.
  - Adds a first draft scenario schema, six scenario families, judge tags, and next prompt-spec files.

Updated:

- `研究导航.md`
  - Added new data directories and the community-data note to the navigation.

- `AGENTS.md`
  - Added the 2026-05-22 persistent requirements and community-data handling rules.

### Pilot Benchmark Specification Drafted

Created the first executable pilot benchmark specification files:

- `deviation-bench/prompts/scenario_schema.yaml`
  - Defines the pilot scenario schema, allowed values, stance scores, model output contract, judge output contract, metrics, exclusions, and quality checks.

- `deviation-bench/prompts/judge_rubric.md`
  - Defines turn-level LLM-as-judge labels for stance, drift events, unjustified reversal, certainty inflation, confabulatory elaboration, recovery success, and safety flags.

- `deviation-bench/prompts/pilot_scenarios.yaml`
  - Contains 20 fictional, low-risk pilot scenarios.
  - Covers self-referential pattern claims, ambiguous technical signals, commitment erosion, emotional validation pressure, social consensus smuggling, and recovery/re-anchoring.
  - YAML parse check passed with `scenario_count=20`.

- `deviation-bench/annotations/标注规范草案.md`
  - Defines human annotation goals, turn-level labeling rules, stance labels, auxiliary labels, safety flags, boundary cases, audit sampling, and quality thresholds.

Updated:

- `AGENTS.md`
  - Added the persistent workflow rule requested by the user: after each stage-level result, update memory bank and commit the work to git.

- `研究导航.md`
  - Added prompt/spec and annotation directories.

### Minimal API-Only Runner Implemented

Created:

- `deviation-bench/src/deviation_bench_pilot.py`
  - Loads and validates `pilot_scenarios.yaml`.
  - Runs baseline, induction, and recovery turns.
  - Supports `mock` provider for offline smoke tests.
  - Supports OpenAI-compatible chat completions via `provider=openai`.
  - Supports separate target model and judge model.
  - Produces JSONL records with turn-level outputs, judge labels, and scenario metrics.

- `deviation-bench/src/README.md`
  - Documents validation, mock smoke test, and OpenAI-compatible invocation.

- `deviation-bench/requirements.txt`
  - Adds `PyYAML>=6.0`.

Validation completed:

- `python3 deviation-bench/src/deviation_bench_pilot.py --validate-only`
  - Loaded 20 scenarios.
  - Validation passed.

- `python3 -m py_compile deviation-bench/src/deviation_bench_pilot.py`
  - Compile check passed.

- Mock smoke test:
  - Command: `python3 deviation-bench/src/deviation_bench_pilot.py --provider mock --judge-provider mock --limit 1 --out deviation-bench/results/pilot/mock_smoke.jsonl`
  - Completed successfully for `uird_pilot_001`.
  - Generated turn-level mock outputs, judge labels, and metrics.
  - `deviation-bench/results/` remains git-ignored as generated experiment output.

### Planning Deliverables Added 2026-05-22 (afternoon)

Three new planning / decision documents written, no code or data changes:

- `deviation-bench/数据现状评估与下一步方案.md`
  - 评估 pilot 数据与原始数据是否满足"可执行优化版"定义的 pilot/v1 要求。
  - 结论：够开始 real-API smoke + 最小 pilot evidence-of-existence；不够支撑完整 pilot 或 v1 paper。
  - §6.5 增补"真实数据 + LLM 合成"专项评估，给出 Bloom-style 四阶段合成 pipeline。

- `deviation-bench/目标收缩-工作流深思考.md`
  - 显式以 `idea-evaluator` + `benchmark-paper-template` + `vibe-research-workflow` 三个 skill 为脚手架，对"重打包真实数据 + 收缩目标"提议做系统评估。
  - 给出三套候选 framing（A: cross-corpus context-retest；B: 真实语料上的 LLM 响应质量；C: A 主榜 + 合成 UIRD 子轨）。
  - 每个 framing 走完 fatal-flaws / 5 维评分 / paradigm probe / feasibility / 5 pillars。
  - §6 列出 5 个与 framing 选择无关、可立刻开始的动作。
  - §7 列出 6 个用户必须自己回答的开放决策点。

- `AGENTS.md` 工作流规则强化（2026-05-22 afternoon）
  - 把"每完成一个完整任务后更新 memory-bank + 单独 commit"从建议升级为硬性规则。
  - 显式定义"完整任务"边界与 per-task closing checklist。

### Table 1 Benchmark Comparison Draft

Created:

- `deviation-bench/paper/table1_benchmark_comparison.md`
  - Drafts the paper-ready benchmark comparison table requested in `目标收缩-工作流深思考.md` §6.
  - Compares weval `ai-psychosis.yml`, `ai-spiral-safety.yml`, Stanford HAI mental-health safety eval, ELEPHANT, `sycophancy-probe.yml`, `hallucination-probe.yml`, `mental-health.yml`, and the proposed Deviation Bench.
  - Records task scope, source type, local item scale, multi-source status, context-retest coverage, multi-turn coverage, recovery metric coverage, real-corpus anchoring, language, and the limitation relative to Deviation Bench.
  - Distills the main differentiation claim: Deviation Bench should be positioned as context-retest reliability for reality-boundary judgments, not as another generic mental-health safety benchmark.

### Next-Step Memory File Added

Created:

- `memory-bank/next-step.md`
  - Defines the actionable handoff queue for future agents.
  - Records the framing questions that still require user confirmation.
  - Details the framing-independent work queue: seed pattern bank, utterance schema, real API smoke test, and Section 2 task/design-goals draft.
  - Adds A/B/C framing-specific roadmaps, data safety rules, completion rules, and the recommended starting procedure for future agents.

Updated:

- `AGENTS.md`
  - Future agents must now read and maintain all three memory-bank files first: `overall-progress.md`, `overall-plan.md`, and `next-step.md`.
  - The per-task completion rule now includes `next-step.md` whenever blockers, user decisions, or recommended next work changes.

- `memory-bank/overall-plan.md`
  - Added `next-step.md` as a Milestone 1 memory deliverable and linked it as the detailed handoff queue.

- `研究导航.md`
  - Added a Future Agent priority-reading section that points first to `AGENTS.md` and the three memory-bank files.

## Current Open Items

- 等待用户回答 `目标收缩-工作流深思考.md` §7 的 6 个开放问题（framing / venue / companion / language / 原文使用阈值 / deadline）。
- Verify the pushed data on GitHub if needed.
- Decide exact model list and API provider configuration for pilot runs.
- Run a real API smoke test once API credentials/model choice are available.
- Review whether the pilot runner should support additional providers beyond OpenAI-compatible chat completions.
- Continue populating implementation/output directories:
  - `deviation-bench/results/`
  - `deviation-bench/paper/`

## Current Best Next Step

优先级 1：等用户对 framing 做出选择，否则后续 pipeline 走向不定。

与 framing 无关、可并行的立即动作（来自 `目标收缩-工作流深思考.md` §6）：

1. 已完成：写 Table 1 Benchmark Comparison Table 草稿，比较 weval / Stanford HAI / ELEPHANT 等 prior，给后续 introduction 的 F1 差异化用。
2. 建议下一步：从 DAIS-C clinical speaker-only + Reddit r/schizophrenia subset 抽 50-80 条 abstracted pattern，落到 `data_sources/patterns/seed_pattern_bank.jsonl`。
3. 写统一 utterance schema 草稿 `prompts/utterance_schema.yaml`。
4. 跑 real-API smoke test（1 target + 1 judge × 1-2 scenario），验证 JSON contract 与 judge 稳定性。
5. 写 Section 2 §Task and Design Goals 草稿（覆盖 G1-G4）。

详细行动队列见 `memory-bank/next-step.md`。
