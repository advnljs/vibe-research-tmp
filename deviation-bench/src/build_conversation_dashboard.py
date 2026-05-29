#!/usr/bin/env python3
"""Build a static browser dashboard for Deviation Bench JSONL outputs."""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "pilot" / "*.jsonl"
DEFAULT_OUT = ROOT / "results" / "dashboard" / "index.html"

STANCE_ORDER = [
    "rejects_unsupported_claim",
    "states_insufficient_evidence",
    "remains_uncertain",
    "mildly_accommodates",
    "endorses_claim",
    "elaborates_claim",
    "action_oriented_escalation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a self-contained Deviation Bench conversation dashboard.")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="JSONL file or glob. Can be repeated. Defaults to deviation-bench/results/pilot/*.jsonl.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output HTML path.")
    parser.add_argument("--title", default="Deviation Bench Conversation Dashboard")
    return parser.parse_args()


def safe_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        try:
            return str(path.resolve().relative_to(ROOT.parent.resolve()))
        except ValueError:
            return str(path)


def expand_inputs(patterns: list[str]) -> list[Path]:
    if not patterns:
        patterns = [str(DEFAULT_INPUT)]
    paths: list[Path] = []
    for pattern in patterns:
        expanded = glob.glob(pattern)
        if expanded:
            paths.extend(Path(item) for item in expanded)
            continue
        path = Path(pattern)
        if path.exists():
            paths.append(path)
    return sorted(set(path.resolve() for path in paths))


def normalize_flags(value: Any) -> list[str]:
    if value is None or value is False or value == "":
        return []
    if value is True:
        return ["true"]
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, False, "")]
    if isinstance(value, dict):
        return [str(key) for key, enabled in value.items() if enabled]
    return [str(value)]


def metric_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def summarize_turns(turns: list[dict[str, Any]]) -> dict[str, Any]:
    drift_turns: list[str] = []
    factual_turns: list[str] = []
    validation_flags: list[str] = []
    safety_flags: list[str] = []
    stance_counts = {stance: 0 for stance in STANCE_ORDER}
    max_score = 0

    for turn in turns:
        judge = turn.get("judge") or {}
        turn_id = str(turn.get("turn_id", ""))
        stance = str(judge.get("stance", ""))
        if stance in stance_counts:
            stance_counts[stance] += 1
        score = judge.get("stance_score", 0)
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            max_score = max(max_score, int(score))
        if judge.get("drift_event"):
            drift_turns.append(turn_id)
        if judge.get("factual_error"):
            factual_turns.append(turn_id)
        validation_flags.extend(normalize_flags(judge.get("judge_validation_flags")))
        safety_flags.extend(normalize_flags(judge.get("safety_flags")))

    recovery_turn = next((turn for turn in turns if turn.get("turn_id") == "recovery"), None)
    recovery_success = None
    if recovery_turn:
        recovery_success = (recovery_turn.get("judge") or {}).get("recovery_success")

    return {
        "turn_count": len(turns),
        "drift_count": len(drift_turns),
        "factual_error_count": len(factual_turns),
        "first_drift_turn": drift_turns[0] if drift_turns else None,
        "first_factual_error_turn": factual_turns[0] if factual_turns else None,
        "validation_flag_count": len(validation_flags),
        "safety_flag_count": len(safety_flags),
        "recovery_success": recovery_success,
        "max_stance_score": max_score,
        "stance_counts": stance_counts,
    }


def expected_turn_count(record: dict[str, Any], prompt_style: str) -> int | None:
    if prompt_style == "structured":
        return 5
    if prompt_style == "naturalistic":
        return 20
    turns = record.get("turns") or []
    return len(turns) if turns else None


def run_status(record: dict[str, Any], prompt_style: str) -> dict[str, Any]:
    turns = record.get("turns") or []
    turn_count = len(turns)
    expected = expected_turn_count(record, prompt_style)
    stopped_early = record.get("stopped_early")
    if stopped_early:
        status = "early_stop"
    elif expected is not None and turn_count < expected:
        status = "partial"
    elif expected is not None and turn_count == expected:
        status = "full"
    else:
        status = "unknown"
    return {
        "status": status,
        "turn_count": turn_count,
        "expected_turn_count": expected,
        "stopped_early": stopped_early,
    }


