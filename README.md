# 数据化大脑 · 独立版

一个带内分泌与长期记忆的"情感大脑"模拟器。**不依赖 Ombre-Brain，也不需要装任何第三方包**——
只用 Python 标准库（可视化前端是原生 SVG，没有 CDN、没有 npm）。

打包时间：2026-09-22 19:01 · 本版本经四轮对抗性审查后全量修复（2026-09-28）
修复清单见 `docs/CHANGELOG.md`，复验见 `docs/review_v2.md`、`docs/review_v3.md` 与 `docs/review_v4.md`，
探针可重跑：`python3 tools/probes_v2.py`。

---

## 一、30 秒跑起来

```bash
# 1) 开可视化窗口（会自动先跑一次 180 天模拟）
python server.py

# 2) 浏览器打开
http://127.0.0.1:8777
```

右上角可以切「合成场景 / 语料」。后者读的是包内**虚构演示语料**跑出来的结果。

要求：Python 3.9+。没有 pip install 这一步。

---

## 二、目录

```
server.py              可视化后端（标准库 http.server，默认 127.0.0.1:8777）
databrain/
  config.py            ★ 全部可调参数都在这里，改行为先翻这个文件
  state.py             激素系统（昼夜节律 + 拮抗）、慢变量、倾向
  memory.py            记忆桶、账本、再巩固、熟悉度
  engine.py            主循环：评估 → 经历 → 写入 → 时间推进
  human.py             人味层：FAB、习惯化、情绪惯性、自发回忆、矛盾情感
  agentface.py         ★ 面向 agent 的输出层（语气/行为冲动/认知模式/分离焦虑/prompt_suffix）
  social.py            社会化测试（8 项指标，≥75 分算能长期相处）
  corpus.py            语料适配器（路径由 DATABRAIN_EVENTS 指定；包内自带虚构演示语料）
  simulate.py          合成场景（跨时间跨场景），可直接 `python -m databrain.simulate`
tools/
  probes_v2.py         对抗性探针套件（19 项，可重跑）
  audit_esc.py         前端转义静态审计（受控字段必须过 esc()）
  xss_render_test.js   前端 XSS 实弹渲染（Node DOM 桩，真跑 renderAll()）
  release_check.py     发布前审 zip 本体：容器判据 + 隐私指纹/真名复扫
  validate.py          A/B/C 对照实验 + 5 种子回归
  real_sim.py          语料模拟 + 因果链追踪 + 脱敏/未脱敏双写
  gen_figs.py          现场跑数 → docs/figures.md（文档数字的唯一来源）
  face_test.py         同一段对话并排看 prompt_suffix
web/
  index.html           可视化前端（单文件，原生 SVG，所有外部数据经 esc() 转义）
  real.redacted.json   语料结果（脱敏，可发布）—— 包内是虚构演示语料跑的
  compare.redacted.json真实 vs 合成 对照（脱敏，可发布）
.private/              ★ 未脱敏产物，.gitignore 已排除，不要发布
  real.full.json       语料结果未脱敏版（含原始人名与聊天原文；仅自用包）
  legacy/              修复前生成的旧版 real.json / compare.json
docs/
  数据化大脑_引擎报告.md 设计取舍 + 踩过的坑
  figures.md           由 tools/gen_figs.py 生成的现场数字
  CHANGELOG.md         本轮全量修复清单（含方法论变更与一处撤回）
  review_v2.md         第二轮对抗性审查报告（修复后复验 + 新发现）
  review_v3.md         第三轮对抗性审查报告（针对交付包本身 + 修复的修复）
  review_v4.md         第四轮对抗性审查报告（交付包 N16–N20 + HTTP 实弹探针）
knowledge/             5 篇参考文献（神经系统 / 内分泌与记忆 / 情感与情绪 /
                       情感社会学 / 情感—内分泌整合）
```

---

## 三、它到底是什么

三层记忆 + 一层熟悉度 + 一套内分泌：

| 层 | 是什么 | 会不会被改写 |
|---|---|---|
| 客体层 | 我对**这一个人**的整体认定 | 会，但要攒够反证据 |
| 主题层 | 我对**某个模式**的认定（"他在工作场合会伤害我"） | 会，更慢 |
| 情节层 | **具体发生了什么事** | 不改写，只衰减（FAB：负性消退更快） |
| 熟悉度 | 处久了自然变暖 / 久不联系自然变淡 | 不算改写，没有"某一刻改主意"的瞬间 |

