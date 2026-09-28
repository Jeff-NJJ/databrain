# 03｜情感(affect) 与 情绪(emotion) 的关系：为「数据化大脑」长期记忆系统建立心理学证据

> 本文目标：在「数据化大脑」当前采用 **Russell 效价–唤醒（valence–arousal, VA）二维圆环模型** 并让 arousal 调节忘忆曲线衰减速度的设计基础上，厘清（1）affect 与 emotion 在学术上的真实关系，（2）连续坐标 vs 离散标签之争对 AI 建模的含义，（3）VA 二维结构的具体内容、局限与记忆效应证据，最终给出可落地的打标与参数化建议。

---

## 0. 开宗明义：情感 vs 情绪 的关系判定

**判定结论：affect 与 emotion 不是简单的上下位关系，而是在不同理论传统下「可通约但有重叠」的概念；在 Russell–Barrett 的建构主义传统里，二者是「原材料（core affect）—范畴化产物（emotion episode）」的加工阶段关系；在基本情绪论（Ekman、Izard）传统里，emotion 被当作先天的、离散的「自然类（natural kind）」，而 affect 只是其主观色调，二者近乎不可通约。**

对 AI 建模最关键的取法是 Russell–Barrett 框架：**core affect（核心情感 = 效价 × 唤醒的持续波动）是底层连续坐标，emotion（情绪）是事后用概念/文化范畴对 core affect 及其情境所做的解读**。因此「先有连续坐标、后有离散标签」在心理学上站得住脚。

| 概念 | 经典定义（含代表来源） | 与 emotion 的关系 | 在 AI 中的可取形态 |
|---|---|---|---|
| **Affect（情感／情动）** | 最广义的「具有效价色调的感受性状态」，含 mood、core affect、情感特质。Russell & Barrett (1999)：核心情感是「可被意识触及的、最简单的基本感受（愉快/不愉快、紧张/放松），未必指向任何对象」 | 上位/容器概念；emotion 是 affect 被情境化、范畴化后的一种形态 | 连续向量 (valence, arousal[, dominance]) |
| **Core affect（核心情感）** | Russell (2003)：「一种神经生理状态，被意识可及地体验为愉悦–不愉悦与唤醒–困倦的整合」；时刻存在、自由浮动 | emotion 的原材料；情绪发作（episode）始于 core affect 变化 | 连续坐标 + 时间戳的时序流 |
| **Emotion（情绪）** | Russell & Barrett (1999)：典型情绪发作（prototypical emotional episode, PEE）含 core affect + 行为改变 + 注意 + 评价 + 主观感受 + 生理变化；Barrett (2006a) 视其为「概念化建构物」 | 由 core affect 经范畴化/评价生成；非先天模块 | 离散标签（如 anger, fear）作为对坐标+情境的高层注释 |
| **Feeling（感受）** | Damasio (1999)：对身体状态的知觉；情绪(身体反应/倾向)被脑「感受」为主观体验 | feeling 是 emotion 的主观面，emotion 是 feeling 的生态行为面 | 主观报告/可观测体征的映射 |
| **Mood（心境）** | 低强度、长时程、对象模糊的 affect；常被视为「无明确起因的、自由浮动的 core affect」 | emotion 的弱/弥散版；emotional episode 的延长态 | 低 arousal、长半衰期的连续坐标 |
| **Affectivity（情感性）** | 个体在 affect 维度上的差异倾向（气质/人格层），如神经质=负性情感易感性 | 产生 emotion 的个体差异基底 | 用户画像的先验（persona prior） |

**分歧总览（各家对「情感与情绪」的根本分歧点）：**
- **离散 vs 连续**：Ekman、Izard 认为存在少数先天、普遍、离散的基本情绪；Russell、Barrett 认为基本感受是连续的 VA 坐标，离散情绪是文化/概念建构。
- **先天模块 vs 心理建构**：基本情绪论主张情绪有专属神经回路（如恐惧↔杏仁核）；建构论（Barrett 2017 的 constructed emotion）主张情绪由内感受预测 + 概念知识「实时组装」，无专属回路。
- **评价（appraisal）是否必要**：Lazarus、Scherer 认为认知评价是情绪生成的必要前提；Zajonc、Barrett 认为 affect 可独立于高级认知产生。
- **层级 vs 平面**：Scherer 的组件加工模型（CPM）把情绪拆成多子系统同步，既含连续维度也含离散成分，是调和二者的一条中间路线。

---

## 1. 概念区分与各家的分歧点

