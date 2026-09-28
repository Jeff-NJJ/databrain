# 内分泌系统 × 记忆：关联证据与建模参数依据

> 文件用途：为「虚拟内分泌引擎」扩展"记忆"维度提供文献支撑。本文聚焦**激素如何调节记忆的编码（encoding）、巩固（consolidation）、提取（retrieval）/遗忘（forgetting）**，并给出可直接转化为参数的核心表与定量时间表。
> 说明：所有引用均经检索核实；凡无法确认卷期/页码/DOI 者，已在文末参考文献中以"具体卷期未核实"或"PMID 未核实"标注，**绝不编造**。效应量级中带 d 值为已发表元分析效应量（Cohen's d），其余为定性评级（小/中/大）。

---

## 1. 引言与总览

记忆并非由单一"存储容量"决定，而是被多种神经内分泌信号在**不同阶段**差异化地调制（modulation）。核心概念是：应激/情绪相关激素不会"整体提升或削弱"记忆，而是**依记忆阶段、受体亚型、基线水平、时刻（昼夜/上午 vs 下午）、情绪唤醒度而产生方向甚至相反的作用**。这正是"数据化大脑"引擎不能简单线性叠加激素浓度的根本原因——大量效应是非线性（倒 U 形/inverted‑U）或阶段分离的。

本文依次梳理：HPA 轴与皮质醇（重点）、情绪性记忆增强、多巴胺、去甲肾上腺素、催产素、血清素、褪黑素/昼夜节律、性激素、以及补充系统（乙酰胆碱、内源性大麻素、胰岛素/IGF、甲状腺素、BDNF）。

---

## 2. HPA 轴与皮质醇（Cortisol）—— 建模核心

### 2.1 级联与时间尺度
下丘脑 CRH → 垂体 ACTH → 肾上腺皮质醇（cortisol；啮齿类为皮质酮 corticosterone）。典型时间尺度：
- **CRH 释放**：秒级脉冲（pulsatile），应激触发后数秒内。
- **ACTH 上升**：静脉注射 CRH 后 10–30 分钟内升至基线 2–4 倍（ACTH 峰值约 30–60 min）。
- **皮质醇峰值**：应激（如 TSST 社会心理应激）后约 **20–30 分钟**达峰；静脉 ACTH/皮质醇给药后 30–60 min 达峰。
- **恢复**：皮质醇血浆半衰期约 60–90 min，行为/认知效应持续数小时；慢性高皮质醇（库欣、长期应激）则导致海马结构可塑性损害（小时→天→周尺度）。

### 2.2 倒 U 形（inverted‑U）与 GR/MR 双受体
皮质醇对记忆的作用呈**倒 U 形**：极低或极高浓度损记忆，中等浓度最优（Kovacs et al. 1976; Lupien & McEwen 1997; Reul & de Kloet 1985）。机制在于两种亲和力不同的糖皮质激素受体：
- **盐皮质激素受体（MR, mineralocorticoid receptor）**：高亲和力，即使在皮质醇昼夜低谷也被大量占据；主要参与**编码/appraisal（评价）与基础记忆效能**。
- **糖皮质激素受体（GR, glucocorticoid receptor）**：低亲和力，仅在皮质醇较高时（应激/上午）才被显著激活；主要参与**巩固（consolidation）增强**与**提取抑制**。

最优记忆出现在"MR 高占据 + GR 低占据"状态（de Kloet et al. 1998）。药物阻断实验直接验证：MR 拮抗剂螺内酯（spironolactone）损害提取（尤其情绪材料）；GR 拮抗剂米非司酮（mifepristone）反而**改善**中性图片提取（Het et al. 2012, Neuropsychopharmacology, 卷期未核实）。

### 2.3 编码 vs 提取的分离效应（重点！）
这是引擎最关键的建模点：
- **巩固（consolidation）**：急性应激/皮质醇**增强**巩固，且对**情绪唤醒材料**更强（Roozendaal 2002; de Quervain et al. 2017）。
- **提取（retrieval）**：高皮质醇**抑制**提取，且情绪材料受抑更甚（de Quervain et al. 2000; Wolf 2009）。注意：**编码与提取均受损**是常见误解——实际是"巩固↑ / 提取↓"的方向分离。
- **编码（encoding）**：急性皮质醇对编码的影响取决于基线——上午（高基线皮质醇）给药偏抑制，下午（低基线）偏增强（见 2.4 元分析）。

### 2.4 定量元分析证据（最关键的量级来源）
- **Het, Ramlow & Wolf (2005)** 对 16 项健康人急性皮质醇给药研究（N≈563）的元分析：
  - 给药于**提取前** → 显著损害，平均 **d = −0.49**。
  - 给药于**学习前**：整体 d = +0.08（无效应），但存在异质性：
    - **上午**研究 → 显著损害 **d = −0.40**；
    - **下午**研究 → 轻度增强 **d = +0.22**。
  → 直接证明"时刻×阶段"的交互，是引擎需建"时间窗口 + 昼夜相位"参数的硬证据。
