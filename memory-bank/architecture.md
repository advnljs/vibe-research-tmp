# Architecture

Last updated: 2026-06-29

## System Boundary

当前主系统 `deviation-bench-new/` 是低 GPU、API-only 的真实数据派生层。它读取已下载且访问/许可状态已记录的真实访谈或社区数据，输出可追溯的多轮 session 和候选现实边界文本信号。

旧 `deviation-bench/` 保留 benchmark、judge、memory-condition runner 和历史研究材料，但其 agent-memory/UIRD 扩展已暂停。

## Main Components

- Source parsers/manifests：`prepare_cases.py`、`prepare_reddit_cases.py`、`data/manifests/`。
- Interview transform：`build_sessions.py` + chunk/consolidation/repair prompts。
- Community route：`build_reddit_sessions.py` + screen/generation prompts。
- Contract/QC：`session_contract.py`、`session.schema.json`、`validate_sessions.py`。
- Release hardening pre-audit：`audit_release.py`、`point_metajudge.md`、release split/audit/point-review manifests。
- Processed outputs：`data/processed/`、`data/screened/`。
- Private working state：ignored `data/work/`。
- Local inspection：`build_dataset_browser.py` -> ignored HTML。
- Historical benchmark system：`deviation-bench/`。
- Project state：`memory-bank/`、`研究导航.md`、`AGENTS.md`。

## Data Flow

1. DAIS-C/FEP：真实多轮 transcript -> deterministic parser -> normalized source turns -> DeepSeek Pro semantic paraphrase -> point consolidation -> structural/PII/overlap QC -> interview/control JSONL。
2. Reddit：真实 single post -> hash dedupe/local exclusion/probe -> DeepSeek Pro semantic screening -> fictional 12-message expansion -> strict PII/overlap QC -> community-fictionalized JSONL。
3. 所有 processed records 保存 source/model/prompt hashes、64k budget、thinking mode、license、parser 和 QC provenance；不保存 source/API raw text。
4. Release hardening pre-audit：processed JSONL -> deterministic source-family split manifest -> point-review queue -> contract/PII/exact duplicate/lexical near-duplicate audit。

## Key Technical Decisions

- One case = one JSONL session；对话主体统一为 OpenAI-style `messages`。
- 正式模型 `deepseek-v4-pro`，smoke 可用 `deepseek-v4-flash`。
- 本地 context window 固定 65,536，输出预留 8,192；不向 provider 发送非标准 context-window 字段。
- DAIS/FEP source turn 一对一语义改写；连续来源词重叠 `>=32` 失败。
- Reddit 只作为文本信号，经虚构扩写；连续来源词重叠 `>=12` 失败。
- `delusion_points` 允许为空，只是 LLM candidate，不是 diagnosis/gold label。
- control、psychosis-related interviews、community-fictionalized sessions 必须分 split 处理。
- 当前 candidate release version 为 `deepseek_v4_pro_sessions_64k_candidate_v0.1.0`；split manifest 是 source-family stratified，control calibration-only。

## Important Constraints

- `data/work/` 不提交；禁止提交 API key、请求/响应、normalized raw text。
- Reddit 社区归属不能当临床 ground truth，输出不能称为真实对话。
- 自动 PII/QC 不能替代发布前治理审查。
- 新增来源前先更新许可/访问状态；不默认抓取新平台数据。
- 不把当前数据用于诊断，也不扩展为 jailbreak/safety-bypass 研究。

## Architecture Change History

- 2026-05-21 to 2026-05-30: UIRD benchmark runner, judge, dashboard, LLM-only validation route.
- 2026-05-31 to 2026-06-05: agent-memory framing, memory scenarios and local memory-condition runner.
- 2026-06-14: auxiliary Phaser/pure-Web UI task completed.
- 2026-06-22: current route changed to `deviation-bench-new/`; completed real interview transformation and screened community-to-fictional session pipeline. Old agent-memory route paused.
- 2026-06-29: added release hardening pre-audit, candidate split/version manifest and point-review units; LLM metajudge and semantic duplicate check remain pending.
