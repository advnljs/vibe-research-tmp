# Deviation Bench Runner

This directory contains the first API-only pilot runner.

Validate scenario files:

```bash
python3 deviation-bench/src/deviation_bench_pilot.py --validate-only
```

Run one offline mock smoke test:

```bash
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider mock \
  --judge-provider mock \
  --limit 1 \
  --out deviation-bench/results/pilot/mock_smoke.jsonl
```

Run against an OpenAI-compatible chat completions endpoint:

```bash
OPENAI_API_KEY=... \
OPENAI_MODEL=... \
python3 deviation-bench/src/deviation_bench_pilot.py \
  --provider openai \
  --judge-provider openai \
  --limit 1 \
  --out deviation-bench/results/pilot/openai_smoke.jsonl
```

Optional environment variables:

- `OPENAI_BASE_URL`, default `https://api.openai.com/v1`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `JUDGE_MODEL`, defaults to `OPENAI_MODEL`

`deviation-bench/results/` is git-ignored because it contains generated outputs.
