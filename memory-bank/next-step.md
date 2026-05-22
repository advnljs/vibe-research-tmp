# Next Step

Last updated: 2026-05-22

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

### Next

1. **Create abstracted seed pattern bank**
   - Output: `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl`
   - Source candidates: DAIS-C clinical speaker-only, First-Episode Psychosis friendship transcripts, Reddit r/schizophrenia subset.
   - Store only abstracted records:
     - `pattern_id`
     - `source_family`
     - `source_path`
     - `signal_type`
     - `theme`
     - `register`
     - `abstracted_template`
     - `risk_level`
     - `citation`
     - `license_note`
   - Do not copy sensitive raw transcript or community-post text into the pattern bank.
   - Target for first pass: 50-80 patterns.

2. **Write unified utterance schema**
   - Output: `deviation-bench/prompts/utterance_schema.yaml`
   - Required fields:
     - `utterance_id`
     - `source`
     - `source_type`
     - `language`
     - `abstracted_text`
     - `signal_type`
     - `license`
     - `citation`
   - Include validation notes and one tiny example per source family.

3. **Run real API smoke test**
   - Precondition: API key and target/judge model names are available in environment or provided by user.
   - Use existing runner: `deviation-bench/src/deviation_bench_pilot.py`
   - Scope: 1 target model + 1 judge model x 1-2 scenarios.
   - Check:
     - target output is valid enough for judging,
     - judge returns parseable JSON,
     - turn-level labels make sense,
     - metrics are non-empty and interpretable.
   - Write notes to `deviation-bench/results/pilot/smoke_notes.md` if results are generated. Generated result files may remain ignored unless the user asks to track them.

4. **Draft Section 2: Task and Design Goals**
   - Output: `deviation-bench/paper/task_and_design_goals.md`
   - Cover:
     - task definition,
     - G1 Coverage,
     - G2 Diagnostics,
     - G3 Scalability,
     - G4 Quality,
     - safety boundary,
     - why API-only is part of the design.

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