### 1.1 Russell 的情感环丛（circumplex）与 core affect
Russell (1980) 用多方法（相似评定、主成分分析等）证明，日常情绪形容词在「愉悦–不愉悦 × 唤醒–困倦」二维圆上成序排列。Russell & Barrett (1999) 进一步区分 **core affect**（人人时刻都处在某种状态）与 **prototypical emotional episode**（有对象、有起因、有评价的完整情绪发作）。二者的关键分歧点在于：环丛只能描述 core affect 的「共通部分」，无法区分同处环上同一点但本质不同的情绪（如 fear 与 anger 都是「负效价 + 高唤醒」，但行为倾向相反）。

### 1.2 Barrett 的建构主义（constructed emotion）
Barrett (2006a, 2006b, 2017) 主张：情绪不是被「触发」的先天反应，而是大脑用概念系统对 interoceptive（内感受）信号做范畴化（categorization）的产物。core affect 是原材料，**emotion = core affect + 情境概念化**。证据来自 fMRI 元分析（Lindquist et al., 2012，未在本次检索逐条核实，列作背景）：不存在「一个脑区=一种情绪」的映射。分歧点：与 Ekman 的直接对立——Barrett 否认情绪是 natural kind。

### 1.3 Ekman 的基本情绪论（basic emotions）
Ekman (1992a, 1992b) 论证存在 6 种跨文化普遍可辨的基本情绪（anger, disgust, fear, happiness, sadness, surprise；后增 contempt），其判据为：独特的普遍面部表情、跨文化一致性、先天性、特定生理模式、特定前因事件、快速自发出现、短暂。分歧点：认为离散类别先于且独立于连续维度。

### 1.4 Izard 的微分情绪理论（Differential Emotions Theory, DET）
Izard (1977, 1991, 2007) 列出约 10–12 种基本情绪（含 interest, shame, guilt, contempt 等），强调每种情绪是相对独立的神经–行为系统，可组合成复杂情绪。分歧点：比 Ekman 更强调动机/人格层面，但与 Ekman 同属「离散先天派」。

### 1.5 Frijda
Frijda (1986, 2007) 以「行动倾向（action tendency）」为核心：情绪是「指向目标对象的、伴有特定行为准备的状态」（如恐惧→退缩）。其「情绪法则」强调情绪与意义评价、情境约束的耦合，立场介于离散与连续之间。

### 1.6 Scherer 的组件加工模型（Component Process Model, CPM）
Scherer (2001, 2005) 把情绪定义为「五个有机体子系统（认知评价、生理支持、动机、表情表达、主观感受）在应对相关事件时的暂时性同步」。评价通过 **刺激评价核查（Stimulus Evaluation Checks, SECs）** 分四功能类展开：相关性（Relevance）、意涵（Implications）、应对潜能（Coping Potential）、规范意义（Normative Significance）。CPM 是对「连续维度 + 离散情绪 + 评价」最系统的整合，分歧点最小但最复杂。

### 1.7 Damasio
Damasio (1999, 2003) 区分 **emotions**（身体层面的自动反应/倾向，含「背景感受 background feeling」与「初级/次级情绪」）与 **feelings**（对这些身体状态的意识知觉）。其视角把 affect 锚定在身体内感受，与 Barrett 的内感受预测论相通，但与纯认知评价派（Lazarus）相对。

---

## 2. 情感先于情绪？连续坐标 vs 离散标签

**Barrett 的「先有原材料后有范畴」论：**
- 核心证据：婴儿与跨语言群体都能报告 valence/arousal 的连续感受，但离散情绪词高度依赖语言与文化范畴（Russell, Lewicka & Niit, 1989；Yik et al., 2011 跨文化验证）。
- 神经证据：内感受感知（insula、ACC）是情绪体验的共享基底，而非每情绪专属回路（Barrett 2017）。
- 推论：AI 应先用连续坐标记录「状态」，再用概念层打离散标签。

**基本情绪论的「先有离散先天模块」论：**
- 核心证据：6 种基本情绪的面部表情在巴布亚新几内亚孤立部落与工业社会间具跨文化一致性（Ekman 1972/1992）；杏仁核损伤选择性损害恐惧相关学习（LeDoux 系；Cahill et al., 1995）。
- 推论：AI 应直接用离散类别（或少量原型）作为记忆索引。

**对建模的直接后果：**
1. 若采用 Barrett 路线 → 内存里情绪 = `(valence, arousal, dominance?)` 连续向量 + 时间戳 + 后来追加的 `label`（anger/fear…）。这天然兼容你已用的 VA 圆环与 arousal 调节衰减。
2. 若采用 Ekman 路线 → 内存标签应是 6–12 个离散槽位。
3. 折中（推荐）：**连续坐标为底层存储，离散标签为可选项注释**——既保留「情感先于情绪」的时间/因果序，又不丢失离散可检索性。

---

## 3. Russell 圆环模型（VA 二维）的具体内容

**二维轴定义（Russell 1980）：**
- **效价 Valence（愉悦–不愉悦）**：横轴，0°=愉悦，180°=不愉悦。
- **唤醒 Arousal（激活–困倦）**：纵轴，90°=高唤醒/激活，270°=低唤醒/困倦。

