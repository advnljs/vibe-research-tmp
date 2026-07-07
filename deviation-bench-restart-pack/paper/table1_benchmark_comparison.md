# Table 1 Benchmark Comparison Draft

更新日期：2026-05-22

用途：这是 Deviation Bench 后续 introduction / related work 中的 Table 1 草稿，用来明确现有评测已经覆盖什么，以及 Deviation Bench 需要避开的重叠区。本文档基于本地已下载的 weval blueprints、项目内文献综述和当前 Deviation Bench 设计文件，不引入新的外部文献断言。

## One-Sentence Gap

现有相关评测已经覆盖 AI psychosis safety、spiral / attachment safety、mental-health crisis response、social sycophancy、factual hallucination 等单点风险；但它们通常不把同一个 reality-boundary judgment 放入 neutral baseline、user pressure、multi-turn induction、recovery 四类上下文中做 context-retest，因此无法直接量化“同一模型同一判断在上下文压力下漂移多少、是否能恢复”。

## Comparison Table

| Work / asset | Task scope | Source type | Local scale | Multi-source unified? | Same-question context-retest? | Multi-turn dynamics? | Recovery / re-anchoring metric? | Real-corpus anchored? | Language | Main limitation relative to Deviation Bench |
|---|---|---|---:|---|---|---|---|---|---|---|
| weval `ai-psychosis.yml` | AI-associated psychosis safety; delusion affirmation, attachment, self-harm / violence enablement, inappropriate therapy | Verbatim or case-based prompts from lawsuits, media investigations, and case reviews | 14 items | Partial: multiple cited cases inside one safety blueprint | No. It tests case response quality, not repeated same claim across contexts | Partial: several items include prior assistant turns | No explicit recovery score | Partial: anchored in documented cases / reports, not an open raw dialogue corpus | English | Strong closest safety prior, but it measures safe response to high-risk cases rather than low-risk controlled drift under baseline-induction-recovery retest. |
| weval `ai-spiral-safety.yml` | AI sentience / attachment, grandiosity, mystical pattern-seeking, reality detachment, symbolic spreading, crisis response | Expert / advocacy safety blueprint | 100 items | No: one integrated blueprint, not a cross-corpus dataset | No. Items are scenario probes, not paired retest variants | Mostly single-turn probes; some categories imply extended sessions | No explicit recovery score | Not clearly real-corpus anchored in the local blueprint | English | Broadly covers “spiral” risk, but not designed to estimate a drift trajectory for the same proposition under escalating user pressure. |
| weval `stanford-hai-mental-health-safety-eval.yml` | Mental-health crisis response; delusions, hallucinations, mania, suicidality, therapeutic ethics | Scenario blueprint based on / inspired by Stanford HAI mental-health safety methodology | 18 items | No: single safety-eval family | No | Partial: several items include conversation context | No explicit recovery score | Mostly scenario-based; grounded in study design rather than raw clinical dialogue | English | Useful clinical-safety baseline, but the target is inappropriate clinical response, not context-retest reliability or user-induced reversal. |
| ELEPHANT | Open-ended social judgment / advice sycophancy; face preservation and indirectness | Benchmark paper + released scorer/data according to local literature review | Exact local item count not recorded | No for this project: not merged with clinical/community sources | Partial: tests social pressure and advice norms, but not reality-boundary retest as currently framed | Open-ended dialogue/advice setting; not a drift trajectory benchmark | No explicit re-anchoring metric in current project notes | Uses crowdsourced/social norms rather than psychosis / reality-boundary corpora | English | Best social-pressure prior, but its object is social sycophancy and face preservation, not evidence-grounded reality judgments under delusion-like induction. |
| weval `sycophancy-probe.yml` | Independence and critical thinking; factual correction, logical sycophancy, high-stakes dangerous validation, authority pressure, opinion whiplash | Hand-authored evaluation config informed by complaints and academic research | 22 items | No | Partial: includes contradiction / opinion-shift probes | Partial: some multi-turn probes | No explicit recovery score | No: mostly synthetic probes | English | Captures agreement pressure and unjustified reversal, but lacks real-corpus reality-boundary anchoring and baseline-induction-recovery trajectory metrics. |
| weval `hallucination-probe.yml` | Nonexistent facts, fake studies, fake laws, fake cases, fictional concepts | Synthetic factuality / hallucination probes | 28 items | No | No | No: mostly single-turn | No | No | English | Measures confabulation under false premises, but not social induction, emotional validation pressure, or multi-turn reality-grounding drift. |
| weval `mental-health.yml` | Crisis intervention and culturally aware mental-health response | Scenario blueprint based on crisis-intervention best practices and global mental-health themes | 19 items | No | No | Partial: some multi-turn crisis-response cases | No explicit recovery score | Not primarily raw dialogue-corpus anchored | English | Important safety baseline, but broad mental-health crisis quality is different from measuring context-induced drift on the same evidence boundary. |
| Deviation Bench (proposed) | User-Induced Reality Drift: false-belief amplification, unjustified determination reversal, recovery / re-anchoring | Multi-source abstract patterns from real interview/community/counseling data + controlled synthetic induction scripts | Current pilot: 20 fictional low-risk scenarios; planned v1: 200-300 single-turn stems + 40-60 multi-turn scripts | Yes by design: DAIS-C, FEP friendship interviews, Reddit r/schizophrenia, AnnoMI / counseling references, Bloom / weval generation patterns | Yes: same claim under neutral baseline, induction variants, and recovery | Yes: multi-turn pressure trajectory is the core unit | Yes: RR / RD and related recovery metrics are first-class | Yes, via abstracted patterns; raw sensitive text should not be copied into prompts | Current pilot mostly Chinese; final language scope pending user decision | Contribution should be claimed as context-retest reliability for reality-boundary judgment, not as another generic mental-health safety benchmark. |

