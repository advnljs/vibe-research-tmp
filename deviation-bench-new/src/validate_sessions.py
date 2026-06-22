#!/usr/bin/env python3
"""Validate processed Deviation Bench New session JSONL files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from session_contract import scan_pii, validate_session_record


def read_sessions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not an object")
            rows.append(value)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    sessions: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in args.inputs:
        for record in read_sessions(path):
            sessions.append(record)
            for error in validate_session_record(record):
                errors.append(f"{record.get('session_id', '<missing>')}: {error}")
            public_texts = [message.get("content", "") for message in record.get("messages") or []]
            public_texts.extend(point.get("summary", "") for point in record.get("delusion_points") or [])
            pii_hits = scan_pii(public_texts)
            if pii_hits:
                errors.append(f"{record.get('session_id', '<missing>')}: public text PII scan hit")

    ids = [record.get("session_id") for record in sessions]
    duplicates = [session_id for session_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate session IDs: {duplicates}")

    total_messages = sum(len(record.get("messages") or []) for record in sessions)
    total_points = sum(len(record.get("delusion_points") or []) for record in sessions)
    print(
        f"sessions={len(sessions)} messages={total_messages} delusion_points={total_points} "
        f"errors={len(errors)}"
    )
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