**八分位（octants）与角度（Russell 1980 原文锚点）：**
0° 愉悦(pleasure) → 45° 兴奋(excitement) → 90° 唤醒(arousal) → 135° 苦恼(distress) → 180° 不愉悦(displeasure) → 225° 抑郁(depression) → 270° 困倦(sleepiness) → 315° 放松(relaxation)。

**「90°/180° 假设」与圆环结构要求：**
- 圆环（circumplex）要求：相隔 90° 的变量**不相关**，相隔 180° 的变量**最大负相关**（互斥）。
- 但实证检验发现结构常呈**椭圆而非正圆**（2021 年系统检验：arousal 维度系统性偏离，实为 ellipse）——意味着 VA 未必严格正交、等距，建模时不宜假设均匀圆对称（Kuppens et al., 2013 亦发现 valence 与 arousal 之间呈弱 V 形而非恒定独立）。

**45° 旋转假设（45-degree rotation hypothesis）：**
Russell (1979)、Watson & Tellegen (1985)、Larsen & Diener (1992) 指出，多种维度模型的「主成分轴」其实是同一 VA 空间旋转 45° 的版本。即 **PANAS 的正性情感（PA）/负性情感（NA）轴，恰落在圆环的两条对角线上（45° 与 225°）**——这是圆环与 PANAS 的几何关系（见第 4 节）。

### 3.1 Russell 圆环上典型情感词的 valence/arousal 坐标表示例（可用作 AI 打标参考）
> 下表坐标为**示意值**：由环上角度几何推导（V=cosθ, A=sinθ，范围 −1~+1），便于直接做向量打标；真实标注请以评分常模（ANEW / Warriner et al. 2013 / 汉语情感词系统）校准。

| # | 角度° | 英文词 | 中文建议译法 | Valence | Arousal | 备注 |
|---|---|---|---|---|---|---|
|1|0|Happy / Pleased|高兴 / 愉快|+1.00|0.00|正效价中性唤醒|
|2|15|Blissful / Joyful|幸福 / 喜悦|+0.97|+0.26|高正效价轻唤醒|
|3|30|Delighted|欣喜|+0.87|+0.50| |
|4|45|Excited / Enthusiastic|兴奋 / 热情|+0.71|+0.71|第一象限代表|
|5|60|Astonished / Elated|惊讶 / 兴高采烈|+0.50|+0.87| |
|6|75|Energetic / Lively|精力充沛 / 活泼|+0.26|+0.97| |
|7|90|Alert / Tense / Activated|警觉 / 紧张 / 被激活|0.00|+1.00|纯高唤醒|
|8|105|Nervous / Anxious|焦虑 / 紧张|-0.26|+0.97|负效价高唤醒|
|9|120|Afraid / Alarmed|恐惧 / 惊恐|-0.50|+0.87| |
|10|135|Distressed / Upset|苦恼 / 心烦|-0.71|+0.71| |
|11|150|Angry / Hostile|愤怒 / 敌意|-0.87|+0.50|愤怒：负效价中高唤醒|
|12|165|Frustrated / Annoyed|沮丧 / 恼火|-0.97|+0.26| |
|13|180|Sad / Unhappy / Miserable|悲伤 / 不快|-1.00|0.00|负效价中性唤醒|
|14|195|Despair / Hopeless|绝望 / 无助|-0.97|-0.26| |
|15|210|Guilty / Ashamed|内疚 / 羞耻|-0.87|-0.50| |
|16|225|Depressed / Blue|抑郁 / 低落|-0.71|-0.71|第三象限代表|
|17|240|Bored / Dull|无聊 / 乏味|-0.50|-0.87| |
|18|255|Weary / Tired|疲惫 / 疲倦|-0.26|-0.97| |
|19|270|Sleepy / Quiet|困倦 / 安静|0.00|-1.00|纯低唤醒|
|20|285|Tranquil / Serene|安宁 / 安详|+0.26|-0.97| |
|21|300|Calm / Satisfied|平静 / 满意|+0.50|-0.87| |
|22|315|Relaxed / Content|放松 / 满足|+0.71|-0.71|第四象限代表|
|23|330|Glad / At ease|乐意 / 自在|+0.87|-0.50| |
|24|345|Cheerful / Amused|快活 / 开心|+0.97|-0.26| |

**局限与批评：**
- **区分力不足**：fear 与 anger 同落「负效价+高唤醒」，需第三维 dominance 才能分开（Mehrabian & Russell 1974 的 PAD；anger 偏支配 dominate，fear 偏顺从 submit）。
- **结构与文化**：中文等文化里「正性激活（ideal affect）」偏好不同（Tsai 等），环的椭圆度受文化差异调制（Yik et al. 2011）。
- **VA 非恒定独立**：Kuppens et al. (2013) 发现二者总体呈弱 V 形，且个体/文化差异大，建模不要把 VA 当静态正交基底。