- **Shields, Sazma, McCullough & Yonelinas (2017)** 对急性应激（含内源皮质醇升高）的元分析：应激在**编码前/提取前**削弱情景记忆，在**编码后（巩固期）**增强记忆——与给药时机范式一致，且效应与情绪效价无关（中性材料同样受益）。
- **Wolf (2009)**：应激/皮质醇对提取的阻断更强于中性材料的情绪唤醒材料，且 fMRI 显示海马活动下降是神经相关。

### 2.5 地塞米松抑制范式（dexamethasone suppression）
地塞米松（dexamethasone）是强效合成糖皮质激素，不结合皮质醇结合球蛋白、易入脑，通过负反馈抑制 HPA 轴。
- **过夜低剂量（1 mg，23:00 口服）**：次日 08:00–09:00 血皮质醇应降至 **< 1.8 µg/dL（≈50 nmol/L）**；敏感性 95%、特异性 80%（库欣筛查）。
- HPA 轴在单剂 1 mg 后约 **24 小时恢复**。
- 该范式可用于引擎：模拟"外源性 GC 负反馈抑制内源皮质醇→提取改善/情绪记忆减弱"的反直觉分支。
- 注意：高剂量（8 mg）地塞米松试验用于鉴别垂体来源 vs 肾上腺/异位来源库欣，抑制 >50% 指向垂体性。

---

## 3. 情绪性记忆增强（Emotionally Enhanced Memory, EEM）

### 3.1 杏仁核（尤其基底外侧杏仁核 BLA）调制海马巩固
情绪唤醒通过**去甲肾上腺素（NE）激活 BLA**，BLA 再上行调制海马巩固（McGaugh 2004; Roozendaal & McGaugh 2011）。BLA 本身**不存储**空间/陈述性记忆，而是"调制器"：损毁 BLA 或向 BLA 注入 β 阻断剂，可阻断糖皮质激素/应激对记忆的增强（Quirarte et al. 1997; Roozendaal & McGaugh 1997）。fMRI 显示编码时杏仁核‑海马耦合强度可预测延迟记忆保持（Ritchey, Dolcos & Cabeza 2008）。

### 3.2 β‑肾上腺素受体阻断剂（普萘洛尔 propranolol）的证据
- **Cahill, Prins, Weber & McGaugh (1994, Nature)**：健康人学习情绪 vs 中性故事前服 propranolol（40 mg），**仅情绪故事的长时记忆受损**，中性不受影响 → 证明情绪记忆增强依赖 β‑肾上腺素能系统。
- **Kroes, Strange & Dolan (2010, Biological Psychiatry)**：propranolol 在**提取时**给药亦可**持续削弱**陈述性情绪记忆增强（24h 后仍存）→ 提示 NE 不仅作用于编码/巩固，也作用于提取（具体卷期/PMID 未核实）。
- 机制经 BLA 而非单纯外周：中枢可透过的 propranolol 起效，但外周型 nadolol 在部分复制中未达显著，故存在争议（central vs peripheral 之争，部分研究未重复 Cahill 范式）。

### 3.3 GANE / 唤醒偏向竞争（arousal‑biased competition）
Mather 等的 **GANE 模型**：唤醒诱发 LC‑NE 释放，在谷氨酸共同释放的"热点（hotspot）"放大高优先级（显著/目标相关）表征并抑制低优先级表征（winner‑take‑more / loser‑take‑less）。这解释了"情绪既可致逆行性增强、也可致逆行性遗忘"的表观矛盾（Mather & Harley 2016）。

---

## 4. 多巴胺（Dopamine, DA）

### 4.1 VTA‑海马与 LC‑海马双通路
中脑 VTA 多巴胺能神经元投射至海马（尤其 CA1、DG），释放 DA 作为"第三因子/教学信号（teaching signal）"触发并维持 LTP（Duszkiewicz et al.; Lisman et al.）。
- **VTA‑海马**：响应**奖赏/预测误差相关新颖性**，时间窗窄，促进语义/情景记忆巩固。
- **LC‑海马（含 LC 神经元共释放 DA）**：响应**环境新颖性**，时间窗较宽（~1 hr），增强空间/物体记忆（Takeuchi et al.; Wagatsuma et al.）。

### 4.2 奖赏预测误差、新颖性/显著性（salience）
DA 编码"值得记住"的事件（奖赏、厌恶、新颖），通过**D1/D5 受体**将早期 LTP（E‑LTP）转化为依赖蛋白合成的晚期 LTP（L‑LTP），即把短期记忆"锁定"为长期（Frey & Morris; 多项海马 D1/D5 研究）。
- **D1/D5 受体**是维持 LTP 与记忆持久性的关键：DG‑D1 缺失损害情境恐惧记忆持久性；CA3–CA1 的 D5 缺失损害空间记忆。
- **多巴胺与遗忘/更新**：DA 亦参与"记忆更新（updating）"与习惯化转换——D1 样受体在背侧纹状体介导目标导向→习惯的转移，提示高 DA 可促进"旧记忆被新关联覆盖"。

