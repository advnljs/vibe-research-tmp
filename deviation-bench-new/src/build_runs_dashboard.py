#!/usr/bin/env python3
"""Build a local dashboard that dynamically reads release-hardening run results."""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "work" / "runs_dashboard"


def classify_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if path.parent.name == "reviews":
        return "review_result"
    if path.parent.name == "manifests" and "release" in path.name:
        return "release_manifest"
    if path.parent.name == "experiments":
        return "experiment_note"
    if path.parent.name == "processed":
        return "processed_summary"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "markdown"
    return "other"


def count_jsonl_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def json_summary(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(value, dict):
        return {}
    summary: dict[str, Any] = {}
    for key in ["run_id", "model", "provider", "generated_at", "dataset_version"]:
        if key in value:
            summary[key] = value[key]
    for key in ["totals", "counts"]:
        if isinstance(value.get(key), dict):
            summary[key] = value[key]
    for key in [
        "input_units",
        "candidate_units",
        "negative_control_units",
        "fingerprint_count",
        "pair_review_count",
    ]:
        if key in value:
            summary[key] = value[key]
    return summary


def discover_results(patterns: list[str]) -> list[dict[str, Any]]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(Path(match) for match in glob.glob(str(pattern)))
    rows = []
    seen: set[Path] = set()
    for path in sorted(paths):
        if not path.exists() or path.is_dir() or path in seen:
            continue
        seen.add(path)
        relative = path.relative_to(ROOT)
        item: dict[str, Any] = {
            "name": path.name,
            "kind": classify_path(path),
            "path": str(relative),
            "fetch_path": "/" + str(relative),
            "suffix": path.suffix.lower().lstrip("."),
            "size_bytes": path.stat().st_size,
        }
        if path.suffix == ".jsonl":
            item["rows"] = count_jsonl_rows(path)
        elif path.suffix == ".json":
            item["summary"] = json_summary(path)
        rows.append(item)
    return rows


def build_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deviation Bench New Runs</title>
<style>
:root{--bg:#f6f4ef;--panel:#fffdf8;--ink:#1f2420;--muted:#69706a;--line:#d8d3c8;--accent:#315c54;--soft:#e6eee8}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,sans-serif}
header{padding:18px 22px;background:var(--panel);border-bottom:1px solid var(--line)}
h1{font-size:22px;margin:0 0 4px}.muted{color:var(--muted)}
.layout{display:grid;grid-template-columns:360px minmax(0,1fr);min-height:calc(100vh - 76px)}
aside{padding:14px;border-right:1px solid var(--line);overflow:auto;max-height:calc(100vh - 76px)}
main{padding:18px 22px;overflow:auto;max-height:calc(100vh - 76px)}
input,select{width:100%;padding:9px 10px;border:1px solid var(--line);background:white;border-radius:6px;margin:0 0 10px}
.run{width:100%;display:block;text-align:left;border:1px solid var(--line);background:var(--panel);border-radius:7px;padding:10px;margin:0 0 8px;cursor:pointer}
.run.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.run strong{display:block}.run small{display:block;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:12px}.card b{display:block;font-size:20px}
pre{white-space:pre-wrap;word-break:break-word;background:#111;color:#f4f4f4;border-radius:7px;padding:14px;max-height:60vh;overflow:auto}
table{border-collapse:collapse;width:100%;background:var(--panel);border:1px solid var(--line);margin-top:12px}
th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top} th{background:var(--soft)}
.pill{display:inline-block;padding:2px 7px;border-radius:999px;background:var(--soft);font-size:12px;margin-right:4px}
@media(max-width:820px){.layout{grid-template-columns:1fr}aside,main{max-height:none}.layout aside{border-right:0;border-bottom:1px solid var(--line)}}
</style>
</head>
<body>
<header><h1>Deviation Bench New Runs</h1><div id="summary" class="muted">loading...</div></header>
<div class="layout">
<aside><input id="search" placeholder="Search run files"><select id="kind"></select><div id="runs"></div></aside>
<main id="detail"><p class="muted">Select a run result.</p></main>
</div>
<script>
const state={index:null,active:null};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function fmtBytes(n){if(n<1024)return `${n} B`; if(n<1048576)return `${(n/1024).toFixed(1)} KB`; return `${(n/1048576).toFixed(1)} MB`}
function matches(item){const q=$('search').value.trim().toLowerCase();const k=$('kind').value;return (!q||[item.name,item.kind,item.path].join(' ').toLowerCase().includes(q))&&(!k||item.kind===k)}
function renderList(){const rows=state.index.results.filter(matches);$('runs').innerHTML=rows.map(item=>`<button class="run ${state.active===item.path?'active':''}" data-path="${esc(item.path)}"><strong>${esc(item.name)}</strong><small>${esc(item.kind)} · ${esc(item.suffix)} · ${fmtBytes(item.size_bytes)}${item.rows?` · ${item.rows} rows`:''}</small></button>`).join('');document.querySelectorAll('.run').forEach(btn=>btn.onclick=()=>show(btn.dataset.path))}
function renderSummary(){const results=state.index.results;const kinds={};for(const item of results)kinds[item.kind]=(kinds[item.kind]||0)+1;$('summary').textContent=`${results.length} result files · ${Object.entries(kinds).map(([k,v])=>`${k}: ${v}`).join(' · ')}`;const opts=['',...Object.keys(kinds).sort()].map(k=>`<option value="${esc(k)}">${esc(k||'all kinds')}</option>`).join('');$('kind').innerHTML=opts}
function scalarCards(item){const cards=[['Kind',item.kind],['Type',item.suffix],['Size',fmtBytes(item.size_bytes)]];if(item.rows)cards.push(['Rows',item.rows]);const s=item.summary||{};for(const key of ['run_id','model','provider','dataset_version','input_units','candidate_units','negative_control_units','fingerprint_count','pair_review_count'])if(s[key]!==undefined)cards.push([key,s[key]]);return `<div class="cards">${cards.map(([k,v])=>`<div class="card"><span class="muted">${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}</div>`}
async function show(path){state.active=path;renderList();const item=state.index.results.find(x=>x.path===path);$('detail').innerHTML=`<h2>${esc(item.name)}</h2>${scalarCards(item)}<p class="muted">${esc(item.path)}</p><p>Loading file content...</p>`;const text=await fetch(item.fetch_path).then(r=>r.text());let body='';if(item.suffix==='json'){try{const obj=JSON.parse(text);body=`<pre>${esc(JSON.stringify(obj,null,2))}</pre>`}catch{body=`<pre>${esc(text)}</pre>`}}else if(item.suffix==='jsonl'){const lines=text.trim().split(/\\n+/).filter(Boolean);const parsed=lines.slice(0,100).map(line=>{try{return JSON.parse(line)}catch{return {raw:line}}});const keys=[...new Set(parsed.flatMap(obj=>Object.keys(obj).slice(0,12)))].slice(0,12);body=`<p class="muted">Showing first ${parsed.length} of ${lines.length} rows.</p><table><thead><tr>${keys.map(k=>`<th>${esc(k)}</th>`).join('')}</tr></thead><tbody>${parsed.map(obj=>`<tr>${keys.map(k=>`<td>${esc(typeof obj[k]==='object'?JSON.stringify(obj[k]):obj[k])}</td>`).join('')}</tr>`).join('')}</tbody></table>`}else{body=`<pre>${esc(text)}</pre>`}$('detail').innerHTML=`<h2>${esc(item.name)}</h2>${scalarCards(item)}<p class="muted">${esc(item.path)}</p>${body}`}
async function boot(){state.index=await fetch('runs_index.json').then(r=>r.json());renderSummary();renderList();if(state.index.results.length)show(state.index.results[0].path)}
$('search').oninput=renderList;$('kind').onchange=renderList;boot().catch(err=>{$('summary').textContent='failed';$('detail').innerHTML=`<pre>${esc(err.stack||err)}</pre>`});
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--pattern", action="append", default=[])
    args = parser.parse_args()
    patterns = args.pattern or [
        str(ROOT / "data" / "manifests" / "*release*.json*"),
        str(ROOT / "data" / "manifests" / "*point_review_units*.jsonl"),
        str(ROOT / "data" / "reviews" / "*.json"),
        str(ROOT / "data" / "reviews" / "*.jsonl"),
        str(ROOT / "data" / "reviews" / "*.md"),
        str(ROOT / "experiments" / "*.md"),
        str(ROOT / "data" / "processed" / "*summary.md"),
    ]
    results = discover_results(patterns)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "runs_index.json").write_text(
        json.dumps({"results": results}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "index.html").write_text(build_html(), encoding="utf-8")
    print(f"runs={len(results)} out={args.out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
