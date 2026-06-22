#!/usr/bin/env python3
"""Parse tracked real interview sources into ignored, normalized case files."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree


NEW_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = NEW_ROOT.parent
OLD_DATA_ROOT = WORKSPACE_ROOT / "deviation-bench" / "data_sources" / "downloaded"
DEFAULT_PREPARED_DIR = NEW_ROOT / "data" / "work" / "prepared_cases"
DEFAULT_MANIFEST = NEW_ROOT / "data" / "manifests" / "source_cases.jsonl"
PARSER_VERSION = "0.1.0"

DAIS_ROOT = OLD_DATA_ROOT / "dais_c" / "extracted" / "DAIS-C-Annotated - Upload"
FEP_ROOT = OLD_DATA_ROOT / "first_episode_psychosis_friendship" / "text"

DAIS_CITATION = (
    "Delgaram-Nejad et al. (2023), Discussing Abstract Ideas in Schizophrenia Corpus, "
    "UK Data Service, doi:10.5255/UKDA-SN-855021."
)
FEP_CITATION = (
    "Huckle, Lemmel, and Johnson (2021), Experiences of friendships of young people "
    "with first-episode psychosis, PLOS ONE 16(7):e0255469."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\ufffd", "'")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \t\r\n|")


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        document = archive.read("word/document.xml")
    root = ElementTree.fromstring(document)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs = []
    for paragraph in root.iter(namespace + "p"):
        parts = []
        for node in paragraph.iter():
            if node.tag == namespace + "t" and node.text:
                parts.append(node.text)
            elif node.tag in {namespace + "tab"}:
                parts.append("\t")
            elif node.tag in {namespace + "br", namespace + "cr"}:
                parts.append("\n")
        joined = "".join(parts).strip()
        if joined:
            paragraphs.append(joined)
    return "\n".join(paragraphs)


def extract_rtf_text(path: Path) -> str:
    """Extract visible-enough text from the corpus RTF files without a new dependency.

    The dialogue speaker tags are literal text in these files. Font/color tables may
    leave harmless noise before the first tag; tagged-turn extraction ignores it.
    """

    text = path.read_bytes().decode("cp1252", errors="replace")

    def decode_hex(match: re.Match[str]) -> str:
        return bytes.fromhex(match.group(1)).decode("cp1252", errors="replace")

    def decode_unicode(match: re.Match[str]) -> str:
        value = int(match.group(1))
        if value < 0:
            value += 65536
        try:
            return chr(value)
        except ValueError:
            return "\ufffd"

    text = re.sub(r"\\'([0-9a-fA-F]{2})", decode_hex, text)
    text = re.sub(r"\\u(-?\d+)\??", decode_unicode, text)
    text = re.sub(r"\\(?:par|line)\b\s?", "\n", text)
    text = re.sub(r"\\tab\b\s?", "\t", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d*\s?", "", text)
    text = re.sub(r"\\([^a-zA-Z])", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    return text


def parse_dais_tagged_text(text: str, case_code: str) -> list[dict[str, str]]:
    speaker = re.escape(case_code)
    pattern = re.compile(
        rf"<\s*(INT|{speaker})\s*>(.*?)<\s*/\s*\1\s*>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    turns: list[dict[str, str]] = []
    for tag, body in pattern.findall(text):
        content = clean_text(body)
        if not content:
            continue
        turns.append(
            {
                "source_turn_id": f"st{len(turns) + 1:04d}",
                "speaker": "interviewer" if tag.upper() == "INT" else "participant",
                "text": content,
            }
        )
    return turns


def parse_dais_file(path: Path) -> list[dict[str, str]]:
    case_code = path.name.rsplit("-FULL", 1)[0]
    if path.suffix.lower() == ".docx":
        text = extract_docx_text(path)
    elif path.suffix.lower() == ".rtf":
        text = extract_rtf_text(path)
    else:
        raise ValueError(f"unsupported DAIS-C format: {path}")
    turns = parse_dais_tagged_text(text, case_code)
    if len(turns) < 2:
        raise ValueError(f"failed to recover dialogue turns from {path}")
    return turns


def parse_fep_table_text(text: str, participant_number: str) -> list[dict[str, str]]:
    turns: list[dict[str, str]] = []
    current_speaker: str | None = None
    current_parts: list[str] = []

    def flush() -> None:
        nonlocal current_speaker, current_parts
        content = clean_text(" ".join(current_parts))
        if current_speaker and content:
            turns.append(
                {
                    "source_turn_id": f"st{len(turns) + 1:04d}",
                    "speaker": current_speaker,
                    "text": content,
                }
            )
        current_speaker = None
        current_parts = []

    for line in text.splitlines():
        if line.count("|") < 4:
            continue
        fields = line.split("|")
        if len(fields) < 5:
            continue
        label = fields[1].strip()
        content = fields[2].strip()
        if label:
            flush()
            if label.upper() == "CH":
                current_speaker = "interviewer"
            elif label == participant_number:
                current_speaker = "participant"
            else:
                current_speaker = None
        if current_speaker and content:
            current_parts.append(content)
    flush()
    return turns


def parse_fep_file(path: Path) -> list[dict[str, str]]:
    match = re.search(r"Participant\s+(\d+)", path.stem, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"cannot identify participant number: {path}")
    turns = parse_fep_table_text(path.read_text(encoding="utf-8", errors="replace"), match.group(1))
    if len(turns) < 2:
        raise ValueError(f"failed to recover dialogue turns from {path}")
    return turns


def relative_to_workspace(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE_ROOT.resolve()).as_posix()


def dais_case_specs() -> Iterable[dict[str, Any]]:
    groups = [
        ("CL", "clinical_schizophrenia", "dais_c_cl"),
        ("CO", "control", "dais_c_co"),
    ]
    for group_code, source_group, prefix in groups:
        source_dir = DAIS_ROOT / f"DAI-C-{group_code}" / "Interactional" / "Full tagged pass"
        paths = sorted(
            path
            for path in source_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".docx", ".rtf"} and not path.name.startswith("~$")
        )
        for index, path in enumerate(paths, start=1):
            yield {
                "session_id": f"{prefix}_{index:03d}",
                "source_dataset": "dais_c",
                "source_group": source_group,
                "source_path": path,
                "source_license": "CC BY-SA 4.0",
                "source_citation": DAIS_CITATION,
                "parser": "dais_interactional_tagged",
                "parse": parse_dais_file,
            }


def fep_case_specs() -> Iterable[dict[str, Any]]:
    paths = sorted(
        FEP_ROOT.glob("Participant *.txt"),
        key=lambda path: int(re.search(r"(\d+)", path.stem).group(1)),
    )
    for index, path in enumerate(paths, start=1):
        yield {
            "session_id": f"fep_friendship_{index:03d}",
            "source_dataset": "first_episode_psychosis_friendship",
            "source_group": "first_episode_psychosis",
            "source_path": path,
            "source_license": "CC BY 4.0",
            "source_citation": FEP_CITATION,
            "parser": "antiword_table_interview",
            "parse": parse_fep_file,
        }


def prepare_case(spec: dict[str, Any], prepared_dir: Path) -> dict[str, Any]:
    source_path: Path = spec["source_path"]
    turns = spec["parse"](source_path)
    role_counts = Counter(turn["speaker"] for turn in turns)
    parse_warnings = []
    if role_counts.get("participant", 0) == 0:
        parse_warnings.append("missing_participant_role")
    if role_counts.get("interviewer", 0) == 0:
        parse_warnings.append("missing_interviewer_role")
    prepared = {
        "schema_version": "0.1.0",
        "session_id": spec["session_id"],
        "source_dataset": spec["source_dataset"],
        "source_group": spec["source_group"],
        "source_license": spec["source_license"],
        "source_citation": spec["source_citation"],
        "source_path": relative_to_workspace(source_path),
        "source_sha256": sha256_file(source_path),
        "parser": spec["parser"],
        "parser_version": PARSER_VERSION,
        "parse_status": "warning" if parse_warnings else "passed",
        "parse_warnings": parse_warnings,
        "turns": turns,
    }
    prepared_dir.mkdir(parents=True, exist_ok=True)
    prepared_path = prepared_dir / f"{spec['session_id']}.json"
    prepared_path.write_text(json.dumps(prepared, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "schema_version": "0.1.0",
        "session_id": spec["session_id"],
        "source_dataset": spec["source_dataset"],
        "source_group": spec["source_group"],
        "source_path": relative_to_workspace(source_path),
        "source_sha256": prepared["source_sha256"],
        "source_license": spec["source_license"],
        "source_citation": spec["source_citation"],
        "parser": spec["parser"],
        "parser_version": PARSER_VERSION,
        "source_turn_count": len(turns),
        "source_char_count": sum(len(turn["text"]) for turn in turns),
        "role_counts": dict(sorted(role_counts.items())),
        "parse_status": prepared["parse_status"],
        "parse_warnings": prepared["parse_warnings"],
        "prepared_path": relative_to_workspace(prepared_path),
        "delusion_ground_truth": False,
        "intended_use": "deidentified_session_conversion_and_candidate_signal_extraction",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", type=Path, default=DEFAULT_PREPARED_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--sources",
        default="dais_c_cl,dais_c_co,fep_friendship",
        help="Comma-separated source prefixes to prepare.",
    )
    args = parser.parse_args()

    selected = {item.strip() for item in args.sources.split(",") if item.strip()}
    specs = []
    if {"dais_c_cl", "dais_c_co"} & selected:
        specs.extend(spec for spec in dais_case_specs() if spec["session_id"].rsplit("_", 1)[0] in selected)
    if "fep_friendship" in selected:
        specs.extend(fep_case_specs())
    if not specs:
        raise ValueError(f"no recognized sources selected: {sorted(selected)}")

    records = [prepare_case(spec, args.prepared_dir) for spec in specs]
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )

    dataset_counts = Counter(record["source_dataset"] for record in records)
    total_turns = sum(record["source_turn_count"] for record in records)
    print(
        f"prepared_cases={len(records)} total_turns={total_turns} "
        f"datasets={dict(sorted(dataset_counts.items()))} manifest={args.manifest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
