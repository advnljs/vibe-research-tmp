# Deviation Bench Tooling Registry

本目录记录后续工具化 / UI 化需要复用的结构化配置。

当前文件：

- `component_registry.yaml`
  - 定义 Deviation Bench 工具界面中的组件类型。
  - 为组件类型选择框提供 `value -> zh/en label` 映射。
  - 语言策略：中文界面使用中文 label；英文和其他语言默认使用英文 label。
  - 记录每类组件的默认尺寸、是否可移动、是否可调整大小。

## 后续 TODO

- 在未来 UI 中让组件位置和大小可修改：
  - 支持拖拽修改 `x` / `y`。
  - 支持 resize handle 修改 `width` / `height`。
  - 将 layout state 与 semantic content 分开保存。
  - 至少保存 `x`、`y`、`width`、`height`、`locked`、`visible`。
- 组件类型选择框必须使用 `component_registry.yaml`，不要在 UI 中硬编码 label。
- 如果 locale 不是中文，组件类型 label 回退英文。