### 4.3 量级
动物与人体一致显示 DA 缺失（PD、ADHD）损害情景/工作记忆；药理增强 D1/D5 可增强 LTP 与记忆持久性（量级多属中‑大，但 humans 直接效应量研究较少）。**注意：DA 对记忆多为阈值/增益式（非线性）作用**——过低或过高 D1 占据均损害（倒 U 形同样适用）。

---

## 5. 去甲肾上腺素（Norepinephrine, NE）

### 5.1 LC‑NE 系统与唤醒
蓝斑（locus coeruleus, LC）是脑内 NE 主要来源。LC 相位爆发（phasic burst）响应新颖/显著事件，释放 NE 至全脑。
- **唤醒（arousal）与记忆**：适度唤醒增强记忆（Yerkes‑Dodson 的 NE 版本）；过高唤醒则损害（应激性遗忘）。
- **Arousal‑biased competition（ABC）**：NE 偏置竞争，提升高显著性表征信噪比（Mather et al. 2015/2016 GANE；具体卷期未核实，理论源自 Mather & Harley 2016）。
- **NE 与情绪记忆巩固**：BLA 内 NE 是情绪记忆增强的必要环节；向 BLA 注入 NE 可维持远期记忆的精确性与海马依赖性（Atsak et al. 2017, PNAS, DOI 10.1073/pnas.1704062114, PMID 28790188）。
- LC‑NE 也与阿尔茨海默病理早期（tau 起始于 LC）相关，提示"认知储备"可能部分来自终身新颖性激活 LC‑NE（Mather & Harley 2016）。

### 5.2 量级
NE 对情绪记忆的增强属**中‑大**效应；propranolol 对情绪（非中性）记忆的削弱 d 约中等（Cahill 1994 等）。

---

## 6. 催产素（Oxytocin, OXT）

### 6.1 社会识别记忆（social recognition memory）
OXT 经典功能为社会联结与**社会识别记忆**（熟悉 vs 陌生个体/对象），主要由嗅结节/伏隔核与社会神经环路介导。鼻内 OXT 增强面孔（而非非社会物体）记忆（Shamay‑Tsoory & Abu‑Akel 2015 社会显著性假说，*Biological Psychiatry*；具体卷期/DOI 未核实）。

### 6.2 对杏仁核的抑制与社会显著性
- **社会显著性假说（social salience hypothesis）**：OXT 通过多巴胺系统将注意导向社会线索、提升社会刺激的显著性，同时可**降低杏仁核对威胁性面孔（愤怒/恐惧）的反应**（Striepens et al. 2012 等）。
- **性别差异（关键）**：
  - **女性**：鼻内 OXT 多在观看负性/威胁社会信息时**增加**杏仁核活动，并增强对"赞美者"的喜好（Gao et al. 2016, PNAS 113:7650‑7654, DOI 10.1073/pnas.1602620113）；在朋友情境下降低杏仁核‑岛叶连接（Ma et al. 2018, NeuroImage, DOI 10.1016/j.neuroimage.2018.08.004, PMID 30086408）。
  - **男性**：OXT 多**降低**杏仁核对负性社会信号的反应（Rilling et al. 2014 等）。
  → 引擎若含 OXT，必须分性别参数，否则会得出相反预测。

### 6.3 量级
OXT 效应多为**小‑中**，且高度依赖背景、依恋类型与性别（Bartz 交互模型）；对记忆的直接增强弱于对"社会显著性/注意导向"的调制。

---

## 7. 血清素（Serotonin, 5‑HT）

### 7.1 情绪、冲动、认知灵活性与记忆
- 降低 5‑HT 周转（如急性色氨酸耗竭）**一致关联长时记忆受损**（Schmitt et al. 2006, Curr Pharm Des 12:2473‑2486, DOI 10.2174/138161206777698909, PMID 16842171）。
- 低 5‑HT 可能**损害认知灵活性（cognitive flexibility）但改善聚焦注意**；刺激 5‑HT 反而损害真正警觉（vigilance）任务。
- **阶段分离（重要）**：Coray & Quednow (2022, Neurosci Biobehav Rev, PMID 35691469) 系统综述指出，低 5‑HT 支持**空间编码**却**损害物体/言语记忆的巩固**；5‑HT4 激动剂与 5‑HT6 拮抗剂是巩固增强的潜在靶点。

### 7.2 量级
总体效应**小‑中**且任务特异；与情绪/冲动的交互强于直接记忆增益。倒 U 形证据较弱，但"相位×任务"分离明确。

---

## 8. 褪黑素（Melatonin）与昼夜节律

### 8.1 睡眠‑清醒节律与记忆巩固
睡眠（尤其慢波睡眠 SWS 与后续 REM）是陈述性记忆巩固的关键窗口。**乙酰胆碱（ACh）在 SWS 期低水平**是海马→新皮层信息回流的"特权窗口"（Gais & Born 2004, PNAS；详见第 10 节）。褪黑素作为昼夜起搏点相位标志，间接通过睡眠结构影响巩固。

