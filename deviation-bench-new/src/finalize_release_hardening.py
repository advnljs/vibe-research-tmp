#!/usr/bin/env python3
"""Finalize reviewed release audit by applying metajudge and duplicate-review decisions."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from build_sessions import read_jsonl, utc_now


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_64k.jsonl"
DEFAULT_PRE_AUDIT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_audit_64k.json"
DEFAULT_POINT_SUMMARY = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k_summary.json"
DEFAULT_PAIR_REVIEWS = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl"
DEFAULT_DUP_SUMMARY = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json"
DEFAULT_REVIEWED_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_reviewed_64k.jsonl"
DEFAULT_REVIEWED_AUDIT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_audit_reviewed_64k.json"
DEFAULT_REPORT = ROOT / "experiments" / "session_release_hardening_actual_flow_2026-06-29.md"
SPLIT_PRIORITY = {"dev_review": 0, "validation": 1, "heldout_candidate": 2, "control_calibration": 3}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def duplicate_exclusion_choice(left: str, right: str) -> str:
    return max(left, right)


def build_review_graph(pair_reviews: list[dict[str, Any]]) -> tuple[dict[str, set[str]], set[str], list[dict[str, Any]]]:
    graph: dict[str, set[str]] = defaultdict(set)
    excluded: set[str] = set()
    decisions: list[dict[str, Any]] = []
    for row in pair_reviews:
        action = row.get("recommended_action")
        if action not in {"same_split", "exclude_one"}:
            continue
        left = str(row.get("left_session_id"))
        right = str(row.get("right_session_id"))
        graph[left].add(right)
        graph[right].add(left)
        decision = {
            "pair_id": row.get("pair_id"),
            "left_session_id": left,
            "right_session_id": right,
            "decision": row.get("decision"),
            "leakage_risk": row.get("leakage_risk"),
            "recommended_action": action,
        }
        if action == "exclude_one":
            excluded_session = duplicate_exclusion_choice(left, right)
            excluded.add(excluded_session)
            decision["deterministic_excluded_session_id"] = excluded_session
        decisions.append(decision)
    return graph, excluded, decisions


def connected_components(graph: dict[str, set[str]]) -> list[set[str]]:
    components = []
    seen: set[str] = set()
    for node in sorted(graph):
        if node in seen:
            continue
        component: set[str] = set()
        queue: deque[str] = deque([node])
        seen.add(node)
        while queue:
            current = queue.popleft()
            component.add(current)
            for neighbor in sorted(graph[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return components


def reviewed_split_rows(
    split_rows: list[dict[str, Any]],
    pair_reviews: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    graph, excluded, pair_decisions = build_review_graph(pair_reviews)
    components = connected_components(graph)
    component_by_session: dict[str, tuple[str, str]] = {}
    rows_by_id = {row["session_id"]: row for row in split_rows}
    for index, component in enumerate(components, start=1):
        included_members = [session_id for session_id in sorted(component) if session_id not in excluded]
        if included_members:
            target_split = min(
                (rows_by_id[session_id]["split"] for session_id in included_members if session_id in rows_by_id),
                key=lambda split: SPLIT_PRIORITY.get(split, 99),
            )
        else:
            target_split = "excluded_duplicate"
        group_id = f"semantic_leakage_group_{index:04d}"
        for session_id in component:
            component_by_session[session_id] = (group_id, target_split)

    reviewed_rows = []
    for row in split_rows:
        output = dict(row)
        output["original_split"] = row["split"]
        group = component_by_session.get(row["session_id"])
        output["semantic_leakage_group_id"] = group[0] if group else None
        output["release_status"] = "included"
        output["release_split"] = row["split"]
        output["release_action"] = "keep_original_split"
        if row["session_id"] in excluded:
            output["release_status"] = "excluded_duplicate_candidate"
            output["release_split"] = "excluded_duplicate"
            output["release_action"] = "exclude_due_to_llm_duplicate_pair"
        elif group and row["split"] != group[1]:
            output["release_split"] = group[1]
            output["release_action"] = "move_to_same_split_due_to_llm_near_duplicate"
        elif group:
            output["release_action"] = "same_split_group_confirmed"
        reviewed_rows.append(output)
    return reviewed_rows, pair_decisions, excluded


def build_report(audit: dict[str, Any], reviewed_audit_path: Path, reviewed_splits_path: Path) -> str:
    totals = audit["reviewed_totals"]
    lines = [
        "# Session release hardening actual flow — 2026-06-29",
        "",
        "## Scope",
        "",
        "本轮完成实际 release-hardening 流程：DeepSeek Pro independent point metajudge、DeepSeek Pro semantic fingerprint + duplicate/leakage pair review、reviewed split/audit materialization，以及动态 runs dashboard。",
        "",
        "## Artifacts",
        "",
        "- Point metajudge: `data/reviews/deepseek_v4_pro_point_metajudge_64k.jsonl`",
        "- Point metajudge summary: `data/reviews/deepseek_v4_pro_point_metajudge_64k_summary.json`",
        "- Semantic fingerprints: `data/reviews/deepseek_v4_pro_session_semantic_fingerprints_64k.jsonl`",
        "- Semantic duplicate pairs: `data/reviews/deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl`",
        "- Semantic duplicate summary: `data/reviews/deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json`",
        f"- Reviewed audit: `{reviewed_audit_path.relative_to(ROOT)}`",
        f"- Reviewed split manifest: `{reviewed_splits_path.relative_to(ROOT)}`",
        "- Dynamic local dashboard: `data/work/runs_dashboard/index.html`",
        "",
        "## Point Metajudge",
        "",
        f"- Units reviewed: {audit['point_metajudge']['input_units']}",
        f"- Candidate points: {audit['point_metajudge']['candidate_units']}",
        f"- Negative controls: {audit['point_metajudge']['negative_control_units']}",
        f"- Candidate acceptance rate: {audit['point_metajudge']['candidate_acceptance_rate']}",
        f"- Candidate revise/reject rate: {audit['point_metajudge']['candidate_revision_or_rejection_rate']}",
        f"- Negative control flag rate: {audit['point_metajudge']['negative_control_flag_rate']}",
        "",
        "## Semantic Duplicate / Leakage Review",
        "",
        f"- Fingerprints: {audit['semantic_duplicate_audit']['fingerprint_count']}",
        f"- Pair reviews: {audit['semantic_duplicate_audit']['pair_review_count']}",
        f"- Duplicate pairs: {audit['semantic_duplicate_audit']['counts']['pair_decision'].get('duplicate', 0)}",
        f"- Near-duplicate pairs: {audit['semantic_duplicate_audit']['counts']['pair_decision'].get('near_duplicate', 0)}",
        f"- Medium/high leakage pairs: {len(audit['semantic_duplicate_audit']['medium_or_high_leakage_pairs'])}",
        "",
        "## Reviewed Split Decisions",
        "",
        f"- Included sessions: {totals['included_sessions']}",
        f"- Excluded duplicate candidates: {totals['excluded_duplicate_candidates']}",
        f"- Same-split moved sessions: {totals['same_split_moved_sessions']}",
        "",
        "Release split counts:",
    ]
    for split, count in audit["reviewed_counts"]["release_split"].items():
        lines.append(f"- `{split}`: {count}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Reviewed split decisions are deterministic applications of LLM review outputs; raw processed sessions are not deleted.",
            "- `excluded_duplicate_candidate` marks sessions that should not enter downstream benchmark release without further policy decision.",
            "- `move_to_same_split_due_to_llm_near_duplicate` prevents reviewed near-duplicate clusters from crossing split boundaries.",
            "- License/privacy/governance review is still required before any public release.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--pre-audit", type=Path, default=DEFAULT_PRE_AUDIT)
    parser.add_argument("--point-summary", type=Path, default=DEFAULT_POINT_SUMMARY)
    parser.add_argument("--pair-reviews", type=Path, default=DEFAULT_PAIR_REVIEWS)
    parser.add_argument("--duplicate-summary", type=Path, default=DEFAULT_DUP_SUMMARY)
    parser.add_argument("--reviewed-splits", type=Path, default=DEFAULT_REVIEWED_SPLITS)
    parser.add_argument("--reviewed-audit", type=Path, default=DEFAULT_REVIEWED_AUDIT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    split_rows = read_jsonl(args.splits)
    pair_rows = read_jsonl(args.pair_reviews)
    reviewed_rows, pair_decisions, excluded = reviewed_split_rows(split_rows, pair_rows)
    write_jsonl(args.reviewed_splits, reviewed_rows)

    pre_audit = load_json(args.pre_audit)
    point_summary = load_json(args.point_summary)
    duplicate_summary = load_json(args.duplicate_summary)
    audit = {
        "dataset_version": pre_audit.get("dataset_version"),
        "generated_at": utc_now(),
        "pre_audit": pre_audit,
        "point_metajudge": point_summary,
        "semantic_duplicate_audit": duplicate_summary,
        "reviewed_totals": {
            "sessions": len(reviewed_rows),
            "included_sessions": sum(row["release_status"] == "included" for row in reviewed_rows),
            "excluded_duplicate_candidates": len(excluded),
            "same_split_moved_sessions": sum(
                row["release_action"] == "move_to_same_split_due_to_llm_near_duplicate"
                for row in reviewed_rows
            ),
            "semantic_pair_decisions_applied": len(pair_decisions),
        },
        "reviewed_counts": {
            "release_split": dict(sorted(Counter(row["release_split"] for row in reviewed_rows).items())),
            "release_status": dict(sorted(Counter(row["release_status"] for row in reviewed_rows).items())),
            "release_action": dict(sorted(Counter(row["release_action"] for row in reviewed_rows).items())),
        },
        "semantic_pair_decisions_applied": pair_decisions,
        "excluded_duplicate_session_ids": sorted(excluded),
        "release_notes": [
            "Point labels remain LLM candidate labels, not clinical ground truth.",
            "Duplicate exclusions are deterministic marks based on LLM pair review; processed records are preserved.",
            "Reviewed split manifest supersedes the candidate split manifest for downstream benchmark construction.",
            "License/privacy/governance review remains required before public release.",
        ],
    }
    args.reviewed_audit.parent.mkdir(parents=True, exist_ok=True)
    args.reviewed_audit.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(audit, args.reviewed_audit, args.reviewed_splits), encoding="utf-8")
    print(
        "sessions={sessions} included={included} excluded={excluded} moved={moved} reviewed_splits={splits}".format(
            sessions=audit["reviewed_totals"]["sessions"],
            included=audit["reviewed_totals"]["included_sessions"],
            excluded=audit["reviewed_totals"]["excluded_duplicate_candidates"],
            moved=audit["reviewed_totals"]["same_split_moved_sessions"],
            splits=args.reviewed_splits,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
