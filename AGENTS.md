# AGENTS.md

This workspace is for the Deviation Bench research project. Future agents should follow this file in addition to system/developer instructions.

## Language and Communication

- The user primarily works in Chinese. Use Chinese for research notes and user-facing summaries unless there is a clear reason to use English.
- Keep explanations concrete and implementation-oriented.
- Prefer updating local project files over only giving advice when the user asks to progress the project.

## Required Project Memory

Maintain these files continuously:

- `memory-bank/overall-progress.md`
  - Update after meaningful completed work.
  - Record what changed, what was downloaded/created, and what remains open.

- `memory-bank/overall-plan.md`
  - Update when the plan, milestone status, or current implementation position changes.
  - Keep the current phase and immediate next actions accurate.

- `研究导航.md`
  - Update when directories, important files, datasets, or installed skills change.

- `AGENTS.md`
  - Update when the user adds persistent requirements or constraints.

After every meaningful stage result:

- Update `memory-bank/overall-progress.md`.
- Update `memory-bank/overall-plan.md` if the plan, current phase, or next action changed.
- Commit the completed stage to git.
- Push to the configured remote when the user has requested remote synchronization for the workspace.

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

As of 2026-05-22:

- Research framing is drafted.
- Data/source collection has expanded through the `todo20260521.txt` continuation.
- Workspace navigation exists.
- Memory bank exists.
- Local git repository exists on branch `main`.
- Remote `origin` is `git@github.com:advnljs/vibe-research-tmp.git`.
- Minimal experiment runner exists.
- No pilot benchmark results exist yet.
- Data manifest and data-use notes exist for the current data wave.
- Pilot scenario schema, judge rubric, 20 low-risk fictional scenarios, and annotation draft exist.
- Minimal API-only runner exists at `deviation-bench/src/deviation_bench_pilot.py`.
- Result summarizer exists at `deviation-bench/src/summarize_pilot_results.py`.
- Offline mock validation/smoke test has passed; no real API pilot has been run yet.
- Full 20-scenario mock run and summary generation have passed.

Recommended next work:

1. Select the first target model and judge model.
2. Run a real API smoke test on 1-2 scenarios.
3. Summarize the real smoke output.
4. Inspect JSON validity, judge labels, and metrics.
5. Adjust prompt contract or judge rubric if needed.
6. Run the 20-scenario pilot over 2-3 models.

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
