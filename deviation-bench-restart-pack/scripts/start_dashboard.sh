#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="127.0.0.1"
PORT="8765"
INPUT_PATTERN="$ROOT/results/pilot/*.jsonl"
OUT_DIR="$ROOT/results/dashboard"
OUT_FILE="$OUT_DIR/index.html"

usage() {
  cat <<'EOF'
Usage: deviation-bench/scripts/start_dashboard.sh [options]

Build and serve the local Deviation Bench conversation dashboard.

Options:
  --host HOST       Host to bind. Default: 127.0.0.1
  --port PORT       Port to serve. Default: 8765
  --input PATTERN   JSONL file or glob. Default: deviation-bench/results/pilot/*.jsonl
  --out FILE        Dashboard HTML output. Default: deviation-bench/results/dashboard/index.html
  -h, --help        Show this help.

Example:
  deviation-bench/scripts/start_dashboard.sh --port 8765
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="${2:?--host requires a value}"
      shift 2
      ;;
    --port)
      PORT="${2:?--port requires a value}"
      shift 2
      ;;
    --input)
      INPUT_PATTERN="${2:?--input requires a value}"
      shift 2
      ;;
    --out)
      OUT_FILE="${2:?--out requires a value}"
      OUT_DIR="$(dirname "$OUT_FILE")"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$OUT_DIR"

python3 "$ROOT/src/build_conversation_dashboard.py" \
  --input "$INPUT_PATTERN" \
  --out "$OUT_FILE"

cat <<EOF

Deviation Bench dashboard is ready.
URL: http://$HOST:$PORT/
Serving directory: $OUT_DIR

Press Ctrl-C to stop the server.
EOF

cd "$OUT_DIR"
exec python3 -m http.server "$PORT" --bind "$HOST"
