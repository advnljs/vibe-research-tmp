# Session release hardening actual flow — 2026-06-29

## Scope

本轮完成实际 release-hardening 流程：DeepSeek Pro independent point metajudge、DeepSeek Pro semantic fingerprint + duplicate/leakage pair review、reviewed split/audit materialization，以及动态 runs dashboard。

## Artifacts

- Point metajudge: `data/reviews/deepseek_v4_pro_point_metajudge_64k.jsonl`
- Point metajudge summary: `data/reviews/deepseek_v4_pro_point_metajudge_64k_summary.json`
- Semantic fingerprints: `data/reviews/deepseek_v4_pro_session_semantic_fingerprints_64k.jsonl`
- Semantic duplicate pairs: `data/reviews/deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl`
- Semantic duplicate summary: `data/reviews/deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json`
- Reviewed audit: `data/manifests/deepseek_v4_pro_release_audit_reviewed_64k.json`
- Reviewed split manifest: `data/manifests/deepseek_v4_pro_release_splits_reviewed_64k.jsonl`
- Dynamic local dashboard: `data/work/runs_dashboard/index.html`

## Point Metajudge

- Units reviewed: 1420
- Candidate points: 1392
- Negative controls: 28
- Candidate acceptance rate: 0.943247
- Candidate revise/reject rate: 0.056753
- Negative control flag rate: 0.0

## Semantic Duplicate / Leakage Review

- Fingerprints: 968
- Pair reviews: 240
- Duplicate pairs: 4
- Near-duplicate pairs: 100
- Medium/high leakage pairs: 104

## Reviewed Split Decisions

- Included sessions: 964
- Excluded duplicate candidates: 4
- Same-split moved sessions: 63

Release split counts:
- `control_calibration`: 13
- `dev_review`: 146
- `excluded_duplicate`: 4
- `heldout_candidate`: 700
- `validation`: 105

## Interpretation

- Reviewed split decisions are deterministic applications of LLM review outputs; raw processed sessions are not deleted.
- `excluded_duplicate_candidate` marks sessions that should not enter downstream benchmark release without further policy decision.
- `move_to_same_split_due_to_llm_near_duplicate` prevents reviewed near-duplicate clusters from crossing split boundaries.
- License/privacy/governance review is still required before any public release.
