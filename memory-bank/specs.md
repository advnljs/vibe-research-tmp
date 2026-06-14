# Specs

Last updated: 2026-06-14

This file records persistent user requirements and project constraints in compact form. The full source of truth remains `AGENTS.md` plus the three primary memory-bank files.

## Persistent User Requirements

- Use Chinese for user-facing summaries unless another language is requested.
- Preserve the original research motivation: challenge situational consistency assumptions in AI evaluation.
- Keep the project low-GPU and LLM API-only.
- Do not convert this into jailbreak or safety-bypass research.
- Use real clinical/community data only as anchors for abstracted patterns or fictional de-identified scenarios by default.
- Do not use human annotation as paper-facing benchmark evidence.
- Use LLM-only validation: primary judge, metajudge/second judge, judge variance, gold controls, and schema/rule checks.
- Main current paper hook: agent memory can be delusive.
- Core comparison: full transcript context vs memory systems within token ranges where full transcript still fits.
- Preserve the hypothesis that direct full transcript may be more reality-grounded than current memory systems in those token regimes.
- Verify mem0, Graphiti, and any other external memory system via official docs/source and pinned versions before paper claims.
- Turn-count / pressure-cadence choices may later be aligned with related papers, but near-term work should prioritize validation and runner reliability.
- Current memory-facing scenario drafts should be longer than 20 turns by default; v0.4 uses 30 target-visible turns.
- Each memory-facing scenario should explicitly include mainline, related facts, and the real-data abstract pattern IDs it reflects.
- For `tmp-webgame-ui/`, use an industry Web game engine and verify the replica by reading and comparing real browser screenshots.
- Build the runtime UI from `tmp-webgame-ui/refer/`; `ui-proto.png` may only be used for offline comparison.
- Preserve paper/book depth with shadows and provide an interactive page-turn animation.

## Current Acceptance Criteria For Next Task

- Memory runner changes must support mock/offline validation first.
- Revised memory-facing scenarios should keep no-new-evidence semantics and pass browser validation, runner conversion, mock rollout, and dashboard generation before use.
- Current scenario acceptance should verify `scenario_description`, `mainline`, `related_facts`, `real_data_anchor`, and `source_pattern_ids`.
- Each memory condition must record trace fields: backend/config, write policy, retrieval policy, context tokens, compression ratio, source turns, evidence relation, verification status, and distortion flags.
- Generated raw results remain under ignored `deviation-bench/results/`.
- Every completed durable task must update memory-bank, commit, and push to `origin/main`.

## Current Forbidden / Restricted Actions

- Do not add production dependencies without user confirmation.
- Do not commit secrets, `.env`, API keys, raw sensitive new data, local logs, or generated dashboards containing raw outputs.
- Do not force push, rebase, reset hard, clean user files, or overwrite unrelated changes.
- Do not treat `uird_pilot_001`, `uird_pilot_002`, `uird_pilot_003`, or `memdraft_001` as fresh unseen paper evidence.