---

## 4. 维度模型 vs 离散模型的其他版本

### 4.1 PAD 模型（Mehrabian & Russell）
PAD = **Pleasure（愉悦度）– Arousal（激活度）– Dominance（优势度/支配度）**。Mehrabian & Russell (1974) 源自环境心理学（物理环境经情感冲击影响人），后被 Lang 用于生理情绪理论。三维度可解释情绪量表大部分方差（P 27%、A 23%、D 14%）。示例坐标：anger ≈ (−0.51, +0.59, +0.25)，即负效价、高唤醒、高支配；fear 则为低支配。**对你系统的含义：若需区分「同点不同质」的情绪，加 dominance 第三维成本很低、收益明显。**

### 4.2 PANAS 与「双因素结构」（Watson & Tellegen）
Watson & Tellegen (1985) 提出情绪两主因素 **PA（正性情感， energetic/enthusiastic）** 与 **NA（负性情感， distressed/upset）**；Watson, Clark & Tellegen (1988) 给出 PANAS 量表。关键发现：**PA 与 NA 是相对独立的两条轴（双变量 bivariate），而非单极的两头**。

### 4.3 效价的「双极（bipolar）vs 双变量（bivariate）」之争
- **Russell 圆环**把 valence 当单极连续体（愉悦↔不愉悦互斥）。
- **Watson/Tellegen 与 Barrett & Russell (1998)** 主张正/负情感是**两个可分离基底**（Cacioppo & Berntson 1994 的「评价空间可分离性」亦支持），人可同时又开心又焦虑。
- **Russell & Carroll (1999)** 则辩护双极性。
- **对 AI 的取舍**：若允许「混合情感」（mixed feelings），应存 (PA, NA) 或 (val+, val−) 双通道，而非单值 valence；若只存单 valence，会丢失混合态信息（如「兴奋又紧张」）。

### 4.4 圆环 ↔ PANAS 关系
几何上 PA 轴 ≈ 圆环 315°方向、NA 轴 ≈ 135°方向，即相对 valence/arousal 轴**旋转 45°**（45°旋转假设）。故二者是可互相线性变换的同一空间的不同投影，不要当成互斥理论。

### 4.5 中文资源
- **汉语情感词系统（CAWS）**：王一牛、周立明、罗跃嘉（2008）《汉语情感词系统的初步编制及评定》，心理学报——提供中文词在愉悦度/激活度/优势度的常模评分，可直接替换为上表的 empirical 坐标。〔DOI/具体卷页待核实，使用前请核对〕
- **中国情绪图片系统（CAPS）**：白露、马慧、黄宇霞、罗跃嘉（2005），中国心理卫生杂志。〔DOI 待核实〕

---

## 5. 情绪的生成机制

### 5.1 评价理论（Appraisal Theory）
- **Lazarus (1991) / Lazarus & Folkman (1984)**：初级评价（事件对己利害）+ 次级评价（应对能力）；情绪由评价引出。
- **Scherer (2001) CPM**：SECs 四功能类（相关性/意涵/应对潜能/规范意义）顺序核查，驱动多子系统同步。
- **Ellsworth & Scherer (2003)**：评价维度（新奇、确定性、意向性、动机一致性等）决定情绪类型与强度。
- 含义：emotion 不是「刺激→情绪」的硬连线，而是「刺激→意义评价→情绪」，故记忆中的情绪标签应绑定「评价了什么」而不仅是「感受如何」。

### 5.2 情绪的主要成分（综合 Scherer CPM 与 Russell & Barrett 1999）
一次情绪发作 = **刺激事件 → 评价 → 生理变化（自主/神经内分泌）→ 表情表达 → 行为倾向（action tendency）→ 主观感受（core affect 被范畴化）**。你的长期记忆若只存「感受坐标」，会丢掉评价与行为倾向；建议至少追加 `appraisal_tags`（如 威胁/损失/挑战）与 `action_tendency`（接近/回避）。

### 5.3 情绪调节（Gross 过程模型）
Gross (1998a, 1998b) 提出五阶段调节：**情境选择 → 情境修改 → 注意分配(attention deployment) → 认知重评(cognitive reappraisal) → 表达抑制(response suppression)**。Gross (2015) 扩展为「扩展过程模型」：调节可发生在生成前/中/后。**对你系统的含义**：用户后来的「认知重评」会改变同一记忆的情绪坐标——应允许记忆的 valence/arousal 随重评而更新（带版本/时间戳），而非冻结初值。

---

## 6. 情绪对认知的影响