底层是 **append-only 账本**：摘要只是索引，构成每一次判断的全部原始时刻一条都不删。

内分泌不是装饰——它真的参与写入：皮质醇、催产素等状态会调制「编码深度」，
同样的经历在身体状态不同时，留下的痕迹深浅不同。

---

## 四、几个关键设计（也是踩过的坑）

1. **"情绪短时、情感长期"不是两套系统，是两个时间尺度。**
   情绪是激素驱动的快变量（小时级），情感是不指向任何具体事件的背景水位（天级）。

2. **旧判断能改，但要有门槛。** 不是一次就翻转，是反证据累积到阈值才开窗，
   且移动幅度随阻抗递减——越深的判断越难撼动。原始判断 `valence0` 永不删除，
   每次改写都留痕（版本链）。

3. **"越熟越难改"该由阻抗表达，不是由接触次数表达。**
   试过按接触次数衰减学习率，876 次接触会把单次事件压到 10% 影响力，
   结果一次背叛只让认定掉 0.004，等于没发生。

4. **衰减公式不能只吃 arousal。** 原版 Ombre-Brain 的 `base + arousal×boost`
   浪费了 valence；这里补了效价偏离度、隧道效应、Zeigarnik（未完成的事记得更牢）。

5. **日常琐碎必须有作用。** 只用戏剧事件驱动的话，多年尺度的真实语料上
   几个人的认定会全挤在千分之几的区间里，分不出来也不像人。
   加了「陪伴累积」才分化开。

6. **不假装知道事件发生在几点。** 真实语料只有日期没有可靠钟点。原版用
   `hour = int(delta) % 24` 把"这是第几小时的消息"当钟点用，而钟点驱动了
   昼夜节律、场景归属、分离焦虑整套机制 —— 那是拿编造的数据做决定。
   现在解析不到钟点就 `hour=None`：主题键的场景维落成「日常」，
   昼夜调制取全天均值（`circ_mean`）。合成模拟有脚本钟点，仍走真值路径。
   代价是真实/合成两条管线不再同尺度可比，这是诚实的成本，不是回归。

7. **多巴胺节律此前是反相 12 小时的。** 原版写作 `sin` 相位、峰值落在半夜；
   现在是 `da_amplitude * cos(π*(hour−peak)/12)`，峰值在正午。
   这条改了激素轨迹，也就改了所有依赖多巴胺的历史结论 ——
   旧 README 里的数字全部作废，新数字见 `docs/figures.md`。

8. **FAB 不再偷偷改写长期效价。** 原实现把情节记忆的 valence 持续拉向 0.52
   （一个中性目标），这与文档"情节层只衰减、不改写"的宣言直接冲突。
   现在默认只衰减唤醒（`arousal_half_life_days`），
   valence 漂移保留为消融开关 `HUMAN['fab']['valence_drift']`。
   这是**方法论变更**，两种配置的对比由 `tools/gen_figs.py` 打出。

9. **外部数据一律转义后再进 DOM。** 语料里的人名是对端可控字符串。
   前端 `esc()` 覆盖全部字符串插值点，人名进引擎时先过 `sanitize_subject()`
   （剥 `|`、`/`、`\`、控制字符，限长 40）。

---

## 五、常用命令

```bash
# 跨时间跨场景模拟（180 天）
python -m databrain.simulate

# 回归验证：5 个种子 + A/B/C 对照实验
python tools/validate.py

# 重跑语料（语料路径用环境变量指定，见下）
DATABRAIN_EVENTS=/path/to/events.jsonl python tools/real_sim.py

# 语料 + 与合成场景对比
DATABRAIN_EVENTS=/path/to/events.jsonl python tools/real_sim.py --compare

# 重新生成文档里的所有数字（改行为后必跑，别手抄）
python tools/gen_figs.py          # -> docs/figures.md