### 8.2 昼夜基因（Bmal1 / Clock）与记忆
海马内存在自主生物钟：Per2 在离体海马呈节律；海马 **LTP 及 MAPK 磷酸化呈昼夜振荡**，破坏该振荡损害长时记忆持久性（rev. Melatonin Regulates Aging… PMC4200827）。**Bmal1 缺失导致学习记忆损害**；褪黑素经上调 Bmal1/Clock‑HDAC3 互作逆转节律紊乱所致认知损害。

### 8.3 量级
褪黑素对急性认知多为中性/轻度保护；在睡眠剥夺、轮班、AD 人群中补充可改善言语/识别记忆（meta‑analysis 22 项 RCT 显示早期 AD 的 MMSE 改善；具体效应量未核实）。属**小‑中、情境依赖**。

---

## 9. 性激素（Sex Hormones）

### 9.1 雌二醇（17β‑estradiol, E2）与海马可塑性
- E2 **升高 CA1 树突棘密度、背向传导（backpropagation）距离与 LTP**（Woolley & McEwen 1992 经典；Fester & Rune 2015, Brain Res 1621:162‑169, DOI 10.1016/j.brainres.2014.10.033）。
- **发情/月经周期**：大鼠 proestrus（E2 高峰）place cells 最稳定；人海马在月经周期亦有结构变化（Jacobs lab）。E2 达峰期（proestrus）激活 Akt/LIMK/TrkB（BDNF 受体）信号。
- **海马局部芳香化酶**可将睾酮转为 E2，局部 E2 是突触可塑性与空间/物体记忆巩固所必需（letrozole 阻断损害两性空间记忆；人乳腺癌患者 letrozole 出现情景记忆缺陷）。
- 孕酮（progestin）在 E2 升棘后短期再升棘、随后 18h 内快速撤棘——**双相（biphasic）**，提示非线性。

### 9.2 睾酮（Testosterone）
睾酮经芳香化为 E2 作用于海马；去势/低睾酮与空间记忆下降相关，但外源睾酮对认知效应不一致（部分研究呈倒 U 形）。需分性别与基线建模。

### 9.3 月经周期与情绪记忆
女性在黄体期（高孕酮/中 E2）对情绪材料的记忆与杏仁核反应存在差异；口服避孕药改变皮质醇‑记忆关系（Kirschbaum et al. 1999 等）。应激对女性记忆影响较男性小且随周期相位变化（Zoladz et al. 2014）。

### 9.4 量级
E2 对海马可塑性的增强属**中‑大**（动物 LTP/棘密度），但对人类行为记忆的增益多为**小‑中**且受周期/年龄（绝经后下降）调节。

---

## 10. 补充系统：乙酰胆碱、内源性大麻素、胰岛素/IGF、甲状腺素、BDNF

### 10.1 乙酰胆碱（Acetylcholine, ACh）
- **编码↑ / 提取↓** 的关键分离：ACh 在觉醒与 REM 高，编码期升高促进新信息获取；SWS 期 ACh 低，释放海马→新皮层回流以巩固；胆碱酯酶抑制剂 physostigmine 阻断 SWS 的去 ACh 释放会**取消陈述性记忆的睡眠增益**（Gais & Born 2004）。人 fMRI：胆碱能刺激**增强编码相关海马活动、降低提取相关杏仁核活动**（Kukolja, Thiel & Fink 2009, PMID 19553452）。
- 空间学习时海马 ACh 在获取期即刻升高、巩固期降低（Deiana, Platt & Riedel 2010, PMID 21108971）。
- 量级：**中**（ACh 是状态切换闸门，方向依赖记忆阶段）。

### 10.2 内源性大麻素（Endocannabinoid, eCB）
- CB1 受体密集分布于 BLA/海马/PFC。eCB 与糖皮质激素**双向对话**：应激快速升高 eCB，eCB 经 GABA 能机制在杏仁核下调 HPA 轴（Di et al. 2003/2016）。
- **巩固**：BLA 内 CB1 激动增强情绪记忆巩固；全身/海马 CB1 激动则多**损害**巩固与提取（位点特异）。
- **消退（extinction）**：CB1 激活**促进**厌恶记忆消退（Marsicano et al. 2002; Chhatwal et al. 2009；综述 PMID 30604182 报告效应量大，Cohen's d ≥ 1.0）。
- **提取**：海马 2‑AG 信号介导糖皮质激素对情绪记忆提取的抑制（Atsak et al. 2012）。
- 量级：位点依赖，**小‑大**，是"应激/创伤记忆弱化"的翻译医学支点。

### 10.3 胰岛素 / IGF‑1（代谢激素与海马）
- 海马胰岛素受体（IR）富集于突触，调节 LTP/LTD、AMPA 受体与树突棘；鼻内胰岛素 5 min 入脑、1 h 达中枢，改善动物与人类记忆（尤其 ApoE ε4 阴性者）（rev. MDPI IJMS 2022, DOI 10.3390/ijms232214417）。
- **IGF‑1/IGF‑2**：海马 CA1 神经元活动依赖性地局部释放，激活 IGF1R 促进突触生长与 LTP；脑 IGF 信号下降关联 AD 与认知衰退（"3 型糖尿病"假说）。
- 量级：**中**，但脑胰岛素抵抗时转为损害（非线性/阈值特性）。