- **情绪一致性效应（mood congruency）**：Bower (1981) 经典发现，当下心境偏向编码/提取与心境一致的材料（快乐时更易回忆快乐事）。→ 检索时宜用「当前 core affect」做相似性偏置。
- **情绪依赖记忆（mood-dependent memory）**：状态依存记忆——提取时情绪状态与编码时越接近，提取越好（Bower 1981；Eich 1995 系）。→ 你的检索可把「编码时 VA」与「查询时 VA」的接近度作为相关性加分项。
- **情绪 Stroop 干扰**：对威胁/负性词的颜色命名更慢（Williams, Mathews & MacLeod 1996）。→ 负性高唤醒内容会在「注意力层面」抢占资源，对应记忆的优先固化。
- **拓展–建构理论（broaden-and-build）**：Fredrickson (2001) 与 Fredrickson & Branigan (2005) 证明正性情绪**拓宽**注意与思维–行动 repertoires，长期建构资源；负性情绪则**收缩**到局部/具体威胁。→ 正性记忆利于「发散/联想」检索，负性记忆利于「聚焦/细节」检索。
- **焦虑对工作记忆的占用（Processing Efficacy Theory）**：Eysenck & Calvo (1992)；Eysenck, Derakshan, Santos & Calvo (2007) 的注意控制理论：焦虑通过「担忧」占用工作记忆容量、**降低加工效能（processing efficiency）但不一定降低成绩（effectiveness）**（因代偿性努力）。→ 高焦虑态下，记忆的「编码带宽」下降，应下调单次写入的信息密度。

---

## 7. 效价与唤醒怎样分别影响记忆（重点）

### 7.1 高唤醒是否「总是」增强记忆？
**不是。** 机制上：情绪唤醒经 **杏仁核→蓝斑–去甲肾上腺素（noradrenaline）/ 皮质醇系统** 调制海马巩固（McGaugh 2004 的 memory modulation hypothesis）。实验因果证据强：学习情绪材料前服用 **β 受体阻滞剂普萘洛尔（propranolol）** 可消除情绪性记忆增强（Cahill, Prins, Weber & McGaugh 1994；杏仁核损伤患者表现一致，Cahill et al. 1995）。
- **一致性结论**：中等强度唤醒（尤其负性）**增强巩固**；但**过高唤醒可损害**编码带宽与外围细节（见隧道记忆），且对「来源/绑定」细节未必有益。

### 7.2 负性 vs 正性的差异
- **负性偏向（negativity bias）**：Baumeister et al. (2001)「bad is stronger than good」综合 200+ 研究；负性信息被更深编码、更慢遗忘、更易传播。
- ** meta 证据**：Murphy & Isaacowitz (2008) 对记忆/注意任务的 meta 分析显示，年轻人对负性（相对中性）的记忆偏好 **Cohen's d ≈ 0.60**，老年人降至 **d ≈ 0.28**（老化 positivity effect）。
- 但**正性高唤醒**（如极度愉快）也能增强记忆，只是效应通常弱于同等唤醒的负性刺激（Ochsner 2000 报告负性项目回忆的「记得感」更强）。

### 7.3 隧道记忆（tunnel memory）
高唤醒 + 负效价 → **中心细节增强、外围细节受损**。证据链：
- Christianson (1992) 综述：情绪应激下对中心/情绪相关细节记忆更好、外围更差。
- Safer, Christianson, Autry & Österlund (1998)：创伤性场景的「隧道」来自对关键细节的精细加工 + 注意边界收窄。
- Berntsen (2002)：自传记忆中「震惊事」中心细节比「快乐事」更多被记住——恐惧比幸福更易触发隧道。
- Burke, Heuer & Reisberg (1992)：情绪事件的中心信息回忆优势。
- 神经机制：杏仁核在情绪编码时「聚焦」中心(gist)信息，牺牲外围（Adolphs et al. 2005 系，见 PMC 综述）。

### 7.4 可量化效应量（近年 meta 分析）
Pereira, Teixeira-Santos, Sampaio & Pinheiro (2023) 对 **53 项研究 / 85 实验 / N=3,040** 的「来源记忆（source memory）」meta 分析给出明确 d：
- **唤醒（arousal）**：高 vs 低唤醒 来源记忆 d=**+0.27**；中 vs 低唤醒 d=**+0.49**（即唤醒越高、来源记忆越好，但高 vs 中无显著差异 d=−0.12）。
- **效价（valence）**：负性 vs 中性 来源记忆 d=**−0.14**；正性 vs 中性 d=**−0.11**（即情绪反而**损害**来源/绑定细节——与「项目记忆增强」形成对照）。
> 解读：情绪**增强「项目/item」记忆、却削弱「来源/source（何人何时何地）」记忆**。这正是隧道记忆在量化上的体现——中心(item)强、外围(source)弱。

