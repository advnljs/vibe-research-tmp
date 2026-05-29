# Deviation Bench Benchmark 对比与研究缺口分析

创建日期：2026-05-29

用途：把 Deviation Bench 与当前最接近的 mental-health safety、sycophancy、multi-turn reliability、hallucination 和自动行为评测工作区分开，形成论文 Table 1 / Introduction gap statement 的第一版材料。

本文件使用 `benchmark-paper-template` 的 gap-analysis 与 benchmark-design 框架：先列 existing landscape，再识别 structural blind spot，最后落到研究问题、设计目标和 reviewer 风险防守。

## 1. 当前最稳的定位

Deviation Bench 不应被写成“AI psychosis benchmark”或“mental-health safety benchmark”。这两个 framing 会直接撞上 Stanford HAI / Weval / Bloom 的近邻工作，而且会引入不必要的临床安全边界。

当前更稳的定位是：

> Deviation Bench measures context-retest reliability of reality-grounded judgment: given the same evidence anchor, does an LLM preserve uncertainty, evidence constraints, and correction ability under repeated user pressure?

中文版本：

> Deviation Bench 测的是“同一模型、同一证据锚点，在用户逐轮施压或改写语境后，是否还能保持现实锚定判断”。它的核心不是诊断用户、也不是复现真实妄想，而是测模型输出判断的情境复测可靠性。

对应 gap pattern：

- 主 gap：**Assumption Violation**。现有很多评测默认用户输入只是一次性 query，或者默认同一模型的 grounded judgment 不会因为社会语境变化而系统偏移。
- 次 gap：**Evaluation Granularity Mismatch**。已有 sycophancy / safety / hallucination 评测往往只给单轮通过/失败或行为 presence，难以分解 drift slope、unjustified reversal、recovery reliability 和 residual drift。

## 2. Table 1 草稿：Closest Prior 对比

| Prior / family | 它主要测什么 | 构造方式 | Deviation Bench 需要避开的重叠 | Deviation Bench 的差异化主张 |
|---|---|---|---|---|
| Weval `ai-psychosis`, `ai-spiral-safety`, `mental-health`, `sycophancy-probe` | 高风险情境下模型是否安全、是否拒绝验证妄想/危机/不当依恋 | YAML blueprint + ideal/should rubric；本地相关蓝图约 14/100/19/22 条 prompt | 不能再做“模型是否应该拒绝 AI psychosis/危机请求”的单轮安全评测 | 把高风险心理健康问题降级为低风险虚构 analogue；主变量是同一 evidence anchor 下的多轮诱导、翻案和纠偏，不是危机响应 |
| Stanford HAI / FAccT mental-health safety eval | LLM 作为 therapy chatbot 时是否污名化、是否不当地回应 delusions / hallucinations / suicidal ideation | 临床 guideline mapping + vignette / transcript-derived scenarios | 不应声称替代 clinical appropriateness benchmark；不应让公开 prompt 变成 therapy safety test | 使用其“do not collude with delusions / reality-check when appropriate”作为 rubric 参考，但 Deviation Bench 的被测对象是一般助手的 reality-grounding 稳定性 |
| Bloom delusional-sycophancy | 自动生成 rollouts 来诱发并评分某个目标行为，如 delusional sycophancy | Understanding -> Ideation -> Rollout -> Judgment 四阶段；行为 presence / elicitation rate | 不应只复刻 Bloom 的 behavior elicitation suite | 借 Bloom-style 生成流程，但加入 controlled evidence anchors、neutral baseline、paraphrase noise、turn-level RDS 曲线和 recovery turn |
| ELEPHANT social sycophancy | 模型是否过度维护用户 face / self-image，尤其在社会判断场景中迎合用户 | 社会语用理论 + advice/AITA-like 场景 + scorer | 不应把全部问题写成“social sycophancy” | Social pressure 只是 UIRD 的诱导通道之一；Deviation Bench 还测 evidence-grounding、unsupported belief amplification、unjustified reversal 和 recovery |
| Anthropic sycophancy line | RLHF / preference model 为什么偏好迎合用户，模型是否牺牲真相换取用户满意 | 偏好实验与 sycophantic response analysis | 不应只做“用户说 A，模型也说 A”的同意率 | 重点放在多轮轨迹：从 insufficient evidence 到 mild accommodation，再到 endorsement / elaboration 的连续漂移 |
| LLMs Get Lost in Multi-Turn Conversation | 多轮不完整需求会让模型任务表现下降和不可靠性上升 | 将单轮完整任务拆成多轮 shards，比较 single-turn vs multi-turn performance | 不应把 drift 仅解释为长上下文或任务分片导致的性能下降 | Deviation Bench 的多轮信息不提供新证据，而是施加主观、情绪、权威或社会压力；核心是无新证据时的判断漂移和能否恢复 |
| Hallucination / factuality probes | 模型是否自己编造事实、法律、引用、医学信息等 | 单轮或短上下文 factual probes，通常以事实正确性为主 | 不应把 user-induced drift 混同为普通 hallucination | UIRD 关注用户先引入 unsupported claim 后，模型是否迁就、合理化、扩写或行动化；错误来源来自互动压力，不只是模型自发生成 |
| General mental-health chat datasets / counseling QA | 支持性回应、咨询风格、危机识别或情绪支持 | 真实或合成问答/对话数据 | 不应把 AnnoMI/CounselChat/MentalChat16K 当作 delusion ground truth | 这些数据只作为“支持但不验证”的风格对照；真实 reality-boundary 数据只抽象成安全场景模式，不直接复制为 prompt |

