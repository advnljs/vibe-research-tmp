# AGENTS.md

This workspace is for the Deviation Bench research project. Future agents should follow this file in addition to system/developer instructions.

## Language and Communication

- The user primarily works in Chinese. Use Chinese for research notes and user-facing summaries unless there is a clear reason to use English.
- Keep explanations concrete and implementation-oriented.
- Prefer updating local project files over only giving advice when the user asks to progress the project.

## Required Project Memory

Future agents must rely on and maintain the three memory-bank files as the first source of project state. Before starting substantive work, read:

- `memory-bank/overall-progress.md`
- `memory-bank/overall-plan.md`
- `memory-bank/next-step.md`

Maintain these files continuously:

- `memory-bank/overall-progress.md`
  - Update after meaningful completed work.
  - Record what changed, what was downloaded/created, and what remains open.

- `memory-bank/overall-plan.md`
  - Update when the plan, milestone status, or current implementation position changes.
  - Keep the current phase and immediate next actions accurate.

- `memory-bank/next-step.md`
  - Update when the actionable queue, blockers, user decisions, or recommended next task changes.
  - Keep the immediate next work and later roadmap explicit enough for the next agent to continue without reconstructing state from scattered documents.

- `研究导航.md`
  - Update when directories, important files, datasets, or installed skills change.

- `AGENTS.md`
  - Update when the user adds persistent requirements or constraints.

After every completed task (the user-confirmed definition is below):

- Update `memory-bank/overall-progress.md`.
- Update `memory-bank/overall-plan.md` if the plan, current phase, or next action changed.
- Update `memory-bank/next-step.md` if the actionable queue, blockers, user decisions, or recommended next task changed.
- Update `研究导航.md` if directories, important files, datasets, or installed skills changed.
- Update `AGENTS.md` if the user added persistent requirements or constraints in the task.
- Commit the completed task to git in a single, focused commit.
- Push the commit to the configured remote `origin/main`.

This is a hard workflow rule, not a recommendation. In this workspace, every completed task must end with memory-bank updates, a focused git commit, and a remote push. Skipping memory-bank updates, skipping the commit, or leaving committed work unpushed leaves the workspace inconsistent for the next session.

### What counts as "a completed task"

A completed task is any unit of work that produces a durable artifact and reaches a stopping point. Examples:

- A new research document or section finalized (e.g., a new analysis file, a paper draft, an evaluation summary).
- A scoped code change merged into the working tree (e.g., a runner update, a new pipeline, a bug fix that compiles and runs).
- A finished data acquisition, conversion, or manifest update.
- A finished planning or decision deliverable (e.g., a target-narrowing decision doc, a roadmap update).

Pure exploration with no artifact does not require a commit. Multiple closely related artifacts produced in one user turn may be bundled into a single commit, but the memory-bank update is still mandatory.

### Per-task closing checklist

Run this checklist explicitly before declaring the task done in the chat:

1. Identify the produced artifact(s).
2. Apply the three memory-bank updates plus navigation / AGENTS updates as applicable.
3. `git add` only the relevant paths (no `-A` / no `.`).
4. `git commit` with a message that names the task outcome.
5. Push to `origin/main` before reporting the task as complete.
6. Surface the commit hash in the chat reply so the user can audit.

## Current Research Focus

Deviation Bench is currently focused on User-Induced Reality Drift:

- Multi-turn user interaction may push an LLM from grounded, evidence-constrained responses toward unsupported delusional elaboration, inappropriate validation, unjustified reversal of earlier determinations, or action-oriented escalation.
- The benchmark should measure whether models maintain reality-grounded judgment under context shifts and user pressure.
- The broader motivation is to challenge the situational consistency assumption in AI evaluation.
- The intended analogy is context-retest reliability / situation-retest reliability, similar to test-retest reliability in psychology.

## User Requirements From 2026-05-21

The user requested all of the following:

- Install skills from `https://github.com/HKUSTDial/Supervisor-Skills` into this workspace.
- Use the installed skills to evaluate the Deviation Bench idea.
- Optimize the idea until it becomes feasible.
- Preserve the original research motivation.
- Keep the approach low GPU and LLM API-only.
- First define and quantify the observed phenomenon clearly.
- The motivating phenomenon is that LLMs can be gradually induced by user messages into delusion-like, reality-detached outputs, or into reversing earlier grounded determinations; stronger models such as GPT-5 appear to reduce this.
- Use clever controlled designs to induce reality-grounding failure for measurement.
- Do not turn this into jailbreak/safety-bypass work.
- Find Bloom-like data generation approaches.
- Find and download real psychology / psychiatry data where legally available.
- The real data requested means dialogue or interview data, mainly related to delusion / psychosis.
- Create a navigation file describing each relevant directory and, where needed, important files.
- Create and maintain `memory-bank/overall-progress.md`.
- Create and maintain `memory-bank/overall-plan.md`.
- Update this `AGENTS.md` with all of today’s persistent requirements.
- Create a local git repository and push it to `git@github.com:advnljs/vibe-research-tmp.git`.
- After the initial conservative push, the user requested that downloaded data also be pushed to the remote.

