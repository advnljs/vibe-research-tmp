#!/usr/bin/env python3
"""Build a static overview report for the current real-data-derived sessions."""

from __future__ import annotations

import argparse
import html
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "reports" / "session_overview_report.html"

SESSION_FILES = {
    "interview": ROOT / "data" / "processed" / "deepseek_v4_pro_interview_sessions_64k.jsonl",
    "control": ROOT / "data" / "processed" / "deepseek_v4_pro_control_sessions_64k.jsonl",
    "reddit": ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl",
}
REVIEWED_SPLITS = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_splits_reviewed_64k.jsonl"
POINT_METAJUDGE = ROOT / "data" / "reviews" / "deepseek_v4_pro_point_metajudge_64k.jsonl"
DUPLICATE_PAIRS = ROOT / "data" / "reviews" / "deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl"
REVIEWED_AUDIT = ROOT / "data" / "manifests" / "deepseek_v4_pro_release_audit_reviewed_64k.json"
REDDIT_SOURCE_CASES = ROOT / "data" / "manifests" / "reddit_source_cases.jsonl"
REDDIT_SCREEN_CANDIDATES = ROOT / "data" / "manifests" / "reddit_screen_candidates.jsonl"
REDDIT_SCREENING = ROOT / "data" / "screened" / "deepseek_v4_pro_reddit_screening_64k.jsonl"
REDDIT_PREP_SUMMARY = ROOT / "data" / "manifests" / "reddit_preparation_summary.md"


