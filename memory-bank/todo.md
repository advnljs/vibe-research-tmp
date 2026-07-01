# Todo

Last updated: 2026-07-01

| Task | Priority | Status | Blocker | Next step |
|---|---|---|---|---|
| Independent point metajudge | P0 | completed | none | Use reviewed audit for downstream; optional future second-model variance check. |
| Semantic duplicate/leakage audit | P0 | completed | none | Reviewed manifest marks 4 excluded duplicate candidates and 63 same-split moves. |
| Dataset version/split manifest | P0 | reviewed freeze complete | final public release still needs governance review | Use `deepseek_v4_pro_release_splits_reviewed_64k.jsonl` for downstream task construction. |
| Review dashboard for results/delusion/narratives/conversations/charts | P0 | completed | none | Use ignored `data/work/review_dashboard/index.html` for dynamically aggregated actual results, LLM narratives, delusion metrics, charts and local inspection. |
| Static session overview / Reddit validity report | P0 | completed | none | Use `deviation-bench-new/reports/session_overview_report.html` to explain 42 true multi-turn interview-derived sessions vs 926 Reddit fictionalized text-signal sessions. |
| Release governance review | P1 | pending | license/privacy interpretation | Check CC BY-SA boundary, Reddit redistribution/privacy, names/entities and rare event chains. |
| Reddit strata validity gate and weighting decision | P1 | pending | downstream task not yet defined | Decide whether to cap, weight, or separately report Reddit fictionalized sessions before benchmark construction. |
| Downstream benchmark redesign | P1 | pending | prepared data should be hardened first | Define task, units, controls and metrics from the new session data layer. |
| Old agent-memory route | P3 | paused | superseded by user direction | Do not resume unless user explicitly redirects. |

## Completed Recently

- 2026-06-22: built `deviation-bench-new/` pipeline, prompts, schema, tests and browser.
- 2026-06-22: completed 42/42 DeepSeek Pro real interview conversions.
- 2026-06-22: screened 2,541 Reddit candidates and generated 926/926 DeepSeek Pro fictional sessions.
- 2026-06-22: validated 968 sessions / 16,408 messages / 1,392 candidate points with 0 contract errors.
- 2026-06-29: generated release audit, split manifest and 1,392 point-review units; local lexical duplicate/leakage pre-audit found 0 pairs at threshold 0.82.
- 2026-06-29: completed actual DeepSeek Pro point metajudge and semantic duplicate/leakage flow; generated reviewed audit/splits and dynamic runs dashboard.
- 2026-06-29: added a richer review dashboard that dynamically shows actual experiment results, delusion/reality-boundary metrics, charts, heatmaps, conversations, metajudge rationales and duplicate/leakage pairs.
- 2026-06-29: added DeepSeek Pro narrative generation from aggregate stats and wired it into the review dashboard.
- 2026-07-01: added static session overview report and generator; highlighted Reddit dominance and synthetic-dialogue validity boundaries.
