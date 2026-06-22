"""Shared validation helpers for Deviation Bench New session data."""

from __future__ import annotations

import difflib
import re
from typing import Any, Iterable


SCHEMA_VERSION = "0.1.0"
ALLOWED_ROLES = {"user", "assistant"}
ALLOWED_CATEGORIES = {
    "persecutory",
    "referential",
    "grandiose",
    "somatic",
    "religious",
    "jealous",
    "nihilistic",
    "control_or_influence",
    "thought_interference",
    "other_reality_boundary",
}
ALLOWED_EXPLICITNESS = {"explicit", "implicit", "unclear"}
LABEL_STATUS = "llm_extracted_candidate_not_diagnosis"
ALLOWED_TRANSFORMS = {"llm_semantic_paraphrase", "llm_fictional_expansion"}

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "url": re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE),
    "phone": re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)"),
    "uk_postcode": re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.IGNORECASE),
}


def normalize_words(text: str) -> list[str]:
    return re.findall(r"[\w']+", text.lower(), flags=re.UNICODE)


def longest_common_word_run(left: str, right: str) -> int:
    left_words = normalize_words(left)
    right_words = normalize_words(right)
    if not left_words or not right_words:
        return 0
    match = difflib.SequenceMatcher(None, left_words, right_words, autojunk=False).find_longest_match(
        0,
        len(left_words),
        0,
        len(right_words),
    )
    return int(match.size)


def scan_pii(texts: Iterable[str], forbidden_tokens: Iterable[str] = ()) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    combined = "\n".join(texts)
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(combined):
            hits.append({"type": label, "value": "[REDACTED_MATCH]"})
    lowered = combined.lower()
    for token in forbidden_tokens:
        token = token.strip()
        if len(token) >= 4 and token.lower() in lowered:
            hits.append({"type": "source_identifier", "value": "[REDACTED_MATCH]"})
    return hits


def validate_chunk_result(
    result: dict[str, Any],
    source_turns: list[dict[str, str]],
    max_source_word_run: int,
) -> tuple[list[str], int]:
    errors: list[str] = []
    messages = result.get("messages")
    if not isinstance(messages, list):
        return ["messages must be a list"], 0
    if len(messages) != len(source_turns):
        errors.append(f"message count {len(messages)} != source turn count {len(source_turns)}")

    maximum_overlap = 0
    for index, source in enumerate(source_turns):
        if index >= len(messages) or not isinstance(messages[index], dict):
            errors.append(f"message[{index}] is missing or not an object")
            continue
        message = messages[index]
        expected_role = "user" if source["speaker"] == "participant" else "assistant"
        if message.get("source_turn_id") != source["source_turn_id"]:
            errors.append(f"message[{index}] source_turn_id mismatch")
        if message.get("role") != expected_role:
            errors.append(f"message[{index}] role mismatch")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"message[{index}] content is empty")
            continue
        overlap = longest_common_word_run(source["text"], content)
        maximum_overlap = max(maximum_overlap, overlap)
        if overlap >= max_source_word_run:
            errors.append(
                f"message[{index}] copies a source run of {overlap} words (limit < {max_source_word_run})"
            )

    points = result.get("candidate_delusion_points", [])
    if not isinstance(points, list):
        errors.append("candidate_delusion_points must be a list")
        points = []
    allowed_ids = {turn["source_turn_id"] for turn in source_turns if turn["speaker"] == "participant"}
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"candidate_delusion_points[{index}] is not an object")
            continue
        if point.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"candidate_delusion_points[{index}] has invalid category")
        if point.get("explicitness") not in ALLOWED_EXPLICITNESS:
            errors.append(f"candidate_delusion_points[{index}] has invalid explicitness")
        source_ids = point.get("source_turn_ids")
        if not isinstance(source_ids, list) or not source_ids or not set(source_ids) <= allowed_ids:
            errors.append(f"candidate_delusion_points[{index}] has invalid participant source_turn_ids")
        confidence = point.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"candidate_delusion_points[{index}] has invalid confidence")
        if not isinstance(point.get("summary"), str) or not point["summary"].strip():
            errors.append(f"candidate_delusion_points[{index}] has empty summary")
    return errors, maximum_overlap


