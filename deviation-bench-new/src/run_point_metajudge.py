#!/usr/bin/env python3
"""Run independent point metajudge review over candidate points and negative controls."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from build_sessions import call_json_task, estimate_tokens, read_jsonl, sha256_text, utc_now
from session_contract import ALLOWED_CATEGORIES, scan_pii


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_INPUT = ROOT / "data" / "manifests" / "deepseek_v4_pro_point_review_units_64k.jsonl"
DEFAULT_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_64k.jsonl"
DEFAULT_PROMPT = ROOT / "prompts" / "point_metajudge.md"
DEFAULT_OUTPUT = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k.jsonl"
DEFAULT_SUMMARY_JSON = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k_summary.json"
DEFAULT_SUMMARY_MD = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k_summary.md"
DEFAULT_KEY_FILE = WORKSPACE_ROOT / "ds_key.txt"
DEFAULT_RUN_ID = "deepseek_v4_pro_point_metajudge_64k"

UNIT_DECISIONS = {
    "candidate_point": {"accept_candidate", "reject_insufficient_evidence", "revise_candidate"},
    "negative_control": {"accept_no_candidate_point", "flag_possible_missed_candidate", "unclear"},
}
ALLOWED_SUPPORT = {"direct", "indirect", "weak_or_none", "not_applicable"}
BOOL_FIELDS = [
    "category_valid",
    "explicitness_valid",
    "summary_overreach",
    "uncertainty_preserved",
    "diagnosis_or_membership_inference",
    "identifying_detail_risk",
]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_splits(path: Path) -> dict[str, dict[str, Any]]:
    return {row["session_id"]: row for row in read_jsonl(path)}


def load_sessions(inputs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in inputs:
        rows.extend(read_jsonl(path))
    return rows


def negative_control_units(
    sessions: list[dict[str, Any]],
    splits: dict[str, dict[str, Any]],
    *,
    dataset_version: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in sorted(sessions, key=lambda item: item["session_id"]):
        if record.get("delusion_points"):
            continue
        split_row = splits.get(record["session_id"], {})
        messages = record.get("messages") or []
        rows.append(
            {
                "dataset_version": dataset_version,
                "review_unit_id": f"{record['session_id']}::negative_control",
                "unit_type": "negative_control",
                "session_id": record["session_id"],
                "point_id": None,
                "split": split_row.get("split"),
                "source_family": split_row.get("source_family"),
                "source_group": record.get("metadata", {}).get("source_group"),
                "category": None,
                "explicitness": None,
                "confidence": None,
                "candidate_summary": None,
                "uncertainty_or_counterevidence": record.get("no_delusion_point_reason"),
                "message_indices": [],
                "evidence_messages": [],
                "local_context_messages": [
                    {
                        "message_index": index,
                        "role": message.get("role"),
                        "content": message.get("content"),
                    }
                    for index, message in enumerate(messages)
                ],
                "review_instruction": "Negative control: verify that no clear participant/user reality-boundary candidate is present in the processed messages.",
            }
        )
    return rows


def normalize_candidate_units(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        item = dict(row)
        item.setdefault("unit_type", "candidate_point")
        normalized.append(item)
    return normalized


def unit_token_estimate(unit: dict[str, Any]) -> int:
    return estimate_tokens(json.dumps(unit, ensure_ascii=False, sort_keys=True))


def make_batches(units: list[dict[str, Any]], max_units: int, max_tokens: int) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_tokens = 0
    for unit in units:
        tokens = unit_token_estimate(unit)
        if current and (len(current) >= max_units or current_tokens + tokens > max_tokens):
            batches.append(current)
            current = []
            current_tokens = 0
        current.append(unit)
        current_tokens += tokens
    if current:
        batches.append(current)
    return batches


def validate_batch_result(parsed: dict[str, Any], units: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    results = parsed.get("results")
    if not isinstance(results, list):
        return ["results must be a list"]
    expected = [unit["review_unit_id"] for unit in units]
    actual = [item.get("review_unit_id") if isinstance(item, dict) else None for item in results]
    if actual != expected:
        errors.append("review_unit_id order mismatch")
    by_id = {unit["review_unit_id"]: unit for unit in units}
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            errors.append(f"results[{index}] is not an object")
            continue
        unit = by_id.get(str(item.get("review_unit_id")))
        unit_type = str(unit.get("unit_type") if unit else "candidate_point")
        if item.get("decision") not in UNIT_DECISIONS.get(unit_type, set()):
            errors.append(f"results[{index}] invalid decision for {unit_type}")
        if item.get("support_level") not in ALLOWED_SUPPORT:
            errors.append(f"results[{index}] invalid support_level")
        for field in BOOL_FIELDS:
            if not isinstance(item.get(field), bool):
                errors.append(f"results[{index}] {field} must be boolean")
        revised_category = item.get("revised_category")
        if revised_category is not None and revised_category not in ALLOWED_CATEGORIES:
            errors.append(f"results[{index}] invalid revised_category")
        revised_summary = item.get("revised_summary")
        if revised_summary is not None and not isinstance(revised_summary, str):
            errors.append(f"results[{index}] revised_summary must be null/string")
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"results[{index}] rationale is required")
        if scan_pii([str(revised_summary or ""), str(rationale or "")]):
            errors.append(f"results[{index}] PII scan hit")
    return errors


def mock_batch(units: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    for unit in units:
        unit_type = unit.get("unit_type", "candidate_point")
        results.append(
            {
                "review_unit_id": unit["review_unit_id"],
                "decision": "accept_no_candidate_point" if unit_type == "negative_control" else "accept_candidate",
                "support_level": "not_applicable" if unit_type == "negative_control" else "direct",
                "category_valid": True,
                "explicitness_valid": True,
                "summary_overreach": False,
                "uncertainty_preserved": True,
                "diagnosis_or_membership_inference": False,
                "identifying_detail_risk": False,
                "revised_category": None,
                "revised_summary": None,
                "rationale": "Mock review accepts the existing unit status.",
            }
        )
    return {"results": results}


def run_batch(
    batch_index: int,
    units: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    payload = {"task": "point_metajudge", "review_units": units}
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + sha256_text(prompt)
        + args.model
        + args.thinking_mode
    )
    work_dir = ROOT / "data" / "work" / "release_hardening_runs" / args.run_id / "point_metajudge"
    cache_path = work_dir / f"batch_{batch_index:04d}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            errors = validate_batch_result(cached["parsed"], units)
            if not errors:
                return batch_index, cached["parsed"]["results"]

    if args.provider == "mock":
        parsed = mock_batch(units)
        raw_response = None
        errors = validate_batch_result(parsed, units)
    else:
        parsed = {}
        raw_response = None
        errors: list[str] = []
        for attempt in range(args.validation_retries + 1):
            try:
                parsed, raw_response = call_json_task(
                    provider=args.provider,
                    api_key=args.api_key,
                    base_url=args.base_url,
                    model=args.model,
                    system_prompt=prompt,
                    payload=payload,
                    temperature=args.temperature,
                    max_tokens=args.max_output_tokens,
                    timeout=args.timeout,
                    max_retries=args.http_retries,
                    context_window_tokens=args.context_window_tokens,
                    thinking_mode=args.thinking_mode,
                    correction_errors=errors or None,
                )
                errors = validate_batch_result(parsed, units)
            except (ValueError, RuntimeError) as exc:
                errors = [str(exc)]
            if not errors:
                break
    work_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "payload_hash": payload_hash,
                "batch_index": batch_index,
                "unit_ids": [unit["review_unit_id"] for unit in units],
                "parsed": parsed,
                "raw_response": raw_response,
                "errors": errors,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if errors:
        raise ValueError(f"point metajudge batch {batch_index} failed: {'; '.join(errors)}")
    return batch_index, parsed["results"]


def attach_metadata(results: list[dict[str, Any]], units: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    units_by_id = {unit["review_unit_id"]: unit for unit in units}
    rows = []
    for item in results:
        unit = units_by_id[item["review_unit_id"]]
        rows.append(
            {
                "run_id": args.run_id,
                "model": args.model,
                "provider": args.provider,
                "generated_at": args.generated_at,
                "dataset_version": unit.get("dataset_version"),
                "unit_type": unit.get("unit_type", "candidate_point"),
                "session_id": unit.get("session_id"),
                "point_id": unit.get("point_id"),
                "split": unit.get("split"),
                "source_family": unit.get("source_family"),
                "source_group": unit.get("source_group"),
                "candidate_category": unit.get("category"),
                "candidate_explicitness": unit.get("explicitness"),
                "candidate_confidence": unit.get("confidence"),
                **item,
            }
        )
    return rows


def write_summary(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    total = len(rows)
    candidates = [row for row in rows if row.get("unit_type") == "candidate_point"]
    negatives = [row for row in rows if row.get("unit_type") == "negative_control"]
    candidate_acceptance_rate = (
        sum(row.get("decision") == "accept_candidate" for row in candidates) / len(candidates)
        if candidates
        else None
    )
    candidate_revision_or_rejection_rate = (
        sum(row.get("decision") in {"reject_insufficient_evidence", "revise_candidate"} for row in candidates)
        / len(candidates)
        if candidates
        else None
    )
    negative_control_flag_rate = (
        sum(row.get("decision") == "flag_possible_missed_candidate" for row in negatives) / len(negatives)
        if negatives
        else None
    )
    summary = {
        "run_id": args.run_id,
        "model": args.model,
        "provider": args.provider,
        "generated_at": args.generated_at,
        "input_units": total,
        "candidate_units": len(candidates),
        "negative_control_units": len(negatives),
        "counts": {
            "decision": dict(sorted(Counter(row.get("decision") for row in rows).items())),
            "decision_by_unit_type": {
                unit_type: dict(sorted(Counter(row.get("decision") for row in rows if row.get("unit_type") == unit_type).items()))
                for unit_type in sorted({str(row.get("unit_type")) for row in rows})
            },
            "source_family": dict(sorted(Counter(row.get("source_family") for row in rows).items())),
            "split": dict(sorted(Counter(row.get("split") for row in rows).items())),
        },
        "candidate_acceptance_rate": round(candidate_acceptance_rate, 6)
        if candidate_acceptance_rate is not None
        else None,
        "candidate_revision_or_rejection_rate": round(candidate_revision_or_rejection_rate, 6)
        if candidate_revision_or_rejection_rate is not None
        else None,
        "negative_control_flag_rate": round(negative_control_flag_rate, 6)
        if negative_control_flag_rate is not None
        else None,
        "diagnosis_or_membership_inference_count": sum(
            row.get("diagnosis_or_membership_inference") is True for row in rows
        ),
        "identifying_detail_risk_count": sum(row.get("identifying_detail_risk") is True for row in rows),
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_lines = [
        "# Point Metajudge Summary",
        "",
        f"- Run ID: `{args.run_id}`",
        f"- Model: `{args.model}`",
        f"- Units: {total}",
        f"- Candidate points: {len(candidates)}",
        f"- Negative controls: {len(negatives)}",
        f"- Candidate acceptance rate: {summary['candidate_acceptance_rate']}",
        f"- Candidate revision/rejection rate: {summary['candidate_revision_or_rejection_rate']}",
        f"- Negative control flag rate: {summary['negative_control_flag_rate']}",
        f"- Diagnosis/membership inference flags: {summary['diagnosis_or_membership_inference_count']}",
        f"- Identifying detail risk flags: {summary['identifying_detail_risk_count']}",
        "",
        "## Decisions",
        "",
    ]
    for decision, count in summary["counts"]["decision"].items():
        md_lines.append(f"- `{decision}`: {count}")
    args.summary_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--base-url", default="https://api.deepseek.com")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--split-manifest", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--processed-input", action="append", type=Path, default=[])
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--summary-md", type=Path, default=DEFAULT_SUMMARY_MD)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--include-negative-controls", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--max-batch-input-tokens", type=int, default=24000)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--context-window-tokens", type=int, default=65536)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--thinking-mode", choices=["disabled", "enabled", "omit"], default="disabled")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--http-retries", type=int, default=2)
    parser.add_argument("--validation-retries", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.context_window_tokens != 65536:
        raise ValueError("this dataset is frozen to a 64k (65536-token) context window")
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output exists; pass --overwrite: {args.output}")
    args.generated_at = utc_now()
    args.api_key = os.getenv("OPENAI_API_KEY", "")
    if args.provider == "openai" and not args.api_key and args.key_file.exists():
        args.api_key = args.key_file.read_text(encoding="utf-8").strip()
    if args.provider == "openai" and not args.api_key:
        raise ValueError(f"API key unavailable: {args.key_file}")

    units = normalize_candidate_units(read_jsonl(args.input))
    if args.include_negative_controls:
        split_rows = load_splits(args.split_manifest)
        processed_inputs = args.processed_input or [
            ROOT / "data" / "processed" / "deepseek_v4_pro_interview_sessions_64k.jsonl",
            ROOT / "data" / "processed" / "deepseek_v4_pro_control_sessions_64k.jsonl",
            ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl",
        ]
        dataset_version = units[0].get("dataset_version") if units else "unknown"
        units.extend(negative_control_units(load_sessions(processed_inputs), split_rows, dataset_version=dataset_version))
    if args.limit is not None:
        units = units[: args.limit]
    prompt = args.prompt.read_text(encoding="utf-8")
    batches = make_batches(units, args.batch_size, args.max_batch_input_tokens)

    results_by_batch: dict[int, list[dict[str, Any]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_batch, batch_index, batch, prompt, args): batch_index
            for batch_index, batch in enumerate(batches, start=1)
        }
        for future in concurrent.futures.as_completed(futures):
            batch_index, batch_results = future.result()
            results_by_batch[batch_index] = batch_results
            print(f"completed_batch={batch_index}/{len(batches)} results={len(batch_results)}", flush=True)

    ordered_results = [
        item
        for batch_index in sorted(results_by_batch)
        for item in results_by_batch[batch_index]
    ]
    rows = attach_metadata(ordered_results, units, args)
    write_jsonl(args.output, rows)
    summary = write_summary(rows, args)
    print(
        f"units={summary['input_units']} candidates={summary['candidate_units']} "
        f"negative_controls={summary['negative_control_units']} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