### 7.5 给你的「Eclipse 参数」调参方向表
下表把 valence/arousal 对记忆三阶段的影响方向与证据强度汇总，**直接对应你用 arousal 调衰减速度的忘忆曲线**：

| 维度 | 编码(encoding) | 巩固(consolidation) | 提取(retrieval) | 证据强度 | 对你系统的参数建议 |
|---|---|---|---|---|---|
| **Arousal 高** | 注意捕获↑、精细加工↑（对中心） | 去甲肾上腺系强化海马巩固↑（Cahill/McGaugh） | 高唤醒线索更易被提取（优先） | 强（有药理因果证据） | **衰减率 k 乘 (1−α·arousal)**：高唤醒→k↓（更慢遗忘）；建议 α≈0.3–0.5 并设上限，避免「过高唤醒」反而因编码带宽下降而失真 |
| **Arousal 低** | 加工浅、易_gate out | 巩固弱 | 提取弱、易被覆盖 | 强 | k 接近基线或略升 |
| **Valence 负** | 负性偏向编码、隧道（中心↑外围↓） | 负性巩固强于正性（negativity bias, d≈0.60 年轻） | 负性记忆更易被调出、更慢遗忘 | 强 | 对「中心细节」额外降 k；同时对「来源/外围」标签**加衰减或降权重**（隧道效应） |
| **Valence 正** | 拓展注意、联想增强 | 巩固增强但弱于同唤醒负性 | 在积极心境下易提取（mood congruency） | 中–强 | 降 k 幅度可小于同唤醒负性；正性高唤醒利于「联想/发散」检索加权 |
| **Valence × Arousal 交互** | 负+高唤醒=最强中心增强+最强外围损伤 | 同左 | 隧道记忆显著 | 强 | 用 (valence<0 ∧ arousal>阈值) 触发「tunnel flag」：中心项长半衰期、外围项短半衰期 |
| **混合/重评** | 认知重评改写坐标 | 重评后巩固按新坐标 | 按最新坐标检索 | 中 | 允许 valence/arousal 带时间戳与版本，检索按「最近一次重评值」而非初值 |

**具体公式化提示（供实现参考，非心理学结论）：**
- 基础忘忆曲线 `R(t)=exp(−k·t)`；令 `k' = k·(1 − α·arousal_sat)·(1 + β·tunnel_penalty_for_peripheral)`，其中 `arousal_sat=min(arousal, cap)`，`tunnel_penalty` 仅在 `valence<0 ∧ arousal>θ` 且该项目被标为 peripheral 时非零。
- dominance 第三维：当需区分 anger/fear 等同 VA 点情绪时，作为离散 `label` 或第三坐标存储，**不参与衰减调制**（现有证据未显示 dominance 直接调制遗忘）。

---

## 8. 结论与对「数据化大脑」的建模建议（≤250 字）

**建议：采用「连续坐标为主、离散标签为辅」的混合架构。** 理由：心理学证据（Russell–Barrett）显示 core affect（VA 连续坐标）是情绪发作的原材料、先于且独立于离散情绪；基本情绪论的离散先天模块证据不足以否定连续底层。落地上：①底层用 `(valence, arousal[, dominance])` 连续向量 + 时间戳存每条记忆的瞬时情感；②离散标签（anger/fear…）作为可选高层注释，绑定「评价标签+行为倾向」；③arousal 调衰减：高唤醒→慢遗忘，但设上限并对「负效价×高唤醒」触发隧道效应（中心长半衰、外围短半衰）；④允许坐标随认知重评版本化更新；⑤正/负情感建议双通道存储以容纳混合情感。这样既守住你现有的 VA 圆环设计，又补上「情感先于情绪」的因果序与隧道记忆的精细衰减。

---

## 参考文献（(作者, 年份, 期刊) + DOI；未核实者已标注）