SOURCE_LABELS = {
    "dais_c_clinical_interview": "DAIS-C clinical real interview",
    "fep_interview": "FEP friendship real interview",
    "dais_c_control_calibration": "DAIS-C control calibration",
    "reddit_fictionalized_text_signal": "Reddit fictionalized text signal",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
    return rows


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def median(values: list[int]) -> float:
    return float(statistics.median(values)) if values else 0.0


def mean(values: list[int]) -> float:
    return float(statistics.mean(values)) if values else 0.0


def source_family(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") or {}
    dataset = metadata.get("source_dataset")
    group = metadata.get("source_group")
    if dataset == "dais_c" and group == "clinical_schizophrenia":
        return "dais_c_clinical_interview"
    if dataset == "dais_c" and group == "control":
        return "dais_c_control_calibration"
    if dataset == "first_episode_psychosis_friendship":
        return "fep_interview"
    if dataset == "reddit_mental_health_zenodo_r_schizophrenia":
        return "reddit_fictionalized_text_signal"
    return str(group or dataset or "unknown")


def source_display(family: str) -> str:
    return SOURCE_LABELS.get(family, family)


def parse_first_int(markdown: str, label: str) -> int | None:
    pattern = re.compile(rf"{re.escape(label)}\s*:\s*`?([0-9,]+)`?", re.IGNORECASE)
    match = pattern.search(markdown)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def stat_row(label: str, sessions: list[dict[str, Any]]) -> dict[str, Any]:
    message_counts = [len(record.get("messages") or []) for record in sessions]
    point_counts = [len(record.get("delusion_points") or []) for record in sessions]
    exact_alternation = sum(
        1
        for record in sessions
        if all(
            record["messages"][index]["role"] != record["messages"][index - 1]["role"]
            for index in range(1, len(record.get("messages") or []))
        )
    )
    start_roles = Counter((record.get("messages") or [{}])[0].get("role") for record in sessions)
    transforms = Counter(
        item.get("transform")
        for record in sessions
        for item in (record.get("message_provenance") or [])
    )
    return {
        "source": label,
        "sessions": len(sessions),
        "messages": sum(message_counts),
        "candidate_points": sum(point_counts),
        "sessions_with_points": sum(1 for value in point_counts if value),
        "messages_min": min(message_counts) if message_counts else 0,
        "messages_median": median(message_counts),
        "messages_mean": mean(message_counts),
        "messages_max": max(message_counts) if message_counts else 0,
        "points_mean": mean(point_counts),
        "points_max": max(point_counts) if point_counts else 0,
        "start_roles": start_roles,
        "exact_alternation": exact_alternation,
        "transforms": transforms,
        "qc_passed": sum(1 for record in sessions if (record.get("quality") or {}).get("status") == "passed"),
        "max_source_word_run": max(
            ((record.get("quality") or {}).get("max_common_source_word_run") or 0)
            for record in sessions
        )
        if sessions
        else 0,
    }


def table(headers: list[str], rows: list[list[Any]], class_name: str = "") -> str:
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f'<table class="{esc(class_name)}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def card(label: str, value: Any, note: str = "", tone: str = "") -> str:
    return (
        f'<article class="card {esc(tone)}"><span>{esc(label)}</span>'
        f"<b>{esc(value)}</b>"
        f"{f'<small>{esc(note)}</small>' if note else ''}</article>"
    )


def bar_list(data: dict[str, int], total: int | None = None) -> str:
    if not data:
        return '<div class="empty">No data</div>'
    maximum = max(data.values()) or 1
    total_value = total if total is not None else sum(data.values())
    rows = []
    for label, value in sorted(data.items(), key=lambda item: (-item[1], item[0])):
        percent = value / total_value if total_value else 0
        width = max(2.0, value / maximum * 100)
        rows.append(
            '<div class="bar-row">'
            f'<div class="bar-label" title="{esc(label)}">{esc(label)}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.2f}%"></div></div>'
            f'<div class="bar-value">{fmt(value)} <small>{pct(percent)}</small></div>'
            "</div>"
        )
    return '<div class="bars">' + "\n".join(rows) + "</div>"


def chip(text: str, tone: str = "") -> str:
    return f'<span class="chip {esc(tone)}">{esc(text)}</span>'


def build_report() -> str:
    sessions: list[dict[str, Any]] = []
    for file_family, path in SESSION_FILES.items():
        for record in read_jsonl(path):
            record["_file_family"] = file_family
            record["_source_family"] = source_family(record)
            sessions.append(record)

    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    session_source: dict[str, str] = {}
    for record in sessions:
        by_source[record["_source_family"]].append(record)
        session_source[record["session_id"]] = record["_source_family"]

    total_sessions = len(sessions)
    total_messages = sum(len(record.get("messages") or []) for record in sessions)
    total_points = sum(len(record.get("delusion_points") or []) for record in sessions)
    sessions_with_points = sum(1 for record in sessions if record.get("delusion_points"))
    real_interview_sessions = len(by_source["dais_c_clinical_interview"]) + len(by_source["fep_interview"]) + len(
        by_source["dais_c_control_calibration"]
    )
    psychosis_related_interview_sessions = len(by_source["dais_c_clinical_interview"]) + len(by_source["fep_interview"])
    reddit_sessions = len(by_source["reddit_fictionalized_text_signal"])
    reddit_points = sum(len(record.get("delusion_points") or []) for record in by_source["reddit_fictionalized_text_signal"])
    non_reddit_points = total_points - reddit_points

    source_rows = [stat_row(source_display(family), rows) for family, rows in sorted(by_source.items())]
    point_categories = Counter(
        point.get("category")
        for record in sessions
        for point in (record.get("delusion_points") or [])
    )
    point_categories_by_source = {
        source_display(family): Counter(
            point.get("category")
            for record in rows
            for point in (record.get("delusion_points") or [])
        )
        for family, rows in by_source.items()
    }

    reviewed_splits = read_jsonl(REVIEWED_SPLITS) if REVIEWED_SPLITS.exists() else []
    split_counts = Counter(row.get("release_split") for row in reviewed_splits)
    status_counts = Counter(row.get("release_status") for row in reviewed_splits)
    action_counts = Counter(row.get("release_action") for row in reviewed_splits)
    excluded_duplicate_ids = {
        row.get("session_id")
        for row in reviewed_splits
        if row.get("release_status") == "excluded_duplicate_candidate"
    }

    metajudge_rows = read_jsonl(POINT_METAJUDGE) if POINT_METAJUDGE.exists() else []
    metajudge_by_source: dict[str, Counter[str]] = defaultdict(Counter)
    for row in metajudge_rows:
        family = row.get("source_family") or session_source.get(row.get("session_id"), "unknown")
        metajudge_by_source[source_display(str(family))][str(row.get("decision"))] += 1
    metajudge_decisions = Counter(row.get("decision") for row in metajudge_rows)
    diagnosis_flags = sum(1 for row in metajudge_rows if row.get("diagnosis_or_membership_inference"))
    identifying_flags = sum(1 for row in metajudge_rows if row.get("identifying_detail_risk"))

    duplicate_rows = read_jsonl(DUPLICATE_PAIRS) if DUPLICATE_PAIRS.exists() else []
    duplicate_decisions = Counter(row.get("decision") for row in duplicate_rows)
    duplicate_actions = Counter(row.get("recommended_action") for row in duplicate_rows)
    leakage_risks = Counter(row.get("leakage_risk") for row in duplicate_rows)

    reviewed_audit = read_json(REVIEWED_AUDIT)
    dataset_version = reviewed_audit.get("dataset_version", "unknown")
    pre_audit = reviewed_audit.get("pre_audit") or {}
    validation_errors = (pre_audit.get("validation_errors") or [])

    reddit_screening = read_jsonl(REDDIT_SCREENING) if REDDIT_SCREENING.exists() else []
    reddit_eligible = sum(1 for row in reddit_screening if row.get("eligible") is True)
    belief_status = Counter(row.get("belief_status") for row in reddit_screening if row.get("eligible") is True)
    rejection_reasons = Counter(
        reason
        for row in reddit_screening
        if row.get("eligible") is not True
        for reason in (row.get("rejection_reasons") or [])
    )
    reddit_prep_text = REDDIT_PREP_SUMMARY.read_text(encoding="utf-8") if REDDIT_PREP_SUMMARY.exists() else ""
    reddit_source_rows = parse_first_int(reddit_prep_text, "Source CSV rows")
    reddit_unique_posts = len(read_jsonl(REDDIT_SOURCE_CASES)) if REDDIT_SOURCE_CASES.exists() else 0
    reddit_screen_candidates = len(read_jsonl(REDDIT_SCREEN_CANDIDATES)) if REDDIT_SCREEN_CANDIDATES.exists() else 0
    reddit_duplicates_removed = parse_first_int(reddit_prep_text, "Duplicate rows removed")
    reddit_too_short = parse_first_int(reddit_prep_text, "Too short")
    reddit_too_long = parse_first_int(reddit_prep_text, "Too long")
    reddit_high_risk = parse_first_int(reddit_prep_text, "High-risk lexical exclusion")
    reddit_pii_link = parse_first_int(reddit_prep_text, "PII/link lexical exclusion")
    reddit_no_probe = parse_first_int(reddit_prep_text, "No reality-boundary lexical probe hit")

    reddit_records = by_source["reddit_fictionalized_text_signal"]
    reddit_message_counts = Counter(len(record.get("messages") or []) for record in reddit_records)
    reddit_exact_alternation = sum(
        1
        for record in reddit_records
        if all(
            record["messages"][index]["role"] != record["messages"][index - 1]["role"]
            for index in range(1, len(record.get("messages") or []))
        )
    )
    reddit_all_synthetic = all((record.get("metadata") or {}).get("dialogue_is_synthetic") is True for record in reddit_records)
    reddit_transforms = Counter(
        item.get("transform")
        for record in reddit_records
        for item in (record.get("message_provenance") or [])
    )

    real_records = by_source["dais_c_clinical_interview"] + by_source["fep_interview"] + by_source["dais_c_control_calibration"]
    real_message_counts = [len(record.get("messages") or []) for record in real_records]
    real_coverage_rates = [
        (record.get("quality") or {}).get("source_turn_coverage_rate")
        for record in real_records
        if (record.get("quality") or {}).get("source_turn_coverage_rate") is not None
    ]
    real_max_overlap = max(
        ((record.get("quality") or {}).get("max_common_source_word_run") or 0)
        for record in real_records
    )
    reddit_max_overlap = max(
        ((record.get("quality") or {}).get("max_common_source_word_run") or 0)
        for record in reddit_records
    ) if reddit_records else 0

    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    reddit_session_share = reddit_sessions / total_sessions if total_sessions else 0
    reddit_point_share = reddit_points / total_points if total_points else 0
    true_interview_share = real_interview_sessions / total_sessions if total_sessions else 0

    source_table_rows = []
    for row in source_rows:
        source_table_rows.append(
            [
                esc(row["source"]),
                esc(fmt(row["sessions"])),
                esc(fmt(row["messages"])),
                esc(fmt(row["candidate_points"])),
                esc(fmt(row["sessions_with_points"])),
                esc(
                    f'{fmt(row["messages_min"])} / {row["messages_median"]:.0f} / '
                    f'{row["messages_mean"]:.1f} / {fmt(row["messages_max"])}'
                ),
                esc(f'{fmt(row["exact_alternation"])} / {fmt(row["sessions"])}'),
                esc(", ".join(f"{key}: {value}" for key, value in sorted(row["transforms"].items()))),
                esc(f'{fmt(row["qc_passed"])} passed; max overlap {row["max_source_word_run"]}'),
            ]
        )

    metajudge_table_rows = []
    for label, counter in sorted(metajudge_by_source.items()):
        metajudge_table_rows.append(
            [
                esc(label),
                esc(fmt(sum(counter.values()))),
                esc(fmt(counter.get("accept_candidate", 0))),
                esc(fmt(counter.get("revise_candidate", 0))),
                esc(fmt(counter.get("reject_insufficient_evidence", 0))),
                esc(fmt(counter.get("accept_no_candidate_point", 0))),
            ]
        )

    risk_rows = [
        [
            chip("需要分层", "warn"),
            esc("Reddit dominates total volume"),
            esc(
                f"Reddit contributes {fmt(reddit_sessions)} / {fmt(total_sessions)} sessions "
                f"({pct(reddit_session_share)}) and {fmt(reddit_points)} / {fmt(total_points)} candidate points "
                f"({pct(reddit_point_share)})."
            ),
            esc("Do not report a single undifferentiated clinical/dialogue benchmark size; keep source-family strata."),
        ],
        [
            chip("有效但有限", "warn"),
            esc("Reddit sessions are synthetic dialogues"),
            esc(
                f"All Reddit records have dialogue_is_synthetic={reddit_all_synthetic}; "
                f"message-count histogram is {dict(reddit_message_counts)}; exact alternation {fmt(reddit_exact_alternation)} / {fmt(reddit_sessions)}."
            ),
            esc("Use as real-text-signal-anchored fictional cases, not as natural multi-turn conversation evidence."),
        ],
        [
            chip("较强", "ok"),
            esc("Real interviews preserve case/turn structure"),
            esc(
                f"{fmt(real_interview_sessions)} real interview-derived sessions; source-turn coverage "
                f"{min(real_coverage_rates):.1f}-{max(real_coverage_rates):.1f}; message count range "
                f"{fmt(min(real_message_counts))}-{fmt(max(real_message_counts))}."
            ),
            esc("This is the high-validity core for real multi-turn dialogue structure, but not all cases contain reality-boundary points."),
        ],
        [
            chip("仍需治理", "warn"),
            esc("Automatic checks are not release approval"),
            esc(
                f"Contract validation errors recorded in reviewed pre-audit: {fmt(len(validation_errors))}; "
                f"max source-word overlap real={real_max_overlap} (<32), reddit={reddit_max_overlap} (<12)."
            ),
            esc("License, privacy, rare-event-chain and ShareAlike review remain required before public release."),
        ],
        [
            chip("方法风险", "warn"),
            esc("Same model family in generation and review"),
            esc(
                f"DeepSeek Pro generated sessions and also ran point metajudge/semantic duplicate review. "
                f"Candidate acceptance {pct(metajudge_decisions.get('accept_candidate', 0) / max(1, total_points))}."
            ),
            esc("Add a second model or judge-variance pass before treating candidate points as stable benchmark labels."),
        ],
    ]

    split_table = table(
        ["Release split/status/action", "Count"],
        [[esc(key), esc(fmt(value))] for key, value in sorted(split_counts.items())]
        + [[esc(f"status: {key}"), esc(fmt(value))] for key, value in sorted(status_counts.items())]
        + [[esc(f"action: {key}"), esc(fmt(value))] for key, value in sorted(action_counts.items())],
    )

    reddit_funnel_rows = [
        ["Source CSV rows", reddit_source_rows],
        ["Unique posts after exact-hash deduplication", reddit_unique_posts],
        ["Duplicate rows removed", reddit_duplicates_removed],
        ["Local LLM screen candidates", reddit_screen_candidates],
        ["DeepSeek Pro eligible text signals", reddit_eligible],
        ["Generated fictional sessions", reddit_sessions],
        ["Too short", reddit_too_short],
        ["Too long", reddit_too_long],
        ["High-risk lexical exclusion", reddit_high_risk],
        ["PII/link lexical exclusion", reddit_pii_link],
        ["No reality-boundary lexical probe hit", reddit_no_probe],
    ]

    source_category_sections = []
    for label, counter in sorted(point_categories_by_source.items()):
        if not counter:
            continue
        source_category_sections.append(
            f"<section class=\"panel\"><h3>{esc(label)} point categories</h3>{bar_list(dict(counter))}</section>"
        )

    html_body = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deviation Bench New 数据整体情况报告</title>
<style>
:root {{
  --bg:#f5f6f8; --panel:#ffffff; --ink:#1d2529; --muted:#647176; --line:#d9e0e4;
  --accent:#2d6f73; --accent2:#725c86; --warn:#a86422; --bad:#9e3b3f; --ok:#34784b;
  --soft:#eaf1f1; --yellow:#fff4df; --green:#e4f1e8; --red:#f5e1e2;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); background:var(--bg); font:14px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
header {{ background:var(--panel); border-bottom:1px solid var(--line); padding:24px 28px; }}
h1 {{ margin:0 0 8px; font-size:26px; line-height:1.2; letter-spacing:0; }}
h2 {{ margin:0 0 12px; font-size:20px; line-height:1.25; }}
h3 {{ margin:0 0 10px; font-size:15px; }}
p {{ margin:8px 0; }}
a {{ color:var(--accent); }}
.subtle {{ color:var(--muted); }}
.wrap {{ max-width:1280px; margin:0 auto; padding:18px 24px 40px; }}
.grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
.two {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
.card,.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
.card {{ padding:14px; min-height:92px; }}
.card span {{ display:block; color:var(--muted); font-size:12px; }}
.card b {{ display:block; font-size:27px; line-height:1.15; margin-top:4px; }}
.card small {{ display:block; color:var(--muted); margin-top:6px; }}
.card.warn {{ background:var(--yellow); border-color:#ead0a0; }}
.card.ok {{ background:var(--green); border-color:#b9d9c4; }}
.panel {{ padding:16px; margin:14px 0; }}
.callout {{ border-left:5px solid var(--accent); background:#fbfdfd; }}
.callout.warn {{ border-left-color:var(--warn); background:var(--yellow); }}
.callout.bad {{ border-left-color:var(--bad); background:var(--red); }}
.chip {{ display:inline-block; border-radius:999px; background:var(--soft); padding:2px 8px; font-size:12px; white-space:nowrap; }}
.chip.ok {{ background:var(--green); color:#17472b; }}
.chip.warn {{ background:var(--yellow); color:#704015; }}
.chip.bad {{ background:var(--red); color:#6f2020; }}
table {{ width:100%; border-collapse:collapse; background:white; border:1px solid var(--line); font-size:13px; }}
th,td {{ text-align:left; vertical-align:top; border-bottom:1px solid var(--line); padding:8px 9px; }}
th {{ background:#edf2f3; color:#2e383c; }}
.bars {{ display:grid; gap:8px; }}
.bar-row {{ display:grid; grid-template-columns:minmax(160px,250px) minmax(0,1fr) 116px; gap:10px; align-items:center; }}
.bar-label {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.bar-track {{ height:17px; background:#e7ecef; border-radius:999px; overflow:hidden; }}
.bar-fill {{ height:100%; background:var(--accent); border-radius:999px; }}
.bar-value {{ text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }}
.bar-value small {{ color:var(--muted); }}
.empty {{ color:var(--muted); padding:12px; border:1px dashed var(--line); border-radius:7px; }}
ul {{ margin:8px 0 0 20px; padding:0; }}
li {{ margin:5px 0; }}
code {{ background:#edf2f3; border-radius:4px; padding:1px 4px; }}
footer {{ color:var(--muted); border-top:1px solid var(--line); margin-top:24px; padding-top:14px; }}
@media (max-width:1000px) {{ .grid,.two {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
@media (max-width:640px) {{ .wrap {{ padding:12px; }} .grid,.two {{ grid-template-columns:1fr; }} .bar-row {{ grid-template-columns:1fr; }} .bar-value {{ text-align:left; }} }}
</style>
</head>
<body>
<header>
  <h1>Deviation Bench New 数据整体情况报告</h1>
  <div class="subtle">Generated at {esc(generated_at)} · dataset version: <code>{esc(dataset_version)}</code></div>
</header>
<main class="wrap">
  <section class="grid">
    {card("Total real-data-derived sessions", fmt(total_sessions), "包含真实访谈派生与 Reddit 文本信号虚构扩写", "ok")}
    {card("Real multi-turn interview-derived", fmt(real_interview_sessions), f"{fmt(psychosis_related_interview_sessions)} psychosis-related + 13 controls", "ok")}
    {card("Reddit fictionalized sessions", fmt(reddit_sessions), f"{pct(reddit_session_share)} of all sessions", "warn")}
    {card("Candidate points", fmt(total_points), f"Reddit contributes {pct(reddit_point_share)}", "warn")}
    {card("Messages", fmt(total_messages), "OpenAI-style role/content messages")}
    {card("Sessions with candidate points", fmt(sessions_with_points), "Includes all Reddit synthetic sessions")}
    {card("Reviewed included sessions", fmt(status_counts.get("included", 0)), f"{fmt(len(excluded_duplicate_ids))} duplicate candidates excluded", "ok")}
    {card("Validation errors", fmt(len(validation_errors)), "Reviewed pre-audit contract/PII validation list", "ok" if not validation_errors else "warn")}
  </section>

  <section class="panel callout warn">
    <h2>核心结论</h2>
    <p>当前数据层总共有 <b>{fmt(total_sessions)}</b> 个 real-data-derived session，但其中只有 <b>{fmt(real_interview_sessions)}</b> 个来自真实多轮访谈的 turn-level 语义改写；<b>{fmt(reddit_sessions)}</b> 个来自 Reddit 单帖文本信号，经 DeepSeek Pro 筛选后虚构扩写为 12-message 对话。</p>
    <p>因此，当前数据可以说是“真实数据派生 session corpus”，但不能把全部 {fmt(total_sessions)} 个 session 说成真实对话，也不能把 Reddit session 当成临床 ground truth 或真实 conversation dynamics。Reddit 更适合作为 <b>community text-signal anchored fictional cases</b> 单独分层使用。</p>
  </section>

  <section class="panel">
    <h2>Source Accounting</h2>
    {table(
        [
            "Source family",
            "Sessions",
            "Messages",
            "Candidate points",
            "Sessions with points",
            "Message count min/median/mean/max",
            "Exact role alternation",
            "Transform",
            "QC",
        ],
        source_table_rows,
    )}
  </section>

  <section class="two">
    <section class="panel">
      <h2>Session Volume By Source</h2>
      {bar_list({source_display(family): len(rows) for family, rows in by_source.items()}, total_sessions)}
    </section>
    <section class="panel">
      <h2>Candidate Points By Category</h2>
      {bar_list(dict(point_categories), total_points)}
    </section>
  </section>

  <section class="panel">
    <h2>Session 设置是否合理？</h2>
    <table>
      <thead><tr><th>判断</th><th>对象</th><th>证据</th><th>使用边界 / 建议</th></tr></thead>
      <tbody>
      {''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in risk_rows)}
      </tbody>
    </table>
  </section>

  <section class="two">
    <section class="panel">
      <h2>Reddit Funnel</h2>
      {table(["Step", "Count"], [[esc(label), esc(fmt(value if value is not None else "unknown"))] for label, value in reddit_funnel_rows])}
    </section>
    <section class="panel">
      <h2>Reddit Eligible Belief Status</h2>
      {bar_list(dict(belief_status), max(1, reddit_eligible))}
      <h3 style="margin-top:16px">Screening Rejection Reasons</h3>
      {bar_list(dict(rejection_reasons), max(1, sum(rejection_reasons.values())))}
    </section>
  </section>

  <section class="panel">
    <h2>Point Metajudge Results</h2>
    <p class="subtle">Independent second pass still used DeepSeek Pro, so this is a consistency check, not gold human evidence.</p>
    {table(
        ["Source family", "Review units", "Accept candidate", "Revise candidate", "Reject insufficient evidence", "Accept no candidate"],
        metajudge_table_rows,
    )}
    <div class="two">
      <section>
        <h3 style="margin-top:16px">Overall decisions</h3>
        {bar_list(dict(metajudge_decisions), max(1, sum(metajudge_decisions.values())))}
      </section>
      <section>
        <h3 style="margin-top:16px">Flags</h3>
        {table(["Flag", "Count"], [["diagnosis_or_membership_inference", esc(fmt(diagnosis_flags))], ["identifying_detail_risk", esc(fmt(identifying_flags))]])}
      </section>
    </div>
  </section>

  <section class="two">
    <section class="panel">
      <h2>Reviewed Split / Release Status</h2>
      {split_table}
    </section>
    <section class="panel">
      <h2>Semantic Duplicate / Leakage Review</h2>
      {table(
          ["Metric", "Count"],
          [
              ["Pair candidates reviewed", esc(fmt(len(duplicate_rows)))],
              ["duplicate", esc(fmt(duplicate_decisions.get("duplicate", 0)))],
              ["near_duplicate", esc(fmt(duplicate_decisions.get("near_duplicate", 0)))],
              ["not_duplicate", esc(fmt(duplicate_decisions.get("not_duplicate", 0)))],
              ["recommended exclude_one", esc(fmt(duplicate_actions.get("exclude_one", 0)))],
              ["recommended same_split", esc(fmt(duplicate_actions.get("same_split", 0)))],
              ["medium/high leakage pairs", esc(fmt(leakage_risks.get("medium", 0) + leakage_risks.get("high", 0)))],
          ],
      )}
    </section>
  </section>

  <section class="panel callout">
    <h2>对 Reddit 派生对话的有效性判断</h2>
    <p>Reddit 数据当前的作用是扩大“现实边界文本信号”的覆盖，而不是提供真实多轮对话。它的优点是来源量大、经过本地排除与 LLM semantic screening、tracked output 不含原帖文本，且严格 source-overlap 阈值通过。它的问题同样明显：上游是单帖，不是交互；所有输出都是固定 12 条消息、严格 user/assistant 交替；所有生成成功的 session 都有至少一个 candidate point；并且同一模型参与了筛选、生成和第一轮复核。</p>
    <p>当前最稳妥的写法是：<b>{fmt(reddit_sessions)} Reddit sessions are fictionalized sessions anchored in screened community text signals</b>。下游 benchmark 不应把它们和 DAIS/FEP 真实访谈混成同一类；建议在 release split 和论文表格中单列 Reddit，并在主指标中使用 source-family weighting 或单独报告。</p>
  </section>

  <section class="panel">
    <h2>What We Can Claim / Cannot Claim</h2>
    <div class="two">
      <section>
        <h3>可以较稳妥地 claim</h3>
        <ul>
          <li>已经生成 {fmt(total_sessions)} 个可结构校验的 real-data-derived OpenAI-style session。</li>
          <li>其中 {fmt(real_interview_sessions)} 个保留真实多轮访谈结构，source-turn coverage 为 1.0。</li>
          <li>{fmt(reddit_sessions)} 个 Reddit 输出是去标识化、虚构扩写的 text-signal sessions。</li>
          <li>Reviewed split 标记 {fmt(status_counts.get("included", 0))} 个 included、{fmt(len(excluded_duplicate_ids))} 个 excluded duplicate candidates。</li>
        </ul>
      </section>
      <section>
        <h3>不能 claim</h3>
        <ul>
          <li>不能说 {fmt(total_sessions)} 个 session 都是真实对话。</li>
          <li>不能说 Reddit 社区归属或 DAIS/FEP 组别就是 delusion diagnosis。</li>
          <li>不能把 `delusion_points` 当 clinical ground truth；它们是 LLM-extracted candidate signals。</li>
          <li>不能把 regex PII=0 和 source-overlap 通过等同于发布伦理/隐私审查完成。</li>
        </ul>
      </section>
    </div>
  </section>

  <section class="panel">
    <h2>Recommended Next Decisions</h2>
    <ol>
      <li>先确定下游 benchmark 的主证据层：建议以 42 个真实多轮访谈派生 session 为结构核心，Reddit 作为单独的 synthetic/community augmentation stratum。</li>
      <li>对 Reddit strata 增加 validity gate：抽样检查 source-signal 是否被过度扩写，或用第二模型评估“是否只保留抽象信号、没有虚构关键证据”。</li>
      <li>主结果表不要按 raw count 让 Reddit 淹没访谈来源；使用 source-family weighting、分表报告或 cap per-source contribution。</li>
      <li>发布前继续做 license/privacy/governance review，尤其是 Reddit 平台隐私、稀有事件链和 DAIS-C ShareAlike 边界。</li>
    </ol>
  </section>

  <section class="panel">
    <h2>Per-source Category Detail</h2>
    {''.join(source_category_sections)}
  </section>

  <footer>
    <p>Inputs: <code>data/processed/*_64k.jsonl</code>, reviewed split/audit manifests, point metajudge outputs, semantic duplicate review outputs, and Reddit screening manifests. This page intentionally does not embed raw transcript text, raw Reddit posts, or raw API responses.</p>
  </footer>
</main>
</body>
</html>
"""
    return html_body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