def normalize_conversation(raw: dict[str, Any], source_file: Path, line_no: int) -> dict[str, Any]:
    record = raw.get("record") if isinstance(raw.get("record"), dict) else raw
    turns = record.get("turns") or []
    metrics = record.get("metrics") or {}
    scenario_id = record.get("scenario_id") or raw.get("scenario_id") or "unknown_scenario"
    model = raw.get("model") or record.get("model") or "unknown_model"
    prompt_style = raw.get("prompt_style") or record.get("prompt_style") or "unknown_style"
    conv_id = f"{source_file.stem}:{line_no}:{scenario_id}:{model}:{prompt_style}"
    summary = summarize_turns(turns)
    status = run_status(record, prompt_style)
    source_inspiration = record.get("source_inspiration") or {}
    source_family = source_inspiration.get("source_family") if isinstance(source_inspiration, dict) else None
    copied_text = source_inspiration.get("copied_text") if isinstance(source_inspiration, dict) else None
    return {
        "id": conv_id,
        "source_file": safe_relative(source_file),
        "line_no": line_no,
        "run_id": raw.get("run_id"),
        "model": model,
        "judge_model": raw.get("judge_model") or record.get("judge_model") or "unknown_judge",
        "provider": raw.get("provider"),
        "judge_provider": raw.get("judge_provider"),
        "scenario_id": scenario_id,
        "track": record.get("track", "unknown_track"),
        "family": record.get("family", "unknown_family"),
        "domain": record.get("domain", "unknown_domain"),
        "safety_level": record.get("safety_level", "unknown_safety"),
        "source_family": source_family or "unknown_source",
        "source_copied_text": copied_text,
        "unsupported_claim": record.get("unsupported_claim"),
        "prompt_style": prompt_style,
        "run_status": status,
        "stopped_early": status["stopped_early"],
        "metrics": metrics,
        "summary": summary,
        "turns": turns,
    }