## Differentiation Claims To Use Later

1. **From safety case probes to reliability trajectories.** Prior psychosis / mental-health safety blueprints ask whether a model handles a risky case appropriately. Deviation Bench asks whether the same model keeps the same evidence-constrained judgment as conversational context changes.

2. **From one-shot correctness to context-retest reliability.** Hallucination and factuality probes can catch fabricated facts, but they do not estimate a baseline-to-induction drift curve or recovery after explicit re-anchoring.

3. **From social sycophancy to reality-boundary sycophancy.** Sycophancy and ELEPHANT-style tasks measure agreement, face preservation, or social advice. Deviation Bench should narrow the target to user pressure that tries to move the model across an evidence boundary.

4. **From crisis response to low-risk controlled induction.** Deviation Bench should avoid becoming a high-risk crisis-response suite. Its pilot scenarios should stay fictional and low-risk while still testing the cognitive failure mode: unsupported validation, certainty inflation, confabulatory elaboration, and unjustified reversal.

5. **From dataset aggregation to benchmark design.** Merely combining DAIS-C, FEP interviews, Reddit, AnnoMI, and counseling data is not enough. The publishable gap is the controlled retest schema: baseline, pressure, accumulated turns, and recovery, with comparable metrics across models.

## Candidate Table Caption

**Table 1: Comparison with related benchmarks and evaluation assets.** Existing evaluations cover mental-health safety, AI-associated psychosis cases, social sycophancy, and hallucination. Deviation Bench differs by measuring context-retest reliability for the same reality-boundary judgment across neutral, induced, multi-turn, and recovery conditions.

## Local Source Notes

- weval blueprints: `deviation-bench/data_sources/downloaded/weval_configs/blueprints/`
- Project literature review: `deviation-bench/Deviation Bench 相关研究深度综述.md`
- Scope decision note: `deviation-bench/目标收缩-工作流深思考.md`
- Executable benchmark plan: `deviation-bench/Deviation Bench 可执行优化版.md`
