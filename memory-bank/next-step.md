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

## Immediate Queue

1. P0：运行 `delusion_points` independent second-pass / metajudge。输入队列和 prompt 已准备好；下一步需要按批调用模型，输出 model disagreement、point precision controls 和 schema validity。不能把第一遍 DeepSeek 提取直接当 gold label。
2. P0：补 dataset-level semantic duplicate / leakage analysis。本轮只完成 deterministic lexical pre-audit；下一步应做 embedding/LLM 语义重复检查，尤其是 926 个 Reddit fictional sessions 和跨 split 风险。
3. P0：将 metajudge 和 semantic duplicate 结果回填到 release audit；如发现冲突或泄漏，调整 split manifest 或标记 exclusions。
4. P1：做发布前治理检查：许可/ShareAlike、社区隐私、残余命名实体和稀有事件链；自动 regex PII=0 不是绝对匿名保证。
5. P1：基于当前 sessions 重新定义下游 benchmark task；在此之前不恢复旧 memory runner 扩展。

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

## Completion Rule

每个阶段性产物完成后：更新 memory bank / `研究导航.md` / `AGENTS.md`（按需），只 add 相关路径，focused commit，并 push `origin/main`。
