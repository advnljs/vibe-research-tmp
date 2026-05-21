# Deviation Bench 可执行优化版

## 0. 当前判断

**结论：可以做，但必须从“全景式上下文漂移”收窄为一个可执行的 benchmark v1。**

首版不要同时做 bias、sycophancy、observer effect、delusion dynamics、CoT faithfulness、NLA、TRACE 和 persona vectors。v1 的目标是先证明一个更小但可发表的问题：

> 同一个模型面对同一个判断任务时，社会压力、评估语境和多轮累积上下文是否会诱导稳定、可测、可恢复或不可恢复的 judgment drift？

这版的核心贡献不是新算法，而是定义一个新的评估维度：**context-induced judgment drift**。

### 研究初心

Deviation Bench 的起点不是“再做一个 AI bias benchmark”，而是对当前 AI 评估体系的一个底层假设提出质疑：**situational consistency**。

当前大多数 AI 评估默认同一模型在不同评估条件下行为一致，因此一次 benchmark 分数可以代表模型的稳定能力。但越来越多证据显示，这个前提并不稳：用户会系统性误判 AI 行为；模型在被观察或被评估时会改变语言策略；多轮交互中，信念和判断可能被上下文持续放大。

所以 Deviation Bench 的初心应该保持为：

> 现有 AI 评估把模型回答当成固定能力点，但真实交互中，模型判断会被社会语境、评估压力和对话历史推动。Deviation Bench 要测量这种“同题同模型的判断轨迹”，把情境一致性从默认假设变成可检验指标。

最早的问题是“模型对某个群体有没有刻板印象”。优化后的问题是更底层的：

> 上下文本身如何诱导偏差？

也就是说，Deviation Bench 不主要问“模型有没有固定偏见”，而是问：

> 同一模型、同一问题，放在不同上下文里，输出是否系统性偏离中性基线？这种偏离有多大、能持续多久、能不能被纠正？

这使项目从伦理层面的 group bias benchmark，转向认知层面的 **context-induced deviation / social judgment deviation benchmark**。传统 bias benchmark 测的是模型对某类群体是否不公；Deviation Bench 测的是模型能不能在上下文变化中保持推理和判断一致性。

最强类比：

> 心理测量有 test-retest reliability；AI 评估也应该有 context-retest reliability。

Deviation Bench 想给 AI 评估体系增加的不是又一个分数，而是一种新的可靠性标尺：**偏离度**。

因此，论文里要避免三个误读：
- 不说“我们发现某模型坏/有病/有偏见”，而说“我们测量模型判断的 context invariance”。
- 不把 delusion / psychosis 当主叙事，只把 trigger / sustain / recovery 作为动力学启发。
- 不依赖 white-box interpretability 才成立；主贡献必须在黑盒 LLM API 上可复现。

### 硬约束

你的实现约束应写进项目设计：

| 约束 | 设计后果 |
|---|---|
| 不依赖高 GPU | 不做训练、不做 activation extraction、不跑大规模开源模型推理 |
| 主要使用 LLM API | 所有主指标必须只依赖 prompt、文本输出、可选 logprobs |
| 可低成本复现 | pilot 控制在 2k 次 API 调用以内，v1 控制在 2-3 万次调用以内 |
| 算法轻量 | 核心算法是 controlled injection、answer parsing、drift scoring、统计检验 |
| 白盒信号非必要 | NLA / TRACE / persona vectors 只作为 related work 或 future work |

## 1. Scope Lock

### v1 只评估

| 范围 | 保留理由 |
|---|---|
| 同题同模型在不同 context 下的判断漂移 | 这是项目最清晰的新评估维度 |
| 黑盒 API / 开源模型都能跑的输出级指标 | 保证闭源 frontier models 可纳入主榜 |
| 单轮 context swap | 最容易复现，作为主基线 |
| social pressure / sycophancy-style pressure | 文献强、现实意义强、效果最可能显著 |
| multi-turn accumulation + recovery | Deviation Bench 的差异化核心 |
| 答案频率、答案翻转、恢复速度、漂移斜率 | 比单纯 accuracy 更能体现 benchmark 价值，且可由 API 输出估计 |

### v1 明确不做

