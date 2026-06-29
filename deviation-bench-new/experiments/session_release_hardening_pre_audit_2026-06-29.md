# Session release hardening pre-audit — 2026-06-29

## Scope

本轮继续 `deviation-bench-new/` 的 data release hardening，完成可复现的本地预审计、split/version manifest 和 second-pass point review queue。该轮不调用新模型，不把 first-pass `delusion_points` 当 gold label。

## Artifacts

- Audit JSON: `data/manifests/deepseek_v4_pro_release_audit_64k.json`
- Split manifest: `data/manifests/deepseek_v4_pro_release_splits_64k.jsonl`
- Point review units: `data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl`
- Metajudge prompt: `prompts/point_metajudge.md`

## Deterministic Audit Results

- Dataset version: `deepseek_v4_pro_sessions_64k_candidate_v0.1.0`
- Sessions: 968
- Messages: 16408
- Candidate points: 1392
- Sessions with candidate points: 940
- Contract / PII validation errors: 0
- Exact duplicate message-content groups: 0
- Lexical near-duplicate pairs at threshold 0.82: 0
- Cross-split lexical near-duplicate pairs at threshold 0.82: 0

## Split Counts

- `control_calibration`: 13
- `dev_review`: 97
- `heldout_candidate`: 761
- `validation`: 97

## Source Family Counts

- `dais_c_clinical_interview`: 15
- `dais_c_control_calibration`: 13
- `fep_interview`: 14
- `reddit_fictionalized_text_signal`: 926

## Interpretation

- `dev_review` / `validation` / `heldout_candidate` 是数据发布和后续 judge 开发的候选 split，不是最终论文 benchmark task 定义。
- `control_calibration` 只包含 DAIS-C control，不与 psychosis-related 或 community-fictionalized sessions 混作 clinical corpus。
- 当前 duplicate audit 是本地 lexical pre-audit；embedding/LLM 语义重复检查仍需后续执行。
- `point_review_units` 为 independent second-pass/metajudge 准备输入；本轮尚未产生 model disagreement 结果。
