# 人体神经系统工作原理（记忆相关神经机制）

> 本文档为「数据化大脑」项目的知识储备，目标是为长期记忆系统 Ombre-Brain 与虚拟内分泌引擎提供**贴近真实生物**的定量神经科学底层原理。内容聚焦记忆相关机制，所有重要论断均标注来源，并在文末给出可当代码常数使用的**定量常数表**。

---

## 一、神经元工作原理（神经元 / Neuron）

神经元（neuron）是神经系统的计算单元，通过"分级电位 → 动作电位 → 突触传递"三级链路处理信息。

### 1.1 静息电位与离子平衡电位
- 典型神经元静息膜电位（resting potential）约 **−70 mV**（膜内相对膜外），由 Na⁺/K⁺-ATPase（每 ATP 泵出 3 个 Na⁺、泵入 2 个 K⁺）与 K⁺ 漏通道共同维持（NeuroWiki；Gor, 未注明年份）。
- 各离子的 Nernst 平衡电位参考值：E_K ≈ **−90 mV**、E_Na ≈ **+60 mV**、E_Cl ≈ **−70 mV**、E_Ca ≈ **+120 mV**（NeuroWiki）。静息时膜对 K⁺ 通透性最高，故静息电位贴近 E_K。

### 1.2 动作电位与去极化/复极化
- **阈值（threshold）** 约 **−55 mV**。一旦达到阈值，电压门控 Na⁺ 通道大量开放，膜电位快速去极化（depolarization）。
- **峰电位（peak）** 典型 **+30 ~ +40 mV**（未达 E_Na，因 K⁺ 通道同步开放）。
- 上升相（去极化）约 **0.5 ms**；整个动作电位全过程约 **1–2 ms**（Anvayaprep；Gor）。
- 复极化（repolarization）由 Na⁺ 通道失活 + 延迟整流 K⁺ 通道开放驱动；常伴随后超极化（after-hyperpolarization, AHP），膜电位短暂降至约 **−80 mV**（Makindo）。

### 1.3 不应期
- **绝对不应期（absolute refractory period）**：Na⁺ 通道处于失活态，任何刺激都无法再触发动作电位，持续约 **1 ms**（外周轴突）。
- **相对不应期（relative refractory period）**：需更强于正常的刺激才能触发，膜处于超极化恢复中。
- 不应期上限决定了发放频率上限：轴突通常 **< 500–1000 Hz**（NeuroWiki）。

### 1.4 髓鞘与跳跃传导
- 髓鞘（myelin，由少突胶质细胞/CNS、施万细胞/PNS 包裹）大幅提高传导速度并降能耗。
- **有髓纤维**传导速度可达 **120–150 m/s**；**无髓纤维**约 **0.5–10 m/s**（NCBI Bookshelf NBK10921）。
- 郎飞结（node of Ranvier）间隙约 **1 μm**，结间段长 **1–2 mm**；电压门控 Na⁺ 通道在结处高密度聚集（>1000 个/μm²），动作电位在结间被动传播、在结点再生，即跳跃传导（saltatory conduction）（OpenExamPrep；KSU 讲义）。
- 膜时间常数 τ = R_m·C_m 与长度常数 λ = √(R_m/R_i) 决定被动传播效率（Courseshub）。

---

## 二、突触传递（突触 / Synapse）

化学突触是神经元间通信的主要形式，信息以"电信号 → 化学信号 → 电信号"转换。

### 2.1 突触间隙与递质释放
- 突触间隙（synaptic cleft）宽约 **20–40 nm**（OpenExamPrep）。
- 动作电位到达末梢 → 电压门控 Ca²⁺ 通道开放；胞外 Ca²⁺ ≈ **1–2 mM**，胞内静息 ≈ **100 nM**，巨大浓度梯度驱动 Ca²⁺ 内流（OpenExamPrep）。
- Ca²⁺ 结合突触结合蛋白（synaptotagmin）→ SNARE 复合体介导囊泡胞裂外排（quantal release，量子化释放）。

