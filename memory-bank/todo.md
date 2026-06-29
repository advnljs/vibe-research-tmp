# Todo

Last updated: 2026-06-29

| Task | Priority | Status | Blocker | Next step |
|---|---|---|---|---|
| Independent point metajudge | P0 | queue prepared | requires API budget/run design | Use `prompts/point_metajudge.md` over `data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl`; report disagreement, not gold labels. |
| Semantic duplicate/leakage audit | P0 | lexical pre-audit complete | semantic model/embedding method not selected | Run embedding or LLM semantic duplicate check over Reddit sessions and cross-split pairs; update release audit/exclusions. |
| Dataset version/split manifest | P0 | candidate freeze complete | final freeze depends on metajudge and semantic duplicate results | Current version `deepseek_v4_pro_sessions_64k_candidate_v0.1.0`; keep clinical/FEP, control, community-fictionalized separated. |
| Release governance review | P1 | pending | license/privacy interpretation | Check CC BY-SA boundary, Reddit redistribution/privacy, names/entities and rare event chains. |
| Downstream benchmark redesign | P1 | pending | prepared data should be hardened first | Define task, units, controls and metrics from the new session data layer. |
| Old agent-memory route | P3 | paused | superseded by user direction | Do not resume unless user explicitly redirects. |

## Completed Recently

- 2026-06-22: built `deviation-bench-new/` pipeline, prompts, schema, tests and browser.
- 2026-06-22: completed 42/42 DeepSeek Pro real interview conversions.
- 2026-06-22: screened 2,541 Reddit candidates and generated 926/926 DeepSeek Pro fictional sessions.
- 2026-06-22: validated 968 sessions / 16,408 messages / 1,392 candidate points with 0 contract errors.
- 2026-06-29: generated release audit, split manifest and 1,392 point-review units; local lexical duplicate/leakage pre-audit found 0 pairs at threshold 0.82.
