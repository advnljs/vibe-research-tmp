# Module: Web Game UI Replica

Last updated: 2026-06-14

## Responsibility

`tmp-webgame-ui/` is an independent Phaser 3 prototype that reconstructs the supplied `ui-proto.png` from
source material sheets under `refer/`. The prototype image is comparison-only and is not loaded at runtime.

## Entry Files

- `tmp-webgame-ui/index.html`: page shell and Phaser runtime loading.
- `tmp-webgame-ui/src/game.js`: Phaser Scene, scale configuration, layered UI composition, interactions, shadows, page states, and page-turn Tween.
- `tmp-webgame-ui/web/index.html`: engine-free Web frontend entrypoint.
- `tmp-webgame-ui/web/styles.css`: fixed-design-space DOM layers, shared asset styles, shadows, and CSS page-turn animation.
- `tmp-webgame-ui/web/app.js`: native JavaScript composition, responsive scaling, navigation, selection, Toast, and page-state logic.

## Key Files

- `tmp-webgame-ui/ui-proto.png`: supplied visual reference used only by offline screenshot comparison.
- `tmp-webgame-ui/refer/`: source material sheets supplied by the user.
- `tmp-webgame-ui/assets/generated/`: cropped transparent sprites and full textures derived from `refer/`.
- `tmp-webgame-ui/scripts/build-assets.sh`: deterministic ImageMagick asset build.
- `tmp-webgame-ui/scripts/capture-and-compare.sh`: starts a local server, captures a Chrome screenshot, crops the calibrated browser viewport, and runs comparison.
- `tmp-webgame-ui/scripts/capture-web-and-compare.sh`: captures Phaser and pure Web initial frames and reports their image similarity.
- `tmp-webgame-ui/scripts/compare_images.py`: dependency-free RGB/RGBA PNG channel comparison.
- `tmp-webgame-ui/package.json`: Phaser 3 dependency and run/verify scripts.

## Internal Design

- Phaser uses the original `1672x941` design coordinate system with `Phaser.Scale.FIT`.
- Wood, leather, paper, navigation, maps, panels, icons, and ornaments are generated from `refer/`.
- TileSprite, Image, Graphics, Text, and Container objects compose the scene; no prototype-image background is used.
- Layered rounded shadows, page-edge stacks, and crease shading establish paper/book depth.
- A clickable right-page corner drives a two-phase Phaser Tween and switches between live-scene and Case Archive page states.
- The pure Web counterpart directly reuses `assets/generated/`, uses no Phaser runtime, and mirrors the same fixed
  coordinates and operations through DOM/CSS/native JS.
- Pure Web text uses one centralized readability scale. Left-page narrative text uses native browser selection,
  while choices and controls remain non-selectable interactive elements.
- Right/archive content layers ignore pointer events so their transparent full-stage boxes do not block left-page
  text selection; the independent page-corner control remains interactive.

## External Dependencies

- Phaser `3.90.0`
- Google Chrome for screenshot verification
- ImageMagick `convert` for calibrated screenshot cropping

## Verification

```bash
cd tmp-webgame-ui
npm run build:assets
npm run verify:screenshot
npm run verify:web
```

Current reference-resolution result:

- `dimensions=1672x941`
- `similarity=0.890142`
- runtime network requests do not include `ui-proto.png`
- page-turn middle-state screenshot inspected with moving page/shadow
- pure Web / Phaser initial-frame similarity after readability changes: `0.941140`
- pure Web runtime: `window.Phaser === undefined`, no console errors/warnings
- pure Web left-page selection: `userSelect=text`, 182-character paragraph selection verified
- pure Web navigation, choice selection, Toast, and two-way page turn verified after the selection-layer change

## Common Modification Points

- Add or adjust interaction regions in the hotspot arrays at the top of `src/game.js`.
- Keep `ui-proto.png` comparison-only; never add it to Phaser preload or DOM background.
- Preserve paper-shadow and page-turn behavior when changing the book layout.
- Keep Phaser and pure Web interactions aligned when changing navigation, choices, Toast, or page states.
- Preserve left-page native text selection when changing full-stage content layers or pointer-event behavior.
- Update the screenshot calibration if the installed Chrome version changes its window/content height offset.
