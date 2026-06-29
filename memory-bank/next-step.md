# Next Step

Last updated: 2026-06-29

## Current Decision State

当前主线已切换到 `deviation-bench-new/`：先完成和硬化真实数据派生 session 数据层。旧 `deviation-bench/` 的 induced-drift / agent-memory 路线暂停，不删除，暂不继续扩展。

已完成的正式数据：

- DAIS-C clinical：15 sessions。
- FEP friendship：14 sessions。
- DAIS-C control calibration：13 sessions。
- Reddit fictionalized reality-boundary text signals：926 sessions。
- 合计：968 sessions / 16,408 messages / 1,392 candidate points。

2026-06-29 已新增 release hardening pre-audit：

- Candidate dataset version：`deepseek_v4_pro_sessions_64k_candidate_v0.1.0`。
- Split manifest：`deviation-bench-new/data/manifests/deepseek_v4_pro_release_splits_64k.jsonl`。
- Audit summary：`deviation-bench-new/data/manifests/deepseek_v4_pro_release_audit_64k.json`。
- Point metajudge queue：`deviation-bench-new/data/manifests/deepseek_v4_pro_point_review_units_64k.jsonl`。
- 本地结果：contract/PII errors 0、exact duplicates 0、lexical near-duplicates 0、cross-split lexical near-duplicates 0。

2026-06-29 actual release-hardening flow 已完成：

- Point metajudge：`deviation-bench-new/data/reviews/deepseek_v4_pro_point_metajudge_64k_summary.json`。
- Semantic duplicate/leakage：`deviation-bench-new/data/reviews/deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json`。
- Reviewed audit：`deviation-bench-new/data/manifests/deepseek_v4_pro_release_audit_reviewed_64k.json`。
- Reviewed split manifest：`deviation-bench-new/data/manifests/deepseek_v4_pro_release_splits_reviewed_64k.jsonl`。
- Dynamic runs dashboard：ignored `deviation-bench-new/data/work/runs_dashboard/index.html`。
- Review dashboard：ignored `deviation-bench-new/data/work/review_dashboard/index.html`，展示实际实验结果、delusion/reality-boundary 指标、LLM 生成自然语言说明、状态图标、统计图表、热力图、session 过滤、完整对话、metajudge rationale 和 duplicate/leakage pair；页面统计由数据动态聚合。
- Reviewed release split：control_calibration 13、dev_review 146、validation 105、heldout_candidate 700、excluded_duplicate 4。

## Immediate Queue

1. P1：做发布前治理检查：许可/ShareAlike、社区隐私、残余命名实体和稀有事件链；自动 regex PII=0 不是绝对匿名保证。
2. P1：基于 reviewed split manifest 重新定义下游 benchmark task；在此之前不恢复旧 memory runner 扩展。
3. P1：如要进入 release package，明确 `excluded_duplicate_candidate` 的处理策略：默认不进入下游 benchmark release，但保留 processed record 和审计谱系。
4. P2：可补第二模型/第二 judge variance check；当前 actual flow 只使用 DeepSeek Pro 作为 metajudge / semantic duplicate reviewer。

## Important Boundaries

- 42 只是原生多轮访谈 case 数，不是最终 session 总数。
- DAIS-C clinical / FEP 都不是 delusion-only；29 个 psychosis-related 访谈中只有 14 个提取到候选点。
- Reddit subreddit membership 不是 diagnosis；926 个输出是虚构对话，不是真实访谈。
- `delusion_points` 是 `llm_extracted_candidate_not_diagnosis`，允许为空。
- 正式数据只使用 `deepseek-v4-pro`；Flash 只做 smoke；context budget 为 65,536。
- `data/work/` 中的 normalized raw turns、API request/response、checkpoint 和浏览页不得提交。

## Handoff Entry Points

- `deviation-bench-new/README.md`
- `deviation-bench-new/experiments/real_data_session_preparation_2026-06-22.md`
- `memory-bank/module-deviation-bench-new.md`
- `deviation-bench-new/data/processed/`
- `deviation-bench-new/data/screened/`
- `deviation-bench-new/src/build_review_dashboard.py`
- `deviation-bench-new/src/generate_review_narratives.py`
- `deviation-bench-new/data/reviews/deepseek_v4_pro_review_narratives_64k.json`
- `deviation-bench-new/data/work/review_dashboard/index.html`（ignored，本地浏览用）

## Completion Rule

每个阶段性产物完成后：更新 memory bank / `研究导航.md` / `AGENTS.md`（按需），只 add 相关路径，focused commit，并 push `origin/main`。