def load_conversations(paths: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    conversations: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append({"source_file": safe_relative(path), "line_no": None, "error": str(exc)})
            continue
        if not any(line.strip() for line in lines):
            errors.append({"source_file": safe_relative(path), "line_no": None, "error": "empty_jsonl"})
            continue
        for line_no, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if not isinstance(raw, dict):
                    raise ValueError("JSONL line is not an object")
                conversations.append(normalize_conversation(raw, path, line_no))
            except Exception as exc:  # noqa: BLE001 - dashboard should report every bad line.
                errors.append({"source_file": safe_relative(path), "line_no": line_no, "error": str(exc)})
    conversations.sort(key=lambda item: (item["scenario_id"], item["model"], item["source_file"], item["line_no"]))
    return conversations, errors


def build_payload(conversations: list[dict[str, Any]], errors: list[dict[str, Any]], paths: list[Path], title: str) -> dict[str, Any]:
    return {
        "title": title,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "input_files": [safe_relative(path) for path in paths],
        "load_errors": errors,
        "stance_order": STANCE_ORDER,
        "conversations": conversations,
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #18202f;
      --muted: #667085;
      --line: #d9dee8;
      --soft: #eef1f6;
      --green: #16815c;
      --teal: #09748a;
      --amber: #b65f00;
      --red: #bf2f2f;
      --purple: #6f46a8;
      --blue: #2f5fbd;
      --shadow: 0 1px 3px rgba(16, 24, 40, 0.08);
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: var(--bg); color: var(--ink); font: 14px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    button, input, select, textarea { font: inherit; }
    button { border: 1px solid var(--line); background: var(--panel); color: var(--ink); border-radius: 6px; padding: 7px 10px; cursor: pointer; }
    button:hover { border-color: #aab3c5; background: #fafbfc; }
    .app { min-height: 100vh; display: grid; grid-template-rows: auto auto 1fr; }
    header { background: var(--panel); border-bottom: 1px solid var(--line); padding: 14px 20px; }
    h1 { margin: 0; font-size: 20px; line-height: 1.2; letter-spacing: 0; }
    .subtle { color: var(--muted); }
    .meta-line { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 6px; color: var(--muted); font-size: 12px; }
    .toolbar { display: grid; grid-template-columns: minmax(180px, 1fr) 170px 190px 170px auto auto auto; gap: 10px; align-items: end; padding: 12px 20px; background: #fbfcfe; border-bottom: 1px solid var(--line); }
    .field { display: grid; gap: 4px; }
    .field label { color: var(--muted); font-size: 12px; }
    .field input, .field select { width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 7px 9px; background: var(--panel); color: var(--ink); }
    .checkline { display: flex; gap: 6px; align-items: center; min-height: 34px; color: var(--muted); }
    .main { display: grid; grid-template-columns: minmax(300px, 390px) minmax(0, 1fr); gap: 14px; padding: 14px 20px 22px; }
    .left, .right { min-width: 0; }
    .section { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); }
    .section + .section { margin-top: 12px; }
    .section-head { padding: 12px 14px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 10px; align-items: center; }
    .section-head h2, .section-head h3 { margin: 0; font-size: 15px; letter-spacing: 0; }
    .section-body { padding: 12px 14px; }
    .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .kpi { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: #fcfdff; min-height: 72px; }
    .kpi strong { display: block; font-size: 24px; line-height: 1.1; }
    .kpi span { color: var(--muted); font-size: 12px; }
    .list { max-height: calc(100vh - 280px); overflow: auto; padding: 8px; }
    .conversation-item { width: 100%; text-align: left; border-radius: 8px; padding: 10px; margin: 0 0 8px; background: var(--panel); border: 1px solid var(--line); display: grid; gap: 6px; }
    .conversation-item.active { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(47, 95, 189, 0.13); }
    .item-title { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; font-weight: 650; }
    .item-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; color: var(--muted); font-size: 12px; }
    .badge-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .badge { display: inline-flex; align-items: center; gap: 4px; border-radius: 999px; border: 1px solid var(--line); padding: 2px 7px; font-size: 12px; color: var(--muted); background: #fff; white-space: nowrap; }
    .badge.green { color: var(--green); border-color: rgba(22, 129, 92, 0.28); background: rgba(22, 129, 92, 0.08); }
    .badge.amber { color: var(--amber); border-color: rgba(182, 95, 0, 0.28); background: rgba(182, 95, 0, 0.09); }
    .badge.red { color: var(--red); border-color: rgba(191, 47, 47, 0.28); background: rgba(191, 47, 47, 0.09); }
    .badge.purple { color: var(--purple); border-color: rgba(111, 70, 168, 0.3); background: rgba(111, 70, 168, 0.09); }
    .badge.teal { color: var(--teal); border-color: rgba(9, 116, 138, 0.28); background: rgba(9, 116, 138, 0.08); }
    .chart-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .chart { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: #fcfdff; min-width: 0; }
    .chart h3 { margin: 0 0 8px; font-size: 13px; color: var(--muted); }
    .bar-row { display: grid; grid-template-columns: minmax(90px, 155px) 1fr 48px; gap: 8px; align-items: center; margin: 7px 0; font-size: 12px; }
    .bar-track { height: 10px; background: var(--soft); border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--blue); border-radius: 999px; min-width: 2px; }
    .heat-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .heat-table th, .heat-table td { border-bottom: 1px solid var(--line); padding: 6px; text-align: left; }
    .heat-cell { border-radius: 4px; padding: 3px 6px; display: inline-block; min-width: 52px; text-align: center; }
    .detail-title { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; align-items: start; }
    .detail-title h2 { margin: 0; font-size: 18px; }
    .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
    .metric { background: #fcfdff; border: 1px solid var(--line); border-radius: 8px; padding: 8px; }
    .metric span { display: block; color: var(--muted); font-size: 12px; }
    .metric strong { font-size: 15px; }
    .timeline { overflow-x: auto; padding: 8px 0 2px; }
    .timeline svg { width: 100%; min-width: 720px; height: 92px; display: block; }
    .turn { border: 1px solid var(--line); border-radius: 8px; margin: 12px 0; background: var(--panel); overflow: hidden; }
    .turn-head { padding: 10px 12px; background: #fbfcfe; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; align-items: center; }
    .turn-title { font-weight: 700; }
    .turn-body { padding: 12px; display: grid; gap: 10px; }
    .dialogue { display: grid; grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr); gap: 10px; }
    .bubble { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: #fcfdff; min-width: 0; }
    .bubble h4, .judge-box h4, .annotation h4 { margin: 0 0 6px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
    .text { white-space: pre-wrap; overflow-wrap: anywhere; }
    .judge-box, .annotation { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: #fff; }
    .judge-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-bottom: 8px; }
    .judge-cell { background: #fcfdff; border: 1px solid var(--line); border-radius: 6px; padding: 7px; min-width: 0; }
    .judge-cell span { display: block; color: var(--muted); font-size: 11px; }
    .judge-cell strong { display: block; overflow-wrap: anywhere; }
    .annotation-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .annotation label { display: flex; gap: 6px; align-items: center; color: var(--ink); }
    .annotation select, .annotation textarea { width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 7px; margin-top: 8px; }
    .annotation textarea { min-height: 76px; resize: vertical; }
    .empty { padding: 24px; color: var(--muted); text-align: center; }
    .small { font-size: 12px; }
    @media (max-width: 1060px) {
      .toolbar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .main { grid-template-columns: 1fr; }
      .list { max-height: 360px; }
      .kpis, .metrics, .chart-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 700px) {
      header, .toolbar, .main { padding-left: 12px; padding-right: 12px; }
      .dialogue, .judge-grid, .annotation-grid, .kpis, .metrics, .chart-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <header>
      <h1 id="page-title"></h1>
      <div class="meta-line" id="meta-line"></div>
    </header>

    <section class="toolbar" aria-label="Dashboard filters">
      <div class="field">
        <label for="search">Search</label>
        <input id="search" type="search" placeholder="scenario, model, turn text">
      </div>
      <div class="field">
        <label for="model-filter">Model</label>
        <select id="model-filter"></select>
      </div>
      <div class="field">
        <label for="scenario-filter">Scenario</label>
        <select id="scenario-filter"></select>
      </div>
      <div class="field">
        <label for="issue-filter">Issue</label>
        <select id="issue-filter">
          <option value="all">All</option>
          <option value="drift">Drift event</option>
          <option value="factual">Factual error</option>
          <option value="recovery">Recovery failure</option>
          <option value="safety">Safety flag</option>
          <option value="validation">Judge validation flag</option>
        </select>
      </div>
      <label class="checkline"><input id="drift-only" type="checkbox"> drift only</label>
      <label class="checkline"><input id="annotated-only" type="checkbox"> annotated only</label>
      <button id="reset-filters" type="button">Reset</button>
    </section>

    <main class="main">
      <aside class="left">
        <section class="section">
          <div class="section-head"><h2>Overview</h2><span class="subtle small" id="filtered-count"></span></div>
          <div class="section-body">
            <div class="kpis" id="kpis"></div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h2>Conversations</h2><button id="export-json" type="button">Export annotations</button></div>
          <div class="list" id="conversation-list"></div>
        </section>
      </aside>

      <section class="right">
        <section class="section">
          <div class="section-head"><h2>Charts</h2><button id="export-csv" type="button">Export CSV</button></div>
          <div class="section-body">
            <div class="chart-grid" id="charts"></div>
          </div>
        </section>
        <section class="section">
          <div class="section-body" id="detail"></div>
        </section>
      </section>
    </main>
  </div>

  <script id="payload" type="application/json">__DATA__</script>
  <script>
    const payload = JSON.parse(document.getElementById("payload").textContent);
    const conversations = payload.conversations || [];
    const stanceOrder = payload.stance_order || [];
    const annotationPrefix = "deviation-dashboard-annotation-v1:";
    const state = {
      search: "",
      model: "all",
      scenario: "all",
      issue: "all",
      driftOnly: false,
      annotatedOnly: false,
      selectedId: conversations[0]?.id || null,
    };

    const scoreColors = ["#16815c", "#1f9f82", "#b65f00", "#d36a2c", "#bf2f2f", "#6f46a8"];

    function esc(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function pct(value) {
      if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
      return `${(Number(value) * 100).toFixed(1)}%`;
    }

    function fmt(value) {
      if (value === null || value === undefined) return "n/a";
      if (typeof value === "boolean") return value ? "true" : "false";
      if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
      return String(value);
    }

    function annotationKey(conversationId, turnId) {
      return `${annotationPrefix}${conversationId}:${turnId}`;
    }

    function getAnnotation(conversationId, turnId) {
      const raw = localStorage.getItem(annotationKey(conversationId, turnId));
      if (!raw) return {};
      try { return JSON.parse(raw) || {}; } catch { return {}; }
    }

    function setAnnotation(conversationId, turnId, annotation) {
      const hasContent = Object.values(annotation).some(value => {
        if (Array.isArray(value)) return value.length > 0;
        return value !== "" && value !== false && value !== null && value !== undefined;
      });
      const key = annotationKey(conversationId, turnId);
      if (hasContent) localStorage.setItem(key, JSON.stringify(annotation));
      else localStorage.removeItem(key);
    }

    function hasAnnotation(conversation) {
      return conversation.turns.some(turn => Object.keys(getAnnotation(conversation.id, turn.turn_id)).length > 0);
    }

    function turnHasIssue(turn, issue) {
      const judge = turn.judge || {};
      if (issue === "drift") return Boolean(judge.drift_event);
      if (issue === "factual") return Boolean(judge.factual_error);
      if (issue === "recovery") return turn.turn_id === "recovery" && judge.recovery_success === false;
      if (issue === "safety") return normalizeFlags(judge.safety_flags).length > 0;
      if (issue === "validation") return normalizeFlags(judge.judge_validation_flags).length > 0;
      return true;
    }

    function normalizeFlags(value) {
      if (value === null || value === undefined || value === false || value === "") return [];
      if (value === true) return ["true"];
      if (Array.isArray(value)) return value.filter(Boolean).map(String);
      if (typeof value === "object") return Object.entries(value).filter(([, enabled]) => enabled).map(([key]) => String(key));
      return [String(value)];
    }

    function conversationText(conversation) {
      return [
        conversation.scenario_id,
        conversation.model,
        conversation.judge_model,
        conversation.track,
        conversation.family,
        conversation.domain,
        conversation.source_family,
        conversation.source_file,
        ...conversation.turns.flatMap(turn => [turn.turn_id, turn.user_prompt, turn.model_output, turn.judge?.rationale]),
      ].join(" ").toLowerCase();
    }

    function filteredConversations() {
      const needle = state.search.trim().toLowerCase();
      return conversations.filter(conversation => {
        if (state.model !== "all" && conversation.model !== state.model) return false;
        if (state.scenario !== "all" && conversation.scenario_id !== state.scenario) return false;
        if (state.driftOnly && !conversation.turns.some(turn => turn.judge?.drift_event || turn.judge?.factual_error)) return false;
        if (state.annotatedOnly && !hasAnnotation(conversation)) return false;
        if (state.issue !== "all" && !conversation.turns.some(turn => turnHasIssue(turn, state.issue))) return false;
        if (needle && !conversationText(conversation).includes(needle)) return false;
        return true;
      });
    }

    function unique(values) {
      return Array.from(new Set(values.filter(Boolean))).sort();
    }

    function initFilters() {
      const modelFilter = document.getElementById("model-filter");
      const scenarioFilter = document.getElementById("scenario-filter");
      modelFilter.innerHTML = `<option value="all">All models</option>` + unique(conversations.map(c => c.model)).map(model => `<option value="${esc(model)}">${esc(model)}</option>`).join("");
      scenarioFilter.innerHTML = `<option value="all">All scenarios</option>` + unique(conversations.map(c => c.scenario_id)).map(scenario => `<option value="${esc(scenario)}">${esc(scenario)}</option>`).join("");
    }

    function bindFilters() {
      const bindings = [
        ["search", "input", value => { state.search = value; }],
        ["model-filter", "change", value => { state.model = value; }],
        ["scenario-filter", "change", value => { state.scenario = value; }],
        ["issue-filter", "change", value => { state.issue = value; }],
      ];
      for (const [id, eventName, setter] of bindings) {
        document.getElementById(id).addEventListener(eventName, event => {
          setter(event.target.value);
          render();
        });
      }
      document.getElementById("drift-only").addEventListener("change", event => {
        state.driftOnly = event.target.checked;
        render();
      });
      document.getElementById("annotated-only").addEventListener("change", event => {
        state.annotatedOnly = event.target.checked;
        render();
      });
      document.getElementById("reset-filters").addEventListener("click", () => {
        state.search = "";
        state.model = "all";
        state.scenario = "all";
        state.issue = "all";
        state.driftOnly = false;
        state.annotatedOnly = false;
        document.getElementById("search").value = "";
        document.getElementById("model-filter").value = "all";
        document.getElementById("scenario-filter").value = "all";
        document.getElementById("issue-filter").value = "all";
        document.getElementById("drift-only").checked = false;
        document.getElementById("annotated-only").checked = false;
        render();
      });
      document.getElementById("export-json").addEventListener("click", exportAnnotationsJson);
      document.getElementById("export-csv").addEventListener("click", exportAnnotationsCsv);
    }

    function aggregate(convs) {
      const turns = convs.flatMap(c => c.turns.map(turn => ({ conversation: c, turn })));
      const driftTurns = turns.filter(item => item.turn.judge?.drift_event);
      const factualTurns = turns.filter(item => item.turn.judge?.factual_error);
      const recoveryTurns = turns.filter(item => item.turn.turn_id === "recovery");
      const recoverySuccess = recoveryTurns.filter(item => item.turn.judge?.recovery_success === true).length;
      return { turns, driftTurns, factualTurns, recoveryTurns, recoverySuccess };
    }

    function renderKpis(convs) {
      const agg = aggregate(convs);
      const statusCounts = new Map();
      for (const conversation of convs) {
        const status = conversation.run_status?.status || "unknown";
        statusCounts.set(status, (statusCounts.get(status) || 0) + 1);
      }
      const html = [
        ["Conversations", convs.length, "loaded after filters"],
        ["Turns", agg.turns.length, "target/judge pairs"],
        ["Full runs", statusCounts.get("full") || 0, `${statusCounts.get("partial") || 0} partial · ${statusCounts.get("early_stop") || 0} early-stop`],
        ["Factual error", pct(agg.turns.length ? agg.factualTurns.length / agg.turns.length : 0), `${agg.factualTurns.length} turns`],
        ["Recovery success", pct(agg.recoveryTurns.length ? agg.recoverySuccess / agg.recoveryTurns.length : 0), `${agg.recoverySuccess}/${agg.recoveryTurns.length}`],
      ].map(([label, value, caption]) => `<div class="kpi"><strong>${esc(value)}</strong><span>${esc(label)} · ${esc(caption)}</span></div>`).join("");
      document.getElementById("kpis").innerHTML = html;
      document.getElementById("filtered-count").textContent = `${convs.length}/${conversations.length}`;
    }

    function groupedRate(convs, field) {
      const groups = new Map();
      for (const conversation of convs) {
        const key = conversation[field] || "unknown";
        if (!groups.has(key)) groups.set(key, { key, turns: 0, factual: 0, drift: 0 });
        const group = groups.get(key);
        for (const turn of conversation.turns) {
          group.turns += 1;
          if (turn.judge?.factual_error) group.factual += 1;
          if (turn.judge?.drift_event) group.drift += 1;
        }
      }
      return Array.from(groups.values()).sort((a, b) => (b.factual / Math.max(b.turns, 1)) - (a.factual / Math.max(a.turns, 1)));
    }

    function barRows(rows, valueKey, denominatorKey, color) {
      const maxValue = Math.max(1, ...rows.map(row => row[valueKey] / Math.max(row[denominatorKey], 1)));
      return rows.map(row => {
        const rate = row[valueKey] / Math.max(row[denominatorKey], 1);
        const width = Math.max(2, Math.round((rate / maxValue) * 100));
        return `<div class="bar-row"><span title="${esc(row.key)}">${esc(row.key)}</span><div class="bar-track"><div class="bar-fill" style="width:${width}%; background:${color}"></div></div><strong>${pct(rate)}</strong></div>`;
      }).join("") || `<div class="empty">No data</div>`;
    }

    function renderCharts(convs) {
      const agg = aggregate(convs);
      const stanceCounts = new Map(stanceOrder.map(stance => [stance, 0]));
      for (const item of agg.turns) {
        const stance = item.turn.judge?.stance || "unknown";
        stanceCounts.set(stance, (stanceCounts.get(stance) || 0) + 1);
      }
      const stanceRows = Array.from(stanceCounts.entries()).map(([key, count]) => ({ key, count, total: agg.turns.length || 1 })).filter(row => row.count);
      const modelRows = groupedRate(convs, "model");
      const scenarioRows = groupedRate(convs, "scenario_id");
      const heatRows = modelRows.slice(0, 12).map(row => `
        <tr>
          <td>${esc(row.key)}</td>
          <td><span class="heat-cell" style="background:${heatColor(row.factual / Math.max(row.turns, 1))}">${pct(row.factual / Math.max(row.turns, 1))}</span></td>
          <td><span class="heat-cell" style="background:${heatColor(row.drift / Math.max(row.turns, 1))}">${pct(row.drift / Math.max(row.turns, 1))}</span></td>
          <td>${row.turns}</td>
        </tr>
      `).join("");
      document.getElementById("charts").innerHTML = `
        <div class="chart"><h3>Factual error rate by model</h3>${barRows(modelRows, "factual", "turns", "var(--red)")}</div>
        <div class="chart"><h3>Factual error rate by scenario</h3>${barRows(scenarioRows, "factual", "turns", "var(--purple)")}</div>
        <div class="chart"><h3>Stance distribution</h3>${barRows(stanceRows, "count", "total", "var(--teal)")}</div>
        <div class="chart"><h3>Model issue heatmap</h3><table class="heat-table"><thead><tr><th>Model</th><th>Factual</th><th>Drift</th><th>Turns</th></tr></thead><tbody>${heatRows || `<tr><td colspan="4">No data</td></tr>`}</tbody></table></div>
      `;
    }

    function heatColor(rate) {
      if (rate >= 0.35) return "rgba(191,47,47,0.20)";
      if (rate >= 0.15) return "rgba(182,95,0,0.18)";
      if (rate > 0) return "rgba(111,70,168,0.14)";
      return "rgba(22,129,92,0.13)";
    }

    function renderConversationList(convs) {
      if (!convs.length) {
        document.getElementById("conversation-list").innerHTML = `<div class="empty">No conversations match the current filters.</div>`;
        return;
      }
      if (!convs.some(c => c.id === state.selectedId)) state.selectedId = convs[0].id;
      document.getElementById("conversation-list").innerHTML = convs.map(conversation => {
        const summary = conversation.summary || {};
        const status = conversation.run_status?.status || "unknown";
        const statusClass = status === "full" ? "green" : status === "early_stop" ? "red" : status === "partial" ? "amber" : "teal";
        const badges = [
          `<span class="badge ${statusClass}">${esc(status)}</span>`,
          summary.factual_error_count ? `<span class="badge red">factual ${summary.factual_error_count}</span>` : `<span class="badge green">no factual</span>`,
          summary.drift_count ? `<span class="badge amber">drift ${summary.drift_count}</span>` : `<span class="badge green">grounded</span>`,
          summary.recovery_success === false ? `<span class="badge red">recovery fail</span>` : summary.recovery_success === true ? `<span class="badge teal">recovery ok</span>` : "",
          hasAnnotation(conversation) ? `<span class="badge purple">annotated</span>` : "",
        ].join("");
        return `
          <button class="conversation-item ${conversation.id === state.selectedId ? "active" : ""}" data-conv-id="${esc(conversation.id)}" type="button">
            <div class="item-title"><span>${esc(conversation.scenario_id)}</span><span class="subtle">${esc(conversation.model)}</span></div>
            <div class="item-grid"><span>${esc(conversation.prompt_style)}</span><span>${summary.turn_count || 0}/${conversation.run_status?.expected_turn_count || "?"} turns</span><span>max ${summary.max_stance_score ?? 0}</span></div>
            <div class="badge-row">${badges}</div>
          </button>
        `;
      }).join("");
      for (const item of document.querySelectorAll(".conversation-item")) {
        item.addEventListener("click", () => {
          state.selectedId = item.dataset.convId;
          render();
        });
      }
    }

    function metricBlock(metrics, summary) {
      const fields = [
        ["rds_auc", metrics.rds_auc],
        ["factual_error_rate", metrics.factual_error_rate],
        ["reality_drift_event_rate", metrics.reality_drift_event_rate],
        ["recovery_success", summary.recovery_success],
        ["first factual", summary.first_factual_error_turn],
        ["first drift", summary.first_drift_turn],
        ["max stance", summary.max_stance_score],
        ["validation flags", summary.validation_flag_count],
      ];
      return fields.map(([label, value]) => `<div class="metric"><span>${esc(label)}</span><strong>${esc(fmt(value))}</strong></div>`).join("");
    }

    function turnBadges(turn) {
      const judge = turn.judge || {};
      const badges = [];
      badges.push(`<span class="badge ${judge.stance_score >= 3 ? "red" : judge.stance_score >= 2 ? "amber" : "green"}">score ${esc(fmt(judge.stance_score))}</span>`);
      if (judge.factual_error) badges.push(`<span class="badge red">factual error</span>`);
      if (judge.drift_event) badges.push(`<span class="badge amber">drift</span>`);
      if (judge.confabulatory_elaboration) badges.push(`<span class="badge purple">confab</span>`);
      if (judge.unjustified_reversal) badges.push(`<span class="badge red">reversal</span>`);
      if (judge.certainty_inflation) badges.push(`<span class="badge amber">certainty</span>`);
      if (turn.turn_id === "recovery" && judge.recovery_success === false) badges.push(`<span class="badge red">recovery fail</span>`);
      for (const flag of normalizeFlags(judge.safety_flags)) badges.push(`<span class="badge red">safety: ${esc(flag)}</span>`);
      for (const flag of normalizeFlags(judge.judge_validation_flags)) badges.push(`<span class="badge teal">judge: ${esc(flag)}</span>`);
      return badges.join("");
    }

    function renderTimeline(conversation) {
      const turns = conversation.turns || [];
      const width = Math.max(760, turns.length * 42);
      const step = width / Math.max(turns.length, 1);
      const cells = turns.map((turn, index) => {
        const judge = turn.judge || {};
        const score = Math.max(0, Math.min(5, Number(judge.stance_score || 0)));
        const x = Math.round(index * step + 8);
        const barHeight = 12 + score * 10;
        const y = 62 - barHeight;
        const color = scoreColors[score] || "#667085";
        const stroke = judge.factual_error ? "#bf2f2f" : judge.drift_event ? "#b65f00" : "#d9dee8";
        return `
          <rect x="${x}" y="${y}" width="${Math.max(16, step - 14)}" height="${barHeight}" rx="4" fill="${color}" stroke="${stroke}" stroke-width="${judge.factual_error ? 3 : 1}"></rect>
          <text x="${x + Math.max(16, step - 14) / 2}" y="78" text-anchor="middle" font-size="10" fill="#667085">${esc(turn.turn_id)}</text>
        `;
      }).join("");
      return `<div class="timeline"><svg viewBox="0 0 ${width} 92" role="img" aria-label="Stance score timeline">
        <line x1="6" y1="62" x2="${width - 6}" y2="62" stroke="#d9dee8"></line>
        ${cells}
      </svg></div>`;
    }

    function annotationHtml(conversation, turn) {
      const annotation = getAnnotation(conversation.id, turn.turn_id);
      const issues = new Set(annotation.issues || []);
      const options = ["", ...stanceOrder].map(stance => `<option value="${esc(stance)}" ${annotation.human_stance === stance ? "selected" : ""}>${stance ? esc(stance) : "human stance"}</option>`).join("");
      const checks = [
        ["strong_factual_error", "强事实错误"],
        ["minor_error_only", "仅轻微数字/转述错误"],
        ["unsupported_endorsement", "无证据背书"],
        ["confabulation", "虚构外部依据"],
        ["recovery_failure", "恢复失败"],
        ["judge_disagreement", "不同意 judge"],
      ].map(([key, label]) => `<label><input type="checkbox" data-issue="${key}" ${issues.has(key) ? "checked" : ""}> ${label}</label>`).join("");
      return `
        <div class="annotation" data-conv-id="${esc(conversation.id)}" data-turn-id="${esc(turn.turn_id)}">
          <h4>Human annotation</h4>
          <div class="annotation-grid">${checks}</div>
          <select data-field="human_stance">${options}</select>
          <textarea data-field="note" placeholder="人工备注：为什么算/不算问题，是否只是 minor slip">${esc(annotation.note || "")}</textarea>
        </div>
      `;
    }

    function renderTurns(conversation) {
      return (conversation.turns || []).map(turn => {
        const judge = turn.judge || {};
        return `
          <article class="turn" id="turn-${esc(turn.turn_id)}">
            <div class="turn-head">
              <div class="turn-title">${esc(turn.turn_id)} · ${esc(judge.stance || "no stance")}</div>
              <div class="badge-row">${turnBadges(turn)}</div>
            </div>
            <div class="turn-body">
              <div class="dialogue">
                <div class="bubble"><h4>User</h4><div class="text">${esc(turn.user_prompt)}</div></div>
                <div class="bubble"><h4>Model output</h4><div class="text">${esc(turn.model_output)}</div></div>
              </div>
              <div class="judge-box">
                <h4>Judge</h4>
                <div class="judge-grid">
                  <div class="judge-cell"><span>stance</span><strong>${esc(judge.stance)}</strong></div>
                  <div class="judge-cell"><span>score</span><strong>${esc(fmt(judge.stance_score))}</strong></div>
                  <div class="judge-cell"><span>factual_error</span><strong>${esc(fmt(judge.factual_error))}</strong></div>
                  <div class="judge-cell"><span>recovery</span><strong>${esc(fmt(judge.recovery_success))}</strong></div>
                </div>
                <div class="text small">${esc(judge.rationale || "")}</div>
              </div>
              ${annotationHtml(conversation, turn)}
            </div>
          </article>
        `;
      }).join("");
    }

    function bindAnnotationControls() {
      for (const root of document.querySelectorAll(".annotation")) {
        const conversationId = root.dataset.convId;
        const turnId = root.dataset.turnId;
        const save = () => {
          const issues = Array.from(root.querySelectorAll("input[data-issue]:checked")).map(input => input.dataset.issue);
          const humanStance = root.querySelector('[data-field="human_stance"]').value;
          const note = root.querySelector('[data-field="note"]').value;
          setAnnotation(conversationId, turnId, { issues, human_stance: humanStance, note });
        };
        root.querySelectorAll("input, select").forEach(control => control.addEventListener("change", () => {
          save();
          render();
        }));
        root.querySelectorAll("textarea").forEach(control => control.addEventListener("input", save));
      }
    }

    function renderDetail(convs) {
      const conversation = convs.find(c => c.id === state.selectedId) || convs[0];
      const detail = document.getElementById("detail");
      if (!conversation) {
        detail.innerHTML = `<div class="empty">Select a conversation to inspect turns and annotations.</div>`;
        return;
      }
      state.selectedId = conversation.id;
      detail.innerHTML = `
        <div class="detail-title">
          <div>
            <h2>${esc(conversation.scenario_id)} · ${esc(conversation.model)}</h2>
            <div class="meta-line">
              <span>${esc(conversation.track)}</span>
              <span>${esc(conversation.family)}</span>
              <span>${esc(conversation.domain)}</span>
              <span>${esc(conversation.prompt_style)}</span>
              <span>${esc(conversation.source_family)}</span>
              <span>${esc(conversation.run_status?.status || "unknown")}: ${esc(conversation.run_status?.turn_count || 0)}/${esc(conversation.run_status?.expected_turn_count || "?")} turns</span>
              <span>${esc(conversation.source_file)}</span>
            </div>
          </div>
          <div class="badge-row">
            <span class="badge teal">judge ${esc(conversation.judge_model)}</span>
            ${conversation.stopped_early ? `<span class="badge amber">stopped ${esc(conversation.stopped_early.turn_id || "")}</span>` : ""}
          </div>
        </div>
        <div class="section" style="margin-top: 12px;"><div class="section-body">
          <div class="metrics">${metricBlock(conversation.metrics || {}, conversation.summary || {})}</div>
          ${renderTimeline(conversation)}
        </div></div>
        ${renderTurns(conversation)}
      `;
      bindAnnotationControls();
    }

    function allAnnotations() {
      const rows = [];
      for (const conversation of conversations) {
        for (const turn of conversation.turns) {
          const annotation = getAnnotation(conversation.id, turn.turn_id);
          if (!Object.keys(annotation).length) continue;
          rows.push({
            conversation_id: conversation.id,
            scenario_id: conversation.scenario_id,
            model: conversation.model,
            source_file: conversation.source_file,
            turn_id: turn.turn_id,
            judge_stance: turn.judge?.stance || "",
            judge_score: turn.judge?.stance_score ?? "",
            judge_factual_error: turn.judge?.factual_error ?? "",
            human_stance: annotation.human_stance || "",
            issues: (annotation.issues || []).join("|"),
            note: annotation.note || "",
          });
        }
      }
      return rows;
    }

    function download(name, content, type) {
      const blob = new Blob([content], { type });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = name;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    }

    function exportAnnotationsJson() {
      download("deviation_dashboard_annotations.json", JSON.stringify(allAnnotations(), null, 2), "application/json");
    }

    function csvCell(value) {
      const text = String(value ?? "");
      return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
    }

    function exportAnnotationsCsv() {
      const rows = allAnnotations();
      const headers = ["conversation_id", "scenario_id", "model", "source_file", "turn_id", "judge_stance", "judge_score", "judge_factual_error", "human_stance", "issues", "note"];
      const csv = [headers.join(","), ...rows.map(row => headers.map(header => csvCell(row[header])).join(","))].join("\n");
      download("deviation_dashboard_annotations.csv", csv, "text/csv;charset=utf-8");
    }

    function render() {
      const convs = filteredConversations();
      renderKpis(convs);
      renderCharts(convs);
      renderConversationList(convs);
      renderDetail(convs);
    }

    function init() {
      document.getElementById("page-title").textContent = payload.title || "Deviation Bench Dashboard";
      document.getElementById("meta-line").innerHTML = [
        `generated ${esc(payload.generated_at || "")}`,
        `${conversations.length} conversations`,
        `${(payload.input_files || []).length} input files`,
        (payload.load_errors || []).length ? `${payload.load_errors.length} load errors` : "no load errors",
      ].map(item => `<span>${item}</span>`).join("");
      initFilters();
      bindFilters();
      render();
    }

    init();
  </script>
</body>
</html>
"""


def build_html(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = str(payload.get("title") or "Deviation Bench Conversation Dashboard")
    return HTML_TEMPLATE.replace("__TITLE__", title).replace("__DATA__", data)


def main() -> None:
    args = parse_args()
    paths = expand_inputs(args.input)
    conversations, errors = load_conversations(paths)
    payload = build_payload(conversations, errors, paths, args.title)
    html = build_html(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"input_files={len(paths)} conversations={len(conversations)} load_errors={len(errors)}")
    print(f"wrote={args.out}")


if __name__ == "__main__":
    main()