### 2.2 兴奋性与抑制性递质
- **谷氨酸（glutamate）** 是中枢主要兴奋性递质，作用于 AMPA、NMDA、kainate 受体。
- **GABA（γ-氨基丁酸）** 是主要抑制性递质，作用于 GABA_A（离子型，Cl⁻ 内流）、GABA_B（代谢型）。
- 其他调制性递质：乙酰胆碱（ACh，注意/编码）、多巴胺（DA，奖赏/强化学习）、去甲肾上腺素（NE，应激/唤醒）、5-羟色胺（5-HT）。

### 2.3 兴奋性/抑制性突触后电位（EPSP / IPSP）
- 单个 EPSP 幅值很小，通常 **0.5–2 mV**（均值约 1 mV），远不足以触发动作电位（ScienceDirect Synaptic Potential；Salk 论文）。
- EPSP 时程约 **20 ms**（在体半宽约 10 ms）；IPSP 峰值离子电导变化持续 **1–2 ms**，恢复静息需 **≤15 ms**（WikiLectures）。
- 在体约需 **40–50 个**同步激活的突触即可将膜电位从 −75 mV 推至 −55 mV 阈值附近（Salk 论文，2012）。

### 2.4 时空总和（Summation）
- **时间总和（temporal summation）**：同一突触的连续输入间隔小于 PSP 时程（约 **15–20 ms**），后一个 PSP 叠加在前一个未衰减的尾迹上。其有效性由**膜时间常数 τ** 决定（τ 越大越易总和）。
- **空间总和（spatial summation）**：不同突触（地理上邻近）近乎同时激活，在初始段（axon hillock / initial segment，阈值最低）代数相加。其有效性由**长度常数 λ** 决定（输入间距小于 λ 时总和更有效）。
- 总和是神经元作为"积分器"的核心：EPSP 相加、IPSP 相减，净电流决定是否在初始段达阈值（ScienceDirect Synaptic Potential）。

---

## 三、突触可塑性与记忆分子机制

长时程增强（LTP，long-term potentiation）由 Bliss 与 Lømo 于 **1973** 在海马发现，是记忆的细胞模型（europepmc 综述）。

### 3.1 NMDA 受体：分子"重合检测器"
- NMDA 受体在静息电位下被 **Mg²⁺** 电压依赖性阻塞；需**谷氨酸结合 + 突触后去极化解除 Mg²⁺ 阻塞**两个条件同时满足，才允许 Ca²⁺ 内流（Neuronal Dynamics EPFL；europepmc）。
- 去极化解除 Mg²⁺ 阻塞约需膜电位升至 **−50 mV 以上**（Neuronal Dynamics）；强去极化（约 30–40 mV）可完全解除（stratacode，未正式发表，标注为辅助理解）。
- NMDA 电流动力学：上升时间常数 τ_rise ≈ **3–15 ms**，衰减时间常数 τ_decay ≈ **40–100 ms**（Neuronal Dynamics）。这给了 NMDA 一个 **~10–100 ms** 的整合窗口，使其成为 pre/post 活动的重合检测器（coincidence detector）。

### 3.2 AMPA 受体与 LTP 表达
- AMPA 受体介导快速（毫秒级）基线传递；LTP 表达主要靠 AMPA 受体的磷酸化（提高电导 **40–60%**）与膜表面插入（trafficking）（mybrainrewired；studyguides）。
- Ca²⁺ 通过 NMDA 内流，**胞内峰浓度可达 ~10 μM**（studyguides，数值未完全核实，参考用）。

### 3.3 诱导阈值与 Hebb 规则
- **协同性（cooperativity）**：单一弱通路不足以诱导 LTP，需多条通路或高频刺激协同去极化越过阈值（Roth-Alpermann 学位论文；Bliss & Collingridge 1993）。
- **联想性（associativity）**：弱刺激与强刺激同时到达同一神经元可共同诱导 LTP（Hebb 规则细胞学证据，Gustafsson & Wigström 1986）。
- **STDP（spike-timing-dependent plasticity）**：pre 峰先于 post 峰 → 增强（LTP）；post 先于 pre → 减弱（LTD）；LTP/LTD 转换发生在**数毫秒**内（Sjöström & Nelson 2002；Cell 综述）。
- 诱导 LTP 的胞内 Ca²⁺ 需超过临界阈值；强 Ca²⁺ 信号→LTP，弱/中度→LTD（"钙假说"）。