- Barrett, L. F. (2006a). Are emotions natural kinds? *Perspectives on Psychological Science, 1*(1), 28–58. https://doi.org/10.1111/j.1745-6916.2006.00003.x
- Barrett, L. F. (2006b). Solving the emotion paradox: Categorization and the experience of emotion. *Personality and Social Psychology Review, 10*(1), 20–46. https://doi.org/10.1207/s15327957pspr1001_2
- Barrett, L. F. (2017). The theory of constructed emotion: An active inference account of interoception and categorization. *Social Cognitive and Affective Neuroscience, 12*(1), 1–23. https://doi.org/10.1093/scan/nsw154
- Barrett, L. F., & Russell, J. A. (1998). Independence and bipolarity in the structure of current affect. *Journal of Personality and Social Psychology, 74*(4), 967–984. https://doi.org/10.1037/0022-3514.74.4.967
- Baumeister, R. F., Bratslavsky, E., Finkenauer, C., & Vohs, K. D. (2001). Bad is stronger than good. *Review of General Psychology, 5*(4), 323–370. https://doi.org/10.1037/1089-2680.5.4.323
- Berntsen, D. (2002). Tunnel memories for autobiographical events. *Memory & Cognition, 30*(7), 1010–1020. https://doi.org/10.3758/BF03194319
- Bower, G. H. (1981). Mood and memory. *American Psychologist, 36*(2), 129–148. https://doi.org/10.1037/0003-066X.36.2.129
- Burke, A., Heuer, F., & Reisberg, D. (1992). Remembering emotional events. *Memory & Cognition, 20*(3), 277–290. https://doi.org/10.3758/BF03199665
- Cacioppo, J. T., & Berntson, G. G. (1994). Relationship between attitudes and evaluative space… *Psychological Bulletin, 115*(3), 401–423. https://doi.org/10.1037/0033-2909.115.3.401
- Cahill, L., Babinsky, R., Markowitsch, H. J., & McGaugh, J. L. (1995). The amygdala and emotional memory. *Nature, 377*, 295–296. https://doi.org/10.1038/377295a0
- Cahill, L., Prins, B., Weber, M., & McGaugh, J. L. (1994). β-adrenergic activation and memory for emotional events. *Nature, 371*, 702–704. 〔具体 DOI 待核实，请核对原文〕
- Christianson, S.-Å. (1992). Emotional stress and eyewitness memory: A critical review. *Psychological Bulletin, 112*(2), 284–309. https://doi.org/10.1037/0033-2909.112.2.284
- Damasio, A. R. (1999). *The Feeling of What Happens: Body and Emotion in the Making of Consciousness*. Harcourt. 〔专著，无 DOI〕
- Damasio, A. R. (2003). *Looking for Spinoza: Joy, Sorrow, and the Feeling Brain*. Harcourt. 〔专著，无 DOI〕
- Ekman, P. (1992a). An argument for basic emotions. *Cognition and Emotion, 6*(3–4), 169–200. https://doi.org/10.1080/02699939208411068
- Ekman, P. (1992b). Are there basic emotions? *Psychological Review, 99*(3), 550–553. https://doi.org/10.1037/0033-295X.99.3.550
- Ellsworth, P. C., & Scherer, K. R. (2003). Appraisal processes in emotion. In R. J. Davidson, K. R. Scherer, & H. H. Goldsmith (Eds.), *Handbook of Affective Sciences*. Oxford University Press. 〔专著章节，无 DOI〕
- Eysenck, M. W., & Calvo, M. G. (1992). Anxiety and performance: The processing efficiency theory. *Cognition and Emotion, 6*(6), 409–434. https://doi.org/10.1080/02699939208409696
- Eysenck, M. W., Derakshan, N., Santos, R., & Calvo, M. G. (2007). Anxiety and cognitive performance: Attentional Control Theory. *Emotion, 7*(2), 336–353. https://doi.org/10.1037/1528-3542.7.2.336
- Fredrickson, B. L. (2001). The role of positive emotions in positive psychology: The broaden-and-build theory. *American Psychologist, 56*(3), 218–226. https://doi.org/10.1037/0003-066X.56.3.218
- Fredrickson, B. L., & Branigan, C. (2005). Positive emotions broaden the scope of attention and thought-action repertoires. *Cognition and Emotion, 19*(3), 313–332. https://doi.org/10.1080/02699930441000238
- Frijda, N. H. (1986). *The Emotions*. Cambridge University Press. 〔专著，无 DOI〕
- Frijda, N. H. (2007). *The Laws of Emotion*. Erlbaum. 〔专著，无 DOI〕
- Gross, J. J. (1998a). Antecedent- and response-focused emotion regulation. *Journal of Personality and Social Psychology, 74*(1), 224–237. https://doi.org/10.1037/0022-3514.74.1.224
- Gross, J. J. (1998b). The emerging field of emotion regulation. *Review of General Psychology, 2*(3), 271–299. https://doi.org/10.1037/1089-2680.2.3.271
- Gross, J. J. (2015). The extended process model of emotion regulation. *Psychological Inquiry, 26*(1), 130–137. https://doi.org/10.1080/1047840X.2015.989751
- Izard, C. E. (1977). *Human Emotions*. Plenum. 〔专著，无 DOI〕
- Izard, C. E. (1991). *The Psychology of Emotions*. Plenum. 〔专著，无 DOI〕
- Izard, C. E. (2007). Basic emotions, natural kinds, emotion schemas, and a new paradigm. *Perspectives on Psychological Science, 2*(4). 〔DOI 待核实〕
- Kuppens, P., Tuerlinckx, F., Russell, J. A., & Barrett, L. F. (2013). The relation between valence and arousal in subjective experience. *Psychological Bulletin, 139*(4), 917–940. https://doi.org/10.1037/a0030811
- Lazarus, R. S. (1991). *Emotion and Adaptation*. Oxford University Press. 〔专著，无 DOI〕
- Lazarus, R. S., & Folkman, S. (1984). *Stress, Appraisal, and Coping*. Springer. 〔专著，无 DOI〕
- McGaugh, J. L. (2004). The amygdala modulates the consolidation of memories of emotionally arousing experiences. *Annual Review of Neuroscience, 27*, 1–28. https://doi.org/10.1146/annurev.neuro.27.070203.144157
- Mehrabian, A., & Russell, J. A. (1974). *An Approach to Environmental Psychology*. MIT Press. 〔专著，无 DOI〕
- Mehrabian, A. (1996). Pleasure–Arousal–Dominance: A general framework for describing and measuring individual differences in temperament. *Current Psychology, 14*(4), 261–292. https://doi.org/10.1007/BF02686918
- Murphy, N. A., & Isaacowitz, D. M. (2008). Preference for emotional information in older and younger adults: A meta-analysis. *Psychology and Aging, 23*(2), 263–286. https://doi.org/10.1037/0882-7974.23.2.263
- Pereira, D. R., Teixeira-Santos, A. C., Sampaio, A., & Pinheiro, A. P. (2023). Examining the effects of emotional valence and arousal on source memory. *Emotion, 23*(6), 1740–1763. https://doi.org/10.1037/emo0001188
- Posner, J., Russell, J. A., & Peterson, B. S. (2005). The circumplex model of affect: An integrative approach to affective neuroscience… *Development and Psychopathology, 17*(3), 715–734. https://doi.org/10.1017/S0954579405050340
- Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology, 39*(6), 1161–1178. https://doi.org/10.1037/h0077714
- Russell, J. A. (2003). Core affect and the psychological construction of emotion. *Psychological Review, 110*(1), 145–172. https://doi.org/10.1037/0033-295X.110.1.145
- Russell, J. A., & Barrett, L. F. (1999). Core affect, prototypical emotional episodes, and other things called emotion. *Journal of Personality and Social Psychology, 76*(5), 805–819. https://doi.org/10.1037/0022-3514.76.5.805
- Russell, J. A., & Carroll, J. M. (1999). On the bipolarity of positive and negative affect. *Psychological Bulletin, 125*(1), 3–30. https://doi.org/10.1037/0033-2909.125.1.3
- Safer, M. A., Christianson, S.-Å., Autry, M. W., & Österlund, K. (1998). Tunnel memory for traumatic events. *Applied Cognitive Psychology, 12*(2), 99–117. https://doi.org/10.1002/(SICI)1099-0720(199804)12:2<99::AID-ACP509>3.0.CO;2-7
- Scherer, K. R. (2001). Appraisal considered as a process of multilevel sequential checking… In K. R. Scherer, A. Schorr, & T. Johnstone (Eds.), *Appraisal Processes in Emotion*. Oxford University Press. https://doi.org/10.1093/oso/9780195130072.003.0005
- Scherer, K. R. (2005). What are emotions? And how can they be measured? *Social Science Information, 44*(4), 695–729. 〔DOI 待核实〕
- Watson, D., & Tellegen, A. (1985). Toward a consensual structure of mood. *Psychological Bulletin, 98*(2), 219–235. https://doi.org/10.1037/0033-2909.98.2.219
- Watson, D., Clark, L. A., & Tellegen, A. (1988). Development and validation of brief measures of positive and negative affect: The PANAS scales. *Journal of Personality and Social Psychology, 54*(6), 1063–1070. https://doi.org/10.1037/0022-3514.54.6.1063
- Williams, J. M. G., Mathews, A., & MacLeod, C. (1996). The emotional Stroop task and psychopathology. *Behaviour Research and Therapy, 34*(9), 675–683. https://doi.org/10.1016/0005-7967(96)00018-0
- Yik, M., Russell, J. A., & Steiger, J. H. (2011). A 12-point circumplex structure of core affect. *Emotion, 11*(4), 705–731. https://doi.org/10.1037/a0023980
- 王一牛、周立明、罗跃嘉（2008）。汉语情感词系统的初步编制及评定。*心理学报*。 〔卷页/DOI 待核实〕
- 白露、马慧、黄宇霞、罗跃嘉（2005）。中国情绪图片系统（CAPS）的建立。*中国心理卫生杂志, 19*(11)。 〔卷页/DOI 待核实〕

> 注明：Ekman (1972) 新几内亚跨文化面部表情原始研究、Lindquist et al. (2012) 情绪神经影像元分析、Tsai et al. (2006) 理想情感文化差、Adolphs et al. (2005) 杏仁核聚焦记忆、Warriner et al. (2013) 英语词情感常模 等作为背景证据在正文提及，其精确 DOI 未在本轮逐一核实，落地打标前建议补查。
