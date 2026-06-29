#!/usr/bin/env python3
"""Build de-identified one-case-per-session JSONL with an LLM."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import re
import socket
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from session_contract import (
    LABEL_STATUS,
    SCHEMA_VERSION,
    longest_common_word_run,
    scan_pii,
    validate_chunk_result,
    validate_consolidation,
    validate_session_record,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_MANIFEST = ROOT / "data" / "manifests" / "source_cases.jsonl"
DEFAULT_PREPARED_DIR = ROOT / "data" / "work" / "prepared_cases"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "deepseek_v4_pro_batch_001.jsonl"
DEFAULT_SUMMARY = ROOT / "data" / "processed" / "deepseek_v4_pro_batch_001_summary.md"
DEFAULT_CHUNK_PROMPT = ROOT / "prompts" / "case_chunk_to_messages.md"
DEFAULT_CONSOLIDATE_PROMPT = ROOT / "prompts" / "consolidate_delusion_points.md"
DEFAULT_REPAIR_PROMPT = ROOT / "prompts" / "repair_source_overlap.md"
DEFAULT_KEY_FILE = WORKSPACE_ROOT / "ds_key.txt"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            rows.append(value)
    return rows


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def estimate_tokens(text: str) -> int:
    """Conservative dependency-free estimate for the current English source data."""

    return max(1, math.ceil(len(text) / 4))


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        value = json.loads(stripped)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    if start < 0:
        raise ValueError("response contains no JSON object")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(stripped)):
        char = stripped[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                value = json.loads(stripped[start : index + 1])
                if not isinstance(value, dict):
                    raise ValueError("top-level response is not a JSON object")
                return value
    raise ValueError("response contains an incomplete JSON object")


def openai_compatible_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: int,
    max_retries: int,
    thinking_mode: str,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if thinking_mode != "omit":
        payload["thinking"] = {"type": thinking_mode}
    request_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=request_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return str(body["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            last_error = RuntimeError(f"API HTTP {exc.code}: {detail}")
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt >= max_retries:
                raise last_error from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout, KeyError, ValueError) as exc:
            last_error = exc
            if attempt >= max_retries:
                raise RuntimeError(f"API request failed: {exc}") from exc
        time.sleep(min(2**attempt, 8))
    raise RuntimeError(f"API request failed: {last_error}")


def split_turns(
    turns: list[dict[str, str]],
    max_chars: int,
    max_turns: int,
) -> list[list[dict[str, str]]]:
    chunks: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    current_chars = 0
    for turn in turns:
        turn_chars = len(turn["text"])
        if current and (len(current) >= max_turns or current_chars + turn_chars > max_chars):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(turn)
        current_chars += turn_chars
    if current:
        chunks.append(current)
    return chunks


def mock_chunk_result(turns: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "messages": [
            {
                "source_turn_id": turn["source_turn_id"],
                "role": "user" if turn["speaker"] == "participant" else "assistant",
                "content": f"[MOCK] De-identified semantic placeholder for {turn['source_turn_id']}.",
            }
            for turn in turns
        ],
        "candidate_delusion_points": [],
        "sensitive_content_flags": [],
        "quality_self_check": {
            "all_source_turns_covered_once": True,
            "roles_preserved": True,
            "no_new_facts": True,
            "deidentified": True,
            "no_long_source_copy": True,
            "diagnosis_inferred": False,
        },
    }


def normalize_chunk_structure(
    parsed: dict[str, Any],
    source_turns: list[dict[str, str]],
) -> dict[str, Any]:
    """Force deterministic role/ID fields when message cardinality is intact."""

    messages = parsed.get("messages")
    if not isinstance(messages, list) or len(messages) != len(source_turns):
        return parsed
    normalized = dict(parsed)
    normalized_messages = []
    repairs = []
    for index, (message, source) in enumerate(zip(messages, source_turns)):
        if not isinstance(message, dict):
            normalized_messages.append(message)
            continue
        output = dict(message)
        expected_role = "user" if source["speaker"] == "participant" else "assistant"
        if output.get("source_turn_id") != source["source_turn_id"]:
            repairs.append(f"message[{index}].source_turn_id")
        if output.get("role") != expected_role:
            repairs.append(f"message[{index}].role")
        output["source_turn_id"] = source["source_turn_id"]
        output["role"] = expected_role
        normalized_messages.append(output)
    normalized["messages"] = normalized_messages
    if repairs:
        normalized["deterministic_structure_repairs"] = repairs
    return normalized


def mock_consolidation() -> dict[str, Any]:
    return {
        "case_summary": "[MOCK] No semantic case summary was generated.",
        "delusion_points": [],
        "no_delusion_point_reason": "Mock mode does not perform semantic signal extraction.",
        "sensitive_content_flags": [],
        "quality_self_check": {
            "participant_evidence_only": True,
            "duplicates_merged": True,
            "uncertainty_preserved": True,
            "no_diagnosis": True,
            "no_quotes": True,
        },
    }


def repair_overlap_messages(
    *,
    parsed: dict[str, Any],
    source_turns: list[dict[str, str]],
    errors: list[str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    indices = sorted(
        {
            int(match.group(1))
            for error in errors
            for match in [re.search(r"message\[(\d+)\] copies", error)]
            if match is not None
        }
    )
    if not indices or any(not error.startswith("message[") or "copies" not in error for error in errors):
        return parsed
    repair_prompt = args.repair_prompt.read_text(encoding="utf-8")
    current_messages = parsed.get("messages") or []
    repair_items = []
    for index in indices:
        if index >= len(source_turns) or index >= len(current_messages):
            return parsed
        repair_items.append(
            {
                "index": index,
                "source_turn_id": source_turns[index]["source_turn_id"],
                "role": current_messages[index].get("role"),
                "source_text": source_turns[index]["text"],
                "current_content": current_messages[index].get("content"),
            }
        )
    last_errors = errors
    for _attempt in range(args.overlap_repair_retries + 1):
        repair_payload = {
            "task": "repair_only_messages_with_excessive_source_overlap",
            "maximum_allowed_consecutive_source_words": args.max_source_word_run - 1,
            "items": repair_items,
        }
        try:
            repaired, _raw = call_json_task(
                provider=args.provider,
                api_key=args.api_key,
                base_url=args.base_url,
                model=args.model,
                system_prompt=repair_prompt,
                payload=repair_payload,
                temperature=args.temperature,
                max_tokens=min(args.max_output_tokens, 4096),
                timeout=args.timeout,
                max_retries=args.http_retries,
                context_window_tokens=args.context_window_tokens,
                thinking_mode=args.thinking_mode,
                correction_errors=last_errors,
            )
        except (ValueError, RuntimeError) as exc:
            last_errors = [str(exc)]
            continue
        messages = repaired.get("messages")
        if not isinstance(messages, list) or len(messages) != len(repair_items):
            last_errors = ["repair response message count mismatch"]
            continue
        repair_errors = []
        for expected, replacement in zip(repair_items, messages):
            if not isinstance(replacement, dict):
                repair_errors.append(f"repair item {expected['index']} is not an object")
                continue
            for field in ["index", "source_turn_id", "role"]:
                if replacement.get(field) != expected[field]:
                    repair_errors.append(f"repair item {expected['index']} {field} mismatch")
            content = replacement.get("content")
            if not isinstance(content, str) or not content.strip():
                repair_errors.append(f"repair item {expected['index']} content is empty")
                continue
            overlap = longest_common_word_run(expected["source_text"], content)
            if overlap >= args.max_source_word_run:
                repair_errors.append(f"repair item {expected['index']} still copies {overlap} words")
            else:
                expected["current_content"] = content
        if repair_errors:
            last_errors = repair_errors
            continue
        output = dict(parsed)
        output["messages"] = [dict(message) for message in current_messages]
        for item in repair_items:
            output["messages"][item["index"]]["content"] = item["current_content"]
        return output
    return parsed


def call_json_task(
    *,
    provider: str,
    api_key: str,
    base_url: str,
    model: str,
    system_prompt: str,
    payload: dict[str, Any],
    temperature: float,
    max_tokens: int,
    timeout: int,
    max_retries: int,
    context_window_tokens: int,
    thinking_mode: str,
    correction_errors: list[str] | None = None,
) -> tuple[dict[str, Any], str | None]:
    if provider == "mock":
        raise AssertionError("mock task must be handled by the caller")
    user_text = json.dumps(payload, ensure_ascii=False, indent=2)
    if correction_errors:
        user_text += (
            "\n\nYour previous answer failed these machine checks. Return a corrected full JSON object:\n- "
            + "\n- ".join(correction_errors[:20])
        )
    estimated_input_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_text) + 32
    input_budget = context_window_tokens - max_tokens
    if estimated_input_tokens > input_budget:
        raise ValueError(
            f"estimated input {estimated_input_tokens} tokens exceeds the explicit {context_window_tokens}-token "
            f"context budget after reserving {max_tokens} output tokens (input budget {input_budget})"
        )
    raw = openai_compatible_completion(
        base_url=base_url,
        api_key=api_key,
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        thinking_mode=thinking_mode,
    )
    return parse_json_object(raw), raw


def run_chunk(
    *,
    prepared: dict[str, Any],
    turns: list[dict[str, str]],
    chunk_index: int,
    chunk_count: int,
    prompt: str,
    prompt_hash: str,
    args: argparse.Namespace,
    case_work_dir: Path,
) -> tuple[dict[str, Any], int]:
    payload = {
        "task": "deidentify_and_normalize_interview_chunk",
        "language_policy": "preserve_source_language",
        "session_surrogate_id": prepared["session_id"],
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "turns": turns,
    }
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + prompt_hash
        + args.model
        + args.thinking_mode
    )
    cache_path = case_work_dir / f"chunk_{chunk_index:03d}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            cached["parsed"] = normalize_chunk_structure(cached["parsed"], turns)
            errors, overlap = validate_chunk_result(cached["parsed"], turns, args.max_source_word_run)
            if not errors:
                return cached["parsed"], overlap

    if args.provider == "mock":
        parsed = mock_chunk_result(turns)
        raw_response = None
        errors, overlap = validate_chunk_result(parsed, turns, args.max_source_word_run)
    else:
        errors = []
        parsed = {}
        raw_response = None
        overlap = 0
        for validation_attempt in range(args.validation_retries + 1):
            request_payload = payload
            if errors and parsed:
                request_payload = dict(payload)
                request_payload["previous_invalid_output"] = parsed
                request_payload["repair_errors"] = errors[:30]
                request_payload["repair_instruction"] = (
                    "Keep every valid field unchanged where possible. Rewrite only the messages/points named by "
                    "the repair errors, then return the complete corrected JSON object."
                )
            try:
                parsed, raw_response = call_json_task(
                    provider=args.provider,
                    api_key=args.api_key,
                    base_url=args.base_url,
                    model=args.model,
                    system_prompt=prompt,
                    payload=request_payload,
                    temperature=args.temperature,
                    max_tokens=args.max_output_tokens,
                    timeout=args.timeout,
                    max_retries=args.http_retries,
                    context_window_tokens=args.context_window_tokens,
                    thinking_mode=args.thinking_mode,
                    correction_errors=errors or None,
                )
                parsed = normalize_chunk_structure(parsed, turns)
                errors, overlap = validate_chunk_result(parsed, turns, args.max_source_word_run)
            except (ValueError, RuntimeError) as exc:
                errors = [str(exc)]
            if not errors:
                break
            if validation_attempt < args.validation_retries:
                time.sleep(args.sleep)
    if errors:
        parsed = repair_overlap_messages(
            parsed=parsed,
            source_turns=turns,
            errors=errors,
            args=args,
        )
        errors, overlap = validate_chunk_result(parsed, turns, args.max_source_word_run)
    if errors:
        raise ValueError(f"chunk {chunk_index}/{chunk_count} failed validation: {'; '.join(errors)}")

    case_work_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "payload_hash": payload_hash,
                "model": args.model,
                "prompt_sha256": prompt_hash,
                "parsed": parsed,
                "raw_response": raw_response,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return parsed, overlap


def run_consolidation(
    *,
    prepared: dict[str, Any],
    transformed_messages: list[dict[str, str]],
    candidate_points: list[dict[str, Any]],
    prompt: str,
    prompt_hash: str,
    args: argparse.Namespace,
    case_work_dir: Path,
) -> dict[str, Any]:
    participant_ids = {
        item["source_turn_id"] for item in transformed_messages if item["role"] == "user"
    }
    payload = {
        "task": "review_complete_session_and_consolidate_candidate_reality_boundary_points",
        "session_surrogate_id": prepared["session_id"],
        "messages": transformed_messages,
        "chunk_candidate_points": candidate_points,
    }
    serialized_payload = json.dumps(payload, ensure_ascii=False)
    if len(serialized_payload) > args.max_consolidation_chars:
        raise ValueError(
            f"consolidation payload has {len(serialized_payload)} chars, above limit "
            f"{args.max_consolidation_chars}; increase --max-consolidation-chars explicitly"
        )
    payload_hash = sha256_text(serialized_payload + prompt_hash + args.model + args.thinking_mode)
    cache_path = case_work_dir / "consolidation.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            if not validate_consolidation(cached["parsed"], participant_ids):
                return cached["parsed"]

    if args.provider == "mock":
        parsed = mock_consolidation()
        raw_response = None
        errors = validate_consolidation(parsed, participant_ids)
    else:
        parsed = {}
        raw_response = None
        errors: list[str] = []
        for validation_attempt in range(args.validation_retries + 1):
            request_payload = payload
            if errors and parsed:
                request_payload = dict(payload)
                request_payload["previous_invalid_output"] = parsed
                request_payload["repair_errors"] = errors[:30]
            try:
                parsed, raw_response = call_json_task(
                    provider=args.provider,
                    api_key=args.api_key,
                    base_url=args.base_url,
                    model=args.model,
                    system_prompt=prompt,
                    payload=request_payload,
                    temperature=args.temperature,
                    max_tokens=args.max_output_tokens,
                    timeout=args.timeout,
                    max_retries=args.http_retries,
                    context_window_tokens=args.context_window_tokens,
                    thinking_mode=args.thinking_mode,
                    correction_errors=errors or None,
                )
                errors = validate_consolidation(parsed, participant_ids)
            except (ValueError, RuntimeError) as exc:
                errors = [str(exc)]
            if not errors:
                break
            if validation_attempt < args.validation_retries:
                time.sleep(args.sleep)
    if errors:
        raise ValueError(f"consolidation failed validation: {'; '.join(errors)}")

    case_work_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "payload_hash": payload_hash,
                "model": args.model,
                "prompt_sha256": prompt_hash,
                "parsed": parsed,
                "raw_response": raw_response,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return parsed


def source_identifier_tokens(prepared: dict[str, Any]) -> list[str]:
    name = Path(prepared["source_path"]).name
    tokens = re.findall(r"[A-Za-z0-9]{4,}", name)
    return [token for token in tokens if token.lower() not in {"full", "participant"}]


def build_session(
    prepared: dict[str, Any],
    chunk_prompt: str,
    consolidate_prompt: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    chunks = split_turns(prepared["turns"], args.chunk_max_chars, args.chunk_max_turns)
    case_work_dir = ROOT / "data" / "work" / "runs" / args.run_id / prepared["session_id"]
    chunk_prompt_hash = sha256_text(chunk_prompt)
    consolidate_prompt_hash = sha256_text(consolidate_prompt)

    transformed: list[dict[str, str]] = []
    candidates: list[dict[str, Any]] = []
    sensitive_flags: set[str] = set()
    maximum_overlap = 0
    estimated_request_inputs = []
    for chunk_index, chunk in enumerate(chunks, start=1):
        chunk_payload = {
            "task": "deidentify_and_normalize_interview_chunk",
            "language_policy": "preserve_source_language",
            "session_surrogate_id": prepared["session_id"],
            "chunk_index": chunk_index,
            "chunk_count": len(chunks),
            "turns": chunk,
        }
        estimated_request_inputs.append(
            estimate_tokens(chunk_prompt)
            + estimate_tokens(json.dumps(chunk_payload, ensure_ascii=False, indent=2))
            + 32
        )
        result, overlap = run_chunk(
            prepared=prepared,
            turns=chunk,
            chunk_index=chunk_index,
            chunk_count=len(chunks),
            prompt=chunk_prompt,
            prompt_hash=chunk_prompt_hash,
            args=args,
            case_work_dir=case_work_dir,
        )
        transformed.extend(result["messages"])
        candidates.extend(result.get("candidate_delusion_points") or [])
        sensitive_flags.update(str(value) for value in result.get("sensitive_content_flags") or [])
        maximum_overlap = max(maximum_overlap, overlap)
        if args.provider != "mock":
            time.sleep(args.sleep)

    consolidation = run_consolidation(
        prepared=prepared,
        transformed_messages=transformed,
        candidate_points=candidates,
        prompt=consolidate_prompt,
        prompt_hash=consolidate_prompt_hash,
        args=args,
        case_work_dir=case_work_dir,
    )
    consolidation_payload = {
        "task": "review_complete_session_and_consolidate_candidate_reality_boundary_points",
        "session_surrogate_id": prepared["session_id"],
        "messages": transformed,
        "chunk_candidate_points": candidates,
    }
    estimated_request_inputs.append(
        estimate_tokens(consolidate_prompt)
        + estimate_tokens(json.dumps(consolidation_payload, ensure_ascii=False, indent=2))
        + 32
    )
    sensitive_flags.update(str(value) for value in consolidation.get("sensitive_content_flags") or [])

    source_index = {turn["source_turn_id"]: index for index, turn in enumerate(prepared["turns"])}
    messages = [{"role": item["role"], "content": item["content"].strip()} for item in transformed]
    message_provenance = [
        {
            "message_index": index,
            "source_turn_ids": [item["source_turn_id"]],
            "transform": "llm_semantic_paraphrase",
        }
        for index, item in enumerate(transformed)
    ]
    points = []
    for point_index, point in enumerate(consolidation["delusion_points"], start=1):
        source_ids = list(dict.fromkeys(str(value) for value in point["source_turn_ids"]))
        points.append(
            {
                "point_id": f"{prepared['session_id']}_dp_{point_index:02d}",
                "category": point["category"],
                "summary": point["summary"].strip(),
                "explicitness": point["explicitness"],
                "message_indices": sorted(source_index[source_id] for source_id in source_ids),
                "source_turn_ids": source_ids,
                "uncertainty_or_counterevidence": str(
                    point.get("uncertainty_or_counterevidence") or ""
                ).strip(),
                "confidence": float(point["confidence"]),
                "label_status": LABEL_STATUS,
            }
        )

    all_public_texts = [message["content"] for message in messages]
    all_public_texts.append(str(consolidation.get("case_summary") or ""))
    all_public_texts.extend(point["summary"] for point in points)
    pii_hits = scan_pii(all_public_texts, source_identifier_tokens(prepared))
    source_ids = [turn["source_turn_id"] for turn in prepared["turns"]]
    covered_ids = [item["source_turn_id"] for item in transformed]
    quality_errors = []
    if source_ids != covered_ids:
        quality_errors.append("source_turn_coverage_or_order_mismatch")
    if pii_hits:
        quality_errors.append("pii_or_source_identifier_scan_hit")
    if maximum_overlap >= args.max_source_word_run:
        quality_errors.append("source_copy_overlap_limit_exceeded")

    record = {
        "schema_version": SCHEMA_VERSION,
        "session_id": prepared["session_id"],
        "messages": messages,
        "message_provenance": message_provenance,
        "delusion_points": points,
        "case_summary": str(consolidation.get("case_summary") or "").strip(),
        "no_delusion_point_reason": consolidation.get("no_delusion_point_reason"),
        "metadata": {
            "language": "en",
            "source_dataset": prepared["source_dataset"],
            "source_group": prepared["source_group"],
            "source_is_real_interview": True,
            "delusion_ground_truth": False,
            "label_interpretation": LABEL_STATUS,
            "sensitive_content_flags": sorted(sensitive_flags),
        },
        "provenance": {
            "source_path": prepared["source_path"],
            "source_sha256": prepared["source_sha256"],
            "source_license": prepared["source_license"],
            "source_citation": prepared["source_citation"],
            "parser": prepared["parser"],
            "parser_version": prepared["parser_version"],
            "source_parse_status": prepared.get("parse_status", "unknown"),
            "source_parse_warnings": prepared.get("parse_warnings") or [],
            "transform_provider": args.provider,
            "transform_model": args.model,
            "run_id": args.run_id,
            "generated_at": args.generated_at,
            "chunk_prompt_sha256": chunk_prompt_hash,
            "consolidation_prompt_sha256": consolidate_prompt_hash,
            "overlap_repair_prompt_sha256": sha256_text(args.repair_prompt.read_text(encoding="utf-8")),
            "source_turn_count": len(prepared["turns"]),
            "chunk_count": len(chunks),
            "context_window_tokens": args.context_window_tokens,
            "max_output_tokens": args.max_output_tokens,
            "thinking_mode": args.thinking_mode,
            "estimated_max_request_input_tokens": max(estimated_request_inputs),
            "token_estimator": "ceil(characters/4)+message_overhead",
        },
        "quality": {
            "status": "passed" if not quality_errors else "failed",
            "errors": quality_errors,
            "source_turn_coverage_rate": len(set(covered_ids) & set(source_ids)) / max(len(source_ids), 1),
            "source_turns_in_original_order": source_ids == covered_ids,
            "source_turns_unique": len(covered_ids) == len(set(covered_ids)),
            "max_common_source_word_run": maximum_overlap,
            "copy_run_failure_threshold": args.max_source_word_run,
            "pii_scan_hits": pii_hits,
            "raw_source_text_written": False,
            "raw_api_response_written_to_processed": False,
            "automatic_checks_only": True,
        },
    }
    contract_errors = validate_session_record(record)
    if contract_errors:
        raise ValueError(f"final session validation failed: {'; '.join(contract_errors)}")
    return record


def select_manifest_records(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = records
    if args.case_ids:
        requested = [value.strip() for value in args.case_ids.split(",") if value.strip()]
        by_id = {record["session_id"]: record for record in records}
        missing = [case_id for case_id in requested if case_id not in by_id]
        if missing:
            raise ValueError(f"unknown case IDs: {missing}")
        selected = [by_id[case_id] for case_id in requested]
    else:
        groups = {value.strip() for value in args.include_groups.split(",") if value.strip()}
        selected = [record for record in records if record.get("source_group") in groups]
    if args.limit is not None:
        selected = selected[: args.limit]
    if not selected:
        raise ValueError("no cases selected")
    return selected


def write_summary(
    path: Path,
    sessions: list[dict[str, Any]],
    failures: list[dict[str, str]],
    args: argparse.Namespace,
) -> None:
    source_counts = Counter(session["metadata"]["source_dataset"] for session in sessions)
    group_counts = Counter(session["metadata"]["source_group"] for session in sessions)
    total_messages = sum(len(session["messages"]) for session in sessions)
    total_points = sum(len(session["delusion_points"]) for session in sessions)
    empty_points = sum(not session["delusion_points"] for session in sessions)
    lines = [
        f"# {args.run_id}",
        "",
        f"- Generated at: `{args.generated_at}`",
        f"- Provider/model: `{args.provider}` / `{args.model}`",
        f"- Context window: `{args.context_window_tokens}` tokens",
        f"- Reserved max output: `{args.max_output_tokens}` tokens",
        f"- Thinking mode: `{args.thinking_mode}`",
        f"- Completed sessions: `{len(sessions)}`",
        f"- Failed sessions: `{len(failures)}`",
        f"- Messages: `{total_messages}`",
        f"- Candidate delusion points: `{total_points}`",
        f"- Sessions with no extracted point: `{empty_points}`",
        f"- Source datasets: `{dict(sorted(source_counts.items()))}`",
        f"- Source groups: `{dict(sorted(group_counts.items()))}`",
        "- Label status: `llm_extracted_candidate_not_diagnosis`",
        "- Raw source/API response included in processed data: `false`",
        "",
        "## Session QC",
        "",
        "| session_id | messages | delusion_points | chunks | max source-word run | QC |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for session in sessions:
        lines.append(
            "| {session_id} | {messages} | {points} | {chunks} | {overlap} | {status} |".format(
                session_id=session["session_id"],
                messages=len(session["messages"]),
                points=len(session["delusion_points"]),
                chunks=session["provenance"]["chunk_count"],
                overlap=session["quality"]["max_common_source_word_run"],
                status=session["quality"]["status"],
            )
        )
    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(f"- `{failure['session_id']}`: {failure['error']}")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "`delusion_points` are LLM-extracted candidate text signals. They are not clinical diagnoses, "
            "participant-level ground truth, or evidence that every psychosis-related interview contains delusions.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--prepared-dir", type=Path, default=DEFAULT_PREPARED_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--chunk-prompt", type=Path, default=DEFAULT_CHUNK_PROMPT)
    parser.add_argument("--consolidate-prompt", type=Path, default=DEFAULT_CONSOLIDATE_PROMPT)
    parser.add_argument("--repair-prompt", type=Path, default=DEFAULT_REPAIR_PROMPT)
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "deepseek-v4-pro"))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--run-id", default="deepseek_v4_pro_batch_001")
    parser.add_argument("--case-ids", help="Comma-separated explicit session IDs in desired order.")
    parser.add_argument(
        "--include-groups",
        default="clinical_schizophrenia,first_episode_psychosis",
        help="Used only when --case-ids is omitted.",
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--chunk-max-chars", type=int, default=22000)
    parser.add_argument("--chunk-max-turns", type=int, default=100)
    parser.add_argument("--max-consolidation-chars", type=int, default=250000)
    parser.add_argument(
        "--max-source-word-run",
        type=int,
        default=32,
        help="Interview-source threshold; community-derived sessions use a stricter separate default of 12.",
    )
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--context-window-tokens", type=int, default=65536)
    parser.add_argument("--thinking-mode", choices=["disabled", "enabled", "omit"], default="disabled")
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--http-retries", type=int, default=3)
    parser.add_argument("--validation-retries", type=int, default=2)
    parser.add_argument("--overlap-repair-retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--workers", type=int, default=1, help="Number of cases processed concurrently.")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"output already exists; pass --overwrite intentionally: {args.output}")
    if args.context_window_tokens != 65536:
        raise ValueError("this dataset run is frozen to a 64k (65536-token) context window")
    if args.max_output_tokens <= 0 or args.max_output_tokens >= args.context_window_tokens:
        raise ValueError("--max-output-tokens must be positive and smaller than the context window")
    args.generated_at = utc_now()
    args.api_key = os.getenv("OPENAI_API_KEY", "")
    if args.provider == "openai" and not args.api_key and args.key_file.exists():
        args.api_key = args.key_file.read_text(encoding="utf-8").strip()
    if args.provider == "openai" and not args.api_key:
        raise ValueError(f"OPENAI_API_KEY is unset and key file is unavailable: {args.key_file}")

    chunk_prompt = args.chunk_prompt.read_text(encoding="utf-8")
    consolidate_prompt = args.consolidate_prompt.read_text(encoding="utf-8")
    records = select_manifest_records(read_jsonl(args.manifest), args)

    def process_case(index_and_record: tuple[int, dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
        index, manifest_record = index_and_record
        prepared_path = WORKSPACE_ROOT / manifest_record["prepared_path"]
        if not prepared_path.exists():
            prepared_path = args.prepared_dir / f"{manifest_record['session_id']}.json"
        prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
        print(
            f"case={index}/{len(records)} session_id={prepared['session_id']} "
            f"source_turns={len(prepared['turns'])}",
            flush=True,
        )
        try:
            return build_session(prepared, chunk_prompt, consolidate_prompt, args), None
        except Exception as exc:  # keep a batch-level failure report without exposing source text
            failure = {"session_id": prepared["session_id"], "error": str(exc)}
            print(f"case_failed session_id={prepared['session_id']} error={exc}", flush=True)
            return None, failure

    indexed_records = list(enumerate(records, start=1))
    if args.workers < 1:
        raise ValueError("--workers must be >= 1")
    if args.workers == 1:
        results = [process_case(item) for item in indexed_records]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            results = list(executor.map(process_case, indexed_records))
    sessions = [session for session, _failure in results if session is not None]
    failures = [failure for _session, failure in results if failure is not None]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(session, ensure_ascii=False) + "\n" for session in sessions),
        encoding="utf-8",
    )
    write_summary(args.summary, sessions, failures, args)
    print(
        f"selected={len(records)} completed={len(sessions)} failed={len(failures)} "
        f"output={args.output} summary={args.summary}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