### 3.4 早期与晚期 LTP 及蛋白合成
- **早期 LTP（E-LTP）**：持续 **< 3 小时**（1–3 小时），依赖已有蛋白的翻译后修饰（磷酸化），无需新蛋白合成（Frey & Morris, *Nature* 1997, PMID:9020359）。
- **晚期 LTP（L-LTP）**：持续 **> 10 小时**，可至**天数–周–年**级别，依赖转录与**新蛋白合成**（Frey & Morris 1997；synaptic consolidation 综述 PMC3368062）。
- 蛋白合成抑制剂（anisomycin、放线菌酮）若在诱导后早期给予，可阻断向 L-LTP 的转变。

### 3.5 突触标记与捕获假说（Synaptic Tagging）
- Frey & Morris（1997）提出：弱刺激诱导的 E-LTP 会在突触处留下一个**不依赖蛋白合成的"突触标记"（synaptic tag）**，标记在 **< 3 小时内**衰减。
- 同一神经元若此前/此后接受过强刺激（产生可扩散的"可塑性相关产物" PRP，如 mRNA、蛋白），这些 PRP 会被标记"捕获"，把 E-LTP 升级为 L-LTP（Frey & Morris 1997）。
- 后续发现 cross-tagging（Sajikumar & Frey 2004），LTP 与 LTD 标记可交互。

### 3.6 下游分子级联：CaMKII 与 CREB
- **CaMKII**（钙/钙调蛋白依赖激酶 II）：被 Ca²⁺/CaM 激活后，于调节域**自磷酸化（Thr286）**，变为 Ca²⁺-非依赖的持续活性状态，相当于"分子开关"，将瞬时 Ca²⁺ 信号转译为持久的激酶活性（Lisman 模型；Hedou 2004；qq 百科）。CaMKII 自磷酸化在 LTP 诱导刺激后 **~30 秒内**发生，活性可持续 **>10 分钟**（mybrainrewired；studyguides）。
- CaMKII 直接磷酸化 AMPA（GluR1）并磷酸化转录因子 **CREB**。
- **CREB**（cAMP 反应元件结合蛋白）：在 **Ser133** 被 PKA 等磷酸化后启动即刻早期基因转录。下游时间线（mybrainrewired）：c-fos（**15–30 分钟**）、Arc/Arg3.1（**30–60 分钟**）、Homer1a（30–90 分钟）、BDNF（**1–4 小时**）。BDNF 缺失小鼠晚期 LTP 维持下降 60–70%。
- 结构重塑：LTP 后活性区面积增大约 30–40%，棘头体积增大约 20–50%（studyguides；mybrainrewired）。

---

## 四、记忆系统分区

### 4.1 海马体及亚区（海马 / Hippocampus）
经典**三突触回路（trisynaptic pathway）**：内嗅皮层 → 齿状回（穿通通路 perforant path）→ CA3（苔藓纤维 mossy fibers）→ CA1（Schaffer 侧支）→ 内嗅皮层/下托（Royal Society；PMID:34769511）。

| 亚区 | 核心计算功能 | 关键特征 |
|---|---|---|
| 齿状回 DG | **模式分离（pattern separation）**：把相似输入正交化为可区分表征，减少干扰 | 颗粒细胞极度稀疏编码（仅 **1–2%** 激活），强 GABA 抑制（Royal Society；PMID:34769511） |
| CA3 | **模式完成（pattern completion）**：由部分线索重建完整记忆；自联想网络 | 具丰富的**递归侧支（recurrent collaterals）**，是联想/自动完成的核心（Royal Society） |
| CA1 | **输出/比较器**：接收 EC 直接单突触输入与 CA3 输出，作"预测误差"检测器 | 投射至下托、EC、前额叶；与情景/语义记忆成绩相关（Royal Society；behaviorneuro） |

