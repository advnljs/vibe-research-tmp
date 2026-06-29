#!/usr/bin/env python3
"""Build a local review dashboard with conversations and release-hardening charts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "work" / "review_dashboard" / "index.html"


def dashboard_fetch_paths() -> dict[str, object]:
    return {
        "processed": [
            "/data/processed/deepseek_v4_pro_interview_sessions_64k.jsonl",
            "/data/processed/deepseek_v4_pro_control_sessions_64k.jsonl",
            "/data/processed/deepseek_v4_pro_reddit_sessions_64k.jsonl",
        ],
        "reviewedSplits": "/data/manifests/deepseek_v4_pro_release_splits_reviewed_64k.jsonl",
        "reviewedAudit": "/data/manifests/deepseek_v4_pro_release_audit_reviewed_64k.json",
        "pointReviews": "/data/reviews/deepseek_v4_pro_point_metajudge_64k.jsonl",
        "pointSummary": "/data/reviews/deepseek_v4_pro_point_metajudge_64k_summary.json",
        "fingerprints": "/data/reviews/deepseek_v4_pro_session_semantic_fingerprints_64k.jsonl",
        "duplicatePairs": "/data/reviews/deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl",
        "duplicateSummary": "/data/reviews/deepseek_v4_pro_semantic_duplicate_audit_64k_summary.json",
        "narratives": "/data/reviews/deepseek_v4_pro_review_narratives_64k.json",
        "experimentNotes": {
            "dataPreparation": "/experiments/real_data_session_preparation_2026-06-22.md",
            "preAudit": "/experiments/session_release_hardening_pre_audit_2026-06-29.md",
            "actualFlow": "/experiments/session_release_hardening_actual_flow_2026-06-29.md",
        },
    }


def build_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deviation Bench New Review Dashboard</title>
<style>
:root{
  --bg:#f4f6f7;--panel:#ffffff;--ink:#1f272a;--muted:#647176;--line:#d7dee2;
  --accent:#2f6f72;--accent-2:#76577c;--warn:#a36126;--bad:#a13f43;--ok:#34784b;
  --user:#e4f0ec;--assistant:#eef1f3;--soft:#edf2f3;--shadow:0 1px 2px rgba(31,39,42,.08)
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.48 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
button,input,select{font:inherit}
header{position:sticky;top:0;z-index:4;background:var(--panel);border-bottom:1px solid var(--line);padding:14px 18px;box-shadow:var(--shadow)}
.topline{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;flex-wrap:wrap}
h1{margin:0;font-size:20px;line-height:1.2;letter-spacing:0}.subtle{color:var(--muted);font-size:13px}
.tabs{display:flex;gap:6px;align-items:center}
.tab{border:1px solid var(--line);background:white;color:var(--ink);padding:7px 10px;border-radius:6px;cursor:pointer;min-width:86px}
.tab.active{border-color:var(--accent);background:#e1f0ef;color:#173f3f}
.metric-grid{display:grid;grid-template-columns:repeat(6,minmax(130px,1fr));gap:9px;margin-top:12px}
.metric{background:white;border:1px solid var(--line);border-radius:7px;padding:9px 10px;min-height:68px}
.metric span{display:block;color:var(--muted);font-size:12px}.metric b{display:block;font-size:22px;line-height:1.2;margin-top:4px}
.main{display:grid;grid-template-columns:370px minmax(0,1fr);min-height:calc(100vh - 156px)}
aside{border-right:1px solid var(--line);background:#fafbfc;padding:12px;overflow:auto;max-height:calc(100vh - 156px)}
main{padding:16px;overflow:auto;max-height:calc(100vh - 156px)}
.filters{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.filters input,.filters select{width:100%;border:1px solid var(--line);border-radius:6px;background:white;padding:8px 9px;min-width:0}
.filters input{grid-column:1/-1}
.session-list{display:flex;flex-direction:column;gap:7px}
.session-item{width:100%;text-align:left;background:white;border:1px solid var(--line);border-radius:7px;padding:9px 10px;cursor:pointer}
.session-item.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.session-item strong{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.session-item small{display:block;color:var(--muted);margin-top:2px}
.badges{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}
.badge{display:inline-block;border-radius:999px;background:var(--soft);padding:2px 7px;font-size:12px;line-height:1.4}
.badge.ok{background:#dfeee4;color:#17472b}.badge.warn{background:#f2e5d8;color:#704015}.badge.bad{background:#f2dddd;color:#6f2020}.badge.purple{background:#eadfec;color:#52335b}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:13px;margin-bottom:12px;box-shadow:var(--shadow)}
.panel h2,.panel h3{margin:0 0 10px;letter-spacing:0}.panel h2{font-size:20px}.panel h3{font-size:15px}
.overview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.result-grid{display:grid;grid-template-columns:repeat(4,minmax(190px,1fr));gap:10px;margin-bottom:12px}
.result-card{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:12px;box-shadow:var(--shadow)}
.result-card h3{margin:0 0 8px;font-size:14px}.result-card .value{font-size:24px;font-weight:700;line-height:1.1}
.result-card .note{display:block;color:var(--muted);font-size:12px;margin-top:4px}
.status-strip{display:grid;grid-template-columns:repeat(3,minmax(190px,1fr));gap:10px;margin-bottom:12px}
.status-item{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:10px 12px;display:flex;gap:8px;align-items:flex-start}
.status-icon{display:inline-block;width:13px;height:13px;border-radius:50%;margin-top:4px;margin-right:6px;flex:0 0 13px;background:var(--muted)}
.status-icon.ok{background:var(--ok)}.status-icon.warn{background:var(--warn)}.status-icon.bad{background:var(--bad)}.status-icon.info{background:var(--accent)}
.status-item b{display:block}.status-item span:last-child{color:var(--muted);font-size:12px}
.artifact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px}
.artifact{display:block;border:1px solid var(--line);border-radius:6px;background:white;padding:8px;text-decoration:none;color:var(--ink)}
.artifact small{display:block;color:var(--muted);margin-top:2px}
.narrative{border-left:4px solid var(--accent);background:#fbfdfd}.narrative p{margin:7px 0}
.narrative ul{margin:8px 0 0 18px;padding:0}.narrative li{margin:4px 0}
.chart-note-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:8px}
.chart-note{border:1px solid var(--line);background:white;border-radius:6px;padding:9px}.chart-note b{display:block;margin-bottom:4px}
.chart{min-height:220px}.bars{display:grid;gap:7px}
.bar-row{display:grid;grid-template-columns:minmax(120px,190px) minmax(0,1fr) 54px;gap:8px;align-items:center}
.bar-label{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#323832}
.bar-track{height:16px;background:#e6ebee;border-radius:999px;overflow:hidden}.bar-fill{height:100%;border-radius:999px;background:var(--accent)}
.bar-value{text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}
.detail-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(330px,.85fr);gap:12px}
.meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}
.meta-cell{border:1px solid var(--line);border-radius:6px;background:white;padding:8px}.meta-cell span{display:block;color:var(--muted);font-size:12px}
.conversation{display:flex;flex-direction:column;gap:8px}
.message{border:1px solid var(--line);border-radius:7px;padding:9px 10px;max-width:920px}
.message.user{align-self:flex-end;background:var(--user);margin-left:38px}.message.assistant{align-self:flex-start;background:var(--assistant);margin-right:38px}
.message-head{display:flex;gap:8px;color:var(--muted);font-size:12px;text-transform:uppercase;margin-bottom:3px}
.point{border-top:1px solid var(--line);padding:10px 0}.point:first-child{border-top:0;padding-top:0}
.point p{margin:6px 0}.rationale{color:#4b565a;background:#f1f4f5;border-radius:6px;padding:8px;margin-top:7px}
.fingerprint-list,.pair-table{font-size:13px}.fingerprint-list div{margin:5px 0}
table{width:100%;border-collapse:collapse;background:white;border:1px solid var(--line);font-size:13px}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:7px 8px}th{background:#eceeea;color:#303730}
table.heatmap th,table.heatmap td{text-align:center;white-space:nowrap}table.heatmap th:first-child,table.heatmap td:first-child{text-align:left}
pre{white-space:pre-wrap;word-break:break-word;background:#f8fafb;border:1px solid var(--line);border-radius:7px;padding:12px;max-height:360px;overflow:auto}
.hidden{display:none!important}
.empty{color:var(--muted);padding:14px;border:1px dashed var(--line);border-radius:7px;background:white}
@media(max-width:1080px){.metric-grid{grid-template-columns:repeat(3,minmax(130px,1fr))}.main{grid-template-columns:1fr}aside,main{max-height:none}aside{border-right:0;border-bottom:1px solid var(--line)}.detail-grid,.overview-grid,.result-grid,.status-strip{grid-template-columns:1fr}}
@media(max-width:640px){.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.filters{grid-template-columns:1fr}.tab{min-width:0;flex:1}.message.user,.message.assistant{margin-left:0;margin-right:0}}
</style>
</head>
<body>
<header>
  <div class="topline">
    <div><h1>Deviation Bench New Review Dashboard</h1><div id="loadStatus" class="subtle">loading</div></div>
    <nav class="tabs">
      <button class="tab active" data-view="overview">Overview</button>
      <button class="tab" data-view="results">Results</button>
      <button class="tab" data-view="delusion">Delusion</button>
      <button class="tab" data-view="sessions">Sessions</button>
      <button class="tab" data-view="duplicates">Duplicates</button>
    </nav>
  </div>
  <section id="metrics" class="metric-grid"></section>
</header>
<div class="main">
  <aside>
    <div class="filters">
      <input id="search" placeholder="Search session, category, summary">
      <select id="sourceFilter"></select>
      <select id="splitFilter"></select>
      <select id="decisionFilter"></select>
      <select id="riskFilter"></select>
    </div>
    <div id="sessionCount" class="subtle"></div>
    <div id="sessionList" class="session-list"></div>
  </aside>
  <main>
    <section id="overviewView"></section>
    <section id="resultsView" class="hidden"></section>
    <section id="delusionView" class="hidden"></section>
    <section id="sessionsView" class="hidden"></section>
    <section id="duplicatesView" class="hidden"></section>
  </main>
</div>
<script>
const paths = __PATHS__;
const state = {sessions:[], splits:new Map(), reviews:new Map(), negatives:new Map(), fingerprints:new Map(), pairs:[], pairsBySession:new Map(), audit:null, pointSummary:null, duplicateSummary:null, narrative:null, notes:{}, active:null, view:'overview'};
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = n => Number.isFinite(n) ? n.toLocaleString('en-US') : String(n ?? '');
async function fetchText(path){const response=await fetch(path); if(!response.ok) throw new Error(`${path} ${response.status}`); return response.text()}
async function fetchJSON(path){return JSON.parse(await fetchText(path))}
async function fetchOptionalJSON(path){try{return await fetchJSON(path)}catch(error){console.warn('optional narrative unavailable', error); return null}}
async function fetchJSONL(path){const text=await fetchText(path); return text.trim().split(/\\n+/).filter(Boolean).map(line=>JSON.parse(line))}
function countBy(rows, fn){const out={}; for(const row of rows){const key=String(fn(row) ?? 'unknown'); out[key]=(out[key]||0)+1} return out}
function groupBy(rows, fn){const out=new Map(); for(const row of rows){const key=String(fn(row) ?? 'unknown'); if(!out.has(key)) out.set(key, []); out.get(key).push(row)} return out}
function maxValue(data){return Math.max(1,...Object.values(data).map(Number))}
function barChart(title, data, color='var(--accent)'){
  const entries=Object.entries(data).sort((a,b)=>b[1]-a[1]);
  const max=maxValue(data);
  const rows=entries.map(([label,value])=>`<div class="bar-row"><div class="bar-label" title="${esc(label)}">${esc(label)}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(2,value/max*100)}%;background:${color}"></div></div><div class="bar-value">${fmt(value)}</div></div>`).join('');
  return `<section class="panel chart"><h3>${esc(title)}</h3><div class="bars">${rows||'<div class="empty">No data</div>'}</div></section>`;
}
function heatmapChart(title, rows, rowFn, colFn){
  const rowKeys=[...new Set(rows.map(row=>String(rowFn(row)||'unknown')))].sort();
  const colKeys=[...new Set(rows.map(row=>String(colFn(row)||'unknown')))].sort();
  const counts=new Map();
  for(const row of rows){
    const key=`${String(rowFn(row)||'unknown')}::${String(colFn(row)||'unknown')}`;
    counts.set(key,(counts.get(key)||0)+1);
  }
  const max=Math.max(1,...counts.values());
  const body=rowKeys.map(rowKey=>`<tr><td>${esc(rowKey)}</td>${colKeys.map(colKey=>{
    const value=counts.get(`${rowKey}::${colKey}`)||0;
    const alpha=value?Math.max(.12,value/max*.82):0;
    return `<td style="background:${value?`rgba(47,111,114,${alpha})`:'transparent'}">${value?fmt(value):''}</td>`;
  }).join('')}</tr>`).join('');
  return `<section class="panel"><h3>${esc(title)}</h3><table class="heatmap"><thead><tr><th></th>${colKeys.map(key=>`<th>${esc(key)}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></section>`;
}
function metric(label, value, note=''){return `<div class="metric"><span>${esc(label)}</span><b>${esc(value)}</b>${note?`<span>${esc(note)}</span>`:''}</div>`}
function pct(value){return Number.isFinite(value) ? `${(value*100).toFixed(1)}%` : 'n/a'}
function sumValues(data){return Object.values(data||{}).reduce((n,v)=>n+(Number(v)||0),0)}
function resultCard(title, value, note='', status='info'){
  return `<article class="result-card"><h3><span class="status-icon ${status}"></span>${esc(title)}</h3><div class="value">${esc(value)}</div>${note?`<span class="note">${esc(note)}</span>`:''}</article>`;
}
function statusItem(title, note, status='info'){
  return `<div class="status-item"><span class="status-icon ${status}"></span><div><b>${esc(title)}</b><span>${esc(note)}</span></div></div>`;
}
function artifactLink(label, path, note){
  return `<a class="artifact" href="${esc(path)}" target="_blank" rel="noreferrer"><b>${esc(label)}</b><small>${esc(note)} · ${esc(path)}</small></a>`;
}
function markdownPreview(text, max=1400){
  const trimmed=String(text||'').trim();
  return esc(trimmed.length>max ? `${trimmed.slice(0,max)}...` : trimmed);
}
function narrativeSection(section, fallbackTitle, fallbackParagraphs=[]){
  const data=section||{};
  const title=data.title||fallbackTitle;
  const paragraphs=(data.paragraphs&&data.paragraphs.length?data.paragraphs:fallbackParagraphs);
  const bullets=data.bullets||[];
  const cautions=data.cautions||[];
  return `<section class="panel narrative"><h3>${esc(title)}</h3>${paragraphs.map(text=>`<p>${esc(text)}</p>`).join('')}${bullets.length?`<ul>${bullets.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}${cautions.length?`<ul>${cautions.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}</section>`;
}
function chartNarratives(targets){
  const aliases={
    'Candidate Categories':['Candidate Categories','delusion_signal_distribution.category'],
    'Metajudge Decision × Candidate Category':['Metajudge Decision × Candidate Category','metajudge.decision_counts'],
    'Source Family × Candidate Category':['Source Family × Candidate Category','delusion_signal_distribution.source_family'],
    'Actual Point Metajudge Decisions':['Actual Point Metajudge Decisions','metajudge.decision_counts'],
    'Reviewed Release Split':['Reviewed Release Split','release.reviewed_counts.release_split']
  };
  const rows=(state.narrative?.narrative?.charts||[]).filter(item=>targets.some(target=>(aliases[target]||[target]).includes(item.target)));
  if(!rows.length) return '';
  return `<section class="panel"><h3>Chart Reading Notes</h3><div class="chart-note-grid">${rows.map(item=>`<div class="chart-note"><b>${esc(item.target)}</b><span>${esc(item.explanation)}</span></div>`).join('')}</div></section>`;
}
function shortText(text, max=160){
  const value=String(text||'').replace(/\s+/g,' ').trim();
  return value.length>max ? `${value.slice(0,max)}...` : value;
}
function openSessionButton(id){return `<button class="tab" data-jump="${esc(id)}">${esc(id)}</button>`}
function badge(text, kind=''){return `<span class="badge ${kind}">${esc(text)}</span>`}
function releaseBadge(row){if(!row)return ''; if(row.release_status==='excluded_duplicate_candidate')return badge('excluded','bad'); if(row.release_action?.startsWith('move'))return badge('moved','warn'); return badge(row.release_split,'ok')}
function reviewKind(decision){if(decision==='accept_candidate'||decision==='accept_no_candidate_point')return 'ok'; if(decision==='revise_candidate'||decision==='flag_possible_missed_candidate'||decision==='unclear')return 'warn'; if(decision==='reject_insufficient_evidence')return 'bad'; return ''}
function riskKind(risk){if(risk==='high')return 'bad'; if(risk==='medium')return 'warn'; if(risk==='low')return 'purple'; return 'ok'}
function hydrateIndexes(){
  for(const row of state.splits.values()){const session=state.sessionsById.get(row.session_id); if(session) session.release=row}
  for(const row of state.pointReviews){
    if(row.unit_type==='negative_control') state.negatives.set(row.session_id,row);
    else {if(!state.reviews.has(row.session_id)) state.reviews.set(row.session_id,[]); state.reviews.get(row.session_id).push(row)}
  }
  for(const row of state.fingerprintRows) state.fingerprints.set(row.session_id,row);
  for(const pair of state.pairs){
    for(const id of [pair.left_session_id,pair.right_session_id]){
      if(!state.pairsBySession.has(id)) state.pairsBySession.set(id,[]);
      state.pairsBySession.get(id).push(pair);
    }
  }
}
function renderMetrics(){
  const included=[...state.splits.values()].filter(r=>r.release_status==='included').length;
  const excluded=[...state.splits.values()].filter(r=>r.release_status!=='included').length;
  const messages=state.sessions.reduce((n,s)=>n+(s.messages||[]).length,0);
  const points=state.sessions.reduce((n,s)=>n+(s.delusion_points||[]).length,0);
  const reviews=countBy(state.pointReviews,r=>r.decision);
  const mediumHigh=state.pairs.filter(p=>p.leakage_risk==='medium'||p.leakage_risk==='high').length;
  $('metrics').innerHTML=[
    metric('Sessions', fmt(state.sessions.length), `${fmt(messages)} messages`),
    metric('Included', fmt(included), `${fmt(excluded)} excluded`),
    metric('Candidate Points', fmt(points), `${fmt(reviews.accept_candidate||0)} accepted`),
    metric('Revise / Reject', fmt((reviews.revise_candidate||0)+(reviews.reject_insufficient_evidence||0)), 'metajudge'),
    metric('Duplicate Pairs', fmt((countBy(state.pairs,p=>p.decision).duplicate)||0), `${fmt((countBy(state.pairs,p=>p.decision).near_duplicate)||0)} near`),
    metric('Leakage Risk', fmt(mediumHigh), 'medium/high pairs')
  ].join('');
}
function renderFilters(){
  const source=countBy([...state.splits.values()], r=>r.source_family);
  const split=countBy([...state.splits.values()], r=>r.release_split);
  const decisions=countBy(state.pointReviews, r=>r.decision);
  const risk=countBy(state.pairs, r=>r.leakage_risk);
  const option=(value,label=value)=>`<option value="${esc(value)}">${esc(label)}</option>`;
  $('sourceFilter').innerHTML=option('','all sources')+Object.keys(source).sort().map(v=>option(v)).join('');
  $('splitFilter').innerHTML=option('','all splits')+Object.keys(split).sort().map(v=>option(v)).join('');
  $('decisionFilter').innerHTML=option('','all decisions')+Object.keys(decisions).sort().map(v=>option(v)).join('');
  $('riskFilter').innerHTML=option('','all risks')+Object.keys(risk).sort().map(v=>option(v)).join('');
}
function sessionHaystack(session){
  const points=(session.delusion_points||[]).flatMap(p=>[p.category,p.summary,p.uncertainty_or_counterevidence]).join(' ');
  const fp=state.fingerprints.get(session.session_id);
  return [session.session_id, session.case_summary, session.metadata?.source_group, session.release?.release_split, points, fp?.semantic_signature].join(' ').toLowerCase();
}
function sessionMatches(session){
  const q=$('search').value.trim().toLowerCase();
  const source=$('sourceFilter').value, split=$('splitFilter').value, decision=$('decisionFilter').value, risk=$('riskFilter').value;
  if(q && !sessionHaystack(session).includes(q)) return false;
  if(source && session.release?.source_family!==source) return false;
  if(split && session.release?.release_split!==split) return false;
  if(decision && !(state.reviews.get(session.session_id)||[]).some(r=>r.decision===decision) && state.negatives.get(session.session_id)?.decision!==decision) return false;
  if(risk && !(state.pairsBySession.get(session.session_id)||[]).some(p=>p.leakage_risk===risk)) return false;
  return true;
}
function renderSessionList(){
  const rows=state.sessions.filter(sessionMatches);
  $('sessionCount').textContent=`${fmt(rows.length)} sessions`;
  $('sessionList').innerHTML=rows.slice(0,500).map(s=>{
    const r=s.release||{}; const reviews=state.reviews.get(s.session_id)||[]; const pairs=state.pairsBySession.get(s.session_id)||[];
    return `<button class="session-item ${state.active===s.session_id?'active':''}" data-id="${esc(s.session_id)}"><strong>${esc(s.session_id)}</strong><small>${esc(r.source_family||s.metadata?.source_group)} · ${esc(r.release_split||'unreviewed')} · ${(s.messages||[]).length} msgs · ${(s.delusion_points||[]).length} pts</small><div class="badges">${releaseBadge(r)}${reviews.slice(0,2).map(x=>badge(x.decision,reviewKind(x.decision))).join('')}${pairs.some(p=>p.leakage_risk==='high')?badge('high risk','bad'):pairs.length?badge(`${pairs.length} pairs`,'purple'):''}</div></button>`;
  }).join('') || '<div class="empty">No matching sessions</div>';
  document.querySelectorAll('.session-item').forEach(btn=>btn.onclick=()=>showSession(btn.dataset.id));
}
function renderOverview(){
  const split=countBy([...state.splits.values()],r=>r.release_split);
  const source=countBy([...state.splits.values()],r=>r.source_family);
  const categories=countBy(state.sessions.flatMap(s=>s.delusion_points||[]),p=>p.category);
  const decisions=countBy(state.pointReviews,r=>r.decision);
  const pairDecisions=countBy(state.pairs,p=>p.decision);
  const pairRisk=countBy(state.pairs,p=>p.leakage_risk);
  const rare=countBy(state.fingerprintRows,r=>r.rare_event_chain_risk);
  $('overviewView').innerHTML=`<div class="overview-grid">${barChart('Reviewed Release Split',split,'var(--accent)')}${barChart('Source Family',source,'var(--accent-2)')}${barChart('Point Categories',categories,'var(--warn)')}${barChart('Metajudge Decisions',decisions,'var(--ok)')}${barChart('Duplicate Pair Decisions',pairDecisions,'var(--bad)')}${barChart('Leakage Risk',pairRisk,'var(--accent-2)')}${barChart('Rare Event Chain Risk',rare,'var(--warn)')}</div>`;
}
function renderResults(){
  const audit=state.audit||{};
  const pre=audit.pre_audit||{};
  const preTotals=pre.totals||{};
  const preCounts=pre.counts||{};
  const point=audit.point_metajudge||state.pointSummary||{};
  const pointCounts=point.counts||{};
  const semantic=audit.semantic_duplicate_audit||state.duplicateSummary||{};
  const semanticCounts=semantic.counts||{};
  const reviewed=audit.reviewed_totals||{};
  const reviewedCounts=audit.reviewed_counts||{};
  const pairDecisions=semanticCounts.pair_decision||countBy(state.pairs,p=>p.decision);
  const pairReviews=sumValues(pairDecisions)||state.pairs.length;
  const validationErrors=preTotals.validation_errors||0;
  const governanceOpen=(audit.release_notes||[]).some(note=>String(note).toLowerCase().includes('governance'));
  const narrative=narrativeSection(
    state.narrative?.narrative?.overall,
    '实际结果说明',
    [`当前页面从 ${fmt(preTotals.sessions||state.sessions.length)} 个 session、${fmt(preTotals.messages||0)} 条 message 和 ${fmt(preTotals.delusion_points||0)} 个候选点动态聚合统计。Reviewed split 和 metajudge 结果已经加载，但公开发布前仍需要治理审查。`]
  );
  const cards=[
    resultCard('Data sessions', fmt(preTotals.sessions||state.sessions.length), `${fmt(preTotals.messages||0)} messages · ${fmt(preTotals.delusion_points||0)} candidate points`, validationErrors===0?'ok':'bad'),
    resultCard('Point metajudge', fmt(point.input_units||state.pointReviews.length), `${fmt(point.candidate_units||0)} candidates · accept ${pct(point.candidate_acceptance_rate)}`, 'ok'),
    resultCard('Negative controls', fmt(point.negative_control_units||0), `flag rate ${pct(point.negative_control_flag_rate)}`, (point.negative_control_flag_rate||0)===0?'ok':'warn'),
    resultCard('Duplicate review', fmt(pairReviews), `${fmt(pairDecisions.duplicate||0)} duplicate · ${fmt(pairDecisions.near_duplicate||0)} near`, (pairDecisions.duplicate||0)>0?'warn':'ok'),
    resultCard('Release included', fmt(reviewed.included_sessions||0), `${fmt(reviewed.excluded_duplicate_candidates||0)} excluded duplicate candidates`, 'ok'),
    resultCard('Same-split moves', fmt(reviewed.same_split_moved_sessions||0), `${fmt(reviewed.semantic_pair_decisions_applied||0)} pair decisions applied`, 'warn'),
    resultCard('PII risk flags', fmt(point.identifying_detail_risk_count||0), 'from point metajudge summary', (point.identifying_detail_risk_count||0)===0?'ok':'bad'),
    resultCard('Governance status', governanceOpen?'pending':'not flagged', 'license/privacy/governance review before public release', governanceOpen?'warn':'info')
  ].join('');
  const statuses=[
    statusItem('Actual flow completed', `${point.model||'deepseek-v4-pro'} point metajudge and semantic duplicate review outputs are loaded.`, 'ok'),
    statusItem('Contract validation passed', `${fmt(validationErrors)} validation errors in reviewed audit pre-check.`, validationErrors===0?'ok':'bad'),
    statusItem('Release still gated', 'Reviewed splits are ready for downstream task design, but public release still needs governance review.', 'warn')
  ].join('');
  const artifacts=[
    artifactLink('Actual flow experiment note', paths.experimentNotes.actualFlow, 'tracked markdown'),
    artifactLink('Reviewed audit JSON', paths.reviewedAudit, 'final aggregate result'),
    artifactLink('Reviewed split manifest', paths.reviewedSplits, 'session-level release split decisions'),
    artifactLink('Point metajudge summary', paths.pointSummary, 'actual DeepSeek Pro review summary'),
    artifactLink('Point metajudge JSONL', paths.pointReviews, '1,420 review-unit records'),
    artifactLink('Duplicate audit summary', paths.duplicateSummary, 'semantic duplicate/leakage result summary'),
    artifactLink('Duplicate pair JSONL', paths.duplicatePairs, '240 pair-review records'),
    artifactLink('Semantic fingerprints JSONL', paths.fingerprints, '968 session fingerprints'),
    artifactLink('LLM narrative JSON', paths.narratives, 'Chinese dashboard explanations generated from aggregate stats')
  ].join('');
  const actualNote=state.notes.actualFlow||'';
  $('resultsView').innerHTML=`${narrative}<section class="status-strip">${statuses}</section><section class="result-grid">${cards}</section><div class="overview-grid">${barChart('Actual Point Metajudge Decisions',pointCounts.decision||{},'var(--ok)')}${barChart('Point Review Source Families',pointCounts.source_family||{},'var(--accent-2)')}${barChart('Reviewed Release Split',reviewedCounts.release_split||{},'var(--accent)')}${barChart('Release Actions Applied',reviewedCounts.release_action||{},'var(--warn)')}${barChart('Semantic Pair Decisions',pairDecisions,'var(--bad)')}${barChart('Leakage Risk',semanticCounts.pair_leakage_risk||{},'var(--accent-2)')}${barChart('Source Specificity Risk',semanticCounts.source_specificity_risk||{},'var(--warn)')}${barChart('Preparation Point Categories',preCounts.points_by_category||{},'var(--accent)')}</div>${chartNarratives(['Actual Point Metajudge Decisions','Reviewed Release Split'])}<section class="panel"><h3>Result Artifacts</h3><div class="artifact-grid">${artifacts}</div></section><section class="panel"><h3>Actual Flow Note Preview</h3><pre>${markdownPreview(actualNote)}</pre></section>`;
}
function renderDelusion(){
  const rows=allPointRows();
  const acceptedRows=rows.filter(acceptedOrRevised);
  const rejectedRows=rows.filter(row=>pointDecision(row)==='reject_insufficient_evidence');
  const overreachRows=rows.filter(row=>row.review?.summary_overreach);
  const diagnosisRows=rows.filter(row=>row.review?.diagnosis_or_membership_inference);
  const implicitRows=rows.filter(row=>row.point.explicitness==='implicit');
  const highConfidenceRows=rows.filter(row=>Number(row.point.confidence)>=0.9);
  const sessionsWithPoints=new Set(rows.map(row=>row.session.session_id));
  const acceptedSessions=new Set(acceptedRows.map(row=>row.session.session_id));
  const noPointSessions=state.sessions.filter(session=>(session.delusion_points||[]).length===0);
  const narrative=narrativeSection(
    state.narrative?.narrative?.delusion,
    'Delusion / reality-boundary 指标说明',
    [`这里的 ${fmt(rows.length)} 个候选信号来自一阶 LLM 抽取，随后由 metajudge 区分 accept、revise 和 reject。当前有 ${fmt(acceptedRows.length)} 个候选被接受或修订，${fmt(rejectedRows.length)} 个候选被拒绝，${fmt(noPointSessions.length)} 个 session 保持空候选列表。`]
  );
  const cards=[
    resultCard('Candidate signals', fmt(rows.length), `${fmt(sessionsWithPoints.size)} sessions with at least one candidate`, 'info'),
    resultCard('Accepted / revised', fmt(acceptedRows.length), `${fmt(acceptedSessions.size)} sessions retain a metajudge-supported signal`, 'ok'),
    resultCard('Rejected candidates', fmt(rejectedRows.length), `${fmt(overreachRows.length)} summary-overreach flags`, rejectedRows.length?'warn':'ok'),
    resultCard('No-point sessions', fmt(noPointSessions.length), `${fmt(countBy(noPointSessions,s=>s.release?.source_family||s.metadata?.source_group).dais_c_control_calibration||0)} controls plus no-signal interviews`, 'info'),
    resultCard('Implicit signals', fmt(implicitRows.length), `${pct(implicitRows.length/Math.max(1,rows.length))} of candidate points`, implicitRows.length?'warn':'ok'),
    resultCard('High confidence', fmt(highConfidenceRows.length), `candidate confidence >= 0.90 before metajudge`, 'info'),
    resultCard('Weak/none support', fmt(rows.filter(row=>row.review?.support_level==='weak_or_none').length), 'metajudge support level', 'warn'),
    resultCard('Diagnosis/member flags', fmt(diagnosisRows.length), 'candidate may infer from group/diagnosis rather than message evidence', diagnosisRows.length?'warn':'ok')
  ].join('');
  const charts=[
    barChart('Candidate Categories', countPointRows(rows,row=>row.point.category),'var(--accent)'),
    barChart('Accepted/Revised Categories', countPointRows(acceptedRows,row=>row.point.category),'var(--ok)'),
    barChart('Rejected Categories', countPointRows(rejectedRows,row=>row.point.category),'var(--bad)'),
    barChart('Explicitness', countPointRows(rows,row=>row.point.explicitness),'var(--accent-2)'),
    barChart('Confidence Buckets', countPointRows(rows,row=>confidenceBucket(row.point.confidence)),'var(--warn)'),
    barChart('Metajudge Support Level', countPointRows(rows,row=>row.review?.support_level||'unreviewed'),'var(--accent)'),
    barChart('Summary Overreach', countPointRows(rows,row=>row.review?.summary_overreach?'overreach':'not_flagged'),'var(--bad)'),
    barChart('No-Point Sessions By Source', countBy(noPointSessions,s=>s.release?.source_family||s.metadata?.source_group),'var(--accent-2)')
  ].join('');
  const heatmaps=[
    heatmapChart('Source Family × Candidate Category', rows, row=>row.sourceFamily, row=>row.point.category),
    heatmapChart('Metajudge Decision × Candidate Category', rows, row=>pointDecision(row), row=>row.point.category)
  ].join('');
  const categoryRows=categoryDecisionRows(rows).map(row=>`<tr><td>${badge(row.category,'purple')}</td><td>${fmt(row.total)}</td><td>${fmt(row.accepted)}</td><td>${fmt(row.revised)}</td><td>${fmt(row.rejected)}</td><td>${fmt(row.explicit)}</td><td>${row.avgConfidence.toFixed(2)}</td></tr>`).join('');
  const densityRows=state.sessions.map(session=>{
    const pointRows=rows.filter(row=>row.session.session_id===session.session_id);
    const decisions=countBy(pointRows, pointDecision);
    return {session, total:pointRows.length, accepted:(decisions.accept_candidate||0)+(decisions.revise_candidate||0), rejected:decisions.reject_insufficient_evidence||0, categories:[...new Set(pointRows.map(row=>row.point.category))].join(', ')};
  }).filter(row=>row.total).sort((a,b)=>b.accepted-a.accepted || b.total-a.total).slice(0,14).map(row=>`<tr><td>${openSessionButton(row.session.session_id)}</td><td>${esc(row.session.release?.source_family||row.session.metadata?.source_group)}</td><td>${fmt(row.total)}</td><td>${fmt(row.accepted)}</td><td>${fmt(row.rejected)}</td><td>${esc(shortText(row.categories,90))}</td></tr>`).join('');
  const concernRows=rows.filter(row=>row.review?.summary_overreach || row.review?.category_valid===false || row.review?.diagnosis_or_membership_inference || pointDecision(row)==='reject_insufficient_evidence' || row.review?.support_level==='weak_or_none').sort((a,b)=>{
    const rank={reject_insufficient_evidence:0,revise_candidate:1,accept_candidate:2,unreviewed:3};
    return (rank[pointDecision(a)]??9)-(rank[pointDecision(b)]??9);
  }).slice(0,14).map(row=>{
    const issues=[row.review?.summary_overreach?'overreach':'',row.review?.category_valid===false?'category invalid':'',row.review?.support_level==='weak_or_none'?'weak support':'',row.review?.diagnosis_or_membership_inference?'diagnosis/member inference':''].filter(Boolean);
    return `<tr><td>${openSessionButton(row.session.session_id)}</td><td>${badge(row.point.category,'purple')}</td><td>${badge(pointDecision(row),reviewKind(pointDecision(row)))}</td><td>${esc(issues.join(', ')||'review concern')}</td><td>${esc(shortText(row.review?.rationale,220))}</td></tr>`;
  }).join('');
  const uncertaintyRows=acceptedRows.filter(row=>row.point.uncertainty_or_counterevidence).sort((a,b)=>Number(b.point.confidence)-Number(a.point.confidence)).slice(0,12).map(row=>`<tr><td>${openSessionButton(row.session.session_id)}</td><td>${badge(row.point.category,'purple')}</td><td>${esc(row.point.explicitness)} / ${esc(row.point.confidence)}</td><td>${esc(shortText(row.point.summary,190))}</td><td>${esc(shortText(row.point.uncertainty_or_counterevidence,220))}</td></tr>`).join('');
  $('delusionView').innerHTML=`${narrative}<section class="status-strip">${statusItem('Candidate, not diagnosis','All delusion/reality-boundary fields are LLM-extracted candidate signals, not clinical ground truth.','warn')}${statusItem('Metajudge calibrated','Counts distinguish first-pass candidates from accept/revise/reject decisions.','ok')}${statusItem('Empty lists are meaningful','Controls and some interviews remain no-point sessions rather than forced labels.','info')}</section><section class="result-grid">${cards}</section><div class="overview-grid">${charts}</div>${chartNarratives(['Candidate Categories','Metajudge Decision × Candidate Category','Source Family × Candidate Category'])}${heatmaps}<section class="panel"><h3>Category × Metajudge Situation</h3><table><thead><tr><th>Category</th><th>Total</th><th>Accepted</th><th>Revised</th><th>Rejected</th><th>Explicit</th><th>Avg conf</th></tr></thead><tbody>${categoryRows}</tbody></table></section><section class="panel"><h3>Highest Signal-Density Sessions</h3><table><thead><tr><th>Session</th><th>Source</th><th>Points</th><th>Accepted/Revised</th><th>Rejected</th><th>Categories</th></tr></thead><tbody>${densityRows}</tbody></table></section><section class="panel"><h3>Metajudge Concern Situations</h3><table><thead><tr><th>Session</th><th>Category</th><th>Decision</th><th>Issue</th><th>Rationale</th></tr></thead><tbody>${concernRows}</tbody></table></section><section class="panel"><h3>Uncertainty / Counterevidence Examples</h3><table><thead><tr><th>Session</th><th>Category</th><th>Explicitness / conf</th><th>Candidate summary</th><th>Uncertainty or counterevidence</th></tr></thead><tbody>${uncertaintyRows}</tbody></table></section>`;
  $('delusionView').querySelectorAll('[data-jump]').forEach(btn=>btn.onclick=()=>{setView('sessions'); showSession(btn.dataset.jump)});
}
function pointReviewFor(point, sessionId){return (state.reviews.get(sessionId)||[]).find(r=>r.point_id===point.point_id)}
function allPointRows(){
  return state.sessions.flatMap(session=>(session.delusion_points||[]).map(point=>({
    session,
    point,
    review: pointReviewFor(point, session.session_id),
    release: session.release||{},
    sourceFamily: session.release?.source_family || session.metadata?.source_group || 'unknown'
  })));
}
function pointDecision(row){return row.review?.decision || 'unreviewed'}
function acceptedOrRevised(row){return ['accept_candidate','revise_candidate'].includes(pointDecision(row))}
function confidenceBucket(value){
  const n=Number(value);
  if(!Number.isFinite(n)) return 'unknown';
  if(n>=0.9) return '0.90-1.00';
  if(n>=0.75) return '0.75-0.89';
  if(n>=0.5) return '0.50-0.74';
  return '<0.50';
}
function countPointRows(rows, fn){return countBy(rows, fn)}
function categoryDecisionRows(rows){
  const categories=[...new Set(rows.map(row=>row.point.category||'unknown'))].sort();
  return categories.map(category=>{
    const subset=rows.filter(row=>(row.point.category||'unknown')===category);
    const decisions=countBy(subset, pointDecision);
    return {
      category,
      total: subset.length,
      accepted: decisions.accept_candidate||0,
      revised: decisions.revise_candidate||0,
      rejected: decisions.reject_insufficient_evidence||0,
      explicit: subset.filter(row=>row.point.explicitness==='explicit').length,
      avgConfidence: subset.reduce((n,row)=>n+(Number(row.point.confidence)||0),0)/Math.max(1,subset.length)
    };
  }).sort((a,b)=>b.total-a.total);
}
function renderPoints(session){
  const points=session.delusion_points||[];
  if(!points.length){const neg=state.negatives.get(session.session_id); return `<div class="empty">No candidate points ${neg?badge(neg.decision,reviewKind(neg.decision)):''}</div>`}
  return points.map(point=>{const review=pointReviewFor(point,session.session_id);return `<article class="point"><div class="badges">${badge(point.category,'purple')}${badge(point.explicitness)}${badge(`conf ${point.confidence}`)}${review?badge(review.decision,reviewKind(review.decision)):''}${review?.diagnosis_or_membership_inference?badge('diagnosis/member inference','warn'):''}</div><p>${esc(point.summary)}</p><div class="subtle">messages ${(point.message_indices||[]).join(', ')} · ${esc(point.uncertainty_or_counterevidence)}</div>${review?`<div class="rationale"><b>Metajudge:</b> ${esc(review.rationale)}${review.revised_summary?`<br><b>Revision:</b> ${esc(review.revised_summary)}`:''}</div>`:''}</article>`}).join('');
}
function renderFingerprint(session){
  const fp=state.fingerprints.get(session.session_id);
  if(!fp) return '<div class="empty">No fingerprint</div>';
  return `<div class="fingerprint-list"><div><b>Signature:</b> ${esc(fp.semantic_signature)}</div><div><b>Pattern:</b> ${esc(fp.core_reality_boundary_pattern)}</div><div><b>Evidence:</b> ${esc(fp.evidence_shape)}</div><div><b>Uncertainty:</b> ${esc(fp.uncertainty_profile)}</div><div><b>Belief objects:</b> ${(fp.belief_objects||[]).map(x=>badge(x)).join('')}</div><div><b>Terms:</b> ${(fp.duplicate_screening_terms||[]).map(x=>badge(x,'purple')).join('')}</div><div>${badge(`source risk: ${fp.source_specificity_risk}`,riskKind(fp.source_specificity_risk))}${fp.rare_event_chain_risk?badge('rare chain','warn'):''}</div></div>`;
}
function renderPairs(session){
  const pairs=state.pairsBySession.get(session.session_id)||[];
  if(!pairs.length) return '<div class="empty">No reviewed duplicate pairs</div>';
  return `<table class="pair-table"><thead><tr><th>Other session</th><th>Decision</th><th>Risk</th><th>Action</th></tr></thead><tbody>${pairs.map(p=>{const other=p.left_session_id===session.session_id?p.right_session_id:p.left_session_id;return `<tr><td><button class="tab" data-jump="${esc(other)}">${esc(other)}</button></td><td>${badge(p.decision, p.decision==='duplicate'?'bad':p.decision==='near_duplicate'?'warn':'ok')}</td><td>${badge(p.leakage_risk,riskKind(p.leakage_risk))}</td><td>${esc(p.recommended_action)}</td></tr>`}).join('')}</tbody></table>`;
}
function renderConversation(session){
  return `<div class="conversation">${(session.messages||[]).map((m,i)=>`<div class="message ${esc(m.role)}"><div class="message-head"><span>${i}</span><span>${esc(m.role)}</span></div><div>${esc(m.content)}</div></div>`).join('')}</div>`;
}
function showSession(id){
  state.active=id; renderSessionList(); const s=state.sessionsById.get(id); if(!s) return;
  const r=s.release||{};
  $('sessionsView').innerHTML=`<section class="panel"><h2>${esc(s.session_id)}</h2><div class="badges">${releaseBadge(r)}${badge(r.source_family||s.metadata?.source_group,'purple')}${badge(`${(s.messages||[]).length} messages`)}${badge(`${(s.delusion_points||[]).length} points`)}</div><p>${esc(s.case_summary||'')}</p><div class="meta-grid"><div class="meta-cell"><span>Release split</span>${esc(r.release_split||'')}</div><div class="meta-cell"><span>Original split</span>${esc(r.original_split||r.split||'')}</div><div class="meta-cell"><span>Release action</span>${esc(r.release_action||'')}</div><div class="meta-cell"><span>Quality</span>${esc(s.quality?.status||'')}</div></div></section><div class="detail-grid"><section><div class="panel"><h3>Conversation</h3>${renderConversation(s)}</div></section><section><div class="panel"><h3>Candidate Points & Metajudge</h3>${renderPoints(s)}</div><div class="panel"><h3>Semantic Fingerprint</h3>${renderFingerprint(s)}</div><div class="panel"><h3>Duplicate / Leakage Pairs</h3>${renderPairs(s)}</div></section></div>`;
  $('sessionsView').querySelectorAll('[data-jump]').forEach(btn=>btn.onclick=()=>showSession(btn.dataset.jump));
}
function renderDuplicates(){
  const rows=[...state.pairs].sort((a,b)=>{
    const rank={high:0,medium:1,low:2,none:3};
    return (rank[a.leakage_risk]??9)-(rank[b.leakage_risk]??9) || a.decision.localeCompare(b.decision);
  });
  $('duplicatesView').innerHTML=`<div class="overview-grid">${barChart('Pair Decisions',countBy(rows,r=>r.decision),'var(--bad)')}${barChart('Leakage Risk',countBy(rows,r=>r.leakage_risk),'var(--accent-2)')}${barChart('Recommended Actions',countBy(rows,r=>r.recommended_action),'var(--warn)')}${barChart('Cross Split Risk',countBy(rows,r=>r.cross_split_risk),'var(--accent)')}</div><section class="panel"><h3>Reviewed Pairs</h3><table><thead><tr><th>Left</th><th>Right</th><th>Decision</th><th>Risk</th><th>Action</th><th>Rationale</th></tr></thead><tbody>${rows.map(r=>`<tr><td><button class="tab" data-jump="${esc(r.left_session_id)}">${esc(r.left_session_id)}</button><div class="subtle">${esc(r.left_split)}</div></td><td><button class="tab" data-jump="${esc(r.right_session_id)}">${esc(r.right_session_id)}</button><div class="subtle">${esc(r.right_split)}</div></td><td>${badge(r.decision,r.decision==='duplicate'?'bad':r.decision==='near_duplicate'?'warn':'ok')}</td><td>${badge(r.leakage_risk,riskKind(r.leakage_risk))}</td><td>${esc(r.recommended_action)}</td><td>${esc(r.rationale)}</td></tr>`).join('')}</tbody></table></section>`;
  $('duplicatesView').querySelectorAll('[data-jump]').forEach(btn=>btn.onclick=()=>{setView('sessions'); showSession(btn.dataset.jump)});
}
function setView(view){
  state.view=view; document.querySelectorAll('.tab[data-view]').forEach(btn=>btn.classList.toggle('active',btn.dataset.view===view));
  $('overviewView').classList.toggle('hidden',view!=='overview'); $('resultsView').classList.toggle('hidden',view!=='results'); $('delusionView').classList.toggle('hidden',view!=='delusion'); $('sessionsView').classList.toggle('hidden',view!=='sessions'); $('duplicatesView').classList.toggle('hidden',view!=='duplicates');
  if(view==='overview') renderOverview(); if(view==='results') renderResults(); if(view==='delusion') renderDelusion(); if(view==='duplicates') renderDuplicates(); if(view==='sessions' && !state.active && state.sessions.length) showSession(state.sessions[0].session_id);
}
async function boot(){
  const processed=await Promise.all(paths.processed.map(fetchJSONL));
  state.sessions=processed.flat(); state.sessionsById=new Map(state.sessions.map(s=>[s.session_id,s]));
  state.splits=new Map((await fetchJSONL(paths.reviewedSplits)).map(r=>[r.session_id,r]));
  state.audit=await fetchJSON(paths.reviewedAudit);
  state.pointSummary=await fetchJSON(paths.pointSummary);
  state.duplicateSummary=await fetchJSON(paths.duplicateSummary);
  state.narrative=await fetchOptionalJSON(paths.narratives);
  state.notes=Object.fromEntries(await Promise.all(Object.entries(paths.experimentNotes).map(async ([key,path])=>[key,await fetchText(path)])));
  state.pointReviews=await fetchJSONL(paths.pointReviews);
  state.fingerprintRows=await fetchJSONL(paths.fingerprints);
  state.pairs=await fetchJSONL(paths.duplicatePairs);
  hydrateIndexes(); renderMetrics(); renderFilters(); renderSessionList(); renderOverview(); renderResults(); renderDelusion(); renderDuplicates();
  if(state.sessions.length) showSession(state.sessions[0].session_id);
  $('loadStatus').textContent=`${fmt(state.sessions.length)} sessions · reviewed release data loaded`;
}
for(const id of ['search','sourceFilter','splitFilter','decisionFilter','riskFilter']) $(id).addEventListener('input',renderSessionList);
document.querySelectorAll('.tab[data-view]').forEach(btn=>btn.onclick=()=>setView(btn.dataset.view));
boot().catch(error=>{$('loadStatus').textContent='load failed'; $('overviewView').innerHTML=`<pre>${esc(error.stack||error)}</pre>`});
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    html = build_html().replace("__PATHS__", json.dumps(dashboard_fetch_paths(), ensure_ascii=False))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(f"out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