### 10.4 甲状腺素（Thyroid hormone, T3/T4）
- 成年期甲减损害海马 LTP（CA1 的 P‑CaMKII、CREB、ERK 下降）与空间/工作记忆；左甲状腺素（L‑T4）替代**完全恢复** LTP 与 RAWM 记忆（Alzoubi et al. 2008, Hippocampus, DOI 10.1002/hipo.20476, PMID 18680156）。
- T3 直接注入齿状回可在无高频刺激下诱导长时程增强。
- 量级：缺乏时**大**损害，替代后恢复；正常范围内 T4 与老年人学习记忆正相关（**小**倒 U/线性正关联）。

### 10.5 BDNF（脑源性神经营养因子）—— 记忆的关键中介
- **Val66Met 多态性**：Met 等位基因降低**活动依赖性** BDNF 分泌、错误定位突触，关联**较差情景记忆**、海马激活异常、海马 NAA 降低（Egan et al. 2003, Cell 112:257‑269, DOI 10.1016/S0092-8674(03)00035-7, PMID 12553913）。
- **运动/睡眠**：运动与睡眠（尤其 SWS）上调 BDNF，促进海马神经发生与突触可塑性；BDNF Val66Met 还与睡眠巩固交互预测陈述性记忆能力（Gosselin et al. 2016, J Neurosci；具体卷期未核实）。
- BDNF 是上述多数激素（E2、DA、IGF、甲状腺素、ACh）下游汇聚点 → 引擎可把 BDNF 设为"记忆巩固的整合变量"。

---

## 11. ★ 核心表：激素 → 记忆阶段 → 方向 → 量级 → 文献

> 方向：↑增强 / ↓抑制 / ⊚倒U（非线性）/ → 促进转换。量级：d= 元分析效应量；否则 小/中/大（定性）。

| 激素/系统 | 记忆阶段 | 方向 | 效应量级 | 关键文献 |
|---|---|---|---|---|
| **皮质醇 (Cortisol)** | 巩固 consolidation | ↑（情绪材料更强） | 中‑大；下午给药 d≈+0.22 | de Quervain 2017; Roozendaal 2002 |
| 皮质醇 | 编码 encoding | ⊚（时刻依赖） | 上午 d≈−0.40 ↓；下午 d≈+0.22 ↑ | Het, Ramlow & Wolf 2005 |
| 皮质醇 | 提取 retrieval | ↓ 抑制 | **d≈−0.49** | Het 2005; de Quervain 2000; Wolf 2009 |
| 皮质醇 | 整体（基线） | ⊚倒U | 极低/极高↓，中优 | Lupien & McEwen 1997; Reul & de Kloet 1985 |
| **MR 受体** | 编码/提取 | ↑（高占据） | 中 | Het et al. 2012 (spironolactone↓) |
| **GR 受体** | 巩固/提取 | ↑巩固 / ↓提取 | 中 | de Kloet 1998; Roozendaal 2002 |
| **NE (LC‑NE)** | 巩固（情绪） | ↑（高优先表征） | 中‑大 | Atsak 2017; Mather & Harley 2016 |
| NE | 提取（情绪） | ↓（高唤醒时） | 中 | Kroes 2010; Mather GANE |
| **DA (VTA/LC‑海马)** | 巩固（新颖/奖赏） | ↑（LTP 维持） | 中‑大 | Duszkiewicz; Takeuchi; Lisman |
| DA | 编码→习惯转换 | → 更新/覆盖 | 中 | DLS/DMS 研究 |
| DA | 整体 | ⊚倒U（D1 占据） | 中 | — |
| **OXT (催产素)** | 社会识别记忆 | ↑ | 小‑中 | Gao 2016; Ma 2018 |
| OXT | 社会显著/注意 | ↑（导向社会线索） | 小‑中 | Shamay‑Tsoory 2015 |
| OXT | 杏仁核（威胁） | ↓（男）/ ↑（女） | 小‑中（性别反向） | Gao 2016; Rilling 2014 |
| **5‑HT (血清素)** | 巩固（物体/言语） | ↑（正常/补充） | 小‑中 | Coray & Quednow 2022 |
| 5‑HT | 空间编码 | ↑（低 5‑HT 支持） | 小‑中 | Coray & Quednow 2022 |
| 5‑HT | 认知灵活性 | ↓（低 5‑HT 损） | 小 | Schmitt 2006 |
| **褪黑素/Melatonin** | 巩固（经睡眠） | ↑（保护/节律） | 小‑中 | MDPI 2025 rev; PMC4200827 |
| **Bmal1/Clock** | 巩固/LTP | ↑（节律必需） | 中（缺失→大损） | Melatonin rev 2015 |
| **E2 (雌二醇)** | 巩固/可塑性 | ↑（棘密度/LTP） | 中‑大（动物）/小‑中（人） | Fester & Rune 2015; Woolley 1992 |
| E2 | 编码（空间） | ↑（proestrus） | 中 | Jacobs lab; Fester 2015 |
| 孕酮 Progestin | 可塑性 | ⊚双相（升后撤） | 中 | Physiol Rev 2014 |
| **睾酮** | 海马记忆 | ⊚倒U/弱 | 小‑中 | — |
| **ACh (乙酰胆碱)** | 编码 encoding | ↑ | 中 | Kukolja 2009; Deiana 2010 |
| ACh | 巩固（SWS 去抑制） | ↑ | 中 | Gais & Born 2004 |
| ACh | 提取 retrieval | ↓（刺激时） | 中 | Kukolja 2009 |
| **eCB (内源性大麻素)** | 巩固（BLA 内） | ↑ | 中‑大 | Campolongo 2009 |
| eCB | 巩固/提取（全身/海马） | ↓ | 中 | rev. PMID 30604182 |
| eCB | 消退 extinction | ↑（大效应） | **d≥1.0** | Marsicano 2002; Chhatwal 2009 |
| **胰岛素/IGF‑1** | 巩固/LTP | ↑（IR 正常） | 中 | IJMS 2022; Alzoubi 2008(IGF) |
| 胰岛素（抵抗） | 记忆 | ↓ | 大（病理） | Talbot 2012 |
| **甲状腺素 T3/T4** | LTP/空间记忆 | ↑（缺乏↓） | 大（缺乏时） | Alzoubi 2008, DOI 10.1002/hipo.20476 |
| **BDNF** | 巩固（整合变量） | ↑（Val/活动依赖） | 中（Met↓） | Egan 2003, PMID 12553913 |
| BDNF | 受运动/睡眠上调 | ↑ | 中 | Gosselin 2016 |

