# Whispers in the Fog UI Replica

基于业界 Web 游戏引擎 **Phaser 3** 复刻 `ui-proto.png`。Phaser Scene 以原始
`1672×941` 设计坐标渲染，并管理纹理加载、响应式缩放、导航、剧情选项、信息卡片、
关系节点和底部控制区域的交互命中层。

为避免浏览器 Canvas/WebGL 对参考图进行颜色空间转换，Phaser Scene 会挂载与其缩放坐标
一致的 DOM 底图层，透明 Phaser WebGL 层负责交互和状态反馈。这样初始帧能保持参考图的
原始颜色与纹理。

## 运行

```bash
npm start
```

打开 `http://127.0.0.1:4173/`。

## 浏览器截图对比

```bash
npm run verify:screenshot
```

脚本会使用 Chrome 在 `1672×941` 视口截图，并将浏览器截图逐通道与参考图比较。
