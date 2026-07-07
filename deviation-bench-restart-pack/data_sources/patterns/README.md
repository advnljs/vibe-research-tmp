# Abstracted Seed Pattern Bank

更新日期：2026-05-29

本目录保存从真实访谈 / 社区数据中抽象出来的 Deviation Bench 场景种子。这里的记录不是原始语料摘录，也不是临床标签；它们只描述可安全迁移到虚构 benchmark 场景中的语言结构、压力机制和现实锚定风险。

## 当前文件

- `seed_pattern_bank.jsonl`
  - 第一版 60 条抽象模式。
  - 来源分布：
    - DAIS-C clinical speaker-only：18 条
    - First-episode psychosis friendship interviews：12 条
    - Reddit Mental Health Dataset `r/schizophrenia` subset：30 条

## JSONL 字段

每行是一个 JSON object：

- `pattern_id`：稳定 ID。
- `source_family`：来源家族，不等同于临床诊断标签。
- `source_path`：本地来源路径，可指向目录或数据文件。
- `signal_type`：抽象文本信号类型。
- `theme`：可迁移到虚构场景的主题。
- `register`：原来源的语域，例如 interview_narrative / community_post。
- `abstracted_template`：抽象模式描述；不得复制真实原文。
- `risk_level`：建议用于公开 benchmark 的风险等级。
- `citation`：来源引用。
- `license_note`：许可和使用边界。
- `source_text_copied`：必须为 `false`。
- `scenario_use`：建议如何转成 fictional scenario。

## 使用边界

- 不把这些记录当作“用户是否有妄想”的诊断标签。
- 不把 subreddit membership、临床组或访谈来源当作个体状态判断。
- 公开 benchmark prompt 必须继续虚构化、去身份化、低风险化。
- 高风险行动、自伤、暴力、跟踪、真实人物指控、医疗/法律/金融建议场景不进入诱导型公开 prompt。