| 暂不做 | 原因 |
|---|---|
| NLA / TRACE / persona vectors 主榜 | 白盒依赖太强，会排除闭源模型，也违反低 GPU 约束 |
| 真实 delusion / psychosis 场景 | 伦理和安全风险高，公开 benchmark 不适合 |
| 大规模开放式心理诊断 | 任务边界不清，reviewer 容易质疑 |
| CoT faithful reasoning 主指标 | CoT 不可靠，只能作为辅助分析 |
| companion method / fine-tuning | 首版 benchmark 先证明评估维度成立，不做训练 |
| 统一所有 context sensitivity 现象 | 范围过大，论文会失焦 |

## 2. 优化后的 Gap Statement

Existing LLM benchmarks usually evaluate model behavior under fixed or weakly varied prompting conditions, implicitly assuming situational consistency: a model's judgment on the same task remains stable across surrounding social, evaluative, and conversational contexts. However, real deployments are not context-neutral: users seek validation, models may infer that they are being evaluated, and multi-turn interactions accumulate framing signals over time. This creates a critical evaluation blind spot: current benchmarks report capability scores without measuring their context-retest reliability.

中文论文叙事可以写成：

> 现有 benchmark 主要回答“模型在某个固定评估条件下会不会答对”，但很少回答“同一个模型、同一个问题，在社会压力、评估语境或多轮上下文变化后，判断是否仍然稳定”。Deviation Bench 将这种情境一致性问题形式化为 context-retest reliability，并用 deviation index 测量上下文诱导的偏离度。

## 3. Closest Prior 区分策略

| Prior | 它测什么 | Deviation Bench 怎么区分 |
|---|---|---|
| Contextual StereoSet | stereotype bias 在 time/place/style/observer 下是否变化 | 它仍是 stereotype/bias benchmark；我们测更一般的 judgment drift，并加入 multi-turn recovery 和 social pressure dynamics |
| JudgeSense | LLM-as-judge 对 prompt paraphrase 的 verdict stability | 它测 judge prompt sensitivity；我们测 answerer model 在社会/评估/对话 context 下的 judgment drift |
| Prior-context sensitivity benchmarks | 多轮或长上下文是否降低 QA accuracy | 它们主要测 performance degradation；我们测偏移方向、持续性、恢复性和 context-induced flip |
| Social desirability bias | 模型在问卷/人格测量中趋向社会期许答案 | 它是 psychometric setting；我们把社会压力扩展到事实、因果、社会判断和政策判断 |
| ELEPHANT | 开放式 social sycophancy / face preservation | 它是 social pressure 专项；我们把它作为一个 track，并与 neutral baseline、context swap、recovery dynamics 统一 |
| Delusion Dynamics | 极端有害对话中的 false belief amplification | 它提供 trigger/sustain/half-life 建模启发；我们用安全化低风险场景测一般 judgment drift |

**论文中的防守句：**

> We do not ask whether a model is biased under a specific demographic axis, nor whether a judge is sensitive to paraphrases. We ask whether the same model's judgment remains invariant under controlled changes in the surrounding social, evaluative, and conversational context.

## 4. v1 Benchmark Tracks

### Track A: Context Swap Invariance

**问题：** 当题目语义不变，只改变 role / audience / evaluation framing 时，模型判断是否改变？

设计：
- 每个 stem 有一个 neutral prompt。
- 添加 3 类 context variant：evaluation framing、observer/audience framing、role framing。
- 不改变事实、证据、候选答案和任务要求。

主指标：
- Answer Flip Rate
- Context Drift Rate
- Directional Drift toward context-suggested answer

可选指标：
- Probability Drift JS, only if the API exposes logprobs or if repeated sampling is affordable.

### Track B: Social Pressure Drift

**问题：** 当用户表达偏好、寻求认同、引入权威压力或面子压力时，模型是否偏离中性判断？

设计：
- 用户先给出一个暗示性立场，例如“我觉得 A 对，你同意吗？”
- 题目证据保持不变，正确或更合理的答案不应随用户立场改变。
- pressure direction 必须被标注，方便计算 drift 是否朝用户偏好移动。

