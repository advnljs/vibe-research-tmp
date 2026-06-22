#!/usr/bin/env python3
"""Screen real community posts and build fictional de-identified multi-turn sessions."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

from build_sessions import call_json_task, read_jsonl, sha256_text, utc_now
from session_contract import (
    ALLOWED_CATEGORIES,
    ALLOWED_EXPLICITNESS,
    LABEL_STATUS,
    SCHEMA_VERSION,
    longest_common_word_run,
    scan_pii,
    validate_session_record,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_CANDIDATES = ROOT / "data" / "manifests" / "reddit_screen_candidates.jsonl"
DEFAULT_SCREEN_PROMPT = ROOT / "prompts" / "screen_reddit_reality_boundary.md"
DEFAULT_GENERATE_PROMPT = ROOT / "prompts" / "reddit_case_to_session.md"
DEFAULT_SCREEN_OUTPUT = ROOT / "data" / "screened" / "deepseek_v4_pro_reddit_screening_64k.jsonl"
DEFAULT_SESSION_OUTPUT = ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k.jsonl"
DEFAULT_SUMMARY = ROOT / "data" / "processed" / "deepseek_v4_pro_reddit_sessions_64k_summary.md"
DEFAULT_KEY_FILE = WORKSPACE_ROOT / "ds_key.txt"
ALLOWED_BELIEF_STATUS = {"active", "retrospective", "questioned", "unclear", "not_applicable"}


def prepared_path(record: dict[str, Any]) -> Path:
    return WORKSPACE_ROOT / record["prepared_path"]


def load_prepared(record: dict[str, Any]) -> dict[str, Any]:
    return json.loads(prepared_path(record).read_text(encoding="utf-8"))


def batches(records: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [records[index : index + size] for index in range(0, len(records), size)]


def validate_screen_result(
    parsed: dict[str, Any],
    batch_records: list[dict[str, Any]],
    max_source_word_run: int,
) -> tuple[list[str], int]:
    errors: list[str] = []
    results = parsed.get("results")
    if not isinstance(results, list):
        return ["results must be a list"], 0
    expected_ids = [record["case_id"] for record in batch_records]
    actual_ids = [item.get("case_id") if isinstance(item, dict) else None for item in results]
    if actual_ids != expected_ids:
        errors.append("screening result case IDs/order do not match the request")
    source_by_id = {record["case_id"]: load_prepared(record)["text"] for record in batch_records}
    maximum_overlap = 0
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            errors.append(f"results[{index}] is not an object")
            continue
        case_id = item.get("case_id")
        if not isinstance(item.get("eligible"), bool):
            errors.append(f"results[{index}] eligible is not boolean")
        if item.get("belief_status") not in ALLOWED_BELIEF_STATUS:
            errors.append(f"results[{index}] has invalid belief_status")
        points = item.get("delusion_points")
        reasons = item.get("rejection_reasons")
        if not isinstance(points, list):
            errors.append(f"results[{index}] delusion_points is not a list")
            points = []
        if item.get("eligible") and not points:
            errors.append(f"results[{index}] eligible item has no delusion_points")
        if not item.get("eligible") and points:
            errors.append(f"results[{index}] ineligible item has delusion_points")
        if not item.get("eligible") and (not isinstance(reasons, list) or not reasons):
            errors.append(f"results[{index}] ineligible item lacks rejection_reasons")
        if item.get("eligible") and item.get("contains_identifying_detail") is not False:
            errors.append(f"results[{index}] eligible item has identifying detail")
        if item.get("diagnosis_inferred") is not False:
            errors.append(f"results[{index}] diagnosis_inferred must be false")
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                errors.append(f"results[{index}].delusion_points[{point_index}] is not an object")
                continue
            if point.get("category") not in ALLOWED_CATEGORIES:
                errors.append(f"results[{index}].delusion_points[{point_index}] invalid category")
            if point.get("explicitness") not in ALLOWED_EXPLICITNESS:
                errors.append(f"results[{index}].delusion_points[{point_index}] invalid explicitness")
            confidence = point.get("confidence")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                errors.append(f"results[{index}].delusion_points[{point_index}] invalid confidence")
            summary = point.get("summary")
            if not isinstance(summary, str) or not summary.strip():
                errors.append(f"results[{index}].delusion_points[{point_index}] empty summary")
                continue
            source_text = source_by_id.get(str(case_id), "")
            overlap = longest_common_word_run(source_text, summary)
            maximum_overlap = max(maximum_overlap, overlap)
            if overlap >= max_source_word_run:
                errors.append(
                    f"results[{index}].delusion_points[{point_index}] copies {overlap} source words"
                )
            if scan_pii([summary, str(point.get("uncertainty_or_counterevidence") or "")]):
                errors.append(f"results[{index}].delusion_points[{point_index}] PII scan hit")
    return errors, maximum_overlap


def normalize_screen_safety(parsed: dict[str, Any]) -> dict[str, Any]:
    """Deterministically fail closed on model-reported privacy/safety conflicts."""

    results = parsed.get("results")
    if not isinstance(results, list):
        return parsed
    normalized = dict(parsed)
    normalized_results = []
    for item in results:
        if not isinstance(item, dict):
            normalized_results.append(item)
            continue
        output = dict(item)
        reasons = list(output.get("rejection_reasons") or [])
        force_reject = False
        if output.get("contains_identifying_detail") is True:
            reasons.append("automatic_exclusion:model_reported_identifying_detail")
            force_reject = True
        if output.get("sensitive_content_flags"):
            reasons.append("automatic_exclusion:model_reported_sensitive_content")
            force_reject = True
        if output.get("diagnosis_inferred") is True:
            reasons.append("automatic_exclusion:model_inferred_diagnosis")
            force_reject = True
        if force_reject:
            output["eligible"] = False
            output["belief_status"] = "not_applicable"
            output["delusion_points"] = []
            output["rejection_reasons"] = list(dict.fromkeys(reasons))
            output["diagnosis_inferred"] = False
        normalized_results.append(output)
    normalized["results"] = normalized_results
    return normalized


def public_rejection_reasons(item: dict[str, Any]) -> list[str]:
    """Keep model prose in ignored checkpoints; publish categorical reasons only."""

    reasons = [
        str(reason)
        for reason in item.get("rejection_reasons") or []
        if str(reason).startswith("automatic_exclusion:")
    ]
    if item.get("eligible") is not True and not reasons:
        reasons.append("model_semantic_ineligible")
    return list(dict.fromkeys(reasons))


def mock_screen_batch(batch_records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "results": [
            {
                "case_id": record["case_id"],
                "eligible": True,
                "belief_status": "unclear",
                "delusion_points": [
                    {
                        "category": "other_reality_boundary",
                        "summary": "[MOCK] A candidate reality-boundary belief is present.",
                        "explicitness": "unclear",
                        "uncertainty_or_counterevidence": "Mock screening does not evaluate semantics.",
                        "confidence": 0.5,
                    }
                ],
                "rejection_reasons": [],
                "sensitive_content_flags": [],
                "contains_identifying_detail": False,
                "diagnosis_inferred": False,
            }
            for record in batch_records
        ]
    }


def screen_batch(
    batch_index: int,
    batch_records: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    items = [
        {"case_id": record["case_id"], "text": load_prepared(record)["text"]}
        for record in batch_records
    ]
    payload = {"task": "screen_community_reality_boundary_text_signals", "items": items}
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + sha256_text(prompt)
        + args.screen_model
        + args.thinking_mode
    )
    work_dir = ROOT / "data" / "work" / "reddit_runs" / args.run_id / "screen"
    cache_path = work_dir / f"batch_{batch_index:04d}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            cached["parsed"] = normalize_screen_safety(cached["parsed"])
            errors, _overlap = validate_screen_result(
                cached["parsed"], batch_records, args.max_source_word_run
            )
            if not errors:
                return cached["parsed"]["results"]

    if args.provider == "mock":
        parsed = mock_screen_batch(batch_records)
        raw_response = None
        errors, overlap = validate_screen_result(parsed, batch_records, args.max_source_word_run)
    else:
        parsed = {}
        raw_response = None
        errors: list[str] = []
        overlap = 0
        for attempt in range(args.validation_retries + 1):
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
                    model=args.screen_model,
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
                parsed = normalize_screen_safety(parsed)
                errors, overlap = validate_screen_result(parsed, batch_records, args.max_source_word_run)
            except (ValueError, RuntimeError) as exc:
                errors = [str(exc)]
            if not errors:
                break
            if attempt < args.validation_retries:
                time.sleep(args.sleep)
    if errors:
        raise ValueError(f"screen batch {batch_index} failed: {'; '.join(errors)}")
    work_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "payload_hash": payload_hash,
                "model": args.screen_model,
                "max_common_source_word_run": overlap,
                "parsed": parsed,
                "raw_response": raw_response,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return parsed["results"]


def run_screening(
    candidates: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    groups = batches(candidates, args.screen_batch_size)

    def process(item: tuple[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        index, group = item
        print(f"screen_batch={index}/{len(groups)} cases={len(group)}", flush=True)
        return screen_batch(index, group, prompt, args)

    indexed = list(enumerate(groups, start=1))
    if args.workers == 1:
        batch_results = [process(item) for item in indexed]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            batch_results = list(executor.map(process, indexed))
    raw_results = [item for group in batch_results for item in group]
    manifest_by_id = {record["case_id"]: record for record in candidates}
    output = []
    for item in raw_results:
        source = manifest_by_id[item["case_id"]]
        output.append(
            {
                "schema_version": "0.1.0",
                "case_id": item["case_id"],
                "eligible": item["eligible"],
                "belief_status": item["belief_status"],
                "delusion_points": item["delusion_points"],
                "rejection_reasons": public_rejection_reasons(item),
                "sensitive_content_flags": (
                    ["model_reported_sensitive_content"]
                    if item.get("sensitive_content_flags")
                    else []
                ),
                "contains_identifying_detail": item.get("contains_identifying_detail"),
                "diagnosis_inferred": False,
                "source_post_sha256": source["source_post_sha256"],
                "source_file": source["source_file"],
                "source_row_number": source["source_row_number"],
                "source_license": source["source_license"],
                "prepared_path": source["prepared_path"],
                "screen_provider": args.provider,
                "screen_model": args.screen_model,
                "context_window_tokens": args.context_window_tokens,
                "screened_at": args.generated_at,
                "label_status": LABEL_STATUS,
            }
        )
    args.screen_output.parent.mkdir(parents=True, exist_ok=True)
    args.screen_output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output),
        encoding="utf-8",
    )
    return output


def mock_generated_session() -> dict[str, Any]:
    messages = []
    for index in range(12):
        role = "user" if index % 2 == 0 else "assistant"
        messages.append(
            {
                "role": role,
                "content": f"[MOCK] {'User account' if role == 'user' else 'Neutral interviewer prompt'} {index + 1}.",
            }
        )
    return {
        "messages": messages,
        "case_summary": "[MOCK] Fictionalized community-derived session.",
        "delusion_points": [
            {
                "category": "other_reality_boundary",
                "summary": "[MOCK] A candidate reality-boundary belief.",
                "explicitness": "unclear",
                "message_indices": [0, 2],
                "uncertainty_or_counterevidence": "Mock generation does not evaluate semantics.",
                "confidence": 0.5,
            }
        ],
        "sensitive_content_flags": [],
        "quality_self_check": {
            "fictionalized_and_deidentified": True,
            "same_core_belief_only": True,
            "assistant_does_not_validate_belief": True,
            "no_new_high_risk_content": True,
            "no_long_source_copy": True,
            "diagnosis_inferred": False,
        },
    }


def validate_generated(
    parsed: dict[str, Any],
    source_text: str,
    max_source_word_run: int,
) -> tuple[list[str], int, list[dict[str, str]]]:
    errors: list[str] = []
    if parsed.get("rejected") is True:
        return [f"generation rejected: {parsed.get('rejection_reason', 'no reason')}"] , 0, []
    messages = parsed.get("messages")
    if not isinstance(messages, list) or len(messages) != 12:
        return ["messages must contain exactly 12 items"], 0, []
    public_texts = []
    maximum_overlap = 0
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            errors.append(f"messages[{index}] is not an object")
            continue
        expected_role = "user" if index % 2 == 0 else "assistant"
        if message.get("role") != expected_role:
            errors.append(f"messages[{index}] role does not alternate from user")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"messages[{index}] content is empty")
            continue
        public_texts.append(content)
        overlap = longest_common_word_run(source_text, content)
        maximum_overlap = max(maximum_overlap, overlap)
        if overlap >= max_source_word_run:
            errors.append(f"messages[{index}] copies {overlap} source words")
    points = parsed.get("delusion_points")
    if not isinstance(points, list) or not points:
        errors.append("delusion_points must be a non-empty list")
        points = []
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"delusion_points[{index}] is not an object")
            continue
        if point.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"delusion_points[{index}] invalid category")
        if point.get("explicitness") not in ALLOWED_EXPLICITNESS:
            errors.append(f"delusion_points[{index}] invalid explicitness")
        indices = point.get("message_indices")
        if not isinstance(indices, list) or not indices or any(
            not isinstance(value, int) or value < 0 or value >= 12 or value % 2 != 0 for value in indices
        ):
            errors.append(f"delusion_points[{index}] must point only to user messages")
        confidence = point.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"delusion_points[{index}] invalid confidence")
        summary = point.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"delusion_points[{index}] empty summary")
        else:
            public_texts.append(summary)
            overlap = longest_common_word_run(source_text, summary)
            maximum_overlap = max(maximum_overlap, overlap)
            if overlap >= max_source_word_run:
                errors.append(f"delusion_points[{index}] summary copies {overlap} source words")
    public_texts.append(str(parsed.get("case_summary") or ""))
    pii_hits = scan_pii(public_texts)
    if pii_hits:
        errors.append("public output PII scan hit")
    return errors, maximum_overlap, pii_hits


def generate_one(
    screen: dict[str, Any],
    prompt: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    source = json.loads((WORKSPACE_ROOT / screen["prepared_path"]).read_text(encoding="utf-8"))
    source_text = source["text"]
    payload = {
        "task": "convert_screened_real_community_case_to_fictional_multiturn_session",
        "case_id": screen["case_id"],
        "language_policy": "preserve_source_language",
        "screening_result": {
            "belief_status": screen["belief_status"],
            "delusion_points": screen["delusion_points"],
        },
        "source_post": source_text,
    }
    payload_hash = sha256_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + sha256_text(prompt)
        + args.generate_model
        + args.thinking_mode
    )
    work_dir = ROOT / "data" / "work" / "reddit_runs" / args.run_id / "generate"
    cache_path = work_dir / f"{screen['case_id']}.json"
    if args.resume and cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("payload_hash") == payload_hash and isinstance(cached.get("parsed"), dict):
            errors, overlap, pii_hits = validate_generated(
                cached["parsed"], source_text, args.max_source_word_run
            )
            if not errors:
                parsed = cached["parsed"]
            else:
                parsed = {}
        else:
            parsed = {}
    else:
        parsed = {}
    raw_response = None
    errors: list[str] = []
    overlap = 0
    pii_hits: list[dict[str, str]] = []
    if not parsed:
        if args.provider == "mock":
            parsed = mock_generated_session()
            errors, overlap, pii_hits = validate_generated(parsed, source_text, args.max_source_word_run)
        else:
            for attempt in range(args.validation_retries + 1):
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
                        model=args.generate_model,
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
                    errors, overlap, pii_hits = validate_generated(
                        parsed, source_text, args.max_source_word_run
                    )
                except (ValueError, RuntimeError) as exc:
                    errors = [str(exc)]
                if not errors:
                    break
                if attempt < args.validation_retries:
                    time.sleep(args.sleep)
        if errors:
            raise ValueError("; ".join(errors))
        work_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(
                {
                    "payload_hash": payload_hash,
                    "model": args.generate_model,
                    "parsed": parsed,
                    "raw_response": raw_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    else:
        errors, overlap, pii_hits = validate_generated(parsed, source_text, args.max_source_word_run)

    session_id = screen["case_id"].replace("reddit_case_", "reddit_syn_")
    points = []
    for index, point in enumerate(parsed["delusion_points"], start=1):
        points.append(
            {
                "point_id": f"{session_id}_dp_{index:02d}",
                "category": point["category"],
                "summary": point["summary"].strip(),
                "explicitness": point["explicitness"],
                "message_indices": point["message_indices"],
                "source_turn_ids": ["source_post"],
                "uncertainty_or_counterevidence": str(
                    point.get("uncertainty_or_counterevidence") or ""
                ).strip(),
                "confidence": float(point["confidence"]),
                "label_status": LABEL_STATUS,
            }
        )
    record = {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "messages": [{"role": item["role"], "content": item["content"].strip()} for item in parsed["messages"]],
        "message_provenance": [
            {
                "message_index": index,
                "source_turn_ids": ["source_post"],
                "transform": "llm_fictional_expansion",
            }
            for index in range(12)
        ],
        "delusion_points": points,
        "case_summary": str(parsed.get("case_summary") or "").strip(),
        "no_delusion_point_reason": None,
        "metadata": {
            "language": "en",
            "source_dataset": "reddit_mental_health_zenodo_r_schizophrenia",
            "source_group": "community_reality_boundary_text_signal",
            "source_is_real_community_post": True,
            "dialogue_is_synthetic": True,
            "delusion_ground_truth": False,
            "label_interpretation": LABEL_STATUS,
            "belief_status": screen["belief_status"],
            "sensitive_content_flags": sorted(set(parsed.get("sensitive_content_flags") or [])),
        },
        "provenance": {
            "source_post_sha256": screen["source_post_sha256"],
            "source_file": screen["source_file"],
            "source_row_number": screen["source_row_number"],
            "source_license": screen["source_license"],
            "screen_model": screen["screen_model"],
            "transform_provider": args.provider,
            "transform_model": args.generate_model,
            "run_id": args.run_id,
            "generated_at": args.generated_at,
            "context_window_tokens": args.context_window_tokens,
            "max_output_tokens": args.max_output_tokens,
            "thinking_mode": args.thinking_mode,
            "screen_prompt_sha256": sha256_text(args.screen_prompt.read_text(encoding="utf-8")),
            "generation_prompt_sha256": sha256_text(prompt),
        },
        "quality": {
            "status": "passed",
            "errors": [],
            "max_common_source_word_run": overlap,
            "copy_run_failure_threshold": args.max_source_word_run,
            "pii_scan_hits": pii_hits,
            "raw_source_text_written": False,
            "raw_api_response_written_to_processed": False,
            "automatic_checks_only": True,
        },
    }
    contract_errors = validate_session_record(record)
    if contract_errors:
        raise ValueError(f"final session contract failed: {'; '.join(contract_errors)}")
    return record


def run_generation(
    screen_rows: list[dict[str, Any]],
    prompt: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    eligible = [row for row in screen_rows if row.get("eligible") is True]
    if args.generate_limit is not None:
        eligible = eligible[: args.generate_limit]

    def process(item: tuple[int, dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
        index, row = item
        print(f"generate_case={index}/{len(eligible)} case_id={row['case_id']}", flush=True)
        try:
            return generate_one(row, prompt, args), None
        except Exception as exc:
            print(f"generate_failed case_id={row['case_id']} error={exc}", flush=True)
            return None, {"case_id": row["case_id"], "error": str(exc)}

    indexed = list(enumerate(eligible, start=1))
    if args.workers == 1:
        results = [process(item) for item in indexed]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            results = list(executor.map(process, indexed))
    sessions = [session for session, _failure in results if session is not None]
    failures = [failure for _session, failure in results if failure is not None]
    args.session_output.parent.mkdir(parents=True, exist_ok=True)
    args.session_output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in sessions),
        encoding="utf-8",
    )
    return sessions, failures


def write_summary(
    screen_rows: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
    failures: list[dict[str, str]],
    args: argparse.Namespace,
) -> None:
    belief_counts = Counter(row["belief_status"] for row in screen_rows if row.get("eligible"))
    category_counts = Counter(
        point["category"] for session in sessions for point in session.get("delusion_points") or []
    )
    lines = [
        f"# {args.run_id}",
        "",
        f"- Generated at: `{args.generated_at}`",
        f"- Screening model: `{args.screen_model}`",
        f"- Session generation model: `{args.generate_model}`",
        f"- Context window: `{args.context_window_tokens}` tokens",
        f"- Thinking mode: `{args.thinking_mode}`",
        f"- Screened candidates: `{len(screen_rows)}`",
        f"- LLM-eligible text-signal cases: `{sum(row.get('eligible') is True for row in screen_rows)}`",
        f"- Generated sessions: `{len(sessions)}`",
        f"- Generation failures: `{len(failures)}`",
        f"- Belief status distribution: `{dict(sorted(belief_counts.items()))}`",
        f"- Generated point categories: `{dict(sorted(category_counts.items()))}`",
        "- Source text included in tracked outputs: `false`",
        "- Label status: `llm_extracted_candidate_not_diagnosis`",
        "",
        "Community membership is not clinical ground truth. Sessions are fictional expansions of screened, "
        "de-identified text signals and must not be represented as real dialogues or diagnoses.",
        "",
    ]
    if failures:
        lines.extend(["## Failures", ""])
        lines.extend(f"- `{item['case_id']}`: {item['error']}" for item in failures)
        lines.append("")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["screen", "generate", "all"], default="all")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--screen-output", type=Path, default=DEFAULT_SCREEN_OUTPUT)
    parser.add_argument("--session-output", type=Path, default=DEFAULT_SESSION_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--screen-prompt", type=Path, default=DEFAULT_SCREEN_PROMPT)
    parser.add_argument("--generate-prompt", type=Path, default=DEFAULT_GENERATE_PROMPT)
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--screen-model", default="deepseek-v4-pro")
    parser.add_argument("--generate-model", default="deepseek-v4-pro")
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--run-id", default="deepseek_v4_pro_reddit_sessions_64k")
    parser.add_argument("--context-window-tokens", type=int, default=65536)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--thinking-mode", choices=["disabled", "enabled", "omit"], default="disabled")
    parser.add_argument("--screen-batch-size", type=int, default=20)
    parser.add_argument("--screen-limit", type=int)
    parser.add_argument("--generate-limit", type=int)
    parser.add_argument("--max-source-word-run", type=int, default=12)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--http-retries", type=int, default=2)
    parser.add_argument("--validation-retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.context_window_tokens != 65536:
        raise ValueError("this dataset is frozen to a 64k (65536-token) context window")
    if args.workers < 1:
        raise ValueError("--workers must be >= 1")
    if args.stage in {"screen", "all"} and args.screen_output.exists() and not args.overwrite:
        raise FileExistsError(f"screen output exists; pass --overwrite: {args.screen_output}")
    if args.stage in {"generate", "all"} and args.session_output.exists() and not args.overwrite:
        raise FileExistsError(f"session output exists; pass --overwrite: {args.session_output}")
    args.generated_at = utc_now()
    args.api_key = os.getenv("OPENAI_API_KEY", "")
    if args.provider == "openai" and not args.api_key and args.key_file.exists():
        args.api_key = args.key_file.read_text(encoding="utf-8").strip()
    if args.provider == "openai" and not args.api_key:
        raise ValueError(f"API key unavailable: {args.key_file}")

    candidates = read_jsonl(args.candidates)
    if args.screen_limit is not None:
        candidates = candidates[: args.screen_limit]
    screen_prompt = args.screen_prompt.read_text(encoding="utf-8")
    generate_prompt = args.generate_prompt.read_text(encoding="utf-8")

    if args.stage in {"screen", "all"}:
        screen_rows = run_screening(candidates, screen_prompt, args)
    else:
        screen_rows = read_jsonl(args.screen_output)
    sessions: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    if args.stage in {"generate", "all"}:
        sessions, failures = run_generation(screen_rows, generate_prompt, args)
    write_summary(screen_rows, sessions, failures, args)
    print(
        f"screened={len(screen_rows)} eligible={sum(row.get('eligible') is True for row in screen_rows)} "
        f"sessions={len(sessions)} failures={len(failures)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