## User Requirements From 2026-05-22

The user asked to continue from `todo20260521.txt`, which means:

- Inspect `deviation-bench/Datasets for a Deviation Bench on Reality-Boundary Language.md`.
- Check whether relevant data listed there can be legally accessed and download what is appropriate.
- Think through the idea of obtaining delusion-related content from communities such as Zhihu or Reddit.
- Prefer existing public datasets and documented access routes before live scraping.
- Consider whether automated judges can detect delusion-like / reality-boundary language signals in collected text.
- Convert any real community/clinical signal only into abstracted, fictional, de-identified dialogue scenarios.
- Keep data/source navigation, progress, plan, and AGENTS updated.

Additional persistent workflow requirement:

- After each stage-level result, update the memory bank and commit the work to git.
- 2026-05-22 强化版：每完成一个完整任务（按上文 "What counts as a completed task" 的定义）必须立即更新 `memory-bank/overall-progress.md`（必要时也更新 `overall-plan.md`、`next-step.md`、`研究导航.md`、`AGENTS.md`），并以单独的、聚焦的 commit 提交。这是硬性规则，不是建议。跨任务批量补 commit 是不允许的。
- 2026-05-22 remote 强化版：每个完整任务完成后，必须把对应 commit push 到 `origin/main`。不能只本地 commit 后等待下一轮再推。
- 2026-05-22 memory-bank 三文件强化版：每个 agent 都要优先依赖并维护 `memory-bank/overall-progress.md`、`memory-bank/overall-plan.md`、`memory-bank/next-step.md`。其中 `next-step.md` 是后续行动队列和更长期路线图，任务完成后若下一步或阻塞状态变化必须更新。

## User Correction From 2026-05-29

- The component-related instruction about component type selection, bilingual labels, and editable component position/size was intended for another agent, not for this Deviation Bench workspace.
- Do not pursue component-selection UI/tooling work in this repository unless the user explicitly re-requests it for Deviation Bench.
- The mistakenly added component registry and tag should be removed from the active project state.

## User Decision From 2026-05-29

- Continue Deviation Bench based on **Framing A**: real-corpus-anchored context-retest reliability benchmark.
- Treat real clinical/community sources as anchors for abstracted patterns and controlled context-retest scenarios, not as raw prompt text.
- Keep the next implementation step focused on S0 real API smoke before S1 synthesis or v1 scale-up.
- For target-facing rollout, prefer naturalistic fictional user dialogue: include identity and emotional trajectory, increase multi-turn depth where needed, and avoid wording that reveals benchmark/test/judge/rubric framing to the target model.
- Naturalistic dialogue may be inspired by abstracted patient/interview/community language patterns, but must not copy real patient, participant, or community text.

## Installed Skills

Installed in the workspace root:

- `idea-evaluator/`
- `benchmark-paper-template/`
- `figure-designer/`
- `intro-drafter/`
- `pre-submission-reviewer/`
- `tech-paper-template/`
- `vibe-research-workflow/`

Use these when their purpose matches the task. In particular:

- Use `idea-evaluator` for research framing and feasibility checks.
- Use `benchmark-paper-template` for benchmark structure, task definition, metrics, and paper skeleton.
- Use `figure-designer` for benchmark figures.
- Use `intro-drafter` for paper introduction.
- Use `pre-submission-reviewer` after pilot results or paper draft.

## Important Local Files

Core research docs:

- `deviation-bench/Deviation Bench 现象定义与量化框架.md`
- `deviation-bench/Deviation Bench 可执行优化版.md`
- `deviation-bench/数据生成方式与心理精神病学数据源清单.md`
- `deviation-bench/Deviation Bench 相关研究深度综述.md`
- `deviation-bench/Datasets for a Deviation Bench on Reality-Boundary Language.md`

Navigation:

- `研究导航.md`

Project memory:

- `memory-bank/overall-progress.md`
- `memory-bank/overall-plan.md`
- `memory-bank/next-step.md`

Data root:

- `deviation-bench/data_sources/`
- `deviation-bench/data_sources/notes/社区语料获取与妄想相关性判定方案.md`
- `deviation-bench/data_sources/notes/数据许可与引用.md`
- `deviation-bench/data_sources/notes/真实语料到场景设计映射.md`

## Data Handling Rules

- Distinguish real clinical/interview data from synthetic or evaluation-config data.
- Do not represent Bloom or Weval configs as real clinical data.
- Do not publicly redistribute sensitive raw interview text unless the license and consent terms clearly allow it.
- `deviation-bench/data_sources/downloaded/` is now tracked at the user's request. Before adding any future raw dataset, verify and record access/license status in `deviation-bench/data_sources/下载清单与访问状态.md`.
- Prefer using real datasets to derive abstract scenario patterns and rubrics, not copying sensitive transcript content directly into benchmark prompts.
- Track source URL, license/access status, citation, local path, and intended use for each dataset.
- For community data such as Reddit or Zhihu, label text signals only. Do not diagnose posters or represent subreddit/community membership as clinical ground truth.
- Do not directly publish raw community posts as benchmark prompts. Derive abstract pressure patterns and rewrite them into fictional, de-identified scenarios.
- Prefer existing public datasets, official APIs, or documented access procedures over ad hoc scraping.
- If future scraping is considered, record platform terms, privacy risk, redistribution rights, collection date, and de-identification procedure before committing anything.

