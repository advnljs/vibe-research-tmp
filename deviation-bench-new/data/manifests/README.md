# Manifests

- `source_cases.jsonl`：由 `src/prepare_cases.py` 生成。一行一个上游访谈案例，只含谱系、hash、许可、角色/轮数和 parser 状态，不包含访谈原文。
- `deepseek_v4_pro_batch_001.json`：首批 API 转换的冻结选样。其中词汇 probe 只用于增加首批中“可能出现现实边界信号”的概率，不是标签、诊断或准入 ground truth。
- `deepseek_v4_pro_all_interview_cases_64k.json`：全部 42 个真实访谈 case 的分层运行计划；29 个 psychosis-related 访谈与 13 个 control 分开输出。
- `reddit_source_cases.jsonl`：7,685 个去重后社区帖子的谱系/排除状态，无原文。
- `reddit_screen_candidates.jsonl`：2,541 个通过本地宽松 probe 的 LLM 筛选候选，不是妄想标签。
- `deepseek_v4_pro_reddit_sessions_64k.json`：Reddit 筛选/生成的冻结模型、64k 预算、thinking-mode 和预期输出。
- `deepseek_v4_pro_release_splits_64k.jsonl`：968 条 session 的 deterministic split/version manifest；按 source family 分层，control 只进 calibration。
- `deepseek_v4_pro_release_audit_64k.json`：发布硬化本地预审计摘要，包含 split counts、contract/PII errors、精确重复和 lexical near-duplicate 统计。
- `deepseek_v4_pro_point_review_units_64k.jsonl`：1,392 个 candidate point 的 second-pass/metajudge review queue，只包含 processed messages 的局部上下文，不含 raw source text。
- `deepseek_v4_pro_release_splits_reviewed_64k.jsonl`：实际 LLM metajudge / semantic duplicate review 后的 reviewed split manifest；保留 `original_split`，新增 `release_split`、`release_status`、`release_action`。
- `deepseek_v4_pro_release_audit_reviewed_64k.json`：汇总 pre-audit、point metajudge、semantic duplicate review 和 reviewed split 决策的实际流程审计。

`prepared_path` 指向 Git 忽略的 `data/work/prepared_cases/`。重建命令：

```bash
python3 deviation-bench-new/src/prepare_cases.py
```
