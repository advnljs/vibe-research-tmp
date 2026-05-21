# Overall Plan

Last updated: 2026-05-21

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

Phase: concept lock + data/source preparation.

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

Current implementation position:

- No formal experiment code yet.
- No final prompt schema yet.
- No pilot result yet.
- Data sources are present, but data manifest and use-policy notes are not yet formalized.

## Milestone Plan

### Milestone 1: Project Memory and Data Hygiene

Status: in progress.

Deliverables:

- `研究导航.md`
- `memory-bank/overall-progress.md`
- `memory-bank/overall-plan.md`
- `AGENTS.md`
- `.gitignore`
- Git remote `origin/main`
- `deviation-bench/data_sources/下载清单与访问状态.md`
- `deviation-bench/data_sources/restricted_or_apply/申请清单.md`
- `deviation-bench/data_sources/notes/数据许可与引用.md`

Exit condition:

- Any future agent can understand what exists, what is real data, what is synthetic/reference config, and what access restrictions apply.

### Milestone 2: Pilot Benchmark Specification

Status: not started.

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

### Milestone 3: Pilot Runner

Status: not started.

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

### Milestone 4: Validate Signal

Status: not started.

Deliverables:

- Model comparison table.
- Repetition variance analysis.
- Human spot-check of judge labels.
- Failure-case taxonomy.

Exit condition:

- The benchmark shows measurable differences between models or conditions, without relying on high-risk prompts.

### Milestone 5: Paper Skeleton

Status: not started.

Deliverables:

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

1. Write a downloaded-data manifest with URLs, checksums where known, counts, license notes, and recommended use.
2. Write the restricted/access application list.
3. Draft pilot prompt schema and judge rubric.
4. Create a small set of fictional scenarios inspired by real-data patterns but not copied from sensitive transcripts.
5. Implement a minimal API-only runner after the spec is stable.

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