本地 Weval 相关蓝图规模粗计：

| Local blueprint | Prompt count by `id` | 对 Deviation Bench 的用途 |
|---|---:|---|
| `ai-psychosis.yml` | 14 | 高风险 verbatim case-based safety 的反例边界 |
| `ai-spiral-safety.yml` | 100 | AI 依恋、现实脱离、pattern-seeking 等风险类别参考 |
| `mental-health.yml` | 19 | crisis / support rubric 参考 |
| `stanford-hai-mental-health-safety-eval.yml` | 18 | clinical safety rubric 参考 |
| `sycophancy-probe.yml` | 22 | factual / logical / dangerous validation 的近邻对照 |
| `overpersonalization-anchor-bias.yml` | 7 | anchor bias 与过度个性化参考 |
| `hallucination-probe.yml` | 28 | ordinary hallucination 与 UIRD 的边界对照 |

## 3. 可放进 Introduction 的 gap statement

英文工作版：

> Existing LLM safety and sycophancy benchmarks ask whether a model gives an appropriate response to isolated risky prompts, whether it agrees with a user, or whether multi-turn interaction degrades task performance. They generally do not test whether the same model preserves a reality-grounded judgment when the factual evidence is held fixed but the surrounding user pressure changes over turns. This leaves context-retest reliability unmeasured: a model may appear safe or factual in a neutral prompt while gradually endorsing, elaborating, or unjustifiably reversing its judgment under repeated unsupported user claims.

中文工作版：

> 现有 LLM safety、sycophancy 和 multi-turn 评测主要问三件事：模型面对单个风险 prompt 是否安全，是否会迎合用户，或多轮对话是否降低任务表现。它们通常不问“证据不变时，同一个模型的现实锚定判断是否会被用户逐轮施压而改变”。因此，当前评测漏掉了 context-retest reliability：模型可能在中性条件下表现 grounded，却在用户反复输入无证据信念后逐步认同、扩写，或无新证据地翻案。

## 4. 研究问题

RQ1: 在低风险、虚构、证据锚定的多轮 episode 中，不同 LLM 的 Reality Drift Score 曲线是否显著不同？

RQ2: 哪些诱导模式最容易造成 drift：premise laundering、commitment erosion、pattern-seeking trap、emotional validation pressure、authority smuggling，还是 social proof pressure？

RQ3: 当给出中性纠偏提示后，模型能否回到最初 evidence-grounded stance？Recovery Reliability 是否比 drift event rate 更能区分强模型和弱模型？

RQ4: 观察到的 drift 是否超过 neutral paraphrase noise？如果不能超过，则该现象只能被解释为普通 prompt sensitivity，不能作为 UIRD 主结论。

## 5. 设计目标 G1-G4

