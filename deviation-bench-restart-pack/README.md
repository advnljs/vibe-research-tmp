# Deviation Bench Restart Pack

更新日期：2026-07-07

这个目录是给下一个 agent 重新启动 Deviation Bench 用的迁移包。它刻意回到旧 `deviation-bench/` 的最初研究动机：测量 LLM 在多轮用户诱导、社会压力和上下文变化下能否保持现实锚定，而不是继续把当前工作重心放在 `deviation-bench-new/` 的大规模数据整理路线。

## 先读什么

1. `01_initial_motivation_and_goals.md`
   - 重新整理最初的研究初心、现象定义、边界、任务轨道和指标。
2. `02_collected_materials_navigation.md`
   - 整理已经搜集的研究文档、数据源、prompt、runner、实验记录和迁移注意事项。
3. `research_docs/00_core_motivation/`
   - 旧路线最关键的概念和可执行方案原文。
4. `data_sources/下载清单与访问状态.md`
   - 所有已下载/受限数据的来源、许可、用途和风险边界。
5. `prompts/` 和 `src/`
   - 如果新 agent 要恢复旧 pilot / runner，可从这里直接接手。

## 目录内容

- `01_initial_motivation_and_goals.md`：重新整理后的初心和目标。
- `02_collected_materials_navigation.md`：迁移包导航和资料索引。
- `research_docs/`：从旧 `deviation-bench/` 复制出的研究文档。
- `data_sources/`：数据清单、数据使用说明、模式库、受限源申请清单，以及本地复制的 `downloaded/` 数据。
- `prompts/`：旧路线的 scenario、judge、metajudge、rewrite 和 memory-facing prompt/schema。
- `src/`：旧 pilot runner、dashboard、rewrite、judge consensus 和 memory-condition 相关脚本。
- `experiments/`：旧路线已经跑过的 S0 / mock / memory-facing 实验记录。
- `paper/`：benchmark comparison / Table 1 类写作草稿。
- `memory_snapshot/`：迁移时的 `AGENTS.md`、`研究导航.md` 和 memory-bank 快照。
- `ds_key.txt`：本地复制的 DeepSeek/API key 文件。这个文件被 `.gitignore` 排除，不会提交或 push。

## 使用边界

- `ds_key.txt` 只用于本地迁移。不要打印、贴到聊天里、提交到 git 或放入公开压缩包。
- `data_sources/downloaded/` 里包含真实访谈、社区数据和第三方仓库快照。使用前必须重新核对许可、隐私和再分发边界。
- 不要直接把真实患者、参与者或社区帖子原文发布成 benchmark prompt。旧路线的安全做法是：真实数据只做抽象模式锚点，再改写为虚构、去标识化、低风险的 evidence-anchor 多轮场景。
- `deviation-bench-new/` 的 968-session 数据整理路线没有放进这个迁移包作为主入口。若要参考它，应回原仓库单独查看，且不要把 926 个 Reddit fictionalized sessions 当作真实对话证据。

## 推荐重启方向

从 `User-Induced Reality Drift (UIRD)` 重新开始：

- 先定义可测现象：无证据信念放大、无新证据翻案、确定性膨胀、虚构性扩写、纠偏恢复。
- 用低风险虚构场景和明确 evidence packet 控制事实边界。
- 保持 API-only / 低 GPU / 不训练模型。
- 使用 LLM-as-judge + metajudge + gold controls + schema/rule validation，不依赖人类标注作为论文证据。
- 真实临床/社区资料只作为抽象模式和数据生成约束，不作为公开 prompt 原文。
