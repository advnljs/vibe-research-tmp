#!/usr/bin/env python3
"""Summarize Deviation Bench pilot JSONL outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


METRIC_FIELDS = [
    "rds_auc",
    "induction_susceptibility",
    "reality_drift_event_rate",
    "unjustified_reversal_rate",
    "recovery_reliability",
    "residual_drift",
]


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL line") from exc
    return records


def numeric_mean(values: list[Any]) -> float | None:
    numeric = [value for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
    return mean(numeric) if numeric else None


def bool_rate(values: list[Any]) -> float | None:
    bools = [value for value in values if isinstance(value, bool)]
    return sum(1 for value in bools if value) / len(bools) if bools else None


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_track: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stance_counts: Counter[str] = Counter()
    safety_counts: Counter[str] = Counter()

    for record in records:
        model = record.get("model", "unknown")
        result = record["record"]
        by_model[model].append(record)
        by_family[result.get("family", "unknown")].append(record)
        by_track[result.get("track", "unknown")].append(record)
        for turn in result.get("turns", []):
            judge = turn.get("judge", {})
            stance_counts[judge.get("stance", "unknown")] += 1
            safety_counts.update(judge.get("safety_flags", []))

    return {
        "records": len(records),
        "models": sorted(by_model.keys()),
        "overall": summarize_group(records),
        "by_model": {key: summarize_group(value) for key, value in sorted(by_model.items())},
        "by_track": {key: summarize_group(value) for key, value in sorted(by_track.items())},
        "by_family": {key: summarize_group(value) for key, value in sorted(by_family.items())},
        "stance_counts": dict(stance_counts),
        "safety_counts": dict(safety_counts),
    }


def summarize_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = [record["record"].get("metrics", {}) for record in records]
    summary: dict[str, Any] = {"n": len(records)}
    for field in METRIC_FIELDS:
        values = [metric.get(field) for metric in metrics]
        if field == "recovery_reliability":
            summary[field] = bool_rate(values)
        else:
            summary[field] = numeric_mean(values)
    return summary


def write_csv(summary: dict[str, Any], path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for group_name, groups in [
        ("overall", {"overall": summary["overall"]}),
        ("model", summary["by_model"]),
        ("track", summary["by_track"]),
        ("family", summary["by_family"]),
    ]:
        for key, values in groups.items():
            row = {"group_type": group_name, "group": key, **values}
            rows.append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["group_type", "group", "n", *METRIC_FIELDS])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Deviation Bench pilot results.")
    parser.add_argument("input", type=Path, help="Pilot JSONL output file.")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--csv-out", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.input)
    summary = summarize(records)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.csv_out:
        write_csv(summary, args.csv_out)


if __name__ == "__main__":
    main()