def validate_consolidation(
    result: dict[str, Any],
    participant_source_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(result.get("case_summary"), str):
        errors.append("case_summary must be a string")
    points = result.get("delusion_points")
    if not isinstance(points, list):
        return errors + ["delusion_points must be a list"]
    reason = result.get("no_delusion_point_reason")
    if points and reason not in {None, ""}:
        errors.append("no_delusion_point_reason must be null when points exist")
    if not points and (not isinstance(reason, str) or not reason.strip()):
        errors.append("no_delusion_point_reason is required when points are empty")
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"delusion_points[{index}] is not an object")
            continue
        if point.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"delusion_points[{index}] has invalid category")
        if point.get("explicitness") not in ALLOWED_EXPLICITNESS:
            errors.append(f"delusion_points[{index}] has invalid explicitness")
        source_ids = point.get("source_turn_ids")
        if not isinstance(source_ids, list) or not source_ids or not set(source_ids) <= participant_source_ids:
            errors.append(f"delusion_points[{index}] has invalid participant source_turn_ids")
        confidence = point.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"delusion_points[{index}] has invalid confidence")
        if not isinstance(point.get("summary"), str) or not point["summary"].strip():
            errors.append(f"delusion_points[{index}] has empty summary")
    return errors


def validate_session_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version mismatch")
    if not isinstance(record.get("session_id"), str) or not record["session_id"]:
        errors.append("session_id is missing")
    messages = record.get("messages")
    provenance = record.get("message_provenance")
    if not isinstance(messages, list) or len(messages) < 2:
        errors.append("messages must contain at least two items")
        messages = []
    if not isinstance(provenance, list) or len(provenance) != len(messages):
        errors.append("message_provenance length must equal messages length")
        provenance = []
    seen_source_ids: list[str] = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            errors.append(f"messages[{index}] is not an object")
            continue
        if set(message) != {"role", "content"}:
            errors.append(f"messages[{index}] must contain only role/content")
        if message.get("role") not in ALLOWED_ROLES:
            errors.append(f"messages[{index}] has invalid role")
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            errors.append(f"messages[{index}] has empty content")
    for index, item in enumerate(provenance):
        if not isinstance(item, dict):
            errors.append(f"message_provenance[{index}] is not an object")
            continue
        if item.get("message_index") != index:
            errors.append(f"message_provenance[{index}] index mismatch")
        source_ids = item.get("source_turn_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"message_provenance[{index}] missing source_turn_ids")
        else:
            seen_source_ids.extend(str(value) for value in source_ids)
        if item.get("transform") not in ALLOWED_TRANSFORMS:
            errors.append(f"message_provenance[{index}] invalid transform")
    transforms = {item.get("transform") for item in provenance if isinstance(item, dict)}
    if transforms == {"llm_semantic_paraphrase"} and len(seen_source_ids) != len(set(seen_source_ids)):
        errors.append("source turn IDs are duplicated in message_provenance")

    points = record.get("delusion_points")
    if not isinstance(points, list):
        errors.append("delusion_points must be a list")
        points = []
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"delusion_points[{index}] is not an object")
            continue
        if point.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"delusion_points[{index}] invalid category")
        if point.get("explicitness") not in ALLOWED_EXPLICITNESS:
            errors.append(f"delusion_points[{index}] invalid explicitness")
        if point.get("label_status") != LABEL_STATUS:
            errors.append(f"delusion_points[{index}] invalid label_status")
        source_ids = point.get("source_turn_ids")
        if not isinstance(source_ids, list) or not source_ids or not set(source_ids) <= set(seen_source_ids):
            errors.append(f"delusion_points[{index}] invalid source_turn_ids")
        indices = point.get("message_indices")
        if not isinstance(indices, list) or not indices or any(
            not isinstance(value, int) or value < 0 or value >= len(messages) for value in indices
        ):
            errors.append(f"delusion_points[{index}] invalid message_indices")
        confidence = point.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"delusion_points[{index}] invalid confidence")
    reason = record.get("no_delusion_point_reason")
    if points and reason not in {None, ""}:
        errors.append("no_delusion_point_reason must be null when points exist")
    if not points and (not isinstance(reason, str) or not reason.strip()):
        errors.append("no_delusion_point_reason required for empty points")
    quality = record.get("quality")
    if not isinstance(quality, dict):
        errors.append("quality must be an object")
    elif quality.get("status") != "passed":
        errors.append("quality.status must be passed")
    return errors
