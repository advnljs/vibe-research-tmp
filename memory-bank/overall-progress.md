# Overall Progress

Last updated: 2026-05-21

This file records completed work and the current state of the Deviation Bench project. Update it after any meaningful research, data, implementation, or planning change.

## Current Project State

Deviation Bench has been narrowed from a broad context-induced deviation idea into a more feasible, API-only benchmark direction:

- Working phenomenon: User-Induced Reality Drift (UIRD), also described as user-induced reality-grounding drift.
- Core observation: in multi-turn interaction, an LLM may move from grounded, evidence-constrained responses toward unsupported delusional elaboration, inappropriate validation, or unjustified reversal of an earlier determination.
- Intended contribution: measure context-retest / situation-retest reliability for LLMs, analogous to test-retest reliability in psychology.
- Compute constraint: low GPU / API-only. The benchmark should not depend on model training, activation extraction, or high-cost inference infrastructure.
- Safety boundary: induction designs should test reality-grounding failure in controlled, fictional, low-risk settings. They should not be jailbreaks, safety bypasses, or prompts that escalate real-world harm.

## Completed Today

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

At the user's request, the downloaded data directory is now tracked in git:

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

## Current Open Items

- Verify the pushed data on GitHub if needed.
- Create first pilot dataset spec: prompt families, scenario schema, induction scripts, recovery scripts, judge rubric, and metric calculation.
- Decide whether v1 benchmark uses only synthetic controlled scenarios, or a hybrid of synthetic scenarios plus real-data-inspired linguistic patterns.
- Start implementation directories:
  - `deviation-bench/src/`
  - `deviation-bench/prompts/`
  - `deviation-bench/annotations/`
  - `deviation-bench/results/`
  - `deviation-bench/paper/`

## Current Best Next Step

Build the pilot benchmark spec before writing code:

1. Define 20 to 30 fictional, low-risk seed scenarios.
2. For each scenario, create baseline, induction, and recovery turns.
3. Write the judge rubric using the stance labels already defined.
4. Run 2 to 3 models through API with multiple repetitions.
5. Calculate RDS, IS, RDER, URR, RR, and residual drift.
