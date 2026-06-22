#!/usr/bin/env python3
"""Prepare de-duplicated Reddit cases for LLM screening without tracking raw posts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
SOURCE_ROOT = (
    WORKSPACE_ROOT
    / "deviation-bench"
    / "data_sources"
    / "downloaded"
    / "reddit_mental_health_zenodo"
)
DEFAULT_WORK_DIR = ROOT / "data" / "work" / "reddit_cases"
DEFAULT_MANIFEST = ROOT / "data" / "manifests" / "reddit_source_cases.jsonl"
DEFAULT_CANDIDATES = ROOT / "data" / "manifests" / "reddit_screen_candidates.jsonl"
DEFAULT_SUMMARY = ROOT / "data" / "manifests" / "reddit_preparation_summary.md"

HIGH_RISK = re.compile(
    r"\b(?:suicid|kill myself|self[- ]harm|murder|shoot|stab|attack|revenge)\b",
    re.IGNORECASE,
)
PII = re.compile(
    r"(?:\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|\bhttps?://\S+|\bwww\.\S+|"
    r"\+?\d[\d ()-]{7,}\d)",
    re.IGNORECASE,
)
REALITY_LEXICAL_PROBE = re.compile(
    r"\b(?:follow(?:ing|ed)?|watch(?:ing|ed)?|spy|spying|plot|conspir|target(?:ing|ed)?|"
    r"against me|poison|signs?|messages?|signals?|meant for me|about me|read my mind|"
    r"mind reading|thought broadcast|thought insertion|control(?:ling|led)? my (?:mind|thoughts)|"
    r"voices?|delusion|delusional|paranoi|government|telepath|implant|simulation|gang stalk|"
    r"stalking me|special powers?|chosen one)\b",
    re.IGNORECASE,
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_files() -> list[Path]:
    return sorted(SOURCE_ROOT.glob("schizophrenia_*_features_tfidf_256.csv"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--min-chars", type=int, default=80)
    parser.add_argument("--max-chars", type=int, default=5000)
    args = parser.parse_args()

    args.work_dir.mkdir(parents=True, exist_ok=True)
    seen_hashes: set[str] = set()
    manifest_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    for source_path in source_files():
        with source_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            for row_number, row in enumerate(csv.DictReader(handle), start=2):
                counts["total_rows"] += 1
                text = str(row.get("post") or "").strip()
                post_hash = sha256_text(text)
                if post_hash in seen_hashes:
                    counts["duplicate"] += 1
                    continue
                seen_hashes.add(post_hash)
                case_id = f"reddit_case_{post_hash[:16]}"
                exclusion_reasons = []
                if len(text) < args.min_chars:
                    exclusion_reasons.append("too_short")
                if len(text) > args.max_chars:
                    exclusion_reasons.append("too_long")
                if HIGH_RISK.search(text):
                    exclusion_reasons.append("high_risk_lexical_exclusion")
                if PII.search(text):
                    exclusion_reasons.append("pii_or_link_lexical_exclusion")
                lexical_candidate = bool(REALITY_LEXICAL_PROBE.search(text))
                if not lexical_candidate:
                    exclusion_reasons.append("no_reality_boundary_lexical_probe_hit")

                status = "screen_candidate" if not exclusion_reasons else "excluded_before_llm_screen"
                for reason in exclusion_reasons:
                    counts[reason] += 1
                counts[status] += 1
                prepared_path = args.work_dir / f"{case_id}.json"
                prepared = {
                    "schema_version": "0.1.0",
                    "case_id": case_id,
                    "source_dataset": "reddit_mental_health_zenodo_r_schizophrenia",
                    "source_file": source_path.name,
                    "source_row_number": row_number,
                    "source_post_sha256": post_hash,
                    "source_license": "ODC-PDDL; Reddit platform/privacy constraints also apply",
                    "text": text,
                }
                prepared_path.write_text(json.dumps(prepared, ensure_ascii=False, indent=2), encoding="utf-8")
                manifest = {
                    "schema_version": "0.1.0",
                    "case_id": case_id,
                    "source_dataset": prepared["source_dataset"],
                    "source_file": source_path.name,
                    "source_row_number": row_number,
                    "source_post_sha256": post_hash,
                    "source_license": prepared["source_license"],
                    "source_char_count": len(text),
                    "status": status,
                    "exclusion_reasons": exclusion_reasons,
                    "lexical_probe_is_label": False,
                    "prepared_path": prepared_path.resolve().relative_to(WORKSPACE_ROOT.resolve()).as_posix(),
                    "delusion_ground_truth": False,
                }
                manifest_rows.append(manifest)
                if status == "screen_candidate":
                    candidate_rows.append(manifest)

    write_jsonl(args.manifest, manifest_rows)
    write_jsonl(args.candidates, candidate_rows)
    lines = [
        "# Reddit Case Preparation Summary",
        "",
        f"- Source CSV rows: `{counts['total_rows']}`",
        f"- Unique posts after exact-hash deduplication: `{len(manifest_rows)}`",
        f"- Duplicate rows removed: `{counts['duplicate']}`",
        f"- LLM screen candidates: `{len(candidate_rows)}`",
        f"- Too short: `{counts['too_short']}`",
        f"- Too long: `{counts['too_long']}`",
        f"- High-risk lexical exclusion: `{counts['high_risk_lexical_exclusion']}`",
        f"- PII/link lexical exclusion: `{counts['pii_or_link_lexical_exclusion']}`",
        f"- No reality-boundary lexical probe hit: `{counts['no_reality_boundary_lexical_probe_hit']}`",
        "",
        "The lexical probe is candidate generation only. It is not a diagnosis, delusion label, or evidence that a post is eligible.",
        "Raw post text is stored only under ignored `data/work/reddit_cases/`; tracked manifests contain hashes and lineage only.",
        "",
    ]
    args.summary.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"source_rows={counts['total_rows']} unique_posts={len(manifest_rows)} "
        f"screen_candidates={len(candidate_rows)} manifest={args.manifest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