---

## 12. ★ 定量时间表：起效 / 峰值 / 半衰期 / 昼夜波动

| 激素/系统 | 起效时间 | 峰值时间 | 恢复半衰期 | 昼夜波动幅度 | 备注 |
|---|---|---|---|---|---|
| **CRH** | 秒级脉冲 | — | 短（分钟） | 脉冲式 | 应激触发数秒 |
| **ACTH** | 数分钟 | CRH 后 10–30 min（2–4×基线） | ~数十分钟 | 晨高夜低 | 晨峰 06–08 时 |
| **皮质醇** | 应激后数分钟 | 峰 **20–30 min**（给药 30–60 min） | 血浆 **60–90 min** | 晨峰 ~15–25 µg/dL，夜谷 <5 µg/dL（幅度 ~3–5×） | 晨高（编码偏抑）、下午低（偏增强） |
| **地塞米松** | 数小时（负反馈） | 服药后 8–9 h（次日晨） | 长（>24 h 抑制） | — | 1 mg 23:00 → 次日 08:00 <1.8 µg/dL |
| **NE (LC)** | 秒–分钟（相位爆发） | 事件后数分钟 | 突触清除秒–分钟 | 唤醒态升高 | GANE 热点持续分钟级 |
| **DA (VTA/LC)** | 秒–分钟 | 新颖/奖赏后数分钟 | 清除分钟级 | 事件驱动 | 维持 LTP 小时级 |
| **OXT** | 鼻内 ~30–60 min 达峰 | 60–90 min | 血浆短（数分钟），中枢效应小时级 | 无固定昼夜 | 性别/背景依赖 |
| **5‑HT** | 分钟–小时（周转变化） | — | 数小时 | 较平缓 | 色氨酸耗竭数小时起效 |
| **褪黑素** | 服后 30–60 min | 夜间 **02:00–04:00**（50–150 pg/mL） | **30–60 min** | 夜间 vs 日间 >10× | 光暗周期相位标志 |
| **E2** | 小时–天（基因/非基因） | 周期 proestrus 峰 | 代谢小时–天 | 月经周期 ~10–100× 波动 | 局部海马芳香化持续合成 |
| **孕酮** | 小时（6 h 升棘） | 后 6 h | 撤棘 18 h | 周期依赖 | 双相 |
| **睾酮** | 小时–天 | 晨高 | 半衰期 ~数小时–天 | 晨高夜低 | 芳香化为 E2 |
| **ACh** | 秒–分钟 | 觉醒/REM 高；SWS 低 | 突触秒级（AChE） | 睡眠态剧变 | SWS 低=巩固窗口 |
| **eCB (2‑AG/AEA)** | 应激后分钟 | 数分钟–小时 | 酶解分钟级 | 应激/唤醒升高 | 与 GC 双向 |
| **胰岛素** | 鼻内 5 min 入脑，1 h 中枢 | 1–2 h | 外周 ~数分钟–小时 | 餐后升高 | 中枢 IR 介导记忆 |
| **IGF‑1** | 小时–天 | — | 长（小时–天） | 运动/睡眠上调 | 穿越 BBB |
| **甲状腺素 T4** | 天–周（替代） | 替代后数天 | T4 ~7 天；T3 ~1 天 | 窄（正常范围内） | 缺乏→大损 |
| **BDNF** | 活动依赖（分钟–小时） | 运动/学习后升高 | 表达小时–天 | 睡眠/运动上调 | Val66Met 降活动分泌 |

