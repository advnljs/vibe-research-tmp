#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REFER_DIR="$ROOT_DIR/refer"
OUTPUT_DIR="$ROOT_DIR/assets/generated"

mkdir -p "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.png" -delete

convert "$REFER_DIR/ai-rpg-assets (1).png" "$OUTPUT_DIR/paper-texture.png"
convert "$REFER_DIR/ai-rpg-assets (2).png" "$OUTPUT_DIR/leather-texture.png"
convert "$REFER_DIR/ai-rpg-assets (3).png" "$OUTPUT_DIR/wood-texture.png"

extract() {
  local source="$1"
  local geometry="$2"
  local output="$3"
  local fuzz="${4:-16%}"

  convert "$source" \
    -crop "$geometry" +repage \
    -alpha on -fuzz "$fuzz" -fill none -draw "matte 0,0 floodfill" \
    -trim +repage "$OUTPUT_DIR/$output"
}

NAV_SHEET="$REFER_DIR/ai-rpg-assets (8).png"
extract "$NAV_SHEET" "280x102+25+25" "nav-world.png"
extract "$NAV_SHEET" "280x102+25+125" "nav-characters.png"
extract "$NAV_SHEET" "280x102+25+220" "nav-memories.png"
extract "$NAV_SHEET" "280x102+25+315" "nav-events.png"
extract "$NAV_SHEET" "280x102+25+410" "nav-map.png"
extract "$NAV_SHEET" "280x102+25+505" "nav-threads.png"

ICON_SHEET="$REFER_DIR/ai-rpg-assets (6).png"
extract "$ICON_SHEET" "210x210+45+55" "icon-world.png" "14%"
extract "$ICON_SHEET" "210x210+290+55" "icon-character.png" "14%"
extract "$ICON_SHEET" "210x210+775+55" "icon-event.png" "14%"
extract "$ICON_SHEET" "230x200+990+65" "icon-map.png" "14%"
extract "$ICON_SHEET" "230x210+985+315" "icon-network.png" "14%"
extract "$ICON_SHEET" "215x210+285+555" "icon-location.png" "14%"
extract "$ICON_SHEET" "215x210+45+805" "icon-eye.png" "14%"
extract "$ICON_SHEET" "190x210+535+790" "icon-key.png" "14%"
extract "$ICON_SHEET" "205x210+775+790" "icon-moon.png" "14%"
extract "$ICON_SHEET" "215x210+285+1015" "icon-book.png" "14%"
extract "$ICON_SHEET" "205x220+535+1000" "icon-quill.png" "14%"
extract "$ICON_SHEET" "205x210+775+1015" "icon-seal.png" "14%"

PANEL_SHEET="$REFER_DIR/ai-rpg-assets (7).png"
extract "$PANEL_SHEET" "390x390+430+45" "panel-aged.png" "18%"
extract "$PANEL_SHEET" "390x390+825+440" "panel-map.png" "18%"
extract "$PANEL_SHEET" "390x390+30+830" "panel-note.png" "18%"
extract "$PANEL_SHEET" "390x390+430+830" "panel-seal-note.png" "18%"

ORNAMENT_SHEET="$REFER_DIR/ai-rpg-assets (5).png"
extract "$ORNAMENT_SHEET" "260x235+70+30" "corner-ornament.png" "14%"
extract "$ORNAMENT_SHEET" "150x155+1015+485" "medallion-compass.png" "14%"