海马是"快速一次性学习"的临时缓冲器，而非永久存储地（H.M. 病例：海马切除后不能形成新陈述性记忆，但运动技能仍可学——QBI）。

### 4.2 内嗅皮层（Entorhinal Cortex, EC）
- 海马的主要输入/输出门户；浅层（II–III 层）发穿通通路。
- 内侧内嗅皮层（MEC）含**网格细胞（grid cells）**；外侧内嗅皮层（LEC）处理物体/特征信息（Nobel 2014 资料；behaviorneuro）。

### 4.3 杏仁核（Amygdala）
- 处理与调制**情绪记忆**，尤其**恐惧条件化（fear conditioning）**依赖基底外侧核（BLA）（QBI；PMC4355270）。
- 杏仁核通过应激激素（肾上腺素/皮质醇）调制海马与新皮层，使情绪唤醒事件记忆更强（McGaugh 框架；QBI）。
- 前额叶（尤其是腹内侧/下边缘区）对杏仁核的抑制参与恐惧消退（extinction）（PMC4355270；Milad & Quirk 2012）。

### 4.4 前额叶（Prefrontal Cortex, PFC）
- **工作记忆（working memory）** 的核心：在线保持并操作信息（QBI；CUNY 教材）。
- 参与编码时的注意导向、以及情景/语义记忆提取（与海马强连接）。左 PFC 偏言语、右 PFC 偏空间（QBI）。

### 4.5 基底神经节与小脑
- **基底神经节/纹状体（basal ganglia / striatum）**：负责**习惯记忆（habit）**、程序性/非陈述性记忆、动作序列自动化（QBI；PMC4355270）。习惯对奖赏价值变化不敏感（Yin & Knowlton 2006）。
- **小脑（cerebellum）**：精细运动控制与**运动学习**（如眨眼条件化、前庭眼反射）（QBI；Steinmetz 1999）。

### 4.6 记忆类型对照
- **陈述性（declarative / explicit）**：可被意识报告——情景记忆（episodic，自传事件，海马依赖）、语义记忆（semantic，事实/知识，逐渐新皮层化）。
- **非陈述性（nondeclarative / implicit）**：程序性记忆（procedural，技能/习惯，基底神经节+小脑）、经典条件化、启动效应。
- **工作记忆**是 PFC 维持的短时在线缓冲，区别于长时记忆。

---

## 五、记忆巩固机制

### 5.1 两类巩固
- **突触巩固（synaptic consolidation）**：诱导后**分钟–小时**级，依赖局部蛋白合成/修饰（Schafe et al. 2000）。
- **系统巩固（systems consolidation）**：记忆在脑区间重组，**天–年**级，海马逐渐将记忆"教"给新皮层（Squire & Alvarez 1995；标准巩固理论）。

### 5.2 标准巩固理论与海马—皮层对话
- **标准模型（standard model）**：新记忆先在海马编码，随反复重激活（尤其睡眠中），新皮层连接增强，逐渐变为**海马非依赖**（Squire & Alvarez 1995；Wiki）。
- 时间梯度：海马依赖阶段常被描述为约 **1 周内**，之后向新皮层转移；整体过程可长达**数年至数十年**（Wiki、Academic.ru，模型相关，存异）。
- **多重痕迹理论（multiple trace theory, MTT）**：情景记忆始终保留海马参与；语义记忆才逐渐独立（Nadel & Moscovitch 1997）。这一分歧至今未完全解决。

### 5.3 睡眠与记忆巩固
睡眠是离线重演与转移的关键窗口（"海马—新皮层对话"）：

