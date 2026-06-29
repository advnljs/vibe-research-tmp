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
        "fingerprints": "/data/reviews/deepseek_v4_pro_session_semantic_fingerprints_64k.jsonl",
        "duplicatePairs": "/data/reviews/deepseek_v4_pro_semantic_duplicate_pairs_64k.jsonl",
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
.hidden{display:none!important}
.empty{color:var(--muted);padding:14px;border:1px dashed var(--line);border-radius:7px;background:white}
@media(max-width:1080px){.metric-grid{grid-template-columns:repeat(3,minmax(130px,1fr))}.main{grid-template-columns:1fr}aside,main{max-height:none}aside{border-right:0;border-bottom:1px solid var(--line)}.detail-grid,.overview-grid{grid-template-columns:1fr}}
@media(max-width:640px){.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.filters{grid-template-columns:1fr}.tab{min-width:0;flex:1}.message.user,.message.assistant{margin-left:0;margin-right:0}}
</style>
</head>
<body>
<header>
  <div class="topline">
    <div><h1>Deviation Bench New Review Dashboard</h1><div id="loadStatus" class="subtle">loading</div></div>
    <nav class="tabs">
      <button class="tab active" data-view="overview">Overview</button>
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
    <section id="sessionsView" class="hidden"></section>
    <section id="duplicatesView" class="hidden"></section>
  </main>
</div>
<script>
const paths = __PATHS__;
const state = {sessions:[], splits:new Map(), reviews:new Map(), negatives:new Map(), fingerprints:new Map(), pairs:[], pairsBySession:new Map(), audit:null, active:null, view:'overview'};
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = n => Number.isFinite(n) ? n.toLocaleString('en-US') : String(n ?? '');
async function fetchText(path){const response=await fetch(path); if(!response.ok) throw new Error(`${path} ${response.status}`); return response.text()}
async function fetchJSON(path){return JSON.parse(await fetchText(path))}
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
function metric(label, value, note=''){return `<div class="metric"><span>${esc(label)}</span><b>${esc(value)}</b>${note?`<span>${esc(note)}</span>`:''}</div>`}
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
function pointReviewFor(point, sessionId){return (state.reviews.get(sessionId)||[]).find(r=>r.point_id===point.point_id)}
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
  $('overviewView').classList.toggle('hidden',view!=='overview'); $('sessionsView').classList.toggle('hidden',view!=='sessions'); $('duplicatesView').classList.toggle('hidden',view!=='duplicates');
  if(view==='overview') renderOverview(); if(view==='duplicates') renderDuplicates(); if(view==='sessions' && !state.active && state.sessions.length) showSession(state.sessions[0].session_id);
}
async function boot(){
  const processed=await Promise.all(paths.processed.map(fetchJSONL));
  state.sessions=processed.flat(); state.sessionsById=new Map(state.sessions.map(s=>[s.session_id,s]));
  state.splits=new Map((await fetchJSONL(paths.reviewedSplits)).map(r=>[r.session_id,r]));
  state.audit=await fetchJSON(paths.reviewedAudit);
  state.pointReviews=await fetchJSONL(paths.pointReviews);
  state.fingerprintRows=await fetchJSONL(paths.fingerprints);
  state.pairs=await fetchJSONL(paths.duplicatePairs);
  hydrateIndexes(); renderMetrics(); renderFilters(); renderSessionList(); renderOverview(); renderDuplicates();
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
