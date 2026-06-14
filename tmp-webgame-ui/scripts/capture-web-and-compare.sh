#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/artifacts"
PHASER_SCREENSHOT="$OUTPUT_DIR/phaser-baseline.png"
WEB_SCREENSHOT="$OUTPUT_DIR/web-frontend.png"
PORT="${PORT:-4173}"

mkdir -p "$OUTPUT_DIR"

python3 -m http.server "$PORT" --directory "$ROOT_DIR" >"$OUTPUT_DIR/web-server.log" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 1

capture() {
  local url="$1"
  local raw="$2"
  local output="$3"
  google-chrome \
    --headless=new \
    --hide-scrollbars \
    --disable-gpu \
    --no-sandbox \
    --force-device-scale-factor=1 \
    --virtual-time-budget=3000 \
    --window-size=1672,1028 \
    --screenshot="$raw" \
    "$url"
  convert "$raw" -crop 1672x941+0+0 +repage "$output"
}

capture "http://127.0.0.1:$PORT/" "$OUTPUT_DIR/phaser-baseline-raw.png" "$PHASER_SCREENSHOT"
capture "http://127.0.0.1:$PORT/web/" "$OUTPUT_DIR/web-frontend-raw.png" "$WEB_SCREENSHOT"

python3 "$ROOT_DIR/scripts/compare_images.py" "$PHASER_SCREENSHOT" "$WEB_SCREENSHOT"