| 睡眠阶段 | 主要脑电 | 频率 | 巩固功能 |
|---|---|---|---|
| N2（浅睡） | **睡眠纺锤波 spindle** | **12–15 Hz**（0.5–2 s 爆发） | 丘脑—皮层耦合，陈述性记忆组织；纺锤密度预测次日记忆成绩 |
| N3 / SWS（慢波睡） | 慢波/慢振荡 SO | **0.5–4 Hz**，SO **<1 Hz** | 海马—皮层信息转移主窗口；占前半夜 |
| 海马尖波涟漪 SWR | **sharp-wave ripple** | **100–250 Hz**（常引 120–200 Hz） | 海马记忆痕迹的压缩重放（数分钟→毫秒），与纺锤耦合 |
| REM | θ 与 γ | θ **4–8 Hz**，γ **30–120 Hz** | 情绪记忆处理、程序/空间记忆整合；占后半夜 |

- 三节律**三重耦合（triple coupling）**：慢振荡（皮层）→ 纺锤（丘脑）→ 涟漪（海马）的精确时间对齐，把重放信息从海马传至新皮层（encyclopedia.pub；kbrain-map）。
- 神经化学：NREM（尤 SWS）乙酰胆碱、去甲肾上腺素低，利于离线巩固；REM 乙酰胆碱高、NE 近零，利于"去情绪化"重组（naopedia；kbrain-map）。
- **突触稳态假说（SHY）**：清醒时突触普遍增强、睡眠时全局缩放，保留强连接、剔除噪声（Tononi & Cirelli；kbrain-map）。

### 5.4 再巩固与更新窗口（Reconsolidation）
- Nader, Schafe & LeDoux（*Nature* 2000, DOI:10.1038/35021052）发现：已巩固的记忆被**提取（retrieval）** 重新激活后，会回到**不稳定的可塑状态**，需重新蛋白合成才能稳定；在此窗口用 anisomycin 阻断可造成遗忘。
- **不稳定窗口**：约 **5 分钟–1 小时**（可延至数小时）；Nader 2000 中若延迟至 **6 小时** 才给药则无遗忘效应（BioNumbers；Nader 2000）。
- **边界条件（boundary conditions）**：仅当提取时伴随**新信息/预测误差**（如情境或 contingencies 改变）才开启再巩固窗口；纯熟悉重演不触发（Agren 2014；Ecker 2015；IJMS 综述 PMC7555418）。这恰是"记忆更新"的生物学基础。

---

## 六、记忆提取与遗忘

### 6.1 提取诱发遗忘（Retrieval-Induced Forgetting, RIF）
- Anderson 等（1994）用检索练习范式证明：反复提取某范畴的部分项目，会损害同范畴**未练习**项目的后续回忆（约 **13%** 效应）。机制被认为是前额叶介导的**自动抑制**（inhibition），而非单纯干扰（ScienceDirect；PMC25484872）。

### 6.2 主动遗忘与神经发生介导的遗忘
- **主动遗忘（active forgetting）**：除衰退外，存在主动清除机制（如 RIF、定向遗忘、突触缩放）。
- **神经发生介导的遗忘（neurogenesis-mediated forgetting）**：Akers 等（*Science* 2014, DOI:10.1126/science.1248903）证明，成体海马齿状回**持续产生新神经元**并整合入环路，会重塑已有回路、使已存记忆"被清除"。运动增加神经发生→已建立的情境恐惧/空间记忆遗忘；药物/基因提高神经发生亦致遗忘，降低则减缓自然遗忘。该机制可最小化前摄干扰（Frankland et al. 2013）。
- 新神经元整合成熟需**数周**（Nature npp 综述 2015）。

### 6.3 间隔效应与最佳间隔（Spacing Effect）
- **间隔效应**：分散学习优于集中（填塞）学习，跨物种保守（Cepeda et al. 2006；mindomax）。
- **Cepeda 等（2006, *Psychological Bulletin* 132(3):354–380）** 元分析 254 研究/317 实验：最佳首次复习间隔约为**目标保持时长的 10–20%**。
  - 目标保持 1 周 → 首次间隔 **1–2 天**；目标 1 月 → **3–6 天**；目标 1 年 → **5–10 周**（warpread；classeva）。
  - 后续间隔应逐级放大（常见约翻倍：1→2→4→8→16 天），3–4 次良好间隔复习即可形成持久记忆（Dunlosky et al. 2013 评为高效技术）。