主指标：
- Social Compliance Rate
- Evidence-Contradicting Agreement Rate
- Validation Language Rate
- Answer Flip Rate under pressure

### Track C: Multi-turn Accumulation and Recovery

**问题：** 上下文逐轮累积后，模型是否越来越偏？给出纠偏信息后能否回到基线？

标准 episode：
1. T0: neutral answer baseline
2. T1-T3: gradually injected framing / pressure / misleading context
3. T4: ask model to restate answer
4. T5: provide correction or neutralization prompt
5. T6-T7: ask again and measure recovery

主指标：
- Drift Slope
- Peak Drift
- Recovery Rounds
- Residual Drift after Correction
- Half-life, if the drift trajectory fits a decay curve

## 5. 数据规模：先 Pilot，再 v1

### Pilot: 2 周内必须完成

| Component | 数量 |
|---|---:|
| Single-turn stems | 50 |
| Context variants per stem | neutral + 3 |
| Multi-turn scripts | 20 |
| Models | 3 |
| Repeated seeds | 2 |
| 预估调用量 | 约 1,500-2,000 |

Pilot 的目标不是发榜，而是验证这个现象是否稳定存在，以及数据 construction 是否可控。

### Paper v1: 8-12 周版本

| Component | 数量 |
|---|---:|
| Single-turn stems | 200-300 |
| Context variants per stem | neutral + 3 |
| Multi-turn scripts | 40-60 |
| Models | 4-6 API models |
| Repeated seeds | 2 |
| 预估调用量 | 约 12,000-25,000 |

这个规模足够写一篇 benchmark paper 的主实验，也不会因为标注和 API 成本失控。

如果预算紧，优先保留：
1. Social Pressure
2. Multi-turn Recovery
3. Context Swap

不要为了模型数量牺牲 repeated seeds 和 neutral paraphrase control；否则 drift 无法和 prompt noise 区分。

## 6. 数据 Schema

每个样本至少包含：

```yaml
id: string
track: context_swap | social_pressure | multi_turn
domain: factual | causal | social_judgment | policy | advice
stem: string
neutral_prompt: string
answer_space: [A, B, C, D]
neutral_reference_answer: string | null
context_variants:
  - context_id: string
    context_type: evaluation | observer | role | user_preference | authority | face_pressure
    prompt: string
    pressure_direction: A | B | C | D | null
    expected_invariant: true
quality_labels:
  ambiguity_level: low | medium | high
  safety_level: low | medium
  requires_domain_expertise: true | false
```

关键约束：
- `expected_invariant=true` 的题目中，context 不应合理改变答案。
- 如果 context 真的改变了事实条件，该样本不能进入主榜。
- ambiguous samples 可以保留到分析集，但不能用于核心 drift 结论。

## 7. 主指标定义

设中性条件下的 repeated API outputs 形成经验答案分布 `P0`，上下文条件 `k` 下形成经验答案分布 `Pk`。如果 API 提供 logprobs，可以用 logprobs；否则用 repeated samples 的答案频率估计。

由于首版必须兼容 LLM API，指标分为 **primary API-only metrics** 和 **optional logprob metrics**。

### Primary API-only metrics

| 指标 | 定义 | 用途 |
|---|---|---|
| Context-Retest Reliability | 同题在 neutral 与 context variants 下保持同一判断的比例 | 对应研究初心中的“情境一致性” |
| Deviation Index | `1 - Context-Retest Reliability`，并扣除 neutral paraphrase noise | 作为 Deviation Bench 的核心总分 |
| Answer Flip Rate | context 条件答案与 neutral 条件答案不同的比例 | 最直观的 judgment drift |
| Context Drift Rate | 对同一题的 repeated API samples 中，context 条件偏离 neutral majority answer 的比例 | 不依赖 logprobs |
| Directional Drift | context 条件下选择 pressure_direction 的频率减去 neutral 条件频率 | 判断是否朝 context 暗示方向漂 |
| Social Compliance Rate | social pressure 下选择用户偏好答案的比例 | 衡量迎合压力 |
| Drift Slope | 多轮中 drift score 对 turn index 的斜率 | 衡量累积效应 |
| Recovery Rounds | 纠偏后回到 neutral answer 或低 drift 阈值所需轮数 | 衡量恢复能力 |
| Residual Drift | 纠偏后仍偏离 neutral majority answer 的比例 | 衡量偏移残留 |
| Neutral Paraphrase Noise | 中性同义改写之间的 drift | 作为所有 drift 的噪声下限 |

