# Specs

Last updated: 2026-06-29

This file records persistent user requirements and project constraints in compact form. The full source of truth remains `AGENTS.md` plus the three primary memory-bank files.

## Persistent User Requirements

- Use Chinese for user-facing summaries unless another language is requested.
- Preserve the original research motivation: challenge situational consistency assumptions in AI evaluation.
- Keep the project low-GPU and LLM API-only.
- Current primary workspace is `deviation-bench-new/`; first prepare all relevant existing real-data-derived synthetic datasets before returning to benchmark experiments.
- Represent each source case as one multi-turn OpenAI-style `messages` session.
- Use `deepseek-v4-pro` for formal transformation/extraction with a 64k (`65,536`) context budget; `deepseek-v4-flash` is allowed for smoke tests only.
- Extract delusion/reality-boundary points per case, but allow an empty list and do not infer points from diagnosis group or source community.
- Keep DAIS-C clinical, FEP, DAIS-C control, and Reddit community-fictionalized outputs distinguishable.
- Do not convert this into jailbreak or safety-bypass research.
- Use real clinical/community data only as anchors for abstracted patterns or fictional de-identified scenarios by default.
- Do not use human annotation as paper-facing benchmark evidence.
- Use LLM-only validation: primary judge, metajudge/second judge, judge variance, gold controls, and schema/rule checks.
- Historical paused paper hook: agent memory can be delusive.
- If resumed, compare full transcript context vs memory systems only within token ranges where full transcript still fits.
- If resumed, preserve the hypothesis that direct full transcript may be more reality-grounded than current memory systems in those token regimes.
- If resumed, verify mem0, Graphiti, and other external memory systems via official docs/source and pinned versions before paper claims.
- Historical memory-facing drafts use 30 target-visible turns and explicit mainline/facts/source-pattern metadata; do not extend them under the current queue.
- For `tmp-webgame-ui/`, use an industry Web game engine and verify the replica by reading and comparing real browser screenshots.
- Build the runtime UI from `tmp-webgame-ui/refer/`; `ui-proto.png` may only be used for offline comparison.
- Preserve paper/book depth with shadows and provide an interactive page-turn animation.
- Keep a pure Web frontend implementation that reuses the same generated assets and mirrors the Phaser version's appearance and operations.
- Keep the pure Web frontend's overall text and buttons readable at the reference viewport, and allow users to select left-page narrative text.

## Current Acceptance Criteria For Data Hardening

- Run an independent LLM second-pass/metajudge over candidate points and negative controls; report disagreement and uncertainty rather than calling the first-pass output gold. This was completed once with DeepSeek Pro on 2026-06-29; optional future work may add a second model for variance.
- Use `deviation-bench-new/data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl` and `deviation-bench-new/prompts/point_metajudge.md` as the current prepared input for candidate-point second-pass review.
- Audit near-duplicates and cross-split leakage before freezing splits. Actual DeepSeek Pro semantic duplicate/leakage review completed on 2026-06-29 and produced a reviewed split manifest.
- Current reviewed split/version manifest still depends on governance review before public release.
- Preserve per-session source/model/prompt/license/QC provenance and dataset hashes.
- Keep normalized source turns, API request/response and checkpoints under ignored `deviation-bench-new/data/work/`.
- Treat regex PII=0 as an automatic check, not a guarantee of anonymity.
- Keep local browser/manual reading as development/governance inspection, not paper-facing annotation.

## Previous Agent-Memory Acceptance Criteria (Paused)

- Memory runner changes must support mock/offline validation first.
- Revised memory-facing scenarios should keep no-new-evidence semantics and pass browser validation, runner conversion, mock rollout, and dashboard generation before use.
- Current scenario acceptance should verify `scenario_description`, `mainline`, `related_facts`, `real_data_anchor`, and `source_pattern_ids`.
- Each memory condition must record trace fields: backend/config, write policy, retrieval policy, context tokens, compression ratio, source turns, evidence relation, verification status, and distortion flags.
- Generated raw results remain under ignored `deviation-bench/results/`.
- Every completed durable task must update memory-bank, commit, and push to `origin/main`.

## Current Forbidden / Restricted Actions

- Do not add production dependencies without user confirmation.
- Do not commit secrets, `.env`, API keys, raw sensitive new data, local logs, or generated dashboards containing raw outputs.
- Do not publish normalized raw community posts or claim that Reddit-derived sessions are real dialogues.
- Do not call DAIS-C/FEP delusion-only corpora or treat `delusion_points` as clinical ground truth.
- Do not force push, rebase, reset hard, clean user files, or overwrite unrelated changes.
- Do not treat `uird_pilot_001`, `uird_pilot_002`, `uird_pilot_003`, or `memdraft_001` as fresh unseen paper evidence.
