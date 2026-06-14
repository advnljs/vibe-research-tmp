#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/artifacts"
SCREENSHOT="$OUTPUT_DIR/browser-screenshot.png"
RAW_SCREENSHOT="$OUTPUT_DIR/browser-screenshot-raw.png"
PORT="${PORT:-4173}"

mkdir -p "$OUTPUT_DIR"

python3 -m http.server "$PORT" --directory "$ROOT_DIR" >"$OUTPUT_DIR/server.log" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 1

google-chrome \
  --headless=new \
  --hide-scrollbars \
  --disable-gpu \
  --no-sandbox \
  --force-device-scale-factor=1 \
  --virtual-time-budget=3000 \
  --window-size=1672,1028 \
  --screenshot="$RAW_SCREENSHOT" \
  "http://127.0.0.1:$PORT/"

convert "$RAW_SCREENSHOT" -crop 1672x941+0+0 +repage "$SCREENSHOT"
python3 "$ROOT_DIR/scripts/compare_images.py" "$ROOT_DIR/ui-proto.png" "$SCREENSHOT"
