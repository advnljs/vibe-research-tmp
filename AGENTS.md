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

Navigation:

- `研究导航.md`

Data root:

- `deviation-bench/data_sources/`

## Data Handling Rules

- Distinguish real clinical/interview data from synthetic or evaluation-config data.
- Do not represent Bloom or Weval configs as real clinical data.
- Do not publicly redistribute sensitive raw interview text unless the license and consent terms clearly allow it.
- Keep `deviation-bench/data_sources/downloaded/` out of git by default because it contains raw downloaded datasets, extracted transcripts, archives, and cloned third-party repositories.
- Prefer using real datasets to derive abstract scenario patterns and rubrics, not copying sensitive transcript content directly into benchmark prompts.
- Track source URL, license/access status, citation, local path, and intended use for each dataset.

Current downloaded sources:

- DAIS-C: `deviation-bench/data_sources/downloaded/dais_c/`
- First-episode psychosis friendship transcripts: `deviation-bench/data_sources/downloaded/first_episode_psychosis_friendship/`
- Bloom main repo: `deviation-bench/data_sources/downloaded/bloom/`
- Bloom experiments branch: `deviation-bench/data_sources/downloaded/bloom_experiments_branch/`
- Weval configs: `deviation-bench/data_sources/downloaded/weval_configs/`

Restricted or application-based sources to track:

- PsychosisBank DISCOURSE-UWO
- PsychosisBank Tang Corpus
- AVATAR Therapy Dialogue Corpus
- DAIC-WOZ
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

As of 2026-05-21:

- Research framing is drafted.
- Data/source collection has started.
- Workspace navigation exists.
- Memory bank exists.
- Local git repository exists on branch `main`.
- Remote `origin` is `git@github.com:advnljs/vibe-research-tmp.git`.
- No formal experiment runner exists yet.
- No pilot benchmark results exist yet.

Recommended next work:

1. Create `deviation-bench/data_sources/下载清单与访问状态.md`.
2. Create `deviation-bench/data_sources/restricted_or_apply/申请清单.md`.
3. Draft pilot scenario schema, prompt families, recovery turns, judge rubric, and metric calculator design.
4. Only then implement an API-only pilot runner.

## Git Repository

Target remote:

- `git@github.com:advnljs/vibe-research-tmp.git`

Current branch:

- `main`

Repository policy:

- Commit research docs, memory bank, navigation, installed skill instructions, and planning files.
- Do not commit raw downloaded clinical/interview data or extracted transcript directories unless the user explicitly requests it and license/consent constraints are checked first.
