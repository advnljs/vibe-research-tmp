# Restart Pack Manifest

更新日期：2026-07-07

## 包含内容

当前 `deviation-bench-restart-pack/` 包含两类内容：

1. 可提交、可审阅的迁移资料：
   - 入口说明：`README.md`
   - 初始动机整理：`01_initial_motivation_and_goals.md`
   - 资料导航：`02_collected_materials_navigation.md`
   - 旧研究文档：`research_docs/`
   - 数据清单与说明：`data_sources/` 中除 `downloaded/` 外的文件
   - prompt / schema：`prompts/`
   - 旧 runner / dashboard / consensus 脚本：`src/`
   - 实验记录：`experiments/`
   - paper 草稿：`paper/`
   - memory 快照：`memory_snapshot/`

2. 本地迁移专用、不会提交的内容：
   - `ds_key.txt`
   - `data_sources/downloaded/`

## 当前数量

- 可提交文件数：74。
- 本地复制的 downloaded 数据文件数：2,568。
- 整个迁移目录大小：约 204MB。
- `data_sources/downloaded/` 大小：约 203MB。

## Git 处理

`deviation-bench-restart-pack/.gitignore` 明确忽略：

- `ds_key.txt`
- `*_key.txt`
- `*key*.txt`
- `data_sources/downloaded/`
- local run outputs / Python cache

因此本次 git commit 只应包含迁移说明、研究文档、导航、prompt、脚本、实验记录和 memory 快照，不包含密钥或重复原始下载数据。

## 迁移方式

如果目标是给另一个本地 agent 直接使用，复制整个目录：

```bash
cp -a deviation-bench-restart-pack /path/to/new/workspace/
```

如果目标是通过 git 远程交接，只能依赖已提交部分；`ds_key.txt` 需要用安全方式另行提供，`data_sources/downloaded/` 可以从原仓库既有 tracked `deviation-bench/data_sources/downloaded/` 或外部来源重新获得。