**重要：** 所有 drift 结论都必须超过 neutral paraphrase noise，否则 reviewer 会说这只是普通 prompt sensitivity。

### Optional logprob metrics

只有在 API 支持 token logprobs 或者可以低成本重复采样时才使用：

| 指标 | 定义 | 使用条件 |
|---|---|---|
| Probability Drift JS | `JS(P0, Pk)` | API 提供候选答案 logprobs，或 repeated samples 足够估计分布 |
| Confidence Drift | 模型自报 confidence 的变化 | 只能作为辅助，不能当主证据 |
| Margin Drift | top answer 与 second answer 的概率差变化 | 需要 logprobs |

主论文不要承诺所有 API 都能提供 logprobs；否则实现会被 provider 限制绑死。

### 推荐主榜分数

主榜不要用一个无法解释的大总分。建议报告三个 headline scores：

| Headline score | 组成 | 含义 |
|---|---|---|
| CRR | Context-Retest Reliability | 模型在上下文变化下保持判断一致的能力 |
| DI | Deviation Index | 上下文诱导偏离度，越高越不稳定 |
| RR | Recovery Reliability | 多轮纠偏后回到中性判断的能力 |

其中 `DI = observed drift - neutral paraphrase noise`。这样可以防止 reviewer 把结果归因于普通 prompt wording sensitivity。

## 8. Construction Pipeline

首版使用 **Controlled Injection**，不是开放式爬数据。

| Stage | Input | Operation | Output | Quality Gate |
|---|---|---|---|---|
| 1. Seed design | 初始任务想法 | 写 neutral stem 和 answer space | clean stems | 题目语义清楚，答案空间可解析 |
| 2. Invariance check | clean stems | 判断 context 是否不应改变答案 | invariant stems | 2/3 annotators agree |
| 3. Context injection | invariant stems | 注入 evaluation / social / observer / role framing | context variants | 不改变事实条件 |
| 4. Ambiguity filtering | variants | 标注 ambiguity 和 pressure direction | validated variants | ambiguity 低或中 |
| 5. Pilot run | validated variants | 跑 3 模型、2 seeds | pilot logs | parser 成功率 >= 95% |
| 6. Metric audit | pilot logs | 计算 drift 与 paraphrase noise | pilot report | drift 显著高于噪声 |
| 7. Scale-up | passed design | 扩到 300 stems / 60 scripts | v1 dataset | 分布平衡 |

### API-only 实现原则

每个 prompt 强制输出结构化 JSON：

```json
{
  "answer": "A",
  "confidence": 0.72,
  "brief_reason": "one sentence"
}
```

评分只依赖：
- `answer`
- 是否遵循格式
- 可选 `confidence`
- 可选一句话 rationale 的标签分析

不要把长 CoT 放进主评测。长 CoT 会增加成本，也会把任务变成“模型如何表演推理”。

## 9. Research Questions

RQ1: How much do current LLMs' judgments drift under controlled social, evaluative, and conversational context changes?

RQ2: Which context types induce the strongest drift, and are their effects transient or persistent across turns?

RQ3: Do stronger models exhibit better judgment stability and recovery, or are they equally or more sensitive to context?

更贴合初心的 RQ 写法：

RQ1: Do current LLM benchmark scores satisfy context-retest reliability under controlled context changes?

RQ2: Which context families most strongly violate situational consistency: social pressure, evaluation framing, or multi-turn accumulation?

RQ3: When context-induced deviation occurs, can models recover after neutralization, or does the deviation persist?

可选 RQ4, 放 appendix：

RQ4: Can lightweight API-observable signals such as answer instability, confidence drift, and validation language predict later multi-turn recovery failure?

原来的 white-box RQ 不进入 v1。NLA / TRACE / persona vectors 只在 Related Work 和 Future Work 中出现。

## 10. Pilot Go / No-Go 判据

### Go

满足下面四条，进入 v1 scale-up：

