#!/usr/bin/env python3
"""Build deterministic release-hardening artifacts for Deviation Bench New."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from session_contract import normalize_words, scan_pii, validate_session_record


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT / "data" / "processed" / "deepseek_v4_pro_interview_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_control_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl",
]
DEFAULT_AUDIT_OUT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_audit_64k.json"
DEFAULT_SPLIT_OUT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_64k.jsonl"
DEFAULT_POINT_REVIEW_OUT = ROOT / "data" / "manifests" / "deepseek_v4_pro_point_review_units_64k.jsonl"
DEFAULT_REPORT_OUT = ROOT / "experiments" / "session_release_hardening_pre_audit_2026-06-29.md"
DEFAULT_DATASET_VERSION = "deepseek_v4_pro_sessions_64k_candidate_v0.1.0"

SOURCE_FAMILY_BY_GROUP = {
    "clinical_schizophrenia": "dais_c_clinical_interview",
    "first_episode_psychosis": "fep_interview",
    "control": "dais_c_control_calibration",
    "community_reality_boundary_text_signal": "reddit_fictionalized_text_signal",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_hash(value: str) -> str:
    return sha256_text(value)[:16]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not an object")
            value["_input_file"] = path.name
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def source_family(record: dict[str, Any]) -> str:
    group = record.get("metadata", {}).get("source_group")
    return SOURCE_FAMILY_BY_GROUP.get(str(group), "unknown_source_family")


def session_messages_payload(record: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"role": str(message.get("role", "")), "content": str(message.get("content", ""))}
        for message in record.get("messages") or []
        if isinstance(message, dict)
    ]


def session_signature(record: dict[str, Any]) -> str:
    payload = json.dumps(session_messages_payload(record), ensure_ascii=False, sort_keys=True)
    return sha256_text(payload)


def session_text(record: dict[str, Any]) -> str:
    return "\n".join(
        f"{message.get('role', '')}: {message.get('content', '')}"
        for message in record.get("messages") or []
        if isinstance(message, dict)
    )


def word_ngrams(text: str, size: int) -> set[str]:
    words = normalize_words(text)
    if not words:
        return set()
    if len(words) < size:
        return {" ".join(words)}
    return {" ".join(words[index : index + size]) for index in range(len(words) - size + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def assign_splits(
    records: list[dict[str, Any]],
    *,
    dev_ratio: float,
    validation_ratio: float,
) -> dict[str, str]:
    assignments: dict[str, str] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        family = source_family(record)
        if family == "dais_c_control_calibration":
            assignments[record["session_id"]] = "control_calibration"
        else:
            grouped[family].append(record)

    for family, family_records in grouped.items():
        ordered = sorted(family_records, key=lambda row: (stable_hash(row["session_id"]), row["session_id"]))
        total = len(ordered)
        if total == 1:
            assignments[ordered[0]["session_id"]] = "heldout_candidate"
            continue
        dev_count = max(1, math.ceil(total * dev_ratio))
        validation_count = max(1, math.ceil(total * validation_ratio))
        if dev_count + validation_count >= total:
            validation_count = max(0, total - dev_count - 1)
        for index, record in enumerate(ordered):
            if index < dev_count:
                split = "dev_review"
            elif index < dev_count + validation_count:
                split = "validation"
            else:
                split = "heldout_candidate"
            assignments[record["session_id"]] = split
    return assignments


def split_manifest_row(
    record: dict[str, Any],
    *,
    dataset_version: str,
    split: str,
    dev_ratio: float,
    validation_ratio: float,
) -> dict[str, Any]:
    metadata = record.get("metadata") or {}
    provenance = record.get("provenance") or {}
    quality = record.get("quality") or {}
    transforms = sorted(
        {
            item.get("transform")
            for item in record.get("message_provenance") or []
            if isinstance(item, dict) and item.get("transform")
        }
    )
    prompt_hashes = {
        key: provenance.get(key)
        for key in [
            "chunk_prompt_sha256",
            "consolidation_prompt_sha256",
            "overlap_repair_prompt_sha256",
            "screen_prompt_sha256",
            "generation_prompt_sha256",
        ]
        if provenance.get(key)
    }
    return {
        "dataset_version": dataset_version,
        "session_id": record["session_id"],
        "split": split,
        "split_method": {
            "name": "deterministic_sha256_stratified_by_source_family",
            "dev_ratio": dev_ratio,
            "validation_ratio": validation_ratio,
            "controls_are_calibration_only": True,
        },
        "source_family": source_family(record),
        "source_dataset": metadata.get("source_dataset"),
        "source_group": metadata.get("source_group"),
        "input_file": record.get("_input_file"),
        "message_count": len(record.get("messages") or []),
        "delusion_point_count": len(record.get("delusion_points") or []),
        "has_candidate_points": bool(record.get("delusion_points")),
        "label_interpretation": metadata.get("label_interpretation"),
        "dialogue_is_synthetic": metadata.get("dialogue_is_synthetic", False),
        "transforms": transforms,
        "transform_model": provenance.get("transform_model"),
        "transform_provider": provenance.get("transform_provider"),
        "context_window_tokens": provenance.get("context_window_tokens"),
        "thinking_mode": provenance.get("thinking_mode"),
        "run_id": provenance.get("run_id"),
        "source_license": provenance.get("source_license"),
        "source_hash": provenance.get("source_sha256") or provenance.get("source_post_sha256"),
        "prompt_hashes": prompt_hashes,
        "message_content_sha256": session_signature(record),
        "quality_status": quality.get("status"),
        "pii_scan_hit_count": len(quality.get("pii_scan_hits") or []),
        "max_common_source_word_run": quality.get("max_common_source_word_run"),
    }


def point_review_units(
    records: list[dict[str, Any]],
    *,
    dataset_version: str,
    split_assignments: dict[str, str],
    context_radius: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        messages = record.get("messages") or []
        for point in record.get("delusion_points") or []:
            message_indices = [
                index
                for index in point.get("message_indices") or []
                if isinstance(index, int) and 0 <= index < len(messages)
            ]
            context_indices = sorted(
                {
                    candidate
                    for index in message_indices
                    for candidate in range(index - context_radius, index + context_radius + 1)
                    if 0 <= candidate < len(messages)
                }
            )
            rows.append(
                {
                    "dataset_version": dataset_version,
                    "review_unit_id": f"{record['session_id']}::{point.get('point_id')}",
                    "session_id": record["session_id"],
                    "point_id": point.get("point_id"),
                    "split": split_assignments[record["session_id"]],
                    "source_family": source_family(record),
                    "source_group": record.get("metadata", {}).get("source_group"),
                    "category": point.get("category"),
                    "explicitness": point.get("explicitness"),
                    "confidence": point.get("confidence"),
                    "candidate_summary": point.get("summary"),
                    "uncertainty_or_counterevidence": point.get("uncertainty_or_counterevidence"),
                    "message_indices": message_indices,
                    "evidence_messages": [
                        {
                            "message_index": index,
                            "role": messages[index].get("role"),
                            "content": messages[index].get("content"),
                        }
                        for index in message_indices
                    ],
                    "local_context_messages": [
                        {
                            "message_index": index,
                            "role": messages[index].get("role"),
                            "content": messages[index].get("content"),
                        }
                        for index in context_indices
                    ],
                    "review_instruction": "Judge against these de-identified processed messages only; do not infer diagnosis or use source group/community membership as evidence.",
                }
            )
    return rows


def validation_errors(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for record in records:
        for error in validate_session_record(record):
            errors.append(f"{record.get('session_id', '<missing>')}: {error}")
        public_texts = [message.get("content", "") for message in record.get("messages") or []]
        public_texts.extend(point.get("summary", "") for point in record.get("delusion_points") or [])
        if scan_pii(public_texts):
            errors.append(f"{record.get('session_id', '<missing>')}: public text PII scan hit")
    return errors


def duplicate_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in records:
        grouped[session_signature(record)].append(record["session_id"])
    return [
        {"message_content_sha256": signature, "session_ids": sorted(session_ids), "count": len(session_ids)}
        for signature, session_ids in grouped.items()
        if len(session_ids) > 1
    ]


def near_duplicate_pairs(
    records: list[dict[str, Any]],
    *,
    split_assignments: dict[str, str],
    threshold: float,
    ngram_size: int,
    max_pairs: int,
) -> tuple[list[dict[str, Any]], int, int]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[source_family(record)].append(record)

    scored: list[dict[str, Any]] = []
    total_pairs = 0
    cross_split_pairs = 0
    for family_records in grouped.values():
        shingles = {record["session_id"]: word_ngrams(session_text(record), ngram_size) for record in family_records}
        for left, right in combinations(family_records, 2):
            score = jaccard(shingles[left["session_id"]], shingles[right["session_id"]])
            if score < threshold:
                continue
            total_pairs += 1
            cross_split = split_assignments[left["session_id"]] != split_assignments[right["session_id"]]
            if cross_split:
                cross_split_pairs += 1
            scored.append(
                {
                    "left_session_id": left["session_id"],
                    "right_session_id": right["session_id"],
                    "source_family": source_family(left),
                    "left_split": split_assignments[left["session_id"]],
                    "right_split": split_assignments[right["session_id"]],
                    "cross_split": cross_split,
                    "jaccard_word_ngram": round(score, 6),
                    "left_message_count": len(left.get("messages") or []),
                    "right_message_count": len(right.get("messages") or []),
                    "left_point_count": len(left.get("delusion_points") or []),
                    "right_point_count": len(right.get("delusion_points") or []),
                }
            )
    scored.sort(key=lambda item: (-item["jaccard_word_ngram"], item["left_session_id"], item["right_session_id"]))
    return scored[:max_pairs], total_pairs, cross_split_pairs


def count_by(records: list[dict[str, Any]], key_fn: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(key_fn(record)) for record in records).items()))


def build_audit(
    records: list[dict[str, Any]],
    *,
    dataset_version: str,
    split_assignments: dict[str, str],
    generated_at: str,
    near_threshold: float,
    ngram_size: int,
    max_near_pairs: int,
) -> dict[str, Any]:
    errors = validation_errors(records)
    exact_duplicates = duplicate_summary(records)
    near_pairs, near_total, cross_split_near_total = near_duplicate_pairs(
        records,
        split_assignments=split_assignments,
        threshold=near_threshold,
        ngram_size=ngram_size,
        max_pairs=max_near_pairs,
    )
    points = [point for record in records for point in record.get("delusion_points") or []]
    return {
        "dataset_version": dataset_version,
        "generated_at": generated_at,
        "audit_scope": {
            "inputs": sorted({str(record.get("_input_file")) for record in records}),
            "near_duplicate_method": f"within-source-family word {ngram_size}-gram Jaccard",
            "near_duplicate_threshold": near_threshold,
            "semantic_embedding_or_llm_duplicate_check_run": False,
            "llm_point_metajudge_run": False,
        },
        "totals": {
            "sessions": len(records),
            "messages": sum(len(record.get("messages") or []) for record in records),
            "delusion_points": len(points),
            "sessions_with_points": sum(1 for record in records if record.get("delusion_points")),
            "validation_errors": len(errors),
        },
        "counts": {
            "by_input_file": count_by(records, lambda record: record.get("_input_file")),
            "by_source_family": count_by(records, source_family),
            "by_source_group": count_by(records, lambda record: record.get("metadata", {}).get("source_group")),
            "by_split": dict(sorted(Counter(split_assignments[record["session_id"]] for record in records).items())),
            "points_by_category": dict(sorted(Counter(point.get("category") for point in points).items())),
            "points_by_explicitness": dict(sorted(Counter(point.get("explicitness") for point in points).items())),
        },
        "validation_errors": errors,
        "exact_duplicate_message_content_groups": exact_duplicates,
        "near_duplicate_pairs": {
            "reported_top_pairs": near_pairs,
            "total_pairs_at_or_above_threshold": near_total,
            "cross_split_pairs_at_or_above_threshold": cross_split_near_total,
            "reported_pair_limit": max_near_pairs,
        },
        "release_notes": [
            "Split manifest is deterministic and stratified by source family; controls are calibration-only.",
            "This pre-audit does not replace independent LLM second-pass/metajudge review.",
            "Near-duplicate analysis is lexical and within source family; semantic/embedding duplicate checks remain a follow-up.",
        ],
    }


def build_report(audit: dict[str, Any], *, split_path: Path, point_path: Path, audit_path: Path) -> str:
    totals = audit["totals"]
    counts = audit["counts"]
    near = audit["near_duplicate_pairs"]
    lines = [
        "# Session release hardening pre-audit — 2026-06-29",
        "",
        "## Scope",
        "",
        "本轮继续 `deviation-bench-new/` 的 data release hardening，完成可复现的本地预审计、split/version manifest 和 second-pass point review queue。该轮不调用新模型，不把 first-pass `delusion_points` 当 gold label。",
        "",
        "## Artifacts",
        "",
        f"- Audit JSON: `{audit_path.relative_to(ROOT)}`",
        f"- Split manifest: `{split_path.relative_to(ROOT)}`",
        f"- Point review units: `{point_path.relative_to(ROOT)}`",
        "- Metajudge prompt: `prompts/point_metajudge.md`",
        "",
        "## Deterministic Audit Results",
        "",
        f"- Dataset version: `{audit['dataset_version']}`",
        f"- Sessions: {totals['sessions']}",
        f"- Messages: {totals['messages']}",
        f"- Candidate points: {totals['delusion_points']}",
        f"- Sessions with candidate points: {totals['sessions_with_points']}",
        f"- Contract / PII validation errors: {totals['validation_errors']}",
        f"- Exact duplicate message-content groups: {len(audit['exact_duplicate_message_content_groups'])}",
        f"- Lexical near-duplicate pairs at threshold {audit['audit_scope']['near_duplicate_threshold']}: {near['total_pairs_at_or_above_threshold']}",
        f"- Cross-split lexical near-duplicate pairs at threshold {audit['audit_scope']['near_duplicate_threshold']}: {near['cross_split_pairs_at_or_above_threshold']}",
        "",
        "## Split Counts",
        "",
    ]
    for split, count in counts["by_split"].items():
        lines.append(f"- `{split}`: {count}")
    lines.extend(["", "## Source Family Counts", ""])
    for family, count in counts["by_source_family"].items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `dev_review` / `validation` / `heldout_candidate` 是数据发布和后续 judge 开发的候选 split，不是最终论文 benchmark task 定义。",
            "- `control_calibration` 只包含 DAIS-C control，不与 psychosis-related 或 community-fictionalized sessions 混作 clinical corpus。",
            "- 当前 duplicate audit 是本地 lexical pre-audit；embedding/LLM 语义重复检查仍需后续执行。",
            "- `point_review_units` 为 independent second-pass/metajudge 准备输入；本轮尚未产生 model disagreement 结果。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    parser.add_argument("--audit-out", type=Path, default=DEFAULT_AUDIT_OUT)
    parser.add_argument("--split-out", type=Path, default=DEFAULT_SPLIT_OUT)
    parser.add_argument("--point-review-out", type=Path, default=DEFAULT_POINT_REVIEW_OUT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    parser.add_argument("--dev-ratio", type=float, default=0.10)
    parser.add_argument("--validation-ratio", type=float, default=0.10)
    parser.add_argument("--near-duplicate-threshold", type=float, default=0.82)
    parser.add_argument("--near-duplicate-ngram-size", type=int, default=5)
    parser.add_argument("--max-near-duplicate-pairs", type=int, default=100)
    parser.add_argument("--point-context-radius", type=int, default=1)
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    input_paths = args.input or DEFAULT_INPUTS
    records: list[dict[str, Any]] = []
    for path in input_paths:
        records.extend(read_jsonl(path))
    records.sort(key=lambda record: record["session_id"])

    generated_at = args.generated_at or utc_now()
    split_assignments = assign_splits(
        records,
        dev_ratio=args.dev_ratio,
        validation_ratio=args.validation_ratio,
    )
    split_rows = [
        split_manifest_row(
            record,
            dataset_version=args.dataset_version,
            split=split_assignments[record["session_id"]],
            dev_ratio=args.dev_ratio,
            validation_ratio=args.validation_ratio,
        )
        for record in records
    ]
    review_rows = point_review_units(
        records,
        dataset_version=args.dataset_version,
        split_assignments=split_assignments,
        context_radius=args.point_context_radius,
    )
    audit = build_audit(
        records,
        dataset_version=args.dataset_version,
        split_assignments=split_assignments,
        generated_at=generated_at,
        near_threshold=args.near_duplicate_threshold,
        ngram_size=args.near_duplicate_ngram_size,
        max_near_pairs=args.max_near_duplicate_pairs,
    )

    write_jsonl(args.split_out, split_rows)
    write_jsonl(args.point_review_out, review_rows)
    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.audit_out.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        build_report(audit, split_path=args.split_out, point_path=args.point_review_out, audit_path=args.audit_out),
        encoding="utf-8",
    )
    print(
        "sessions={sessions} messages={messages} delusion_points={points} "
        "validation_errors={errors} near_pairs={near_pairs} cross_split_near_pairs={cross_split}".format(
            sessions=audit["totals"]["sessions"],
            messages=audit["totals"]["messages"],
            points=audit["totals"]["delusion_points"],
            errors=audit["totals"]["validation_errors"],
            near_pairs=audit["near_duplicate_pairs"]["total_pairs_at_or_above_threshold"],
            cross_split=audit["near_duplicate_pairs"]["cross_split_pairs_at_or_above_threshold"],
        )
    )
    print(f"audit={args.audit_out}")
    print(f"splits={args.split_out}")
    print(f"point_review_units={args.point_review_out}")
    print(f"report={args.report_out}")
    return 0 if audit["totals"]["validation_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