| Goal | Deviation Bench 的实现要求 | 当前状态 |
|---|---|---|
| G1 Coverage | 覆盖 false-belief amplification、unjustified reversal、supportive validation boundary、social pressure、recovery | 20 个中文 multi-turn pilot 已覆盖雏形；仍缺 single-turn context swap 与英文对照 |
| G2 Diagnostics | 不只给总分，要分 turn / family / induction pattern / recovery | runner 已有 turn-level judge 和 scenario metrics；仍需统一 utterance schema 与分析表 |
| G3 Scalability | API-only、低 GPU、Controlled Injection + Bloom-style generation | mock runner 已跑通；real API smoke 未跑 |
| G4 Quality | LLM judge 需和人审 audit 对齐；真实数据只作 pattern seed | judge rubric 与标注规范已写；尚无人审一致性数据 |

## 6. Reviewer 风险与防守句

| 风险 | 可能的 reviewer 质疑 | 防守策略 |
|---|---|---|
| F1: 与 mental-health safety eval 重叠 | 这不就是 Stanford HAI / Weval 的 psychosis safety 吗？ | 明确公开 benchmark 不测真实危机响应，不复制高风险 prompt；只测固定 evidence anchor 下的情境复测可靠性 |
| F1: 与 sycophancy benchmark 重叠 | 这不就是又一个 sycophancy 测试吗？ | sycophancy 是诱导机制之一，主指标是 RDS-AUC / URR / RR；包含 recovery 和 evidence anchoring |
| F3: 只是 prompt sensitivity | 换个说法模型当然会变 | 必须加入 neutral paraphrase noise；drift 结论只在超过 noise 下限时成立 |
| F7: 数据伦理 | 是否用了真实患者/社区原文？ | 真实数据只抽象模式；公开场景 fictional、低风险、去身份化；不诊断真实用户 |
| F10: judge 不可靠 | LLM judge 会不会偏？ | 先跑 50-100 turn 人审 audit；报告主标签 agreement，不达标则先改 rubric |
| F8: scope 过大 | 同时做 psychosis、sycophancy、multi-turn、hallucination 太散 | 论文主线只保留 context-retest reliability；其他 prior 是对比项，不是并列研究目标 |

## 7. 对后续实现的直接约束

1. 新增样本必须显式包含 `evidence_anchor` 和 `unsupported_claim`，否则无法证明“没有新证据仍翻案”。
2. 每个 multi-turn episode 必须包含 recovery turn，否则无法测 RR / RD。
3. 必须补 neutral paraphrase control，否则 reviewer 可以把所有 drift 都归因于普通措辞敏感性。
4. 真实临床/社区文本只能进入 `source_inspiration` 或 abstract pattern bank，不进入公开 prompt 原文。
5. 如果继续走 Framing A / C，Table 1 应把 “context-retest reliability” 放到最右侧作为 `Ours` 的核心 differentiator。

## 8. 一手来源与本地依据

一手来源：

- Laban et al., *LLMs Get Lost In Multi-Turn Conversation*, ICLR 2026 / arXiv 2505.06120: https://openreview.net/pdf?id=VKGTGGcwl6
- Cheng et al., *ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs*, ICLR 2026: https://openreview.net/pdf?id=igbRHKEiAs
- Anthropic, *Towards Understanding Sycophancy in Language Models*, 2023: https://www.anthropic.com/news/towards-understanding-sycophancy-in-language-models/
- Moore et al., *Expressing stigma and inappropriate responses prevents LLMs from safely replacing mental health providers*, FAccT 2025: https://spirals.stanford.edu/assets/pdf/moore_expressing_2025.pdf
- Stanford HAI, *Exploring the Dangers of AI in Mental Health Care*, 2025-06-11: https://hai.stanford.edu/news/exploring-the-dangers-of-ai-in-mental-health-care
- Anthropic, *Introducing Bloom: an open source tool for automated behavioral evaluations*, 2026: https://www.anthropic.com/research/bloom
- Weval configs repository: https://github.com/weval-org/configs

本地依据：

- `deviation-bench/Deviation Bench 现象定义与量化框架.md`
- `deviation-bench/Deviation Bench 可执行优化版.md`
- `deviation-bench/目标收缩-工作流深思考.md`
- `deviation-bench/data_sources/downloaded/weval_configs/blueprints/`
- `deviation-bench/data_sources/downloaded/bloom_experiments_branch/experiments/`
- `deviation-bench/prompts/pilot_scenarios.yaml`
