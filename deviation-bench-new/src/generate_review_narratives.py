#!/usr/bin/env python3
"""Generate Chinese narrative explanations for the local review dashboard."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from build_sessions import call_json_task, read_jsonl, sha256_text, utc_now


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_KEY_FILE = WORKSPACE_ROOT / "ds_key.txt"
DEFAULT_PROMPT = ROOT / "prompts" / "review_narrative.md"
DEFAULT_OUTPUT = ROOT / "data" / "reviews" / "deepseek_v4_pro_review_narratives_64k.json"
DEFAULT_RUN_ID = "deepseek_v4_pro_review_narratives_64k"

PROCESSED_INPUTS = [
    ROOT / "data" / "processed" / "deepseek_v4_pro_interview_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_control_sessions_64k.jsonl",
    ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl",
]
REVIEWED_AUDIT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_audit_reviewed_64k.json"
REVIEWED_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_reviewed_64k.jsonl"
POINT_REVIEWS = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k.jsonl"
SEMANTIC_DUPLICATE_SUMMARY = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json"


def load_sessions(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(read_jsonl(path))
    return rows


def count_by(rows: list[Any], fn) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str(fn(row) or "unknown")] += 1
    return dict(counter)


def confidence_bucket(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if number >= 0.90:
        return "0.90-1.00"
    if number >= 0.75:
        return "0.75-0.89"
    if number >= 0.50:
        return "0.50-0.74"
    return "<0.50"


def point_rows(
    sessions: list[dict[str, Any]],
    splits: dict[str, dict[str, Any]],
    point_reviews: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for session in sessions:
        split = splits.get(session["session_id"], {})
        for point in session.get("delusion_points") or []:
            review = point_reviews.get(f"{session['session_id']}::{point.get('point_id')}")
            rows.append(
                {
                    "session_id": session["session_id"],
                    "source_family": split.get("source_family") or session.get("metadata", {}).get("source_group"),
                    "release_split": split.get("release_split"),
                    "category": point.get("category"),
                    "explicitness": point.get("explicitness"),
                    "confidence_bucket": confidence_bucket(point.get("confidence")),
                    "decision": review.get("decision") if review else "unreviewed",
                    "support_level": review.get("support_level") if review else "unreviewed",
                    "summary_overreach": bool(review.get("summary_overreach")) if review else False,
                    "diagnosis_or_membership_inference": bool(review.get("diagnosis_or_membership_inference"))
                    if review
                    else False,
                }
            )
    return rows


def top_items(counts: dict[str, int], limit: int = 8) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit])


def build_stats() -> dict[str, Any]:
    sessions = load_sessions(PROCESSED_INPUTS)
    splits = {row["session_id"]: row for row in read_jsonl(REVIEWED_SPLITS)}
    audit = json.loads(REVIEWED_AUDIT.read_text(encoding="utf-8"))
    duplicate_summary = json.loads(SEMANTIC_DUPLICATE_SUMMARY.read_text(encoding="utf-8"))
    review_rows = read_jsonl(POINT_REVIEWS)
    point_review_by_id = {row["review_unit_id"]: row for row in review_rows}
    candidates = [row for row in review_rows if row.get("unit_type") == "candidate_point"]
    negative_controls = [row for row in review_rows if row.get("unit_type") == "negative_control"]
    points = point_rows(sessions, splits, point_review_by_id)
    decisions = Counter(row["decision"] for row in points)
    no_point_sessions = [session for session in sessions if not session.get("delusion_points")]
    accepted_or_revised = [
        row for row in points if row["decision"] in {"accept_candidate", "revise_candidate"}
    ]
    rejected = [row for row in points if row["decision"] == "reject_insufficient_evidence"]
    overreach = [row for row in points if row["summary_overreach"]]
    diagnosis_flags = [row for row in points if row["diagnosis_or_membership_inference"]]

    stats = {
        "dataset_version": audit.get("dataset_version"),
        "generated_from": {
            "processed_inputs": [path.name for path in PROCESSED_INPUTS],
            "reviewed_audit": REVIEWED_AUDIT.name,
            "reviewed_splits": REVIEWED_SPLITS.name,
            "point_reviews": POINT_REVIEWS.name,
        },
        "totals": {
            "sessions": len(sessions),
            "messages": sum(len(session.get("messages") or []) for session in sessions),
            "candidate_points": len(points),
            "sessions_with_candidate_points": len({row["session_id"] for row in points}),
            "no_point_sessions": len(no_point_sessions),
            "review_units": len(review_rows),
            "candidate_review_units": len(candidates),
            "negative_control_units": len(negative_controls),
        },
        "metajudge": {
            "decision_counts": dict(Counter(row["decision"] for row in review_rows)),
            "candidate_decision_counts": dict(decisions),
            "accepted_or_revised_candidate_points": len(accepted_or_revised),
            "rejected_candidate_points": len(rejected),
            "summary_overreach_flags": len(overreach),
            "diagnosis_or_membership_inference_flags": len(diagnosis_flags),
            "negative_control_flag_rate": audit.get("point_metajudge", {}).get("negative_control_flag_rate"),
            "candidate_acceptance_rate": audit.get("point_metajudge", {}).get("candidate_acceptance_rate"),
        },
        "delusion_signal_distribution": {
            "category": top_items(count_by(points, lambda row: row["category"]), 12),
            "accepted_or_revised_category": top_items(count_by(accepted_or_revised, lambda row: row["category"]), 12),
            "rejected_category": top_items(count_by(rejected, lambda row: row["category"]), 12),
            "source_family": top_items(count_by(points, lambda row: row["source_family"]), 8),
            "explicitness": count_by(points, lambda row: row["explicitness"]),
            "confidence_bucket": count_by(points, lambda row: row["confidence_bucket"]),
            "support_level": count_by(points, lambda row: row["support_level"]),
        },
        "release": {
            "reviewed_totals": audit.get("reviewed_totals", {}),
            "reviewed_counts": audit.get("reviewed_counts", {}),
            "field_notes": {
                "excluded_duplicate_candidates": (
                    "Number of duplicate candidate sessions excluded from the reviewed release manifest; "
                    "this is not a count of delusion candidate points."
                ),
                "included_sessions": "Number of sessions included in the reviewed release manifest.",
            },
        },
        "duplicate_audit": {
            "fingerprint_count": duplicate_summary.get("fingerprint_count"),
            "pair_decision": duplicate_summary.get("counts", {}).get("pair_decision", {}),
            "pair_leakage_risk": duplicate_summary.get("counts", {}).get("pair_leakage_risk", {}),
            "source_specificity_risk": duplicate_summary.get("counts", {}).get("source_specificity_risk", {}),
        },
        "interpretation_boundaries": [
            "delusion_points are LLM-extracted candidate reality-boundary signals, not clinical diagnosis.",
            "DAIS/FEP source group and Reddit community membership must not be treated as delusion labels.",
            "Empty candidate lists are valid and should remain visible.",
            "Metajudge decisions calibrate first-pass extraction but are still LLM-only review outputs.",
        ],
    }
    stats["input_hash"] = sha256_text(json.dumps(stats, ensure_ascii=False, sort_keys=True))
    return stats


def mock_narrative(stats: dict[str, Any]) -> dict[str, Any]:
    totals = stats["totals"]
    meta = stats["metajudge"]
    categories = stats["delusion_signal_distribution"]["category"]
    top_category = next(iter(categories.items()), ("unknown", 0))
    return {
        "schema_version": "0.1.0",
        "language": "zh-CN",
        "overall": {
            "title": "数据层已进入可审阅状态",
            "paragraphs": [
                (
                    f"当前页面从 {totals['sessions']} 个 session 和 {totals['messages']} 条 message 动态聚合统计。"
                    f"其中 {totals['candidate_points']} 个 reality-boundary 候选点来自一阶抽取，"
                    f"{totals['no_point_sessions']} 个 session 保持空候选列表。"
                )
            ],
            "bullets": [
                "这些统计用于数据审阅和后续 benchmark 构造，不是临床诊断结论。",
                "Reviewed split manifest 应作为后续任务入口。",
            ],
        },
        "delusion": {
            "title": "候选信号需要结合 metajudge 阅读",
            "paragraphs": [
                (
                    f"候选点最多的类别是 {top_category[0]}（{top_category[1]} 个）。"
                    f"Metajudge 接受或修订了 {meta['accepted_or_revised_candidate_points']} 个候选点，"
                    f"拒绝了 {meta['rejected_candidate_points']} 个候选点。"
                ),
                (
                    f"有 {meta['summary_overreach_flags']} 个 summary-overreach 标记，"
                    f"{meta['diagnosis_or_membership_inference_flags']} 个 diagnosis/member inference 标记。"
                    "这些位置应该优先在对话视图中复查。"
                ),
            ],
            "bullets": [
                "先看 category 和 source-family 分布，再看 decision × category 热力图。",
                "空候选列表是有效结果，尤其用于控制组和没有明确信号的访谈。",
            ],
            "cautions": stats["interpretation_boundaries"],
        },
        "charts": [
            {
                "target": "Candidate Categories",
                "explanation": "显示一阶抽取最常见的 reality-boundary 候选类别，不能直接解释为真实患病比例。",
            },
            {
                "target": "Metajudge Decision × Candidate Category",
                "explanation": "用于查看哪些类别更容易被接受、修订或拒绝，帮助识别抽取口径过宽的位置。",
            },
            {
                "target": "Source Family × Candidate Category",
                "explanation": "用于区分访谈来源和 Reddit fictionalized text-signal 来源的候选信号结构。",
            },
        ],
        "session_reading_guide": [
            "从 Delusion 页进入高密度 session，再跳转到 Sessions 页核对完整对话和 metajudge rationale。",
            "优先复查 rejected、summary-overreach、weak_or_none support 和 diagnosis/member inference 标记。",
        ],
        "limitations": [
            "该说明是基于聚合统计生成的解释，不替代治理审查。",
            "LLM narrative 不应作为 paper-facing 人类标注或临床判断。",
        ],
    }


def validate_narrative(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    for section in ["overall", "delusion"]:
        if not isinstance(value.get(section), dict):
            errors.append(f"{section} must be an object")
            continue
        if not isinstance(value[section].get("title"), str) or not value[section]["title"].strip():
            errors.append(f"{section}.title is required")
        for field in ["paragraphs", "bullets"]:
            if not isinstance(value[section].get(field), list) or not all(
                isinstance(item, str) and item.strip() for item in value[section].get(field, [])
            ):
                errors.append(f"{section}.{field} must be non-empty strings")
    if not isinstance(value.get("charts"), list) or not value["charts"]:
        errors.append("charts must be a non-empty list")
    for field in ["session_reading_guide", "limitations"]:
        if not isinstance(value.get(field), list) or not value[field]:
            errors.append(f"{field} must be a non-empty list")
    return errors


def build_output(narrative: dict[str, Any], stats: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "run_id": args.run_id,
        "generated_at": utc_now(),
        "provider": args.provider,
        "model": args.model if args.provider != "mock" else "mock",
        "input_hash": stats["input_hash"],
        "stats": stats,
        "narrative": narrative,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--base-url", default="https://api.deepseek.com")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--context-window-tokens", type=int, default=65536)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--http-retries", type=int, default=2)
    parser.add_argument("--thinking-mode", choices=["disabled", "default"], default="disabled")
    args = parser.parse_args()

    stats = build_stats()
    if args.provider == "mock":
        narrative = mock_narrative(stats)
    else:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key and args.key_file.exists():
            api_key = args.key_file.read_text(encoding="utf-8").strip()
        if not api_key:
            raise SystemExit("OPENAI_API_KEY or --key-file is required for provider=openai")
        prompt = args.prompt.read_text(encoding="utf-8")
        payload = {
            "task": "write_dashboard_narrative",
            "stats": stats,
        }
        narrative, _raw = call_json_task(
            provider=args.provider,
            api_key=api_key,
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
        )
    errors = validate_narrative(narrative)
    if errors:
        raise SystemExit("narrative validation failed: " + "; ".join(errors))
    output = build_output(narrative, stats, args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"out={args.output} input_hash={stats['input_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
