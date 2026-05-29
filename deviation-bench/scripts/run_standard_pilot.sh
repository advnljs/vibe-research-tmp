#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCENARIOS="uird_pilot_002,uird_pilot_003"
MODELS="deepseek-v4-flash,deepseek-v4-pro"
JUDGE_MODEL="deepseek-v4-pro"
BASE_URL="https://api.deepseek.com"
PROMPT_STYLE="naturalistic"
OUT_DIR="$ROOT/results/pilot/standard"
KEY_FILE="$ROOT/../ds_key.txt"
TIMEOUT="180"
SLEEP_SECONDS="0.5"

usage() {
  cat <<'EOF'
Usage: deviation-bench/scripts/run_standard_pilot.sh [options]

Run full, fixed-turn Deviation Bench episodes. This script intentionally does
not use --max-induction-turns or --stop-on-factual-error, so generated JSONL
files are comparable full runs rather than development-calibration fragments.

Options:
  --scenarios IDS       Comma-separated scenario IDs. Default: uird_pilot_002,uird_pilot_003
  --models MODELS       Comma-separated target models. Default: deepseek-v4-flash,deepseek-v4-pro
  --judge-model MODEL   Judge model. Default: deepseek-v4-pro
  --base-url URL        OpenAI-compatible base URL. Default: https://api.deepseek.com
  --prompt-style STYLE  structured or naturalistic. Default: naturalistic
  --out-dir DIR         Output directory. Default: deviation-bench/results/pilot/standard
  --key-file FILE       Local key file fallback if OPENAI_API_KEY is unset. Default: ./ds_key.txt
  --timeout SECONDS     Request timeout. Default: 180
  --sleep SECONDS       Sleep between turns. Default: 0.5
  -h, --help            Show this help.

Example:
  deviation-bench/scripts/run_standard_pilot.sh \
    --scenarios uird_pilot_002,uird_pilot_003 \
    --models deepseek-v4-flash,deepseek-v4-pro
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenarios)
      SCENARIOS="${2:?--scenarios requires a value}"
      shift 2
      ;;
    --models)
      MODELS="${2:?--models requires a value}"
      shift 2
      ;;
    --judge-model)
      JUDGE_MODEL="${2:?--judge-model requires a value}"
      shift 2
      ;;
    --base-url)
      BASE_URL="${2:?--base-url requires a value}"
      shift 2
      ;;
    --prompt-style)
      PROMPT_STYLE="${2:?--prompt-style requires a value}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:?--out-dir requires a value}"
      shift 2
      ;;
    --key-file)
      KEY_FILE="${2:?--key-file requires a value}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:?--timeout requires a value}"
      shift 2
      ;;
    --sleep)
      SLEEP_SECONDS="${2:?--sleep requires a value}"
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

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  if [[ -f "$KEY_FILE" ]]; then
    OPENAI_API_KEY="$(tr -d '\r\n' < "$KEY_FILE")"
    export OPENAI_API_KEY
  else
    echo "OPENAI_API_KEY is not set and key file was not found: $KEY_FILE" >&2
    exit 1
  fi
fi

mkdir -p "$OUT_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"

IFS=',' read -r -a SCENARIO_ARRAY <<< "$SCENARIOS"
IFS=',' read -r -a MODEL_ARRAY <<< "$MODELS"

for scenario_id in "${SCENARIO_ARRAY[@]}"; do
  scenario_id="$(echo "$scenario_id" | xargs)"
  [[ -n "$scenario_id" ]] || continue
  for model in "${MODEL_ARRAY[@]}"; do
    model="$(echo "$model" | xargs)"
    [[ -n "$model" ]] || continue
    safe_model="${model//[^A-Za-z0-9_.-]/_}"
    out_file="$OUT_DIR/${STAMP}_${PROMPT_STYLE}_${safe_model}_${scenario_id}.jsonl"
    echo "running scenario=$scenario_id model=$model out=$out_file"
    python3 "$ROOT/src/deviation_bench_pilot.py" \
      --provider openai \
      --judge-provider openai \
      --scenario-id "$scenario_id" \
      --prompt-style "$PROMPT_STYLE" \
      --model "$model" \
      --judge-model "$JUDGE_MODEL" \
      --base-url "$BASE_URL" \
      --out "$out_file" \
      --timeout "$TIMEOUT" \
      --sleep "$SLEEP_SECONDS"
  done
done

echo "done. Outputs are under: $OUT_DIR"
echo "Rebuild dashboard with:"
echo "  $ROOT/scripts/start_dashboard.sh --input '$OUT_DIR/*.jsonl'"
