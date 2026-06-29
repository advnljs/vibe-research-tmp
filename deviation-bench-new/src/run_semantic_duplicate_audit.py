#!/usr/bin/env python3
"""Run LLM-assisted semantic duplicate and leakage audit for processed sessions."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

from build_sessions import call_json_task, estimate_tokens, read_jsonl, sha256_text, utc_now
from session_contract import scan_pii


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_INPUTS = [
    ROOT / "data" / "processed" / "deepseek_v4_pro_interview_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_control_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl",
]
DEFAULT_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_64k.jsonl"
DEFAULT_FINGERPRINT_PROMPT = ROOT / "prompts" / "session_semantic_fingerprint.md"
DEFAULT_PAIR_PROMPT = ROOT / "prompts" / "semantic_duplicate_pair_review.md"
DEFAULT_FINGERPRINT_OUTPUT = ROOT / "data" / "reviews" / "deepseek_v4_pro_session_semantic_fingerprints_64k.jsonl"
DEFAULT_PAIR_OUTPUT = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl"
DEFAULT_SUMMARY_JSON = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json"
DEFAULT_SUMMARY_MD = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_audit_64k_summary.md"
DEFAULT_KEY_FILE = WORKSPACE_ROOT / "ds_key.txt"
DEFAULT_RUN_ID = "deepseek_v4_pro_semantic_duplicate_audit_64k"

ALLOWED_RISK = {"low", "medium", "high"}
ALLOWED_PAIR_DECISIONS = {"duplicate", "near_duplicate", "not_duplicate", "unclear"}
ALLOWED_LEAKAGE_RISK = {"none", "low", "medium", "high"}
ALLOWED_ACTIONS = {"keep", "same_split", "exclude_one", "manual_review"}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_sessions(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(read_jsonl(path))
    return rows


def load_splits(path: Path) -> dict[str, dict[str, Any]]:
    return {row["session_id"]: row for row in read_jsonl(path)}


def compact_messages(record: dict[str, Any], max_messages: int) -> list[dict[str, Any]]:
    messages = record.get("messages") or []
    if len(messages) <= max_messages:
        indices = list(range(len(messages)))
    else:
        point_indices = {
            index
            for point in record.get("delusion_points") or []
            for index in point.get("message_indices") or []
            if isinstance(index, int) and 0 <= index < len(messages)
        }
        seed = set(range(min(4, len(messages))))
        seed.update(range(max(0, len(messages) - 4), len(messages)))
        for index in point_indices:
            seed.update(range(max(0, index - 1), min(len(messages), index + 2)))
        indices = sorted(seed)
        if len(indices) > max_messages:
            indices = indices[: max_messages // 2] + indices[-(max_messages - max_messages // 2) :]
    return [
        {
            "message_index": index,
            "role": messages[index].get("role"),
            "content": messages[index].get("content"),
        }
        for index in indices
    ]


def fingerprint_payload_item(record: dict[str, Any], split_row: dict[str, Any], max_messages: int) -> dict[str, Any]:
    return {
        "session_id": record["session_id"],
        "source_family": split_row.get("source_family"),
        "source_group": record.get("metadata", {}).get("source_group"),
        "split": split_row.get("split"),
        "case_summary": record.get("case_summary"),
        "candidate_points": [
            {
                "category": point.get("category"),
                "summary": point.get("summary"),
                "explicitness": point.get("explicitness"),
                "uncertainty_or_counterevidence": point.get("uncertainty_or_counterevidence"),
            }
            for point in record.get("delusion_points") or []
        ],
        "compact_messages": compact_messages(record, max_messages),
    }


def make_token_batches(items: list[dict[str, Any]], max_items: int, max_tokens: int) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_tokens = 0
    for item in items:
        tokens = estimate_tokens(json.dumps(item, ensure_ascii=False, sort_keys=True))
        if current and (len(current) >= max_items or current_tokens + tokens > max_tokens):
            batches.append(current)
            current = []
            current_tokens = 0
        current.append(item)
        current_tokens += tokens
    if current:
        batches.append(current)
    return batches


def validate_fingerprint_batch(parsed: dict[str, Any], items: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    results = parsed.get("results")
    if not isinstance(results, list):
        return ["results must be a list"]
    expected = [item["session_id"] for item in items]
    actual = [item.get("session_id") if isinstance(item, dict) else None for item in results]
    if actual != expected:
        errors.append("session_id order mismatch")
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            errors.append(f"results[{index}] is not an object")
            continue
        for field in [
            "semantic_signature",
            "core_reality_boundary_pattern",
            "evidence_shape",
            "uncertainty_profile",
            "rationale",
        ]:
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"results[{index}] {field} is required")
        for field in ["belief_objects", "distinctive_nonidentifying_elements", "duplicate_screening_terms"]:
            if not isinstance(item.get(field), list):
                errors.append(f"results[{index}] {field} must be a list")
        if item.get("source_specificity_risk") not in ALLOWED_RISK:
            errors.append(f"results[{index}] invalid source_specificity_risk")
        if not isinstance(item.get("rare_event_chain_risk"), bool):
            errors.append(f"results[{index}] rare_event_chain_risk must be boolean")
        texts = [
            str(item.get("semantic_signature") or ""),
            str(item.get("core_reality_boundary_pattern") or ""),
            str(item.get("rationale") or ""),
            " ".join(str(value) for value in item.get("belief_objects") or []),
            " ".join(str(value) for value in item.get("distinctive_nonidentifying_elements") or []),
        ]
        if scan_pii(texts):
            errors.append(f"results[{index}] PII scan hit")
    return errors


def mock_fingerprint_batch(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "results": [
            {
                "session_id": item["session_id"],
                "semantic_signature": "Mock generic session fingerprint.",
                "core_reality_boundary_pattern": "mock_pattern",
                "belief_objects": ["mock object"],
                "evidence_shape": "mock evidence shape",
                "uncertainty_profile": "mixed",
                "distinctive_nonidentifying_elements": ["mock element"],
                "duplicate_screening_terms": ["mock", item["session_id"]],
                "source_specificity_risk": "low",
                "rare_event_chain_risk": False,
                "rationale": "Mock fingerprint.",
            }
            for item in items
        ]
    }


def run_fingerprint_batch(
    batch_index: int,
    items: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    payload = {"task": "session_semantic_fingerprint", "sessions": items}
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + sha256_text(prompt)
        + args.model
        + args.thinking_mode
    )
    work_dir = ROOT / "data" / "work" / "release_hardening_runs" / args.run_id / "fingerprints"
    cache_path = work_dir / f"batch_{batch_index:04d}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            errors = validate_fingerprint_batch(cached["parsed"], items)
            if not errors:
                return batch_index, cached["parsed"]["results"]

    if args.provider == "mock":
        parsed = mock_fingerprint_batch(items)
        raw_response = None
        errors = validate_fingerprint_batch(parsed, items)
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
                errors = validate_fingerprint_batch(parsed, items)
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
                "session_ids": [item["session_id"] for item in items],
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
        raise ValueError(f"fingerprint batch {batch_index} failed: {'; '.join(errors)}")
    return batch_index, parsed["results"]


def fingerprint_text(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("semantic_signature") or ""),
        str(row.get("core_reality_boundary_pattern") or ""),
        str(row.get("evidence_shape") or ""),
        str(row.get("uncertainty_profile") or ""),
        " ".join(str(value) for value in row.get("belief_objects") or []),
        " ".join(str(value) for value in row.get("distinctive_nonidentifying_elements") or []),
        " ".join(str(value) for value in row.get("duplicate_screening_terms") or []),
    ]
    return " ".join(parts)


def token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_']+", text.lower()) if len(token) >= 3}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def build_pair_candidates(
    fingerprints: list[dict[str, Any]],
    *,
    max_pairs: int,
    min_score: float,
) -> list[dict[str, Any]]:
    tokens = {row["session_id"]: token_set(fingerprint_text(row)) for row in fingerprints}
    scored: list[dict[str, Any]] = []
    for left, right in combinations(fingerprints, 2):
        same_family = left.get("source_family") == right.get("source_family")
        if not same_family:
            continue
        score = jaccard(tokens[left["session_id"]], tokens[right["session_id"]])
        if score < min_score:
            continue
        cross_split = left.get("split") != right.get("split")
        scored.append(
            {
                "pair_id": f"{left['session_id']}__{right['session_id']}",
                "lexical_fingerprint_score": round(score, 6),
                "cross_split": cross_split,
                "left": left,
                "right": right,
            }
        )
    scored.sort(key=lambda item: (-item["lexical_fingerprint_score"], item["pair_id"]))
    return scored[:max_pairs]


def pair_payload_item(pair: dict[str, Any]) -> dict[str, Any]:
    def compact(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": row["session_id"],
            "split": row.get("split"),
            "source_family": row.get("source_family"),
            "semantic_signature": row.get("semantic_signature"),
            "core_reality_boundary_pattern": row.get("core_reality_boundary_pattern"),
            "belief_objects": row.get("belief_objects"),
            "evidence_shape": row.get("evidence_shape"),
            "uncertainty_profile": row.get("uncertainty_profile"),
            "distinctive_nonidentifying_elements": row.get("distinctive_nonidentifying_elements"),
            "duplicate_screening_terms": row.get("duplicate_screening_terms"),
        }

    return {
        "pair_id": pair["pair_id"],
        "lexical_fingerprint_score": pair["lexical_fingerprint_score"],
        "cross_split": pair["cross_split"],
        "left": compact(pair["left"]),
        "right": compact(pair["right"]),
    }


def validate_pair_batch(parsed: dict[str, Any], pairs: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    results = parsed.get("results")
    if not isinstance(results, list):
        return ["results must be a list"]
    expected = [pair["pair_id"] for pair in pairs]
    actual = [item.get("pair_id") if isinstance(item, dict) else None for item in results]
    if actual != expected:
        errors.append("pair_id order mismatch")
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            errors.append(f"results[{index}] is not an object")
            continue
        if item.get("decision") not in ALLOWED_PAIR_DECISIONS:
            errors.append(f"results[{index}] invalid decision")
        if item.get("leakage_risk") not in ALLOWED_LEAKAGE_RISK:
            errors.append(f"results[{index}] invalid leakage_risk")
        if not isinstance(item.get("cross_split_risk"), bool):
            errors.append(f"results[{index}] cross_split_risk must be boolean")
        if item.get("recommended_action") not in ALLOWED_ACTIONS:
            errors.append(f"results[{index}] invalid recommended_action")
        for field in ["shared_semantic_elements", "distinguishing_elements"]:
            if not isinstance(item.get(field), list):
                errors.append(f"results[{index}] {field} must be a list")
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(f"results[{index}] rationale is required")
        if scan_pii([str(rationale or ""), " ".join(str(value) for value in item.get("shared_semantic_elements") or [])]):
            errors.append(f"results[{index}] PII scan hit")
    return errors


def mock_pair_batch(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "results": [
            {
                "pair_id": pair["pair_id"],
                "decision": "not_duplicate",
                "leakage_risk": "none",
                "cross_split_risk": False,
                "recommended_action": "keep",
                "shared_semantic_elements": [],
                "distinguishing_elements": ["mock distinction"],
                "rationale": "Mock pair review does not find duplication.",
            }
            for pair in pairs
        ]
    }


def run_pair_batch(
    batch_index: int,
    pairs: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    payload_pairs = [pair_payload_item(pair) for pair in pairs]
    payload = {"task": "semantic_duplicate_pair_review", "pairs": payload_pairs}
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + sha256_text(prompt)
        + args.model
        + args.thinking_mode
    )
    work_dir = ROOT / "data" / "work" / "release_hardening_runs" / args.run_id / "duplicate_pairs"
    cache_path = work_dir / f"batch_{batch_index:04d}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            errors = validate_pair_batch(cached["parsed"], pairs)
            if not errors:
                return batch_index, cached["parsed"]["results"]

    if args.provider == "mock":
        parsed = mock_pair_batch(pairs)
        raw_response = None
        errors = validate_pair_batch(parsed, pairs)
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
                errors = validate_pair_batch(parsed, pairs)
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
                "pair_ids": [pair["pair_id"] for pair in pairs],
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
        raise ValueError(f"duplicate pair batch {batch_index} failed: {'; '.join(errors)}")
    return batch_index, parsed["results"]


def run_parallel_batches(
    fn: Any,
    batches: list[list[dict[str, Any]]],
    prompt: str,
    args: argparse.Namespace,
    label: str,
) -> list[dict[str, Any]]:
    results_by_batch: dict[int, list[dict[str, Any]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(fn, batch_index, batch, prompt, args): batch_index
            for batch_index, batch in enumerate(batches, start=1)
        }
        for future in concurrent.futures.as_completed(futures):
            batch_index, batch_results = future.result()
            results_by_batch[batch_index] = batch_results
            print(f"{label}_batch={batch_index}/{len(batches)} results={len(batch_results)}", flush=True)
    return [item for batch_index in sorted(results_by_batch) for item in results_by_batch[batch_index]]


def attach_fingerprint_metadata(
    fingerprints: list[dict[str, Any]],
    payload_items: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    by_id = {item["session_id"]: item for item in payload_items}
    rows = []
    for item in fingerprints:
        source = by_id[item["session_id"]]
        rows.append(
            {
                "run_id": args.run_id,
                "model": args.model,
                "provider": args.provider,
                "generated_at": args.generated_at,
                "session_id": item["session_id"],
                "source_family": source.get("source_family"),
                "source_group": source.get("source_group"),
                "split": source.get("split"),
                "candidate_point_count": len(source.get("candidate_points") or []),
                **item,
            }
        )
    return rows


def attach_pair_metadata(
    pair_reviews: list[dict[str, Any]],
    pair_candidates: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    by_id = {item["pair_id"]: item for item in pair_candidates}
    rows = []
    for review in pair_reviews:
        candidate = by_id[review["pair_id"]]
        rows.append(
            {
                "run_id": args.run_id,
                "model": args.model,
                "provider": args.provider,
                "generated_at": args.generated_at,
                "pair_id": review["pair_id"],
                "left_session_id": candidate["left"]["session_id"],
                "right_session_id": candidate["right"]["session_id"],
                "source_family": candidate["left"].get("source_family"),
                "left_split": candidate["left"].get("split"),
                "right_split": candidate["right"].get("split"),
                "candidate_cross_split": candidate["cross_split"],
                "lexical_fingerprint_score": candidate["lexical_fingerprint_score"],
                **review,
            }
        )
    return rows


def write_summary(
    fingerprints: list[dict[str, Any]],
    pair_candidates: list[dict[str, Any]],
    pair_reviews: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    summary = {
        "run_id": args.run_id,
        "model": args.model,
        "provider": args.provider,
        "generated_at": args.generated_at,
        "fingerprint_count": len(fingerprints),
        "pair_candidate_count": len(pair_candidates),
        "pair_review_count": len(pair_reviews),
        "pair_candidate_min_score": args.pair_min_score,
        "pair_candidate_max_pairs": args.max_pair_reviews,
        "counts": {
            "source_family": dict(sorted(Counter(row.get("source_family") for row in fingerprints).items())),
            "source_specificity_risk": dict(
                sorted(Counter(row.get("source_specificity_risk") for row in fingerprints).items())
            ),
            "rare_event_chain_risk": dict(
                sorted(Counter(str(row.get("rare_event_chain_risk")) for row in fingerprints).items())
            ),
            "pair_decision": dict(sorted(Counter(row.get("decision") for row in pair_reviews).items())),
            "pair_leakage_risk": dict(sorted(Counter(row.get("leakage_risk") for row in pair_reviews).items())),
            "pair_recommended_action": dict(
                sorted(Counter(row.get("recommended_action") for row in pair_reviews).items())
            ),
        },
        "medium_or_high_leakage_pairs": [
            {
                "pair_id": row["pair_id"],
                "left_session_id": row["left_session_id"],
                "right_session_id": row["right_session_id"],
                "decision": row.get("decision"),
                "leakage_risk": row.get("leakage_risk"),
                "recommended_action": row.get("recommended_action"),
            }
            for row in pair_reviews
            if row.get("leakage_risk") in {"medium", "high"}
        ],
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_lines = [
        "# Semantic Duplicate Audit Summary",
        "",
        f"- Run ID: `{args.run_id}`",
        f"- Model: `{args.model}`",
        f"- Fingerprints: {len(fingerprints)}",
        f"- Pair candidates reviewed: {len(pair_reviews)}",
        f"- Medium/high leakage pairs: {len(summary['medium_or_high_leakage_pairs'])}",
        "",
        "## Pair Decisions",
        "",
    ]
    for decision, count in summary["counts"]["pair_decision"].items():
        md_lines.append(f"- `{decision}`: {count}")
    md_lines.extend(["", "## Recommended Actions", ""])
    for action, count in summary["counts"]["pair_recommended_action"].items():
        md_lines.append(f"- `{action}`: {count}")
    args.summary_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--base-url", default="https://api.deepseek.com")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--split-manifest", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--fingerprint-prompt", type=Path, default=DEFAULT_FINGERPRINT_PROMPT)
    parser.add_argument("--pair-prompt", type=Path, default=DEFAULT_PAIR_PROMPT)
    parser.add_argument("--fingerprint-output", type=Path, default=DEFAULT_FINGERPRINT_OUTPUT)
    parser.add_argument("--pair-output", type=Path, default=DEFAULT_PAIR_OUTPUT)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--summary-md", type=Path, default=DEFAULT_SUMMARY_MD)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fingerprint-batch-size", type=int, default=10)
    parser.add_argument("--pair-batch-size", type=int, default=20)
    parser.add_argument("--max-batch-input-tokens", type=int, default=24000)
    parser.add_argument("--max-compact-messages", type=int, default=16)
    parser.add_argument("--pair-min-score", type=float, default=0.20)
    parser.add_argument("--max-pair-reviews", type=int, default=240)
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
    for path in [args.fingerprint_output, args.pair_output, args.summary_json, args.summary_md]:
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"output exists; pass --overwrite: {path}")
    args.generated_at = utc_now()
    args.api_key = os.getenv("OPENAI_API_KEY", "")
    if args.provider == "openai" and not args.api_key and args.key_file.exists():
        args.api_key = args.key_file.read_text(encoding="utf-8").strip()
    if args.provider == "openai" and not args.api_key:
        raise ValueError(f"API key unavailable: {args.key_file}")

    sessions = load_sessions(args.input or DEFAULT_INPUTS)
    sessions.sort(key=lambda item: item["session_id"])
    if args.limit is not None:
        sessions = sessions[: args.limit]
    splits = load_splits(args.split_manifest)
    payload_items = [
        fingerprint_payload_item(record, splits.get(record["session_id"], {}), args.max_compact_messages)
        for record in sessions
    ]
    fingerprint_prompt = args.fingerprint_prompt.read_text(encoding="utf-8")
    fingerprint_batches = make_token_batches(
        payload_items,
        max_items=args.fingerprint_batch_size,
        max_tokens=args.max_batch_input_tokens,
    )
    fingerprints = run_parallel_batches(
        run_fingerprint_batch,
        fingerprint_batches,
        fingerprint_prompt,
        args,
        "fingerprint",
    )
    fingerprint_rows = attach_fingerprint_metadata(fingerprints, payload_items, args)
    write_jsonl(args.fingerprint_output, fingerprint_rows)

    pair_candidates = build_pair_candidates(
        fingerprint_rows,
        max_pairs=args.max_pair_reviews,
        min_score=args.pair_min_score,
    )
    pair_prompt = args.pair_prompt.read_text(encoding="utf-8")
    pair_batches = make_token_batches(
        pair_candidates,
        max_items=args.pair_batch_size,
        max_tokens=args.max_batch_input_tokens,
    )
    pair_reviews_raw = (
        run_parallel_batches(run_pair_batch, pair_batches, pair_prompt, args, "pair") if pair_batches else []
    )
    pair_rows = attach_pair_metadata(pair_reviews_raw, pair_candidates, args)
    write_jsonl(args.pair_output, pair_rows)
    summary = write_summary(fingerprint_rows, pair_candidates, pair_rows, args)
    print(
        f"fingerprints={summary['fingerprint_count']} pair_candidates={summary['pair_candidate_count']} "
        f"pair_reviews={summary['pair_review_count']} medium_high={len(summary['medium_or_high_leakage_pairs'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