---

## 13. 建模不可线性叠加的要点（给引擎的警示）

1. **倒 U 形（inverted‑U）必须非线性实现**：皮质醇（整体）、DA（D1 占据）、睾酮、5‑HT（部分）、胰岛素（抵抗阈值）、E2（双相/孕酮）均为非线性。建议用饱和函数（如 `f(x)=x/(x+k)` 或高斯钟形）而非线性加权。
2. **阶段分离**：同一激素对编码/巩固/提取方向可相反（皮质醇 ↑巩固↓提取；ACh ↑编码↓提取）。引擎的状态向量必须区分这三个阶段，不能只用一个"记忆强度"标量。
3. **受体亚型分流**：皮质醇 MR（高亲和，编码/appraisal）vs GR（低亲和，巩固↑/提取↓）应作为两个独立状态变量，其比值（MR/GR balance）决定净效。
4. **昼夜相位门控**：皮质醇上午偏抑编码、下午偏增强；ACh 的 SWS 低谷是巩固窗口；褪黑素/Bmal1 提供节律相位输入。需引入"时刻/睡眠状态"作为门控变量。
5. **情绪唤醒作为放大器与放大器阈值**：NE/杏仁核‑海马耦合在中等唤醒增强、过高唤醒（应激）转为抑制（GANE/ABC）。建议把"唤醒度"设为调制增益而非简单加项。
6. **性别与周期**：OXT 对杏仁核男女反向；E2/孕酮随周期大幅波动；女性应激记忆效应较小且随相位变化。若引擎含社会化或性别参数，必须分支。
7. **位点/通路特异性**：eCB、DA、NE 的效应高度依赖脑区（BLA vs 海马 vs PFC），全局浓度无法预测方向——引擎若分脑区模块会更贴近证据。
8. **交互（cross‑talk）**：GC↔eCB 双向、E2↔BDNF(TrkB)、IGF↔BDNF、DA↔ACh——建议设 BDNF 为汇聚整合变量，吸收多激素下游信号。

---

## 14. 参考文献（附 DOI / PMID）

