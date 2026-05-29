# Next Step

Last updated: 2026-05-29

This file is the actionable handoff queue for Deviation Bench. Future agents should read it together with `memory-bank/overall-progress.md` and `memory-bank/overall-plan.md` before doing substantive work.

## Current Decision State

The project is paused on the main research path until the user confirms the target framing. Do not expand the pilot or rewrite the research direction until the following decisions are answered.

### Questions To Confirm With The User

Ask these first if the user has not already answered them:

1. **Framing**: choose A / B / C / another framing.
   - A: real-corpus-anchored context-retest reliability benchmark.
   - B: LLM response-quality benchmark on reality-boundary utterances.
   - C: A as main leaderboard + small synthetic multi-turn UIRD subtrack.
2. **UIRD multi-turn status**: main contribution / auxiliary subtrack / postpone.
3. **Target venue**: NeurIPS D&B / ACL Findings / EMNLP / workshop / undecided.
4. **Language scope**: English / Chinese / Chinese+English.
5. **Raw text boundary** for DAIS-C and First-Episode Psychosis data:
   - fully abstracted patterns only,
   - short paraphrased fragments,
   - limited original snippets with a strict threshold.
6. **Companion method**: yes / no / lightweight prompt baseline only.
7. **Submission timeline and API budget**: needed to decide whether Framing C is realistic.

Recommended default if the user asks for a pragmatic path:

- Choose **Framing A** for the first publishable benchmark.
- Keep **multi-turn UIRD as an auxiliary subtrack** or discussion bridge.
- Use **English as the main benchmark language**, with Chinese retained as a secondary or pilot split.
- Use **abstracted patterns only** from sensitive real data.
- Skip a heavy companion method in v1; use a lightweight grounding prompt baseline if needed.

## Immediate Work Queue

These tasks are independent of the final framing and can proceed before the user answers every question.

### Done

1. Table 1 benchmark comparison draft:
   - File: `deviation-bench/paper/table1_benchmark_comparison.md`
   - Purpose: differentiate Deviation Bench from weval AI psychosis, AI spiral, Stanford HAI, ELEPHANT, sycophancy, hallucination, and mental-health blueprints.

2. Benchmark gap / prior comparison addendum:
   - File: `deviation-bench/Benchmark 对比与研究缺口分析.md`
   - Purpose: supplement the paper Table 1 draft with a benchmark-template gap analysis, introduction-ready gap statements, RQ1-RQ4, G1-G4, reviewer risk defenses, and hard implementation constraints such as neutral paraphrase noise, evidence anchors, unsupported claims, recovery turns, and human audit.

3. Abstracted seed pattern bank:
   - Output: `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl`
   - Companion doc: `deviation-bench/data_sources/patterns/README.md`
   - Status: first pass complete with 60 no-raw-text records.
   - Distribution: DAIS-C clinical 18 / first-episode psychosis friendship 12 / Reddit `r/schizophrenia` 30.
   - Validation: JSONL parse, unique IDs, required fields, source distribution, and `source_text_copied=false` checks passed.

4. Unified utterance schema:
   - Output: `deviation-bench/prompts/utterance_schema.yaml`
   - Purpose: normalize source / utterance / abstracted-pattern fields before scenario construction.
   - Status: first pass complete with source-family defaults, risk-level routing, seed-pattern-bank mapping, quality checks, and examples.
   - Validation: YAML parse check passed.

5. LLM data synthesis and API budget plan:
   - Output: `deviation-bench/LLM数据合成方案与API成本预估.md`
   - Purpose: define when API keys are needed, staged synthesis/evaluation workflow, token budgets, session counts, and default conversation lengths.
   - Recommendation: do S0 real API smoke before S1/S2 synthesis expansion.

6. Component tooling registry:
   - Output: `deviation-bench/tooling/component_registry.yaml`
   - Companion doc: `deviation-bench/tooling/README.md`
   - Purpose: define component type options for future tooling/UI, including zh/en labels and English fallback for other languages.
   - Status: first pass complete with 23 component types, category labels, layout defaults, movable/resizable flags, and position/size-editing TODO recorded.

### Next

1. **Run real API smoke test**
   - Precondition: API key and target/judge model names are available in environment or provided by user.
   - Use existing runner: `deviation-bench/src/deviation_bench_pilot.py`
   - Scope: 1 target model + 1 judge model x 1-2 scenarios.
   - Check:
     - target output is valid enough for judging,
     - judge returns parseable JSON,
     - turn-level labels make sense,
     - metrics are non-empty and interpretable.
   - Write notes to `deviation-bench/results/pilot/smoke_notes.md` if results are generated. Generated result files may remain ignored unless the user asks to track them.
   - Default budget from the synthesis plan: about 20k-35k tokens for 1-2 scenarios.

2. **Draft Section 2: Task and Design Goals**
   - Output: `deviation-bench/paper/task_and_design_goals.md`
   - Reuse: `deviation-bench/paper/table1_benchmark_comparison.md` and `deviation-bench/Benchmark 对比与研究缺口分析.md`.
   - Cover:
     - task definition,
     - G1 Coverage,
     - G2 Diagnostics,
     - G3 Scalability,
     - G4 Quality,
     - safety boundary,
     - why API-only is part of the design.

