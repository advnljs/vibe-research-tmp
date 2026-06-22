# Todo

Last updated: 2026-06-22

| Task | Priority | Status | Blocker | Next step |
|---|---|---|---|---|
| Independent point metajudge | P0 | pending | requires API budget/run design | Rejudge all/stratified points plus negative controls; report disagreement, not gold labels. |
| Semantic duplicate/leakage audit | P0 | pending | none | Embed or LLM-check Reddit sessions and cross-source overlap; produce clusters and split constraints. |
| Dataset version/split manifest | P0 | pending | metajudge and duplicate policy should be specified | Freeze separate clinical/FEP, control, community-fictionalized splits and hashes. |
| Release governance review | P1 | pending | license/privacy interpretation | Check CC BY-SA boundary, Reddit redistribution/privacy, names/entities and rare event chains. |
| Downstream benchmark redesign | P1 | pending | prepared data should be hardened first | Define task, units, controls and metrics from the new session data layer. |
| Old agent-memory route | P3 | paused | superseded by user direction | Do not resume unless user explicitly redirects. |

## Completed Recently

- 2026-06-22: built `deviation-bench-new/` pipeline, prompts, schema, tests and browser.
- 2026-06-22: completed 42/42 DeepSeek Pro real interview conversions.
- 2026-06-22: screened 2,541 Reddit candidates and generated 926/926 DeepSeek Pro fictional sessions.
- 2026-06-22: validated 968 sessions / 16,408 messages / 1,392 candidate points with 0 contract errors.