- 艾宾浩斯遗忘曲线（1880s）：无复习时 24 小时内大量衰退，之后渐缓。间隔复习在曲线触底前"拦截"并抬高基线。

---

## 七、Place Cell / Grid Cell 与认知地图

- **位置细胞（place cell）**：O'Keefe（**1971**）在海马发现，当动物处于特定空间位置时放电；海马通过位置细胞集群构建环境的**认知地图（cognitive map）**（O'Keefe & Nadel 1978；Nobel 2014）。
- **网格细胞（grid cell）**：Moser 夫妇（**2005**）在内嗅皮层（MEC）发现，其放电场呈**正六边形网格**排列，构成空间坐标系；网格具模块化（≥4–5 个模块），尺度沿背—腹轴系统性变化（从小尺度到大尺度）（Nobel 2014；Sainsbury Wellcome 讲座）。
- 配套细胞：头方向细胞（head-direction）、边界细胞（border）、速度细胞（speed）共同构成"脑内 GPS"（Nobel 2014）。
- 睡眠时清醒期的网格相位相关性被保留，提示同一地图在离线态仍表达（Moser 讲座）。
- 临床相关：阿尔茨海默病早期即累及海马与内嗅皮层，导致空间定向障碍（Nobel 2014）。

---

## 八、可用于代码参数化的定量常数表

> 下列数值为文献报道的典型量级，供 Ombre-Brain 建模作常数/默认值。标注"未核实"者为单篇来源或辅助估计，建模时建议留可调接口。

| 参数名 | 典型数值 | 单位 | 来源 | 备注 |
|---|---|---|---|---|
| 静息膜电位 V_rest | −70 | mV | NeuroWiki; Gor | 由 K⁺ 漏通道主导 |
| 动作电位阈值 V_th | −55 | mV | NeuroWiki; Wikipedia | 轴丘/初始段最低 |
| 峰电位 V_peak | +30 ~ +40 | mV | Anvayaprep; Gor | 接近但未达 E_Na |
| 后超极化 AHP | ~−80 | mV | Makindo | 短时 |
| K⁺ 平衡电位 E_K | −90 | mV | NeuroWiki | |
| Na⁺ 平衡电位 E_Na | +60 | mV | NeuroWiki | |
| Ca²⁺ 平衡电位 E_Ca | +120 | mV | NeuroWiki | |
| 动作电位时长 | 1–2（上升相 ~0.5） | ms | Anvayaprep; Gor | |
| 绝对不应期 | ~1 | ms | NeuroWiki | Na⁺ 失活 |
| 发放频率上限 | <500–1000 | Hz | NeuroWiki | 受不应期限制 |
| 膜时间常数 τ_m | ~10（范围 1–20） | ms | Courseshub;  squid 轴突 ~1ms | 决定时间总和 |
| 长度常数 λ | ~0.3–0.6 | cm | Courseshub(λ≈0.32cm) | 决定空间总和 |
| 有髓传导速度 | 120–150 | m/s | NBK10921 | 跳跃传导 |
| 无髓传导速度 | 0.5–10 | m/s | NBK10921 | |
| 郎飞结间隙 | ~1 | μm | OpenExamPrep | |
| 突触间隙宽 | 20–40 | nm | OpenExamPrep | |
| 胞外/内 Ca²⁺ | 1–2 / ~100 (nM) | mM / nM | OpenExamPrep | |
| 单 EPSP 幅值 | 0.5–2（均值~1） | mV | ScienceDirect; Salk 2012 | 需总和才达阈 |
| EPSP 时程（半宽） | ~10（总~20） | ms | Salk 2012; WikiLectures | 时间总和窗口 |
| IPSP 电导恢复 | ≤15 | ms | WikiLectures | |
| 触发 AP 所需同步突触 | ~40–50 | 个 | Salk 2012 | 在体估计 |
| NMDA 上升 τ | 3–15 | ms | Neuronal Dynamics | |
| NMDA 衰减 τ | 40–100 | ms | Neuronal Dynamics | 整合窗口~10–100ms |
| NMDA 解阻塞阈值 | > −50（去极化） | mV | Neuronal Dynamics | Mg²⁺ 依赖 |
| LTP 诱导刺激 | 100 Hz × 1s 或 15 Hz × 15s | — | europepmc 综述 | Bliss & Lømo 1973 |
| NMDA-LTD 频率 | 0.5–3 | Hz | europepmc | |
| 早期 LTP (E-LTP) | < 3（1–3） | 小时 | Frey & Morris 1997 | 不依赖新蛋白合成 |
| 晚期 LTP (L-LTP) | > 10 小时（天–年） | 小时/天 | Frey & Morris 1997 | 依赖转录/蛋白合成 |
| 突触标记衰减 | < 3 | 小时 | Frey & Morris 1997 | 捕获 PRP 的窗口 |
| CaMKII 自磷酸化时机 | ~30 秒内；活性 >10 分 | s / min | mybrainrewired; studyguides | Thr286 |
| CREB 磷酸化位点 | Ser133 | — | mybrainrewired | PKA 等 |
| c-fos 表达 | 15–30 | 分钟 | mybrainrewired | 即刻早期基因 |
| Arc 表达 | 30–60 | 分钟 | mybrainrewired | |
| BDNF 表达 | 1–4 | 小时 | mybrainrewired | 晚期 LTP 关键 |
| 系统巩固时间尺度 | 天–年（可至数十年） | — | Squire & Alvarez 1995; Wiki | 标准模型 |
| 睡眠纺锤波频率 | 12–15 | Hz | encyclopedia.pub; brainmatters | N2 期 |
| 慢振荡 SO | < 1 | Hz | encyclopedia.pub | N3/SWS |
| 尖波涟漪 SWR | 100–250（常120–200） | Hz | encyclopedia.pub; cannelevate | 海马重放 |
| REM θ | 4–8 | Hz | encyclopedia.pub | |
| REM γ | 30–120 | Hz | encyclopedia.pub | |
| 睡眠周期 | ~90 | 分钟 | brainmatters; kbrain-map | NREM+REM |
| 再巩固不稳定窗口 | 5 分–1 小时（可至数小时） | min/h | BioNumbers; Nader 2000 | 6h 后给药无效 |
| 最佳首次复习间隔 | 目标时长的 10–20% | % | Cepeda et al. 2006 | 间隔效应 |
| RIF 效应量 | ~13 | % | Goodmon & Anderson 2011 | 提取诱发遗忘 |
| DG 稀疏激活比例 | 1–2 | % | PMID:34769511 | 模式分离 |
| 新神经元成熟整合 | ~数周 | 周 | Nature npp 2015 | 神经发生遗忘 |