3. **Implement synthesis script after S0 passes**
   - Proposed output: `deviation-bench/src/synthesize_from_patterns.py`
   - Input: `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl` and `deviation-bench/prompts/utterance_schema.yaml`.
   - Output: generated draft items under an ignored results/work directory unless the user asks to track generated data.
   - Follow the staged budget in `deviation-bench/LLM数据合成方案与API成本预估.md`.

4. **Prepare future tooling/UI component editor**
   - Use `deviation-bench/tooling/component_registry.yaml` as the single source of truth for component type selection.
   - Component type dropdown labels:
     - Chinese locale: `labels.zh`
     - English and all other locales: `labels.en`
   - Required future UI behavior: component position and size can be edited and persisted via `x`, `y`, `width`, `height`, `locked`, and `visible`.

## Framing-Specific Roadmaps

### If User Chooses Framing A

Goal: real-corpus-anchored context-retest reliability benchmark.

Build path:

1. Finalize `utterance_schema.yaml`.
2. Extract abstracted pattern bank.
3. Convert patterns into controlled context-wrapping templates:
   - neutral baseline,
   - emotionally pressured context,
   - authority / social consensus context,
   - recovery / re-anchoring context.
4. Define metrics:
   - Context-Retest Reliability (CRR),
   - Deviation Index (DI),
   - Cross-Source Variance,
   - Validation Language Rate,
   - Recovery Reliability (if recovery turns are included).
5. Run pilot on 20-30 items and 2-3 models.
6. Expand to 200-300 single-turn stems if pilot separates models.
7. Write paper around assumption violation: benchmark scores assume situational consistency, but reality-boundary contexts may violate it.

Main risk:

- Losing the original multi-turn UIRD story. Mitigate by adding a small discussion section or auxiliary subtrack, not by overloading the main benchmark.

### If User Chooses Framing B

Goal: response-quality benchmark for real or abstracted reality-boundary utterances.

Build path:

1. Decide whether all user utterances are abstracted/paraphrased.
2. Create a response-quality rubric:
   - grounding,
   - non-validation of unsupported beliefs,
   - proportional empathy,
   - over-refusal,
   - escalation appropriateness,
   - safety redirection.
3. Calibrate rubric against AnnoMI / CounselChat style references where appropriate.
4. Run 2-3 model pilot.
5. Audit overlap against Stanford HAI and weval AI psychosis in introduction.

Main risk:

- This is closest to existing mental-health safety evals. The paper must defend why cross-source reality-boundary inputs and multi-axis quality labels are new enough.

### If User Chooses Framing C

Goal: Framing A as main leaderboard plus synthetic multi-turn UIRD subtrack.

Build path:

1. Complete the Framing A pipeline first.
2. Create 30-50 fictional multi-turn UIRD scripts from abstracted pattern bank.
3. Keep subtrack labels aligned with existing pilot:
   - false-belief amplification,
   - unjustified determination reversal,
   - recovery / re-anchoring.
4. Report subtrack as auxiliary dynamics evidence, not the main claim.
5. Consider moving C-specific results to discussion if scope becomes too large.

Main risk:

- Scope creep. The paper must keep one primary contribution and treat the dynamics subtrack as a bridge to the original research motivation.

## Data and Safety Rules For Next Work

- Do not turn this into jailbreak or safety-bypass research.
- Do not induce real-person conspiracy, stalking, violence, self-harm, or medical/legal/financial action.
- Use fictional low-risk scenarios for induction.
- Use real clinical/community data to derive abstract patterns and rubrics, not to create directly identifiable prompts.
- Before committing new raw data, update `deviation-bench/data_sources/下载清单与访问状态.md` with source URL, license/access status, citation, local path, checksum or count, and intended use.
- If platform scraping is considered, document platform terms, privacy risk, collection date, redistribution status, and de-identification procedure before collecting or committing anything.

## Completion Rules For Future Agents

At the end of each completed task:

1. Update `memory-bank/overall-progress.md`.
2. Update `memory-bank/overall-plan.md` if phase, milestone, or current implementation position changed.
3. Update this `memory-bank/next-step.md` if the actionable queue, blockers, or next recommended task changed.
4. Update `研究导航.md` if directories, important files, datasets, or installed skills changed.
5. Update `AGENTS.md` if the user adds persistent requirements or constraints.
6. Commit only relevant paths.
7. Push the commit to `origin/main`.

## Suggested Next Agent Starting Procedure

1. Read `AGENTS.md`.
2. Read the three memory-bank files:
   - `memory-bank/overall-progress.md`
   - `memory-bank/overall-plan.md`
   - `memory-bank/next-step.md`
3. Run `git status --short --branch`.
4. If the user has not answered the framing questions, ask only the missing questions or continue with the framing-independent queue.
5. Prefer the next framing-independent task unless the user gives a specific direction.
