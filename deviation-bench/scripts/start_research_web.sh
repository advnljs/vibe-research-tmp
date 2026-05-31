#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="127.0.0.1"
PORT="8768"
OUT_DIR="$ROOT/results/web"
RESULT_GLOB="$ROOT/results/pilot/memory_real/*.jsonl"

usage() {
  cat <<'EOF'
Usage: deviation-bench/scripts/start_research_web.sh [options]

Build and serve the local Deviation Bench web workspace.

Options:
  --host HOST          Host to bind. Default: 127.0.0.1
  --port PORT          Port to serve. Default: 8768
  --out-dir DIR        Web output directory. Default: deviation-bench/results/web
  --result-glob GLOB   Real API JSONL glob. Default: deviation-bench/results/pilot/memory_real/*.jsonl
  -h, --help           Show this help.
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
    --out-dir)
      OUT_DIR="${2:?--out-dir requires a value}"
      shift 2
      ;;
    --result-glob)
      RESULT_GLOB="${2:?--result-glob requires a value}"
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

python3 "$ROOT/src/build_scenario_browser.py" \
  --out "$OUT_DIR/scenarios.html"

python3 "$ROOT/src/build_conversation_dashboard.py" \
  --input "$RESULT_GLOB" \
  --out "$OUT_DIR/memory_real_dashboard.html"

if [[ -f "$ROOT/results/working/memory_runner_all_mock.jsonl" ]]; then
  python3 "$ROOT/src/build_conversation_dashboard.py" \
    --input "$ROOT/results/working/memory_runner_all_mock.jsonl" \
    --out "$OUT_DIR/mock_all_dashboard.html"
fi

python3 "$ROOT/src/build_web_index.py" \
  --result-glob "$RESULT_GLOB" \
  --out "$OUT_DIR/index.html"

cat <<EOF

Deviation Bench web workspace is ready.
URL: http://$HOST:$PORT/
Serving directory: $OUT_DIR

Press Ctrl-C to stop the server.
EOF

cd "$OUT_DIR"
exec python3 -m http.server "$PORT" --bind "$HOST"