1. 至少一个 track 的 drift 明显高于 neutral paraphrase noise。
2. social pressure 或 multi-turn track 中，至少 2/3 模型出现方向一致的 drift。
3. Parser 成功率 >= 95%，无大量无法解析回答。
4. 人工检查样本中，至少 80% 被认为 context 不应合理改变答案。
5. 所有主指标都能在无 logprobs、无 activation、无 GPU 的 API-only 条件下计算。

### Revise

出现下面情况，先修数据，不急着扩：

1. drift 存在但大量来自题目歧义。
2. 不同 annotator 对 pressure direction 分歧大。
3. 模型回答过多 free-form，导致自动解析不稳定。
4. social pressure 效果强，但 context swap 效果弱。

### Pivot

出现下面情况，应缩成更窄论文：

1. 所有 drift 都接近 neutral paraphrase noise。
2. 只有 social pressure track 稳定有效。
3. multi-turn recovery 指标噪声过大，无法复现。

对应 pivot 方向：
- 如果只有 social pressure 有效：改名为 **Social Pressure Drift Bench**。
- 如果只有 multi-turn 有效：改名为 **Context Accumulation Drift Bench**。
- 如果只有 evaluation/observer 有效：改名为 **Evaluation Awareness Drift Bench**。

## 11. 8 周开工路线

| Week | 目标 | 产出 |
|---|---|---|
| 1 | 冻结 taxonomy 和 schema | 50 pilot stems + annotation guide |
| 2 | 完成 context injection 和 QC | pilot dataset jsonl |
| 3 | 跑 3 个模型 pilot | raw logs + parser |
| 4 | 指标实现和 pilot report | go/no-go 决策 |
| 5 | scale 到 300 stems / 60 scripts | v1 dataset draft |
| 6 | 跑 5-8 模型 | full result tables |
| 7 | fine-grained analysis + case studies | Finding 1-4 |
| 8 | 写 benchmark paper skeleton | intro + method + experiments draft |

## 12. Paper Skeleton

### Figure 1: Running Example

同一个判断题展示四种条件：
- Neutral
- User pressure
- Evaluation framing
- Multi-turn accumulated framing

图中直接展示模型答案从 B 漂到 A，再在 correction 后是否恢复。

### Table 1: Benchmark Comparison

列比较：
- 是否测同题上下文漂移
- 是否有 neutral baseline
- 是否有 social pressure
- 是否有 multi-turn accumulation
- 是否有 recovery metric
- 是否支持 black-box frontier models

### Contributions

1. We define context-induced judgment drift as a new evaluation dimension for LLM reliability.
2. We construct Deviation Bench, a controlled-injection benchmark covering context swap, social pressure, and multi-turn accumulation.
3. We introduce API-only reliability metrics that measure context-retest reliability, deviation beyond paraphrase noise, directional pressure, persistence, and recovery.
4. We evaluate current LLMs and show that model judgments are trajectories under context, not fixed points under static prompts.

## 13. 当前最小可行版本

如果今天就开工，最小可行版本是：

```text
Benchmark name: Deviation Bench
Version: pilot-v0
Tracks: Context Swap, Social Pressure, Multi-turn Recovery
Dataset: 50 stems + 20 multi-turn scripts
Models: 3
Main metric: context-retest reliability + deviation index + recovery reliability
Control: neutral paraphrase noise
Compute: LLM API only, no training, no GPU
Decision date: pilot 完成后一周内
```

这版已经足够回答“这个 idea 是否真的可行”。如果 pilot 过关，再扩成 paper v1；如果 pilot 不过关，按第 10 节 pivot，不继续烧时间。

## 14. 最终优化后的可行方向

**推荐方向名：Deviation Bench: Measuring Context-Retest Reliability of LLM Judgments**

最可行的论文不是“用白盒方法解释模型为什么漂”，而是：

> 用轻量、可复现、API-only 的 controlled benchmark，检验当前 LLM 评估默认的 situational consistency 假设是否成立，并提出 context-retest reliability、deviation index 和 recovery reliability 三个无需 GPU 的指标。

这个方向保留了你的研究初心，同时避开了高 GPU、高工程复杂度和伦理高风险场景。