1. Het S, Ramlow G, Wolf OT (2005) A meta-analytic review of the effects of acute cortisol administration on human memory. *Psychoneuroendocrinology* 30(8):771–784. **DOI 10.1016/j.psyneuen.2005.03.005; PMID 15919583.**
2. de Quervain DJ-F, Roozendaal B, McGaugh JL (2000) Acute cortisone administration impairs retrieval of long-term declarative memory in humans. *Nat Neurosci* 3(4):313–314. **DOI 10.1038/73042（PMID 未核实）.**
3. de Quervain D, Schwabe L, Roozendaal B (2017) Stress, glucocorticoids and memory: implications for treating fear-related disorders. *Nat Rev Neurosci* 18(1):7–19. **DOI 10.1038/nrn.2016.155.**
4. Roozendaal B (2002) Stress and memory: opposing effects of glucocorticoids on memory consolidation and memory retrieval. *Neurobiol Learn Mem* 78(3):578–595. **DOI 10.1006/nlme.2002.4080; PMID 12559837.**
5. Roozendaal B, McGaugh JL (2011) Memory modulation. *Behav Neurosci* 125(6):797–824. **DOI 10.1037/a0026187; PMID 22122145.**
6. Wolf OT (2009) Stress and memory in humans: twelve years of progress? *Brain Res* 1293:142–154. **DOI 10.1016/j.brainres.2009.04.013; PMID 19376098.**
7. Shields GS, Sazma MA, McCullough AM, Yonelinas AP (2017) The effects of acute stress on episodic memory: A meta-analysis and integrative review. *Psychol Bull* 143(6):636–675. **DOI 10.1037/bul0000100.**
8. Cahill L, Prins B, Weber M, McGaugh JL (1994) β-adrenergic activation and memory for emotional events. *Nature* 371:702–704. **DOI 10.1038/371702a0; PMID 7935815.**
9. Kroes MCW, Strange BA, Dolan RJ (2010) β-Adrenergic blockade during memory retrieval in humans evokes a sustained reduction of declarative emotional memory enhancement. *Biol Psychiatry*（具体卷期/PMID 未核实）.
10. Mather M, Harley CW (2016) The locus coeruleus: essential for maintaining cognitive function and the aging brain. *Trends Cogn Sci* 20(3):214–226. **DOI 10.1016/j.tics.2016.01.001.**
11. Atsak P, et al. (2017) Noradrenergic activation of the basolateral amygdala maintains hippocampus-dependent accuracy of remote memory. *PNAS* 114(34):9176–9181. **DOI 10.1073/pnas.1704062114; PMID 28790188.**
12. Egan MF, Kojima M, Callicott JH, et al. (2003) The BDNF val66met polymorphism affects activity-dependent secretion of BDNF and human memory and hippocampal function. *Cell* 112(2):257–269. **DOI 10.1016/S0092-8674(03)00035-7; PMID 12553913.**
13. Gosselin N, et al. (2016) BDNF Val66Met polymorphism interacts with sleep consolidation to predict ability to create new declarative memories. *J Neurosci*（具体卷期未核实）.
14. Coray R, Quednow BB (2022) The role of serotonin in declarative memory: A systematic review of animal and human research. *Neurosci Biobehav Rev*（卷期未核实）. **PMID 35691469.**
15. Schmitt JAJ, Wingen M, Ramaekers JG, Evers EAT, Riedel WJ (2006) Serotonin and human cognitive performance. *Curr Pharm Des* 12(20):2473–2486. **DOI 10.2174/138161206777698909; PMID 16842171.**
16. Gao S, Becker B, Luo L, et al., Kendrick KM (2016) Oxytocin, the peptide that bonds the sexes also divides them. *PNAS* 113(27):7650–7654. **DOI 10.1073/pnas.1602620113.**
17. Ma X, Zhao W, Luo R, et al., Kendrick KM (2018) Sex- and context-dependent effects of oxytocin on social sharing. *NeuroImage*（卷期未核实）. **DOI 10.1016/j.neuroimage.2018.08.004; PMID 30086408.**
18. Shamay-Tsoory SG, Abu-Akel A (2015) The Social Salience Hypothesis of Oxytocin. *Biol Psychiatry*（卷期/DOI 未核实）.
19. Fester L, Rune GM (2015) Sexual neurosteroids and synaptic plasticity in the hippocampus. *Brain Res* 1621:162–169. **DOI 10.1016/j.brainres.2014.10.033.**
20. Woolley DW, McEwen BS (1992) Estradiol mediates fluctuation in hippocampal synapse density during the estrous cycle in the adult rat. *J Neurosci* 12(7):2549–2554（PMID 未核实）.
21. Alzoubi KH, Gerges NZ, Aleisa AM, Alkadhi KA (2008) Levothyroxin restores hypothyroidism-induced impairment of hippocampus-dependent learning and memory. *Hippocampus* 19(1)（页码未核实）. **DOI 10.1002/hipo.20476; PMID 18680156.**
22. Kukolja J, Thiel CM, Fink GR (2009) Cholinergic stimulation enhances neural activity associated with encoding but reduces neural activity associated with retrieval in humans. *J Neurosci*（卷期未核实）. **PMID 19553452.**
23. Deiana S, Platt B, Riedel G (2010) The cholinergic system and spatial learning. *Behav Brain Res*（卷期未核实）. **PMID 21108971.**
24. Gais S, Born J (2004) Declarative memory consolidation: the sleep benefit. *PNAS*（卷期未核实；慢波睡眠 ACh 与陈述性记忆巩固）.
25. Endocannabinoid & memory review (2019) Tempering aversive/traumatic memories with cannabinoids. *Psychopharmacology*（卷期未核实）. **PMID 30604182（报告 eCB 促进消退效应量 Cohen's d ≥ 1.0）.**
26. Insulin/IGF-1 and hippocampal memory review (2022) *Int J Mol Sci* 23(22):14417. **DOI 10.3390/ijms232214417.**
27. Melatonin & circadian memory review (2015) Melatonin Regulates Aging and Neurodegeneration through … Circadian Rhythm Pathways. *PMC4200827**（开放综述）.
28. Lupien SJ, McEwen BS (1997) The acute effects of corticosteroids on cognition: integration of animal and human studies. *Brain Res Rev* 24:1–27（PMID 未核实）.
29. Reul JMHM, de Kloet ER (1985) Two receptor systems for corticosterone in rat brain: microdistribution and differential occupation. *Endocrinology* 117:2505–2511（PMID 未核实）.

---

## 15. 总结（≤250 字）

内分泌系统对记忆的调制以**阶段分离**与**非线性**为核心规律：皮质醇呈倒 U 形，增强巩固（尤其情绪材料，下午更显）而抑制提取（d≈−0.49），由 MR（编码/appraisal）与 GR（巩固↑/提取↓）双受体分流；NE/DA 经 BLA‑海马与 VTA/LC‑海马通路增益新颖/情绪记忆，但高唤醒转抑制（GANE）；OXT 提升社会显著性且**男女对杏仁核作用反向**；E2 经棘密度/LTP 增强海马记忆并随周期双相波动；ACh 在 SWS 低谷开放巩固窗口（↑编码↓提取）；eCB 位点依赖地调节巩固/提取并促进消退；BDNF 为多条通路的整合中介。引擎必须区分编码/巩固/提取三态、用饱和/钟形函数实现倒 U、引入昼夜与性别/周期门控，并以 BDNF 作汇聚变量，方能贴合上述证据而非线性叠加。
