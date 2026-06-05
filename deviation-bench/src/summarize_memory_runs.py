#!/usr/bin/env python3
"""Summarize memory-condition runs and compute MIDA against full transcript."""

from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


MIDA_METRICS = [
    "rds_auc",
    "factual_error_rate",
    "reality_drift_event_rate",
    "confabulatory_elaboration_rate",
    "certainty_inflation_rate",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Deviation Bench memory-condition JSONL runs.")
    parser.add_argument("--input", action="append", required=True, help="JSONL path or glob. Can repeat.")
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def resolve_inputs(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            paths.extend(Path(match) for match in matches)
        elif Path(pattern).exists():
            paths.append(Path(pattern))
    return sorted(set(path.resolve() for path in paths))


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def relation_matches(relation: str, target: str) -> bool:
    return relation == target


def trace_metrics(turns: list[dict[str, Any]]) -> dict[str, Any]:
    traces = [turn.get("memory_trace") or {} for turn in turns]
    assemblies = [trace.get("context_assembly") or {} for trace in traces]
    context_items = [item for trace in traces for item in (trace.get("context_items") or [])]
    provenance_items = [item for item in context_items if item.get("provenance_available")]
    distortion_items = [item for item in context_items if item.get("distortion_flags")]
    evaluated_relation_items = [
        item for item in context_items if item.get("relation_check_status") not in {None, "not_evaluated"}
    ]

    evidence_turns = 0
    unsupported_turns = 0
    for trace in traces:
        items = trace.get("context_items") or []
        if any(relation_matches(str(item.get("evidence_relation")), "evidence_anchor") for item in items):
            evidence_turns += 1
        if any(relation_matches(str(item.get("evidence_relation")), "unsupported_claim") for item in items):
            unsupported_turns += 1

    recovery_index = next((index for index, trace in enumerate(traces) if trace.get("turn_id") == "recovery"), None)
    post_recovery_traces = traces[recovery_index + 1 :] if recovery_index is not None else []
    recovery_retained = (
        any(
            relation_matches(str(item.get("evidence_relation")), "recovery_anchor")
            for trace in post_recovery_traces
            for item in (trace.get("context_items") or [])
        )
        if post_recovery_traces
        else None
    )
    full_tokens = [
        value
        for value in (numeric(assembly.get("full_transcript_tokens")) for assembly in assemblies)
        if value is not None
    ]
    context_tokens = [
        value
        for value in (numeric(assembly.get("condition_context_tokens")) for assembly in assemblies)
        if value is not None
    ]
    compression = [
        value
        for value in (numeric(assembly.get("compression_ratio")) for assembly in assemblies)
        if value is not None
    ]
    turn_count = len(traces)
    return {
        "turn_count": turn_count,
        "average_full_transcript_tokens": mean(full_tokens),
        "average_condition_context_tokens": mean(context_tokens),
        "average_compression_ratio": mean(compression),
        "evidence_retention_rate": evidence_turns / turn_count if turn_count else None,
        "unsupported_claim_retention_rate": unsupported_turns / turn_count if turn_count else None,
        "recovery_anchor_retention": recovery_retained,
        "provenance_coverage": len(provenance_items) / len(context_items) if context_items else None,
        "memory_distortion_rate": len(distortion_items) / len(context_items) if context_items else None,
        "relation_evaluation_coverage": (
            len(evaluated_relation_items) / len(context_items) if context_items else None
        ),
    }


def load_runs(paths: list[Path]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            record = raw.get("record") if isinstance(raw.get("record"), dict) else raw
            metrics = dict(record.get("metrics") or {})
            recovery = metrics.get("recovery_reliability")
            metrics["recovery_failure_rate"] = None if recovery is None else float(not recovery)
            runs.append(
                {
                    "source_file": str(path),
                    "line_number": line_number,
                    "run_id": raw.get("run_id"),
                    "scenario_id": record.get("scenario_id"),
                    "model": raw.get("model") or record.get("model"),
                    "judge_model": raw.get("judge_model") or record.get("judge_model"),
                    "prompt_style": raw.get("prompt_style") or record.get("prompt_style"),
                    "memory_model": raw.get("memory_model"),
                    "memory_provider": raw.get("memory_provider"),
                    "memory_condition": (
                        raw.get("memory_condition") or record.get("memory_condition") or "full_transcript"
                    ),
                    "memory_config": record.get("memory_config") or {},
                    "token_window": (record.get("memory_config") or {}).get("token_window"),
                    "metrics": metrics,
                    "memory_metrics": trace_metrics(record.get("turns") or []),
                }
            )
    return runs


def comparison_key(run: dict[str, Any]) -> tuple[Any, ...]:
    return (
        run.get("scenario_id"),
        run.get("model"),
        run.get("judge_model"),
        run.get("prompt_style"),
        run.get("token_window"),
    )


def aggregate_metric(runs: list[dict[str, Any]], section: str, metric: str) -> float | None:
    values = [
        value
        for value in (numeric(run.get(section, {}).get(metric)) for run in runs)
        if value is not None
    ]
    return mean(values)


def condition_config_key(run: dict[str, Any]) -> tuple[Any, ...]:
    return (
        run["memory_condition"],
        run.get("memory_provider"),
        run.get("memory_model"),
        json.dumps(run.get("memory_config") or {}, ensure_ascii=False, sort_keys=True),
    )


def build_summary(paths: list[Path], runs: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        groups[comparison_key(run)].append(run)

    comparisons: list[dict[str, Any]] = []
    for key, group in sorted(groups.items(), key=lambda item: str(item[0])):
        baselines = [run for run in group if run["memory_condition"] == "full_transcript"]
        if not baselines:
            continue
        condition_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for run in group:
            condition_groups[condition_config_key(run)].append(run)
        for condition_key, condition_runs in sorted(condition_groups.items(), key=lambda item: str(item[0])):
            condition = condition_key[0]
            metrics: dict[str, Any] = {}
            for metric in MIDA_METRICS + ["recovery_failure_rate"]:
                baseline_value = aggregate_metric(baselines, "metrics", metric)
                condition_value = aggregate_metric(condition_runs, "metrics", metric)
                metrics[metric] = {
                    "full_transcript": baseline_value,
                    "condition": condition_value,
                    "mida": (
                        condition_value - baseline_value
                        if condition_value is not None and baseline_value is not None
                        else None
                    ),
                }
            memory_metrics = {
                metric: aggregate_metric(condition_runs, "memory_metrics", metric)
                for metric in [
                    "average_full_transcript_tokens",
                    "average_condition_context_tokens",
                    "average_compression_ratio",
                    "evidence_retention_rate",
                    "unsupported_claim_retention_rate",
                    "provenance_coverage",
                    "memory_distortion_rate",
                    "relation_evaluation_coverage",
                ]
            }
            recovery_values = [
                run["memory_metrics"].get("recovery_anchor_retention")
                for run in condition_runs
                if run["memory_metrics"].get("recovery_anchor_retention") is not None
            ]
            memory_metrics["recovery_anchor_retention"] = (
                sum(1 for value in recovery_values if value) / len(recovery_values) if recovery_values else None
            )
            comparisons.append(
                {
                    "scenario_id": key[0],
                    "model": key[1],
                    "judge_model": key[2],
                    "prompt_style": key[3],
                    "token_window": key[4],
                    "condition": condition,
                    "memory_provider": condition_key[1],
                    "memory_model": condition_key[2],
                    "memory_config": condition_runs[0].get("memory_config") or {},
                    "run_count": len(condition_runs),
                    "baseline_run_count": len(baselines),
                    "metrics": metrics,
                    "memory_metrics": memory_metrics,
                }
            )

    return {
        "input_files": [str(path) for path in paths],
        "run_count": len(runs),
        "comparison_count": len(comparisons),
        "mida_definition": "condition metric minus matched full_transcript metric",
        "comparisons": comparisons,
    }


def main() -> None:
    args = parse_args()
    paths = resolve_inputs(args.input)
    if not paths:
        raise ValueError("no input files matched")
    runs = load_runs(paths)
    summary = build_summary(paths, runs)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"wrote={args.out} runs={len(runs)} comparisons={summary['comparison_count']}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