---

## 九、参考文献

1. Bliss TVP, Lømo T (1973). Long-lasting potentiation of synaptic transmission in the dentate area of the anaesthetized rabbit following stimulation of the perforant path. *J Physiol*. （LTP 发现）
2. Frey U, Morris RGM (1997). Synaptic tagging and long-term potentiation. *Nature* 385:533–536. **PMID:9020359 / DOI:10.1038/385533a0**.（早期/晚期 LTP、突触标记）
3. Squire LR, Alvarez P (1995). Retrograde amnesia and memory consolidation: a neurobiological perspective. *Curr Opin Neurobiol* 5:169–177.（标准巩固理论）
4. Nader K, Schafe GE, LeDoux JE (2000). Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval. *Nature* 406:722–726. **DOI:10.1038/35021052**.（再巩固）
5. Akers KG et al. (2014). Hippocampal neurogenesis regulates forgetting during adulthood and infancy. *Science* 344:598–602. **DOI:10.1126/science.1248903**.（神经发生介导遗忘）
6. Cepeda NJ, Pashler H, Vul E, Wixted J, Rohrer D (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychol Bull* 132(3):354–380.（间隔效应）
7. Anderson MC, Bjork RA, Bjork EL (1994). Remembering can cause forgetting: Retrieval dynamics in long-term memory. *J Exp Psychol Learn Mem Cogn* 20(5):1063–1087.（RIF）
8. O'Keefe J (1971). Place units in the hippocampus of the freely moving rat. *Exp Neurol* 31:573–590.（位置细胞）
9. Hafting T, Fyhn M, Molden S, Moser MB, Moser EI (2005). Microstructure of a spatial map in the entorhinal cortex. *Nature* 436:801–806.（网格细胞，2014 诺奖）
10. Sjöström PJ, Nelson SB (2002). Spike timing, calcium signals and synaptic plasticity. *Curr Opin Neurobiol* 12:305–314.（STDP；EPSP-AP 阈值约 2.3 mV 于体）
11. Dudai Y (2004). The neurobiology of consolidations, or, how stable is the engram? *Annu Rev Psychol* 55:51–86.（巩固综述，未逐句引用，作为背景）
12. Frankland PW, Bontempi B (2005). The organization of recent and remote memory. *Nat Rev Neurosci* 6:119–130.（系统巩固）
13. Tononi G, Cirelli C (2014). Sleep and the price of plasticity. *Neuron* 81:12–34.（突触稳态假说 SHY，背景）
14. Milad MR, Quirk GJ (2012). Fear extinction: clinical relevance and cognitive mechanisms. *Behav Neurosci* 126:702–715.（前额叶—杏仁核消退）
15. Dunlosky J et al. (2013). Improving students' learning with effective learning techniques. *Psychol Sci Public Interest* 14(1):4–58.（分散练习高效评级）
16. Wang SH, Morris RGM (2010). Hippocampal-neocortical interactions in memory formation, consolidation, and reconsolidation. *Annu Rev Psychol* 61:49–79.（海马—新皮层对话）
17. Bear MF (1997). How do memories leave their mark? *Nature* 385:481–482.（突触标记评论）
18. Lisman J et al. (2002). The molecular basis of CaMKII function in synaptic plasticity. *Nat Rev Neurosci* 3:175–190.（CaMKII 分子开关，背景）
19. Redondo RL, Morris RGM (2011). Making memories last: the synaptic tagging and capture hypothesis. *Nat Rev Neurosci* 12:17–30.（标签与捕获综述）
20. Neuronal Dynamics (EPFL) Ch.3.1 — NMDA 受体动力学 τ_rise/τ_decay。（在线教材，用于 NMDA 时间窗数值）

**未核实/辅助来源说明**：胞内 Ca²⁺ 峰 ~10 μM（studyguides，单篇，建议作为可调参数而非硬常数）；"海马依赖阶段约 1 周""系统巩固可至 1–2 十年"在时间尺度上模型间有分歧（标准模型 vs MTT），建模时应参数化而非固定；Mg²⁺ 完全解阻塞需 ~30–40 mV 去极化（stratacode 为非正式网页，仅供定性理解）。Adam 等无关项已按需求排除。

---

## 总结

本文档系统整理了记忆相关的神经科学底层原理：从神经元电生理（静息/动作电位、不应期、跳跃传导的时间常数），到突触传递（EPSP/IPSP、时空总和），再到突触可塑性（LTP/LTD、NMDA/AMPA、CaMKII/CREB、早期/晚期 LTP、突触标记）、记忆系统分区（海马亚区、内嗅、杏仁核、前额叶、基底神经节、小脑）、巩固与睡眠（标准模型、纺锤/涟漪、再巩固窗口）、提取与遗忘（RIF、神经发生遗忘、间隔效应），以及 place/grid cell。核心交付是一张**定量常数表**（约 50 项带数值/单位/来源），可直接作为 Ombre-Brain 的建模默认值。

**未能充分核实之处**：① 系统巩固的精确时间尺度（标准模型"1 周—数十年"与 MTT 分歧）只能给范围；② 胞内 Ca²⁺ 峰值、Mg²⁺ 完全解阻塞的去极化幅度缺乏高引综述交叉印证，已标注为可调参数；③ 部分数值来自教材/在线资源（如 Neuronal Dynamics、NeuroWiki）而非一手论文，已在表中区分来源可信度。建议后续针对 CaMKII 动力学、STDP 精确窗口、睡眠节律与记忆因果关系补查一手电生理/行为论文。
