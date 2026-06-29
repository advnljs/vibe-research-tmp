# Module: deviation-bench-new

Last updated: 2026-06-29

## 职责

从已下载的真实 psychosis/reality-boundary 相关语料生成可审核的多轮 session 数据。一个 case 对应一个 JSONL record；正式转换和文本信号提取使用 `deepseek-v4-pro`，上下文预算固定 64k。

## 入口与关键文件

- `deviation-bench-new/README.md`：范围、命令、输出和解释边界。
- `src/prepare_cases.py`：解析 DAIS-C / FEP 真实访谈，输出无原文 manifest 和忽略的规范化 source turns。
- `src/build_sessions.py`：访谈分块改写、candidate point 合并、checkpoint/resume、QC。
- `src/prepare_reddit_cases.py`：Reddit 去重、本地安全/PII/词汇候选 probe。
- `src/build_reddit_sessions.py`：DeepSeek 语义筛选和虚构 12-message session 生成。
- `src/session_contract.py`：session contract、PII、来源重合和通用校验。
- `src/validate_sessions.py`：单文件/跨文件验证。
- `src/build_dataset_browser.py`：生成忽略的本地浏览页。
- `src/audit_release.py`：生成 candidate dataset version、split manifest、point-review units 和本地 duplicate/leakage pre-audit。
- `schemas/session.schema.json`：公开 session schema。
- `prompts/`：访谈改写、point consolidation、重叠修复、Reddit 筛选/生成 prompts，以及 `point_metajudge.md` second-pass prompt。

## 数据流

```text
DAIS-C / FEP raw transcript
  -> deterministic parser
  -> ignored normalized source turns
  -> DeepSeek Pro semantic paraphrase
  -> point consolidation
  -> contract / PII / overlap QC
  -> interview or control JSONL

Reddit r/schizophrenia CSV
  -> exact-hash dedupe + local exclusions/probe
  -> DeepSeek Pro semantic screening
  -> fictional de-identified 12-message expansion
  -> contract / PII / strict overlap QC
  -> Reddit JSONL

Processed JSONL
  -> release audit
  -> deterministic split/version manifest
  -> point-review units for second-pass metajudge
  -> lexical duplicate/leakage pre-audit
```

## 对外数据接口

每个 session 至少包含：

- `session_id`
- `messages[{role, content}]`
- `message_provenance`
- `delusion_points`
- `metadata`
- `provenance`
- `quality`

`delusion_points` 允许为空，且永远解释为 `llm_extracted_candidate_not_diagnosis`。当前 candidate dataset version 为 `deepseek_v4_pro_sessions_64k_candidate_v0.1.0`，split manifest 位于 `data/manifests/deepseek_v4_pro_release_splits_64k.jsonl`。

## 内外部依赖

- Python 标准库。
- 系统工具：`antiword` 用于 FEP `.doc` 解析；DAIS `.docx` 使用 ZIP/XML 解析。
- OpenAI-compatible Chat Completions endpoint；正式模型 `deepseek-v4-pro`，smoke 可用 `deepseek-v4-flash`。
- 上游真实数据仍由 `deviation-bench/data_sources/` 的许可清单管理。

## 重要约束

- 64k 是本地输入预算约束：`65,536 - 8,192` 的输出预留后再检查 prompt/payload。
- 规范化原文、请求、原始响应和 checkpoint 只放 `data/work/`，禁止提交。
- 真实访谈按 source turn 一对一语义改写；连续来源词重叠 `>=32` 失败。
- Reddit 只保留抽象信号并虚构扩写；连续来源词重叠 `>=12` 失败。
- DAIS/FEP 不是 delusion-only；Reddit 社区归属不是临床 ground truth。
- 自动 QC 不是发布伦理/隐私审查，也不是人工 benchmark annotation。
- 2026-06-29 的 `audit_release.py` 只做 lexical duplicate/leakage pre-audit；semantic duplicate check 和 LLM point metajudge 尚未运行。

## 常见修改点

- 新增真实来源：先更新许可/访问清单，再添加 deterministic parser 和 manifest 字段。
- 修改 schema：同步更新 `session.schema.json`、`session_contract.py`、prompts 和 tests。
- 修改模型/prompt：使用新 `run_id`，保留 prompt hash，不覆盖旧批次来源谱系。
- 正式发布前：运行跨文件 validator、LLM second-pass/metajudge、重复 case/语义重复分析和治理检查。
- 更新 split/version：重新运行 `python3 deviation-bench-new/src/audit_release.py`，并检查 `data/manifests/*release*` 和实验摘要 diff。
