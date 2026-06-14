# Whispers in the Fog UI Replica

基于业界 Web 游戏引擎 **Phaser 3** 重新搭建 `ui-proto.png` 的界面结构。运行时不加载
`ui-proto.png`；桌面、皮革、纸页、导航、地图、卡片、图标和装饰都来自 `refer/`，
经 `scripts/build-assets.sh` 裁切为透明 sprites 后，由 Phaser 的 Scene、Graphics、
TileSprite、Image、Text、Container 和 Tween 组合。

界面包含多层书本/纸张阴影、页边堆叠、中缝阴影，以及点击右下页角触发的翻页动画。

## 运行

```bash
npm run build:assets
npm start
```

打开 `http://127.0.0.1:4173/`。

## 浏览器截图对比

```bash
npm run verify:screenshot
```

脚本会使用 Chrome 在 `1672×941` 视口截图，输出与参考图的逐通道差异和相似度指标。
参考图只用于离线截图对比，不参与运行时渲染。

当前重建初始帧验证：

- `dimensions=1672x941`
- `similarity=0.890142`
- Chrome 网络请求中没有 `ui-proto.png`

点击右页右下角的折角区域可以在场景面板与 Case Archive 页面之间翻页。
