#!/usr/bin/env python3
"""Build a local static browser for processed Deviation Bench New sessions."""

from __future__ import annotations

import argparse
import glob
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "work" / "web" / "index.html"


def load_inputs(patterns: list[str]) -> list[dict[str, Any]]:
    paths = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        paths.extend(matches or [pattern])
    sessions = []
    seen = set()
    for value in paths:
        path = Path(value)
        if not path.exists() or path in seen:
            continue
        seen.add(path)
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    record = json.loads(line)
                    record["_input_file"] = path.name
                    sessions.append(record)
    return sessions


def build_html(sessions: list[dict[str, Any]]) -> str:
    payload = json.dumps(sessions, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deviation Bench New Dataset Browser</title>
<style>
:root{{--bg:#f4f1ea;--panel:#fffdf8;--ink:#20201d;--muted:#6b6961;--line:#d8d2c5;--accent:#5b4938;--user:#e8f0ea;--assistant:#eee9e0}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
header{{padding:20px 24px;background:var(--panel);border-bottom:1px solid var(--line)}} h1{{margin:0 0 6px;font-size:23px}} .muted{{color:var(--muted)}}
.layout{{display:grid;grid-template-columns:340px minmax(0,1fr);min-height:calc(100vh - 90px)}}
aside{{border-right:1px solid var(--line);padding:16px;overflow:auto;max-height:calc(100vh - 90px)}} main{{padding:22px;overflow:auto;max-height:calc(100vh - 90px)}}
input{{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:white;margin-bottom:12px}}
.item{{display:block;width:100%;text-align:left;padding:10px 11px;margin:0 0 8px;border:1px solid var(--line);border-radius:8px;background:var(--panel);cursor:pointer}}
.item.active{{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}} .item small{{display:block;color:var(--muted)}}
.meta,.points{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:16px}} .meta-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}}
.message{{max-width:880px;padding:11px 13px;margin:8px 0;border-radius:10px;border:1px solid var(--line)}} .message.user{{margin-left:auto;background:var(--user)}} .message.assistant{{background:var(--assistant)}}
.role{{font-size:12px;text-transform:uppercase;color:var(--muted);margin-bottom:3px}} .point{{border-top:1px solid var(--line);padding:10px 0}} .point:first-child{{border-top:0}}
.badge{{display:inline-block;padding:2px 7px;border-radius:999px;background:#e7dfd3;margin-right:5px;font-size:12px}}
@media(max-width:800px){{.layout{{grid-template-columns:1fr}} aside{{max-height:300px;border-right:0;border-bottom:1px solid var(--line)}} main{{max-height:none}}}}
</style>
</head>
<body>
<header><h1>Deviation Bench New Dataset Browser</h1><div id="summary" class="muted"></div></header>
<div class="layout"><aside><input id="search" placeholder="搜索 session / source / category"><div id="list"></div></aside><main id="detail"><p class="muted">选择一个 session。</p></main></div>
<script>
const sessions={payload};
const list=document.getElementById('list'),detail=document.getElementById('detail'),search=document.getElementById('search');
let active=null;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
document.getElementById('summary').textContent=`${{sessions.length}} sessions · ${{sessions.reduce((n,s)=>n+(s.messages||[]).length,0)}} messages · ${{sessions.reduce((n,s)=>n+(s.delusion_points||[]).length,0)}} candidate points`;
function haystack(s){{return [s.session_id,s.metadata?.source_dataset,s.metadata?.source_group,...(s.delusion_points||[]).map(p=>p.category)].join(' ').toLowerCase()}}
function renderList(){{const q=search.value.trim().toLowerCase();const rows=sessions.filter(s=>!q||haystack(s).includes(q));list.innerHTML=rows.map(s=>`<button class="item ${{active===s.session_id?'active':''}}" data-id="${{esc(s.session_id)}}"><strong>${{esc(s.session_id)}}</strong><small>${{esc(s.metadata?.source_group)}} · ${{(s.messages||[]).length}} messages · ${{(s.delusion_points||[]).length}} points</small></button>`).join('');list.querySelectorAll('button').forEach(b=>b.onclick=()=>show(b.dataset.id))}}
function show(id){{active=id;const s=sessions.find(x=>x.session_id===id);if(!s)return;renderList();const points=(s.delusion_points||[]).length?(s.delusion_points||[]).map(p=>`<div class="point"><span class="badge">${{esc(p.category)}}</span><span class="badge">${{esc(p.explicitness)}}</span><span class="badge">confidence ${{esc(p.confidence)}}</span><p>${{esc(p.summary)}}</p><small class="muted">messages ${{esc((p.message_indices||[]).join(', '))}} · ${{esc(p.uncertainty_or_counterevidence)}}</small></div>`).join(''):`<p class="muted">No candidate point. ${{esc(s.no_delusion_point_reason)}}</p>`;detail.innerHTML=`<h2>${{esc(s.session_id)}}</h2><section class="meta"><div class="meta-grid"><div><b>Source</b><br>${{esc(s.metadata?.source_dataset)}}</div><div><b>Group</b><br>${{esc(s.metadata?.source_group)}}</div><div><b>Model</b><br>${{esc(s.provenance?.transform_model)}}</div><div><b>QC</b><br>${{esc(s.quality?.status)}}</div></div><p>${{esc(s.case_summary)}}</p><small class="muted">${{esc(s.metadata?.label_interpretation)}}</small></section><section class="points"><h3>Candidate delusion/reality-boundary points</h3>${{points}}</section><section><h3>Messages</h3>${{(s.messages||[]).map((m,i)=>`<div class="message ${{esc(m.role)}}"><div class="role">${{i}} · ${{esc(m.role)}}</div>${{esc(m.content)}}</div>`).join('')}}</section>`}}
search.oninput=renderList;renderList();if(sessions.length)show(sessions[0].session_id);
</script>
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="JSONL path or glob; repeatable.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    patterns = args.input or [str(ROOT / "data" / "processed" / "*.jsonl")]
    sessions = load_inputs(patterns)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_html(sessions), encoding="utf-8")
    print(f"sessions={len(sessions)} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