Current downloaded sources:

- DAIS-C: `deviation-bench/data_sources/downloaded/dais_c/`
- First-episode psychosis friendship transcripts: `deviation-bench/data_sources/downloaded/first_episode_psychosis_friendship/`
- Bloom main repo: `deviation-bench/data_sources/downloaded/bloom/`
- Bloom experiments branch: `deviation-bench/data_sources/downloaded/bloom_experiments_branch/`
- Weval configs: `deviation-bench/data_sources/downloaded/weval_configs/`
- AnnoMI: `deviation-bench/data_sources/downloaded/annomi/`
- MentalChat16K: `deviation-bench/data_sources/downloaded/mentalchat16k/`
- CounselChat: `deviation-bench/data_sources/downloaded/counselchat/`
- MDD-5k: `deviation-bench/data_sources/downloaded/mdd_5k/`
- Reddit Mental Health Dataset r/schizophrenia subset: `deviation-bench/data_sources/downloaded/reddit_mental_health_zenodo/`
- RedditMentalhealth sample: `deviation-bench/data_sources/downloaded/reddit_mentalhealth_sample/`
- PDCH public metadata only: `deviation-bench/data_sources/downloaded/pdch_metadata/`
- EATD-Corpus Git LFS pointer only: `deviation-bench/data_sources/downloaded/eatd_corpus_pointer/`

Restricted or application-based sources to track:

- PsychosisBank DISCOURSE-UWO
- PsychosisBank Tang Corpus
- AVATAR Therapy Dialogue Corpus
- DAIC-WOZ
- PDCH full ScienceDB dataset
- MODMA
- D4
- HOPE / MEMO
- Psych8k
- TalkBank control corpora such as DementiaBank, AphasiaBank, and FluencyBank
- SMHD and related non-dialogue social-media sources as lower priority

## Safety Boundary

Allowed:

- Controlled, fictional, low-risk induction patterns that test whether a model maintains uncertainty, evidence constraints, and correction ability.
- Measuring drift, unjustified reversal, confabulatory elaboration, and recovery.
- Evaluating whether a model appropriately refuses, redirects, or grounds claims.

Not allowed:

- Jailbreak prompts or instructions to bypass safety policies.
- Real-person conspiracy induction.
- Medical, legal, financial, self-harm, violence, stalking, or other real-world action escalation.
- Prompts designed to worsen a real user’s mental health state.

## Current Implementation Position

As of 2026-05-29:

- Research framing is drafted.
- User selected Framing A: real-corpus-anchored context-retest reliability benchmark.
- Data/source collection has expanded through the `todo20260521.txt` continuation.
- Workspace navigation exists.
- Memory bank exists with three required files: `overall-progress.md`, `overall-plan.md`, and `next-step.md`.
- Local git repository exists on branch `main`.
- Remote `origin` is `git@github.com:advnljs/vibe-research-tmp.git`.
- Minimal experiment runner exists.
- Data manifest and data-use notes exist for the current data wave.
- Pilot scenario schema, judge rubric, 20 low-risk fictional scenarios, and annotation draft exist.
- Minimal API-only runner exists at `deviation-bench/src/deviation_bench_pilot.py`.
- Offline mock validation/smoke test has passed.
- S0 real API smoke has been run on `uird_pilot_001`:
  - targets: `deepseek-v4-flash`, `deepseek-v4-pro`
  - judge: `deepseek-v4-pro`
  - tracked summary: `deviation-bench/experiments/s0_deepseek_smoke_2026-05-29.md`
- S0 finding: real API path works and target outputs stayed grounded in the quick read, but judge numeric labels were inconsistent with `judge_rubric.md`; raw metrics are not reliable until judge-output validation/normalization is implemented.
- Naturalistic rollout support now exists for `uird_pilot_001` with 8 target-facing turns and no benchmark/test framing in the target-visible prompt.

Recommended next work:

1. Read `memory-bank/next-step.md` for the current action queue and framing blockers.
2. Rerun S0 with `--prompt-style naturalistic` on `uird_pilot_001`.
3. Inspect normalized judge fields and validation flags before expanding to more scenarios or S1 synthesis.
4. Extend naturalistic dialogue fields to more pilot scenarios if S0 labels look stable.
5. Draft `deviation-bench/paper/task_and_design_goals.md` once the smoke path is stable.

## Git Repository

Target remote:

- `git@github.com:advnljs/vibe-research-tmp.git`

Current branch:

- `main`

Repository policy:

- Commit research docs, memory bank, navigation, installed skill instructions, and planning files.
- Downloaded data is now committed because the user explicitly requested it and currently tracked sources have open license/access notes recorded.
- For future raw clinical/interview data, check and record license/consent/access status before committing.
- If third-party examples contain fake or real-looking secrets, redact them before committing; GitHub push protection blocked Bloom sabotage examples until Stripe-like placeholder keys were replaced.
