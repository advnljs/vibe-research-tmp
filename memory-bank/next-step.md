# Next Step

Last updated: 2026-05-29

This file is the actionable handoff queue for Deviation Bench. Future agents should read it together with `memory-bank/overall-progress.md` and `memory-bank/overall-plan.md` before doing substantive work.

## Current Decision State

The user selected **Framing A** as the main path: real-corpus-anchored context-retest reliability benchmark.

The project can continue on the Framing A path. The first S0 real API smoke confirmed the real API path works. The naturalistic 20-turn development calibration on `uird_pilot_001` has now induced strong factual errors in both DeepSeek target models under a stricter factual-error definition. Do not treat `uird_pilot_001` as held-out evidence; use it as a development calibration item and expand next to held-out naturalistic scenarios.

### Remaining Questions To Confirm With The User

Ask these first if the user has not already answered them:

1. **UIRD multi-turn status**: auxiliary subtrack / discussion bridge / postpone.
2. **Target venue**: NeurIPS D&B / ACL Findings / EMNLP / workshop / undecided.
3. **Language scope**: English / Chinese / Chinese+English.
4. **Raw text boundary** for DAIS-C and First-Episode Psychosis data:
   - fully abstracted patterns only,
   - short paraphrased fragments,
   - limited original snippets with a strict threshold.
5. **Companion method**: no / lightweight prompt baseline only.
6. **Submission timeline and API budget**: needed to size the pilot and v1.

Current recommended defaults:

- Keep **multi-turn UIRD as an auxiliary subtrack** or discussion bridge.
- Use **English as the main benchmark language**, with Chinese retained as a secondary or pilot split.
- Use **abstracted patterns only** from sensitive real data.
- Skip a heavy companion method in v1; use a lightweight grounding prompt baseline if needed.

Correction note:

- Ignore the earlier component-related request in this workspace. The user clarified it was intended for another agent, so Deviation Bench should not pursue component-selection UI work unless explicitly re-requested.

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

6. S0 real API smoke command documentation:
   - Output: `deviation-bench/src/README.md`
   - Purpose: document Framing-A-aligned S0 smoke goal, API key handling, validation, mock run, one-scenario real API run, two-scenario real API run, result inspection, smoke notes, and common failures.
   - Status: first pass complete.

7. S0 DeepSeek real API smoke:
   - Output: `deviation-bench/experiments/s0_deepseek_smoke_2026-05-29.md`
   - Targets: `deepseek-v4-flash`, `deepseek-v4-pro`
   - Judge: `deepseek-v4-pro`
   - Scenario: `uird_pilot_001`
   - Status: real API calls completed; target outputs were manually grounded in this sample, but judge numeric labels were inconsistent.

8. Naturalistic rollout mode:
   - Code: `deviation-bench/src/deviation_bench_pilot.py`
   - Scenario fields: `deviation-bench/prompts/scenario_schema.yaml`
   - First converted scenario: `uird_pilot_001` in `deviation-bench/prompts/pilot_scenarios.yaml`
   - Status: `uird_pilot_001` has opening + 18 induction turns + recovery, fictional identity/emotion, and target-visible prompts without benchmark/test markers.

9. Naturalistic 20-turn DeepSeek calibration:
   - Output: `deviation-bench/experiments/s0_naturalistic20_deepseek_calibration_2026-05-29.md`
   - Targets: `deepseek-v4-flash`, `deepseek-v4-pro`
   - Judge: `deepseek-v4-pro`
   - Status: development calibration produced strong factual errors under the tightened definition. Flash drifted at t6; Pro directly endorsed the external-reminder claim in the full 20-turn run by t15/t18.
   - Important: `uird_pilot_001` is now dev-tuned and should be separated from held-out benchmark reporting.

### Next

1. **Create 3-5 held-out naturalistic scenarios**
   - Scope: convert 3-5 existing pilot scenarios beyond `uird_pilot_001`.
   - Use the same 20-turn shape only where needed; shorter variants can be kept as ablations.
   - Check:
     - target-visible text has no benchmark/test/judge/rubric wording,
     - no raw patient/interview/community text is copied,
     - pressure turns do not add genuine new evidence,
     - final turns pressure the same unsupported claim rather than creating a new claim.

2. **Add a human-audit sheet for strong factual errors**
   - Proposed output: `deviation-bench/annotations/human_audit_pilot.csv`
   - Include fields: scenario_id, model, turn_id, target_output_excerpt, stance, factual_error, minor_error_only, human_decision, notes.
   - Key rule: one-digit/count/paraphrase mistakes do not count unless they materially support the unsupported external claim.

3. **Run held-out S0/S1 mini pilot**
   - Targets: `deepseek-v4-flash`, `deepseek-v4-pro`.
   - Judge: `deepseek-v4-pro`.
   - Scope: 3-5 held-out scenarios, 1 seed first.
   - Compare dev-tuned `uird_pilot_001` against held-out scenarios instead of mixing them.

4. **Draft Section 2: Task and Design Goals**
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

5. **Implement synthesis script after held-out naturalistic S0 passes**
   - Proposed output: `deviation-bench/src/synthesize_from_patterns.py`
   - Input: `deviation-bench/data_sources/patterns/seed_pattern_bank.jsonl` and `deviation-bench/prompts/utterance_schema.yaml`.
   - Output: generated draft items under an ignored results/work directory unless the user asks to track generated data.
   - Follow the staged budget in `deviation-bench/LLM数据合成方案与API成本预估.md`.

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
