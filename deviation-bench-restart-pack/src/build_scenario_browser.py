#!/usr/bin/env python3
"""Build a static browser for Deviation Bench scenario drafts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "prompts" / "memory_scenario_drafts.yaml"
DEFAULT_OUT = ROOT / "results" / "scenario_browser" / "index.html"

TARGET_MARKERS = [
    "benchmark",
    "rubric",
    "judge",
    "stance",
    "JSON",
    "json",
    "测试",
    "评测",
    "基准",
    "裁判",
    "评分",
    "可选答案",
    "已知事实",
    "证据锚点",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a self-contained scenario browser.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Scenario draft YAML.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output HTML path.")
    parser.add_argument("--validate-only", action="store_true", help="Validate input and exit.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError(f"{path} must contain a scenarios list")
    return data


def validate_scenario(scenario: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scenario_id = scenario.get("scenario_id", "<missing id>")
    required = [
        "scenario_id",
        "title",
        "track",
        "family",
        "domain",
        "language",
        "safety_level",
        "source_inspiration",
        "scenario_description",
        "mainline",
        "related_facts",
        "real_data_anchor",
        "objective_boundary",
        "memory_test_design",
        "dialogue",
    ]
    for field in required:
        if field not in scenario:
            errors.append(f"{scenario_id}: missing {field}")

    source = scenario.get("source_inspiration") or {}
    if source.get("copied_text") is not False:
        errors.append(f"{scenario_id}: source_inspiration.copied_text must be false")
    source_pattern_ids = source.get("source_pattern_ids")
    if not isinstance(source_pattern_ids, list) or not source_pattern_ids:
        errors.append(f"{scenario_id}: source_inspiration.source_pattern_ids must be a non-empty list")

    if not str(scenario.get("scenario_description", "")).strip():
        errors.append(f"{scenario_id}: scenario_description must be non-empty")
    mainline = scenario.get("mainline")
    if not isinstance(mainline, list) or len(mainline) < 3:
        errors.append(f"{scenario_id}: mainline must contain at least 3 steps")
    related_facts = scenario.get("related_facts") or {}
    for field in ["verified_facts", "missing_or_unverified", "unsupported_inference_to_resist"]:
        value = related_facts.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{scenario_id}: related_facts.{field} must be a non-empty list")
    if not str(related_facts.get("recovery_fact_check", "")).strip():
        errors.append(f"{scenario_id}: related_facts.recovery_fact_check must be non-empty")

    real_anchor = scenario.get("real_data_anchor") or {}
    for field in ["source_summary", "citation", "use_boundary"]:
        if not str(real_anchor.get(field, "")).strip():
            errors.append(f"{scenario_id}: real_data_anchor.{field} must be non-empty")
    for field in ["pattern_ids", "pattern_roles"]:
        value = real_anchor.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{scenario_id}: real_data_anchor.{field} must be a non-empty list")

    boundary = scenario.get("objective_boundary") or {}
    if boundary.get("claim_supported_by_anchor") is not False:
        errors.append(f"{scenario_id}: claim_supported_by_anchor must be false")
    if boundary.get("induction_turns_add_new_evidence") is not False:
        errors.append(f"{scenario_id}: induction_turns_add_new_evidence must be false")
    anchor = boundary.get("evidence_anchor") or {}
    for field in ["facts", "missing_evidence", "supported_grounded_answer"]:
        if field not in anchor:
            errors.append(f"{scenario_id}: evidence_anchor missing {field}")
    if not boundary.get("unsupported_claim"):
        errors.append(f"{scenario_id}: missing unsupported_claim")

    memory_design = scenario.get("memory_test_design") or {}
    for field in ["early_anchor_turn_ids", "unsupported_claim_turn_ids", "recovery_turn_ids", "expected_memory_failures"]:
        value = memory_design.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{scenario_id}: memory_test_design.{field} must be a non-empty list")

    dialogue = scenario.get("dialogue") or []
    if not isinstance(dialogue, list) or len(dialogue) < 8:
        errors.append(f"{scenario_id}: dialogue must contain at least 8 turns")
    seen_turns: set[str] = set()
    for turn in dialogue if isinstance(dialogue, list) else []:
        turn_id = str(turn.get("turn_id", ""))
        if not turn_id:
            errors.append(f"{scenario_id}: dialogue turn missing turn_id")
        if turn_id in seen_turns:
            errors.append(f"{scenario_id}: duplicate turn_id {turn_id}")
        seen_turns.add(turn_id)
        for field in ["role", "pressure_type", "user_prompt", "adds_new_evidence", "expected_model_behavior"]:
            if field not in turn:
                errors.append(f"{scenario_id}: turn {turn_id or '<missing>'} missing {field}")
        if turn.get("role") != "user":
            errors.append(f"{scenario_id}: turn {turn_id} role must be user")
        if turn.get("adds_new_evidence") is not False:
            errors.append(f"{scenario_id}: turn {turn_id} adds new evidence")
        prompt = str(turn.get("user_prompt", ""))
        for marker in TARGET_MARKERS:
            if marker in prompt:
                errors.append(f"{scenario_id}: turn {turn_id} exposes marker {marker!r}")

    if dialogue:
        if dialogue[0].get("turn_id") != "opening":
            errors.append(f"{scenario_id}: first dialogue turn must be opening")
        if dialogue[-1].get("turn_id") != "recovery":
            errors.append(f"{scenario_id}: last dialogue turn must be recovery")
    return errors


def validate_dataset(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for scenario in data["scenarios"]:
        if not isinstance(scenario, dict):
            errors.append("scenario entry is not a mapping")
            continue
        scenario_id = str(scenario.get("scenario_id", ""))
        if scenario_id in seen_ids:
            errors.append(f"duplicate scenario_id {scenario_id}")
        seen_ids.add(scenario_id)
        errors.extend(validate_scenario(scenario))
    return errors


def build_payload(data: dict[str, Any], input_path: Path) -> dict[str, Any]:
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "input_file": str(input_path),
        "dataset": {
            "name": data.get("dataset_name"),
            "version": data.get("dataset_version"),
            "status": data.get("status"),
            "description": data.get("description"),
            "construction_principles": data.get("construction_principles") or {},
        },
        "scenarios": data["scenarios"],
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Deviation Bench Scenario Browser</title>
  <style>
    :root {
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #647084;
      --line: #d8dee8;
      --soft: #eef2f6;
      --blue: #255db7;
      --green: #147a5b;
      --amber: #a85c00;
      --red: #ba2e42;
      --purple: #6a45a2;
      --shadow: 0 1px 3px rgba(16, 24, 40, 0.08);
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: var(--bg); color: var(--ink); font: 14px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    button, input, select { font: inherit; }
    button { border: 1px solid var(--line); background: var(--panel); color: var(--ink); border-radius: 6px; padding: 7px 10px; cursor: pointer; }
    button:hover { border-color: #aeb7c7; }
    header { background: var(--panel); border-bottom: 1px solid var(--line); padding: 16px 22px; }
    h1 { margin: 0; font-size: 21px; line-height: 1.2; letter-spacing: 0; }
    h2, h3 { letter-spacing: 0; }
    .meta { display: flex; flex-wrap: wrap; gap: 12px; color: var(--muted); font-size: 12px; margin-top: 6px; }
    .toolbar { display: grid; grid-template-columns: minmax(220px, 1fr) 180px 190px 180px auto; gap: 10px; padding: 12px 22px; background: #fbfcfd; border-bottom: 1px solid var(--line); align-items: end; }
    .field { display: grid; gap: 4px; }
    .field label { color: var(--muted); font-size: 12px; }
    .field input, .field select { width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 7px 9px; background: var(--panel); color: var(--ink); }
    .main { display: grid; grid-template-columns: minmax(320px, 420px) minmax(0, 1fr); gap: 14px; padding: 14px 22px 24px; }
    .section { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); min-width: 0; }
    .section + .section { margin-top: 12px; }
    .section-head { padding: 12px 14px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 10px; align-items: center; }
    .section-head h2, .section-head h3 { margin: 0; font-size: 15px; }
    .section-body { padding: 12px 14px; }
    .subtle { color: var(--muted); }
    .small { font-size: 12px; }
    .kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .kpi { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: #fcfdff; min-height: 66px; }
    .kpi strong { display: block; font-size: 23px; line-height: 1.1; }
    .kpi span { color: var(--muted); font-size: 12px; }
    .list { padding: 8px; max-height: calc(100vh - 300px); overflow: auto; }
    .scenario-item { width: 100%; text-align: left; border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 10px; margin: 0 0 8px; display: grid; gap: 7px; }
    .scenario-item.active { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(37, 93, 183, 0.13); }
    .item-title { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; font-weight: 700; }
    .badge-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .badge { display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 2px 7px; color: var(--muted); font-size: 12px; background: #fff; white-space: nowrap; }
    .badge.green { color: var(--green); border-color: rgba(20, 122, 91, 0.28); background: rgba(20, 122, 91, 0.08); }
    .badge.amber { color: var(--amber); border-color: rgba(168, 92, 0, 0.28); background: rgba(168, 92, 0, 0.08); }
    .badge.red { color: var(--red); border-color: rgba(186, 46, 66, 0.28); background: rgba(186, 46, 66, 0.08); }
    .badge.purple { color: var(--purple); border-color: rgba(106, 69, 162, 0.28); background: rgba(106, 69, 162, 0.08); }
    .detail-title { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; align-items: start; }
    .detail-title h2 { margin: 0; font-size: 19px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .box { border: 1px solid var(--line); border-radius: 8px; background: #fcfdff; padding: 10px; min-width: 0; }
    .box h3 { margin: 0 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
    ul { margin: 6px 0 0 18px; padding: 0; }
    li { margin: 3px 0; }
    .turn { border: 1px solid var(--line); border-radius: 8px; margin: 10px 0; overflow: hidden; background: #fff; }
    .turn-head { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; padding: 9px 11px; background: #fbfcfd; border-bottom: 1px solid var(--line); }
    .turn-body { padding: 11px; display: grid; gap: 8px; }
    .text { white-space: pre-wrap; overflow-wrap: anywhere; }
    .tagline { display: flex; flex-wrap: wrap; gap: 6px; }
    .objective { border-left: 3px solid var(--green); }
    .claim { border-left: 3px solid var(--red); }
    .memory { border-left: 3px solid var(--purple); }
    .empty { padding: 26px; text-align: center; color: var(--muted); }
    @media (max-width: 1050px) {
      .toolbar { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .main { grid-template-columns: 1fr; }
      .list { max-height: 380px; }
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 680px) {
      header, .toolbar, .main { padding-left: 12px; padding-right: 12px; }
      .kpis { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Deviation Bench Scenario Browser</h1>
    <div class="meta" id="meta"></div>
  </header>
  <section class="toolbar">
    <div class="field">
      <label for="search">Search</label>
      <input id="search" type="search" placeholder="scenario, claim, prompt text">
    </div>
    <div class="field">
      <label for="track-filter">Track</label>
      <select id="track-filter"></select>
    </div>
    <div class="field">
      <label for="family-filter">Family</label>
      <select id="family-filter"></select>
    </div>
    <div class="field">
      <label for="domain-filter">Domain</label>
      <select id="domain-filter"></select>
    </div>
    <button id="reset" type="button">Reset</button>
  </section>
  <main class="main">
    <aside>
      <section class="section">
        <div class="section-head"><h2>Overview</h2><span id="count" class="subtle small"></span></div>
        <div class="section-body"><div class="kpis" id="kpis"></div></div>
      </section>
      <section class="section">
        <div class="section-head"><h2>Scenario Drafts</h2></div>
        <div class="list" id="scenario-list"></div>
      </section>
    </aside>
    <section class="section">
      <div class="section-body" id="detail"></div>
    </section>
  </main>
  <script id="payload" type="application/json">__DATA__</script>
  <script>
    const payload = JSON.parse(document.getElementById("payload").textContent);
    const scenarios = payload.scenarios || [];
    const state = { search: "", track: "all", family: "all", domain: "all", selected: scenarios[0]?.scenario_id || null };

    function esc(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
    }

    function unique(values) {
      return Array.from(new Set(values.filter(Boolean))).sort();
    }

    function listItems(values, fallback = "None") {
      if (!Array.isArray(values) || values.length === 0) return `<p class="subtle">${esc(fallback)}</p>`;
      return `<ul>${values.map(item => `<li>${esc(item)}</li>`).join("")}</ul>`;
    }

    function badges(values, cls = "") {
      if (!Array.isArray(values)) return "";
      return values.map(value => `<span class="badge ${cls}">${esc(value)}</span>`).join("");
    }

    function scenarioText(scenario) {
      const boundary = scenario.objective_boundary || {};
      const anchor = boundary.evidence_anchor || {};
      return [
        scenario.scenario_id, scenario.title, scenario.track, scenario.family, scenario.domain,
        scenario.scenario_description,
        ...(scenario.mainline || []),
        boundary.unsupported_claim, boundary.expected_grounded_stance,
        ...(anchor.facts || []), ...(anchor.missing_evidence || []),
        ...(scenario.related_facts?.verified_facts || []),
        ...(scenario.related_facts?.missing_or_unverified || []),
        ...(scenario.related_facts?.unsupported_inference_to_resist || []),
        scenario.real_data_anchor?.source_summary,
        scenario.real_data_anchor?.citation,
        scenario.real_data_anchor?.use_boundary,
        ...(scenario.real_data_anchor?.pattern_ids || []),
        ...(scenario.real_data_anchor?.pattern_roles || []),
        ...(scenario.dialogue || []).flatMap(turn => [turn.turn_id, turn.pressure_type, turn.user_prompt, turn.expected_model_behavior]),
      ].join(" ").toLowerCase();
    }

    function filtered() {
      const needle = state.search.trim().toLowerCase();
      return scenarios.filter(scenario => {
        if (state.track !== "all" && scenario.track !== state.track) return false;
        if (state.family !== "all" && scenario.family !== state.family) return false;
        if (state.domain !== "all" && scenario.domain !== state.domain) return false;
        if (needle && !scenarioText(scenario).includes(needle)) return false;
        return true;
      });
    }

    function init() {
      document.getElementById("meta").innerHTML = [
        `dataset=${esc(payload.dataset?.name || "")}`,
        `version=${esc(payload.dataset?.version || "")}`,
        `status=${esc(payload.dataset?.status || "")}`,
        `generated=${esc(payload.generated_at || "")}`,
      ].map(item => `<span>${item}</span>`).join("");
      fillSelect("track-filter", "All tracks", unique(scenarios.map(item => item.track)));
      fillSelect("family-filter", "All families", unique(scenarios.map(item => item.family)));
      fillSelect("domain-filter", "All domains", unique(scenarios.map(item => item.domain)));
      document.getElementById("search").addEventListener("input", event => { state.search = event.target.value; render(); });
      document.getElementById("track-filter").addEventListener("change", event => { state.track = event.target.value; render(); });
      document.getElementById("family-filter").addEventListener("change", event => { state.family = event.target.value; render(); });
      document.getElementById("domain-filter").addEventListener("change", event => { state.domain = event.target.value; render(); });
      document.getElementById("reset").addEventListener("click", () => {
        state.search = ""; state.track = "all"; state.family = "all"; state.domain = "all";
        document.getElementById("search").value = "";
        document.getElementById("track-filter").value = "all";
        document.getElementById("family-filter").value = "all";
        document.getElementById("domain-filter").value = "all";
        render();
      });
      render();
    }

    function fillSelect(id, label, values) {
      const select = document.getElementById(id);
      select.innerHTML = `<option value="all">${esc(label)}</option>` + values.map(value => `<option value="${esc(value)}">${esc(value)}</option>`).join("");
    }

    function render() {
      const visible = filtered();
      if (!visible.some(item => item.scenario_id === state.selected)) state.selected = visible[0]?.scenario_id || null;
      renderKpis(visible);
      renderList(visible);
      renderDetail(visible.find(item => item.scenario_id === state.selected));
    }

    function renderKpis(visible) {
      const totalTurns = visible.reduce((sum, scenario) => sum + (scenario.dialogue || []).length, 0);
      const claims = visible.filter(scenario => scenario.objective_boundary?.claim_supported_by_anchor === false).length;
      document.getElementById("count").textContent = `${visible.length} shown`;
      document.getElementById("kpis").innerHTML = [
        ["Scenarios", visible.length],
        ["Dialogue turns", totalTurns],
        ["Closed-world", claims],
      ].map(([label, value]) => `<div class="kpi"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`).join("");
    }

    function renderList(visible) {
      const list = document.getElementById("scenario-list");
      if (!visible.length) {
        list.innerHTML = `<div class="empty">No scenarios match the filters.</div>`;
        return;
      }
      list.innerHTML = visible.map(scenario => {
        const active = scenario.scenario_id === state.selected ? " active" : "";
        const boundary = scenario.objective_boundary || {};
        return `
          <button class="scenario-item${active}" data-id="${esc(scenario.scenario_id)}">
            <div class="item-title"><span>${esc(scenario.title)}</span><span class="subtle small">${esc(scenario.scenario_id)}</span></div>
            <div class="subtle small">${esc(boundary.unsupported_claim || "")}</div>
            <div class="badge-row">
              <span class="badge green">${esc(scenario.track)}</span>
              <span class="badge">${esc(scenario.family)}</span>
              <span class="badge">${esc((scenario.dialogue || []).length)} turns</span>
            </div>
          </button>
        `;
      }).join("");
      list.querySelectorAll(".scenario-item").forEach(button => {
        button.addEventListener("click", () => {
          state.selected = button.dataset.id;
          render();
        });
      });
    }

    function renderDetail(scenario) {
      const detail = document.getElementById("detail");
      if (!scenario) {
        detail.innerHTML = `<div class="empty">Select a scenario.</div>`;
        return;
      }
      const boundary = scenario.objective_boundary || {};
      const anchor = boundary.evidence_anchor || {};
      const memory = scenario.memory_test_design || {};
      const related = scenario.related_facts || {};
      const real = scenario.real_data_anchor || {};
      detail.innerHTML = `
        <div class="detail-title">
          <div>
            <h2>${esc(scenario.title)}</h2>
            <div class="meta">
              <span>${esc(scenario.scenario_id)}</span>
              <span>${esc(scenario.track)}</span>
              <span>${esc(scenario.family)}</span>
              <span>${esc(scenario.domain)}</span>
              <span>${esc(scenario.split_candidate)}</span>
            </div>
          </div>
          <div class="badge-row">
            <span class="badge green">${esc(scenario.safety_level)}</span>
            <span class="badge amber">draft</span>
            <span class="badge">${esc((scenario.dialogue || []).length)} turns</span>
          </div>
        </div>
        <section class="section" style="margin-top: 12px;">
          <div class="section-head"><h3>Scenario Overview</h3></div>
          <div class="section-body grid">
            <div class="box"><h3>Description</h3><div class="text">${esc(scenario.scenario_description)}</div></div>
            <div class="box"><h3>Mainline</h3>${listItems(scenario.mainline)}</div>
            <div class="box"><h3>Real Data Anchor</h3>
              <div class="text">${esc(real.source_summary)}</div>
              <div class="tagline" style="margin-top: 8px;">${badges(real.pattern_ids, "purple")}</div>
            </div>
            <div class="box"><h3>Pattern Roles</h3>${listItems(real.pattern_roles)}</div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h3>Related Facts</h3></div>
          <div class="section-body grid">
            <div class="box objective"><h3>Verified facts</h3>${listItems(related.verified_facts)}</div>
            <div class="box"><h3>Missing or unverified</h3>${listItems(related.missing_or_unverified)}</div>
            <div class="box claim"><h3>Inference to resist</h3>${listItems(related.unsupported_inference_to_resist)}</div>
            <div class="box objective"><h3>Recovery fact check</h3><div class="text">${esc(related.recovery_fact_check)}</div></div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h3>Source Boundary</h3></div>
          <div class="section-body grid">
            <div class="box"><h3>Citation</h3><div class="text">${esc(real.citation)}</div></div>
            <div class="box"><h3>Use boundary</h3><div class="text">${esc(real.use_boundary)}</div></div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h3>Objective Boundary</h3></div>
          <div class="section-body grid">
            <div class="box objective"><h3>Evidence anchor</h3>${listItems(anchor.facts)}</div>
            <div class="box"><h3>Missing evidence</h3>${listItems(anchor.missing_evidence)}</div>
            <div class="box claim"><h3>Unsupported claim</h3><div class="text">${esc(boundary.unsupported_claim)}</div></div>
            <div class="box objective"><h3>Grounded stance</h3><div class="text">${esc(boundary.expected_grounded_stance)}</div></div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h3>Memory Test Design</h3></div>
          <div class="section-body grid">
            <div class="box memory"><h3>Expected failures</h3>${badges(memory.expected_memory_failures, "purple")}</div>
            <div class="box"><h3>Conditions</h3>${badges(memory.memory_conditions_to_test)}</div>
            <div class="box"><h3>Anchor turns</h3>${badges(memory.early_anchor_turn_ids, "green")}</div>
            <div class="box"><h3>Claim turns</h3>${badges(memory.unsupported_claim_turn_ids, "red")}</div>
          </div>
        </section>
        <section class="section">
          <div class="section-head"><h3>Dialogue</h3><span class="subtle small">target-visible user turns</span></div>
          <div class="section-body">
            ${(scenario.dialogue || []).map(renderTurn).join("")}
          </div>
        </section>
      `;
    }

    function renderTurn(turn) {
      const tags = turn.memory_probe_tags || [];
      return `
        <article class="turn">
          <div class="turn-head">
            <strong>${esc(turn.turn_id)}</strong>
            <div class="badge-row">
              <span class="badge">${esc(turn.pressure_type)}</span>
              ${turn.adds_new_evidence ? '<span class="badge red">new evidence</span>' : '<span class="badge green">no new evidence</span>'}
            </div>
          </div>
          <div class="turn-body">
            <div class="text">${esc(turn.user_prompt)}</div>
            <div class="tagline">${badges(tags, "purple")}</div>
            <div class="box"><h3>Expected model behavior</h3><div class="text">${esc(turn.expected_model_behavior)}</div></div>
          </div>
        </article>
      `;
    }

    init();
  </script>
</body>
</html>
"""


def build_html(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__DATA__", data)


def main() -> None:
    args = parse_args()
    data = load_yaml(args.input)
    errors = validate_dataset(data)
    if errors:
        raise SystemExit("scenario validation failed:\n" + "\n".join(errors))
    if args.validate_only:
        print(f"validation=ok scenarios={len(data['scenarios'])}")
        return

    payload = build_payload(data, args.input)
    html = build_html(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"wrote {args.out} scenarios={len(data['scenarios'])}")


if __name__ == "__main__":
    main()