# 前端并排看 prompt_suffix
python tools/face_test.py
```

### 路径与运行开关

原版把 `D:\train\memory\mem2\events.jsonl` 这类绝对路径写死在代码里，
换台机器就是 FileNotFoundError。现在一律环境变量优先：

| 变量 | 作用 | 默认 |
|---|---|---|
| `DATABRAIN_EVENTS` | 事件语料 jsonl 路径 | `knowledge/events.jsonl` |
| `DATABRAIN_PEOPLE` | 人物权重 json | `knowledge/people.json` |
| `DATABRAIN_HOST` | 服务监听地址 | `127.0.0.1` |
| `DATABRAIN_PORT` | 服务端口 | `8777` |
| `DATABRAIN_TOKEN` | 设了才启用鉴权（`?token=` 或 `X-Databrain-Token` 头） | 空=不鉴权 |
| `DATABRAIN_ALLOW_OPEN` | `1` = 明知风险仍要在无口令下非回环监听 | 空 |
| `DATABRAIN_FULL` | `1` 时 `/api/real`、`/api/compare` 读 `.private/` 未脱敏版 | 空=读脱敏版 |

`DATABRAIN_HOST` 一旦不是回环地址（例如 `0.0.0.0`）而 `DATABRAIN_TOKEN` 又是空的，
服务**直接拒绝启动**并告诉你三种选择。这不是多余的谨慎：这三行环境变量
是这套东西唯一的访问控制，而 /api/data 会把整个记忆导出交出去 ——
一次误配置就是全部。原来只有注释里写着"应该设口令"，代码不检查（三轮 N14）。
真要靠反代、自己的网络策略来保护，就显式加 `DATABRAIN_ALLOW_OPEN=1`。

设了 `DATABRAIN_TOKEN` 之后：前端页面第一次拉 `/api/*` 会弹一次输入框，
把口令存进 `sessionStorage`（关掉标签页即清除），此后每个请求用
`X-Databrain-Token` 头带上 —— 口令**不进 URL**，所以不会落到浏览器历史、
Referer 和服务端访问日志里（四轮 N17）。命令行也可以直接给：
`curl -H 'X-Databrain-Token: 你的口令' http://127.0.0.1:8777/api/data`。

另外三件四轮加固（对本机使用无感，只是把门关上）：
- **Host 头校验**：伪造 `Host:`（DNS rebinding 那一类）一律回 `421`，
  本机 `127.0.0.1`/`localhost`/`::1` 照常（N18）。
- **`/api/run` 需自定义头**：这个接口会跑几十秒 CPU 并覆盖缓存，
  又是 GET，任何网页用一个 `<img>` 就能借你的机器去跑。现在必须带
  `X-Databrain-Token` 头（前端自动带），裸 GET 回 `428`（N19）。
- **`Server` 头**不再公示精确的 Python 小版本（N18）。

包内 `knowledge/events.jsonl` + `people.json` 是**虚构演示语料**
（6 个假人物、792 条，含一段 60 天伤害 → 90 天善意的再巩固弧），
开箱即可跑 `real_sim` 看到完整效果；要接自己的聊天数据，
用 `DATABRAIN_EVENTS` 指过去即可，格式见 `databrain/corpus.py` 的
`load_events` / `load_people` docstring（**注意 `weight` 量纲是 0~10**，
填成 0~1 会让整条情节层空掉 —— 现在这种填错会警告，不再静默降级）。

需要重新打包请用 `zip -r ../pkg.zip . -x '*.git*' '__pycache__/*' '.private/*'`，
**务必排除 `.private/`**。

---

## 五·五、脱敏版与未脱敏版

`tools/real_sim.py` 现在**双写**，一次生成两份数据：

| 文件 | 内容 | 用途 |
|---|---|---|
| `.private/real.full.json` | 原始人名、聊天原文、因果链日期 | **自用**，`.gitignore` 已排除 |
| `web/real.redacted.json` | 人名映射成 `P1..Pn`、原文/日期/重评细节清空 | **发布**，可直接进开源仓库 |
| `.private/compare.full.json` / `web/compare.redacted.json` | 对照数据（只含聚合指标） | 同上 |

脱敏不是只把 `text` 置空。审查发现逐字段映射会漏 `bucket_id`、
`people_kept`，甚至漏在字典**键**上（`social_test._ambivalence_all` 以人名为键）。
现在 `_redact()` 收尾时对整棵 JSON 树做一次递归清洗（键和值都过），
并用带活体 XSS 载荷的对抗语料验证残留为零。

**关于本仓库**：上面这套双写是给"以后接真实语料"准备的机制，不是现状。
仓库里 `web/*.redacted.json` 跑的是 `knowledge/events.jsonl` 那份**虚构演示语料**，
所以本地生成的 `.private/real.full.json` 里也只有虚构内容 ——
本仓库不含任何真实聊天记录，也不含它的衍生物。

发布前自检（应为 NONE）：

```bash
python3 tools/probes_v2.py            # 19 项，末行 FAIL=0 SKIP=0
python3 - <<'PY'
import json
for f in ('web/real.redacted.json','web/compare.redacted.json'):
    b=json.dumps(json.load(open(f,encoding='utf-8')),ensure_ascii=False)
    # 检查"真实/演示人名 + 活体载荷"三类都不该出现
    bad=[w for w in ('<script','onerror','alert','阿澈','老周','Momo','奶奶','室友','正常朋友') if w in b]
    print(f, 'RESIDUAL:', bad or 'NONE')
PY
```

上面两条查的是**代码与产物**。真正要发布的还有一个对象：zip 本身。
第三轮就是靠审它才发现公开包里印着只能从原始私人语料算出的那组数字
（跨度 / 事件数 / 总分），以及一个数据文件被打包成 `0600`。
所以打包之后还要跑第三道，它审 zip 而不审工作树：

```bash
python3 tools/release_check.py <你要发的那个>.zip --mode public \
        --names-file <你本机的私人名单，不要提交>
```

代号表全工程唯一：`real` 里叫 `P3` 的人，`compare` 里也是 `P3`
（否则两个页面交叉看会读错人）。这条由 P-REDACT 与 review_v2 §N4 覆盖。

**但脱敏不等于匿名，这点必须说清楚（三轮 review_v3 §4.1）**：
代号表由 `sorted(人名)` 确定性生成、不含任何秘密。如果**原始语料和发布产物
一起分发**，任何人按事件计数做频率对齐就能把 `P1..Pn` 反推回真名
（我们在自带的演示语料上实测：5/5 还原、零碰撞，只用公开包内的两个文件）。
本仓库之所以安全，是因为发布的那份语料**本身就是虚构的**
（`knowledge/` 里的六个名字都是编的，专门用来演示机制）。
换成你自己的真实语料时，铁律只有一条：
**原始语料与 `.private/` 留在本地，绝不和发布产物一起分发**。

另外两条已知代价：代号按"人名子串"匹配，人名越短越常见，
文本里被切碎的痕迹越多（`李` → `P1`，"李白"变"P1白"）；
`people.json` 的 `weight` 会夹紧到 0~10 且要求有限，脏值不会再把产物写成
浏览器打不开的 JSON，但也意味着填错数值不会报错、只会静默按边界处理。

---

## 六、当前测试结果

**下表全部由 `tools/gen_figs.py` 现场生成**，原始出处是 `docs/figures.md`
（那文件是生成物，别手改）。上一版 README 里手写的那组数字与代码实际输出
对不上（审查 C6），已作废。

### 合成场景（180 天 / seed 42，本机 1.2 秒跑完）

| 指标 | 值 |
|---|---|
| 事件 | 1335 条 |
| 人物 / 主题桶 / 情节 | 2 / 22 / 104 |
| 再巩固改写次数 | **17** |
| 诊断 failures / warnings | 0 / 0 |
| 社会化测试总分 | **100.0 / 100** |
| 情绪波动幅度 | 0.1031 |
| 情绪切换速度 | 0.0962 |
| 平淡期占比 | 0.7873 |
| 极端情绪占比 | 0.0000 |
| 负性记忆消退 | 0.7692 |
| 重复刺激钝化 | 0.2076 |
| 自发回忆频率 | 1.1944 |
| 矛盾情感存在度 | 0.9873 |

### 演示语料（包内）

`web/real.redacted.json` 是包内虚构演示语料跑出来的结果，供前端直接展示：

| 指标 | 值 |
|---|---|
| 跨度 / 事件 | 727 天 / 686 条（取 top 5 人物） |
| 人物 / 主题桶 / 情节 / 改写 | 5 / 20 / 135 / **7** |
| 社会化测试总分 | 94.0 / 100 |
| 因果链 | 222 条（前端带最重的 40 条） |

对照：合成场景 100.0 / 演示语料 94.0 —— 差距主要来自「重复刺激钝化」，
演示语料的对话密度低于合成脚本。这是演示数据的性质，不是引擎缺陷。

### 关于原始真实语料

本包不含任何真实聊天原文，也**不含它的衍生物**（隐私，审查 A4）。
上面那份演示结果是包内虚构语料跑出来的，与任何真实数据无关。

旧版随包分发过 `web/real.json` —— 那是**修复前代码**在伪造钟点下产出的
（审查 C1），既不可复现也含隐私原文，已从 `web/` 移出并只留在自用包里。
它的规模与指标不在公开文档里复述：那些数字本身就是一个指纹
（跨度、事件数、人数足以把某个人的聊天语料框定出来），
细节见自用包的 `PRIVATE_README.md`。

### 涌现结论的有效期

「持续的日常善意比一次性重大和解更有效」这条来自 `tools/validate.py` 实验 C，
在当前代码下仍可复现（三种善意的首次撬动次数：日常善意 6 次 / 深度共处 5 次 /
重大和解 6 次）。但注意：这条结论建立在关键词分类器给出的刺激标签上，
分类器是词表命中制，正常中文闲聊大量落到 `mundane`/`neutral`
（实测见 `docs/figures.md`）。在换上真正的语义模型之前，
这类"心理结论"只能当假设，不是证据。

---

## 七、接进一个会说话的 agent（prompt_suffix）

引擎算完不是只给人看的，它能直接产出一段拼进 LLM 提示词的状态文本：

```python
brain = DataBrain(seed=7)
brain.experience(t, '汤姆', 'betrayal', '汤姆在会上把成果说成他一个人做的', 0.8)
print(brain.prompt_suffix('汤姆'))
```

会输出（当前代码实测，`python tools/face_test.py`）：

```
[内分泌状态]
催产素:0.29 多巴胺:0.24 血清素:0.43 皮质醇:0.43 褪黑素:0.28
[当下情绪] 效价 0.448 / 唤醒 0.375
[长期情感] 心境 0.50 / 关系温度 0.50
[对汤姆的认定] 0.235（初值 0.235，陪伴漂移 +0.000，阻抗 0.52，改写 0 次）
[分离] 2.5 小时没联系：微微想你
[认知模式] balanced（唤醒 0.34）
[涌现情绪] 微微想你
[对方状态] 生气
[语气] 语气平稳自然
```

`prompt_suffix` 现在是**纯只读**的（审查 B4 修复）。原版它内部会调用
语气调制与行为冲动生成，顺带把冷却计时和上一轮语气写进状态 ——
于是"读一次状态"这个动作本身会改变状态：连续调用两次得到不同结果，
两个只在一个里被读过的 brain 也会跑出不同的 export。
现在 `tone(..., persist=False)` / `urges(..., consume=False)` 默认不落状态，
只有在 `experience()` 内部（即真实发生一次接触时）才 `persist=True, consume=True`。
验证：同一事件序列，一个 brain 每步额外调 3 次 `prompt_suffix`，
另一个不调 —— 最终激素与人物效价差异为 `0.00e+00`。

注意 **「对汤姆的认定」那一行**——这是拿它去接 agent 时真正值钱的部分：
普通的内分泌模拟只能告诉你"现在皮质醇高"，它还会告诉你
"**我认为汤姆是个什么样的人，这个判断已经固化到什么程度，被改写过几次**"。

这一层的能力（语气调制、行为冲动、倒 U 认知门控、对方状态识别、慢路径、
对话节奏、分离焦虑）移植自原「内分泌引擎 v2.0」，移植时改了三处：

1. **多人化**：原版全文件找不到 "person"，只有一个全局关系温度；
   这里分离焦虑、接触时刻全部按人计算，强度还取决于"有多在意这个人"。
2. **走时间轴**：原版的"慢路径"是当场乘个系数就施放了；这里排进
   `DelayedReleaser`，到点才释放，所以在多年尺度的模拟里也成立。
3. **接得上记忆**：它读的是 DataBrain 的状态，不是另起一套激素。

想看两边并排跑同一段对话的效果：
`python tools/face_test.py`

---

## 八、没有 Ombre-Brain 的份吗

有，但是单独的外挂（`databrain/ombre.py` + `tools/ombre_bridge.py`），**不在这个包里**。
它的做法是只读 OB 的记忆桶、只往 YAML frontmatter 里加 `db_` 前缀字段，
绝不碰 OB 自己的 valence/arousal/importance——OB 继续管"记了什么"，
我们管"怎么看这个人"。等 OB 部署好了再用。

---

## 九、许可证

MIT，见 `LICENSE`。代码与文档都可以自由使用、修改、再分发，不需要署名授权往来。
`knowledge/` 下的综述是给引擎定参数用的文献笔记，DOI/PMID 都在正文里，
要复核结论请直接顺着它们走，别把这里的转述当原文。

