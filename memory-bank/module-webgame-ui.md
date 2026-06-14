# Module: Web Game UI Replica

Last updated: 2026-06-14

## Responsibility

`tmp-webgame-ui/` is an independent Phaser 3 prototype that reproduces the supplied `ui-proto.png` and adds
game-style interaction hotspots without changing the initial visual frame.

## Entry Files

- `tmp-webgame-ui/index.html`: page shell and Phaser runtime loading.
- `tmp-webgame-ui/src/game.js`: Phaser Scene, scale configuration, hotspots, hover feedback, selection state, and toast feedback.

## Key Files

- `tmp-webgame-ui/ui-proto.png`: supplied visual reference and base artwork.
- `tmp-webgame-ui/scripts/capture-and-compare.sh`: starts a local server, captures a Chrome screenshot, crops the calibrated browser viewport, and runs comparison.
- `tmp-webgame-ui/scripts/compare_images.py`: dependency-free RGB/RGBA PNG channel comparison.
- `tmp-webgame-ui/package.json`: Phaser 3 dependency and run/verify scripts.

## Internal Design

- Phaser uses the original `1672x941` design coordinate system with `Phaser.Scale.FIT`.
- A Scene-controlled DOM background preserves the source image's exact color and texture.
- A transparent Phaser Canvas layer owns navigation, choices, cards, controls, hover states, selections, and toast feedback.
- The DOM base layer is intentional: browser Canvas/WebGL rendering changed source colors during screenshot verification.

## External Dependencies

- Phaser `3.90.0`
- Google Chrome for screenshot verification
- ImageMagick `convert` for calibrated screenshot cropping

## Verification

```bash
cd tmp-webgame-ui
npm run verify:screenshot
```

Expected reference-resolution result:

- `dimensions=1672x941`
- `mean_absolute_error=0.000000`
- `max_channel_error=0`
- `changed_channels=0/4720056`

## Common Modification Points

- Add or adjust interaction regions in the hotspot arrays at the top of `src/game.js`.
- Keep the initial frame free of visible overlays so screenshot verification remains exact.
- Update the screenshot calibration if the installed Chrome version changes its window/content height offset.
