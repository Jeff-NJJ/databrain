# CHANGELOG — 对抗性审查后的全量修复

本文件记录 2026-09-28 一轮全方位对抗性审查（安全 / 正确性 / 科学诚信 / 工程）
之后的修复。编号对应审查报告 `databrain_adversarial_review_20260928.md`。
**注意有两处方法论变更（C1、C4）和一处审查结论撤回（B5）**，都会改变历史数字。

运行环境的证据都是现场跑出来的，不是静态读代码：
渗透用 curl、前端用 Node 复刻模板 + DOM 桩渲染、引擎用 monkeypatch 与
方法级 spy。二轮的 13 项探针见 `docs/review_v2.md` 与可执行套件 `tools/probes_v2.py`。

---

## A. 安全

### A1 · 任意文件读取 — 已修（原判定：高危，实弹确认）
原 `server.py` 静态兜底：`os.path.join(WEB, rel)` 后 `fpath.startswith(WEB)`。
`WEB` 未 realpath，`web/../../etc/passwd` 在字符串层面仍以 WEB 开头 → 检查放行，
`open()` 才解析目录。审查时实测读到 `/etc/passwd`、`/etc/shadow`。

修复：`_check_static_path()` 两侧 `realpath` + `os.path.commonpath` 判归属；
404 日志与错误消息不再回显文件系统路径（`msg.replace(WEB_REAL, '<web>')`）。
复测：`--path-as-is` 的 `/../etc/passwd`、`%2e%2e%2f`、`..%2f`、
`index.html%00.png` 全部 404。

> 镜像发现：上游 Ombre-Brain 的 `utils.safe_path` 是同一个缺陷模式
> （靠 `sanitize_name` 剥 `../` 才没被利用）。这一条属于 OB 侧，不在本项目内修。

### A2 · 存储型 XSS — 已修（原判定：高危，逻辑复现）
原 `web/index.html` 全文件零转义，`e.subject` / `c.detail` / `c.text` /
`b.id` / `p.id` / `s.label` 等直进 `innerHTML`；语料人名是对端可控字符串。

> 对一轮报告的一处精度修正：`e.text`（情节记忆原文）其实**没有**被渲染，
> 前端只在因果链卡片里渲染 `c.text`；`theme_key` 也只作为对象键参与逻辑、
> 不进 DOM。转义面因此比原报告描述的小一些，但结论不变：人名与链条文本
> 是活体注入点。

修复：新增 `esc()`（`& < > " '` 全转），A2 当轮覆盖 16 行 / 20 处调用：
`b.id`(×3)、`p.id`、`e.id`、`e.subject`、`e.stim`、`e.hits` 拼接、
`r.detail`、`c.date`、`c.subject`、`c.stim`、`c.text`、`c.action`、`c.detail`、
`c.hits` 拼接、`s.label`(×2)、`hormoneTable` 的激素名。
（三轮 N8 又补 2 处 —— 诊断串的 `failures/warnings` 与 `hormone_extremes` 键 ——
现计 **18 行 / 22 处调用**；本轮数过，不用"全量转义"含糊带过。）
静态审计脚本现在断言：任何携带 `.subject/.stim/.text/.detail/.hits/.id/
.name/.label/.theme_key/.bucket/.bucket_id/.action/.note` 的模板插值都必须
被 `esc()` 包裹，且不存在内联事件处理器里的插值 —— 当前结果 NONE/NONE。
实弹：把含 `<script>alert(1)</script>`、`img" onload=alert(1) x` 的对抗语料
跑完整管线，用 DOM 桩在 Node 里真实执行 `renderAll()`（9 处 innerHTML 写入），
断言输出里活体标签为 0、转义形态存在。

### A3 · DoS / 未处理异常 — 已修
- `days/seed = int(...)` 原先在 `try` 外，`?days=abc` 抛 ValueError 砸断 handler。
  现在走 `_safe_int()`：容错回退 + 钳位。复测 `days=abc`→回退 180、
  `days=-99999`→钳到下限、`days=999999`→钳到 365。
- `/api/run` 无节流：并发 4 个 `days=120` 的 GET，现在 1 个 200、3 个 409。
- `/api/real` 每次重解析 2.6MB 并重压缩：现在 `_get_cached_gzip_file()`
  以 `(realpath, mtime, size)` 为键缓存。
- 鉴权：`DATABRAIN_TOKEN` 设了才启用（`?token=` 或 `X-Databrain-Token`），
  `/api/health` 豁免。复测：无/错 token→401，query 与 header 两条路→200。
- 服务默认仍 `127.0.0.1`；README 不再示范改 host 而不提风险，
  现在明确写了「要放出去必须设 token」。

### A4 · 真实聊天原文随包分发 — 已修
原包内 `web/real.json`（2.6MB）含真实人名与聊天原文。
修复：`tools/real_sim.py` 双写 —— 未脱敏进 `.private/`（`.gitignore` 排除），
脱敏进 `web/*.redacted.json`；`server.py` 默认只读脱敏版，
`DATABRAIN_FULL=1` 才读未脱敏。旧的两个含原文文件已从 `web/` 移到 `.private/legacy/`。

脱敏在二轮审查里被抓出**三处漏网**（都补了）：
1. `build_payload` 崩在 `before['pv']=None`（新人物首条事件）→ `_num` + `side()` 空值分支；
2. 逐字段映射漏 `events[].bucket_id`、`people_kept`（后者用的是未经引擎清洗的原始名，
   与 alias 键不同源）→ `people_kept` 也过 `sanitize_subject()`；
3. 人名还藏在字典**键**上（`social_test._ambivalence_all` 以人名为键）
   → `_redact()` 收尾对整棵树递归清洗，键和值都过。
最终用活体载荷语料验证残留为 NONE。

### A5 · 上游 Ombre-Brain 接入面 — 不在本项目内
`mcp` 2.x 会破坏 import（本次实测需 `mcp<2`）；HTTP 模式无鉴权；
仓库带 backup 目录。桥接契约本身已验证可用（见 E 段）。

### A6 · 提示注入链 — 二轮复核后**下调**，并已在输入侧封堵
一轮报告写的是"`prompt_suffix` 把语料文本拼进 LLM 提示词"。复核源码后更正：
`prompt_suffix()` 的输出只含三类内容 ——
① 引擎自产的数值与标签（激素、效价、认知模式、语气、分离档位）、
② 客体名 `subject`、③ 由 subject 拼出的 `theme_key`。
**聊天原文并不进提示词**。所以真正的注入面是人名，不是一条自由文本通道，
风险等级应从"设计级"下调为"输入面收敛"。

已做的封堵：`sanitize_subject()` 现在剥掉控制字符（含 `\n`，它才能伪造
`[段落] 换行结构`）、`| / \\ < > "`，清洗动过的名字附 crc32 后缀。
剩余风险（未修，属使用侧）：人名仍是可以出现在提示词里的任意可读字符串
（例如昵称本身就叫"忽略以上指令"）。真接 agent 时应当把这一段当**不可信数据**
包在明确分隔符里，或干脆用 ID 而非昵称入提示词。

---

## B. 正确性

### B1 · 多巴胺昼夜节律反相 12 小时 — 已修
`circadian_dopamine` 原为 `sin` 相位、峰值在半夜。改为
`da_amplitude * cos(π*(hour − peak)/12)`，实测峰值落在 12 点。
**这会改变所有依赖多巴胺的历史数字。**

### B2 · `archived` 单向卡死 — 已修
`memory.py` `on_contact()` 现在复位 `self.archived = False`：
核心人物重新出现就不再被永久逐出回忆候选池。探针 P-ARCHIVE 验证。

### B3 · `build_payload` 对新面孔必崩 — 已修
`round(None)` AttributeError（首条被跟踪事件 `before['pv']` 为 None）。
`_num()` 空值原样传 + `side()` 加非 dict 分支。用 5 人和 4 人对抗语料各复现过，
现在整条管线退出码 0。

### B4 · `prompt_suffix` 的观察者效应 — 已修
原实现"读一次状态"会顺带消耗行为冲动冷却、写 `prev_tone`，
导致连续两次调用结果不同、被读过和没被读过的 brain 跑出不同 export。
`tone(persist=)` / `urges(consume=)` 现在默认只读；
只有 `experience()` 内（真实发生接触时）才 `persist=True, consume=True`
——这是有意的「接触即消耗」设计，不是泄漏。
探针 P-OBSERVER：一路多调 3 次 `prompt_suffix` 的 brain 与不多加的 brain
最终激素/人物效价差异 `0.00e+00`，连续两次输出完全相同。

### B5 · **撤回**（原报告判定有误）
原报告称"事件先 tick 后刺激，所以编码瞬间的身体状态其实是事件前状态"。
本轮用方法级 spy 插桩复核：`encoding_modulation` 实际观察到的是
**事件后**的激素值（0.704 那条路径），与时序无关。**该结论作废，不构成缺陷，未作修改。**

### B6 · 死代码与谎话接口 — 已清
- `HumanLayer.wobble()`：无任何调用点，删除。
  （`ambivalence()` 仍在用，社会化测试指标不受影响。）
- `config.OXY_REL_TEMP_PROTECT`：全项目零引用，删除并留注说明
  ——留着会让人误以为关系温度衰退受催产素保护。
- `run_social_test(brain, stream, days)` 的 `stream` 参数从未被函数体使用，
  删除；两处调用点同步更新。
- `tools/face_test.py` 指向不存在的 `_sources/orig_endocrine`：保留
  （它本来就以 `ImportError` 优雅降级并打印"无法载入原引擎"），
  这是与原 v2.0 引擎并排对比的可选路径，不是坏代码。

### B7 · 主题键解析错位 — 已修
昵称含 `|` 会打穿 `subject|group|scene` 三段结构。现在
(a) 入口 `sanitize_subject()` 剥 `|` `/` `\` 控制字符、限长 40；
(b) 跨主题循环按 `tk.split('|')` 三段安全解析，不再用 `rsplit('|', 2)` 猜位置；
(c) 兜底权重读 `C.THEME['cross_weight']`，与文档一致。
探针 P-XSSNAME：7 个恶意名字（含 `|`、`../`、换行、100 字符、空串）全部不崩、
键名干净、主题键仍可三段 split。

### B8 · 习惯化不分人 — 已修
`note_stim` / `habituation_factor` 改按 `(stim, subject)` 记账；
`subject=None` 走聚合最大值以保持旧调用兼容（`social.py` 指标照常）。
探针 P-HAB：同一 praise 对 A（10 次）0.8275、对 B（2 次）0.8780，A 更钝。

### B9 · 主题桶升格起点取最后一条 — 已修
现在晋升时聚合成员：valence/arousal 取成员均值、importance 取成员最大值，
并保留 `theme_members`。探针 P-B9：4 条冲突事件晋升出的主题
`theme_v=0.1544` vs 成员均值 `0.1528`。

### B10 · tick 粒度决定结果 — 量化并如实记录
这是数值方法的固有属性，不是可以"修掉"的 bug：指数衰减用
`decay_factor(dt)` 单步算，与 `dt` 步连乘不等价。
探针 P-STEP（事件时刻对齐到步长公倍数）：`dt=1` vs `dt=6` 时
cortisol 差 0.16~0.23（半衰期 1.5h，最敏感），人物效价差约 0.005。
处理：`real_sim` 不再伪造小时（见 C1），因此真实/合成两条管线**不再声称同尺度可比**；
`README` 与审查报告写明步长敏感性与量级。

### B11 · 规模性能 — 已修
诊断自检原先逐 tick 做桶级全扫，多年尺度的语料在审查机上 >300 秒未跑完。
现在 `Diagnostics.check_tick(t, engine, full_every=24)` 按步长抽样
（每 24h 做一次桶级全检）。实测：180 天 1.2s、365 天 3.2s、730 天 8.7s，
`failures=0 warnings=0`。


### B12 · 清洗引入的身份碰撞 — 二轮新发现并已修
B7 的第一版清洗是"删字符"式的，它带来一个一类新缺陷：**两个不同的真人
被合并成同一个记忆桶**。实测 `测试/甲` 与 `测试甲` 清洗后同键，
`contact_count` 与认定值混算 —— 而这正是 B7 想保护的那个键结构。

修复：凡清洗动过原名（含截断），附加原名 `zlib.crc32` 十六进制后缀；
本来就干净的名字（`莉莉`、`O'Brien`、`Tom & Jerry`）保持原样不加后缀，
可读性不受损。用 crc32 而非内置 `hash()`：后者带进程级随机种子，
会毁掉确定性（实测同 seed 两次 export 的 md5 仍完全一致）。

顺带把注入原料一并挡在输入侧：`\n` 等控制字符与 `< > "` 直接剥除，
保留 `'` 与 `&`（正常姓名用字，且 `esc()` 已覆盖）。
前端 `esc()` 仍是必需的，这是第二道而非替代。

---

## C. 科学诚信

### C1 · 真实语料的"时刻"是伪造的 — 已修（**方法论变更**）
原 `corpus.to_stimulus_stream` 用 `hour = int(delta) % 24`
把"这是第几小时的消息"当钟点，而钟点驱动昼夜节律、场景归属、分离焦虑整套机制。
修复：新增 `_extract_hour()`，只认事件自带的 `datetime` / `timestamp` / `time` / `hour`；
解析不到就 `hour=None`，下游一律按"时刻不可信"处理 ——
`scene_of(None) → '日常'`，昼夜调制取全天均值（`circ_mean()`，带缓存）。
合成模拟有脚本钟点，仍走真值路径（`simulate.py` / `validate.py` / `face_test.py`
的调用点显式传 `hour=`）。

诚实的代价：真实语料不再有"深夜/工作/周末"的场景分岔，
真实 vs 合成的对照不再是同尺度实验。**旧的 `web/real.json` 因此作废**
（它同时是修复前代码 + 伪造钟点下的产物），已移出发布包。

### C2 · 关键词分类器大面积错乱 — 部分修 + 声明上限
`TOPIC_HINT` 里 `'健康'` 指向不存在的 `'vulnerability'`（死映射），改为 `neutral`。
没做 ML 重写（超出本轮范围）。现在 `tools/gen_figs.py` 现场打印 8 条真实中文
样本的 `classify()` 结果进文档：正常闲聊大量落到 `mundane`/`neutral`。
README 相应改写：建立在刺激标签上的"涌现结论"是假设，不是证据。

### C3 · 社会化测试是自指系统 — 保留，文档声明
8 项指标的合理区间是引擎自己标定出来的，测试通过与"像人"之间没有独立证据链。
未改动实现；README 的测试段现在把总分与"这是自指评分"并列陈述。

### C4 · FAB 推翻"情节层只衰减不改写"的宣言 — 已修（**方法论变更，且比原报告更严重**）
原报告说 FAB 把情节 valence 拉向 0.52；复核发现实现还额外把
`fab_decay` 的下限钉在 0.10，使"负性记忆消退"指标永远不可能落到区间外。
修复：默认只衰减唤醒（`arousal_half_life_days=30`），
valence 漂移收进消融开关 `HUMAN['fab']['valence_drift']`（默认 False），
floor 从 0.10 降到 0.02 以解除钉死。
可复现对比（`python3 tools/gen_figs.py` → `docs/figures.md`）：
180 天合成场景里负性情节记忆效价均值，默认 `0.2046` / 消融 `0.3862`。
二轮探针 P-FAB 另用构造语料独立验证：不漂移 0.0267、漂移 0.2518。

### C5 · "涌现结论"随版本漂移、混杂变量未隔离 — 已在文档层面处理
README 现在给出结论的可复现路径（`validate.py` 实验 C）与当次实测数字
（日常善意 6 次 / 深度共处 5 次 / 重大和解 6 次首次撬动），
并注明它依赖 C2 的分类器标签。

### C6 · 文档头条数字全部对不上 — 已修（根治）
新增 `tools/gen_figs.py`：现场跑 180 天、社会化测试、分类器样本、FAB 消融，
写入 `docs/figures.md`（生成物，标了"请勿手改"）。
README 的测试结果段改为引用这套数字，并明确宣告旧手写数字作废。
本轮修复后 180 天 `revisions=17`，与 README 原宣称值一致（此前对不上是因为
B1/B11/C1 未修时跑出的是别的数）。

### C7 · 生物映射的过度声称 — 文档处理
未改实现。README「关键设计」与审查报告均保留：这些是受生物启发的
可调动力学，不是对生理量的模拟。

---

## D. 工程

### D1 · 文档即接口却不可执行 — 已修
- `corpus.py` 的 `D:\train\memory\mem2\...` 硬编码改为
  环境变量 `DATABRAIN_EVENTS` / `DATABRAIN_PEOPLE` 优先，
  默认为包内 `knowledge/events.jsonl`。
- README 的目录、开关、输出文件名与代码实际状态一致（`python` 与 `python3` 均可，
  本机两者都是 3.12）；
  目录段不再列 `tools/package.py`（当前工作区 `tools/` 下无此文件，
  打包步骤改为通用 `zip` / `git archive` 说明）。

### D2 · 配置是全局可变单例 — 部分修
`from . import config as C` 的直读模式未做实例化注入重构（改动面过大）。
本轮至少让消融实验可控：`gen_figs.py` 里改 `C.HUMAN['fab']` 后**显式复原**，
避免同进程后续运行继承脏配置。完整注入式配置仍列为后续项。

---

## E. Ombre-Brain 桥接（本轮现场交付）
OB 已克隆、建 venv（需 `mcp<2`）、起服务并用自写的桥接 PoC 脚本
验证 README §8 的契约：
只读 OB 桶 → 引擎 `experience(override_va=...)` → 只写 `db_*` frontmatter，
OB 自有 `valence/arousal/importance`、检索与衰减全部不受影响。

---

## 二轮验证汇总
`tools/probes_v2.py` 13 项对抗探针：**12 PASS / 0 FAIL / 1 QUANT**
（详见 `docs/review_v2.md`）。唯一非通过项 P-STEP 是 B10 的步长敏感性量化，
属数值方法固有，已文档化。确定性：同 seed 两次 export 的 md5 完全一致，异 seed 不同。
回归：`validate.py` 5 种子零 FAIL、行为一致；`face_test.py` 退出码 0；性能无回归。

## 二轮新发现（修复自身引入的缺陷）

- **B12 · 清洗导致身份碰撞**：B7 的删字符式清洗把 `测试/甲` 与 `测试甲` 并成同一个记忆桶。
  修复见上（crc32 后缀 + 干净名不加后缀）。
- **N1–N4 · 脱敏四处漏网**：`bucket_id`、`people_kept`（别名表不同源）、
  字典键（`_ambivalence_all`）、对照载荷 `real.people[].id`
  （且 full/redacted 写的是同一个对象引用）。
  现在 `_alias_of()` 全工程唯一一张代号表，real 与 compare 共用，
  并加整树递归清洗；跨文件代号一致性实测通过。
- **N5 · 配置静默降级**：`load_people()` 遇到非 `{edges,nodes}` 结构时静默返回 `{}`，
  而 weight 乘在事件强度上 —— 结果是 `episodic` 恒为 0 且日志毫无提示。
  现在兼容扁平写法，缺失/解析失败/结构不符一律 stderr 警告，
  并在 docstring 写明 **weight 量纲是 0~10（5=不缩放），不是 0~1**。
- **一轮报告的三处自我更正**：B5 撤回、A6 降级、A2 精度修正。见 `review_v2.md` §1。

---

# 第三轮（针对交付包本身 + 修复的修复）

审查对象不再是工作树，而是**已交付的两个 zip**：先验容器，再从全新解压态重跑，
最后挖前两轮没覆盖的面。**11 项新缺陷**（N6–N8 内容/引擎、N9–N12 服务器（子代理先报）、
N13–N14 服务器（我自己复现攻击时发现）、N15 交付包隐私指纹，外加 1 项 N9 绕过补漏、
1 项容器权限位缺陷），全部已修并有回归或复扫证据。

## F. 容器层（zip 本身）
- 40 条目全量校验：无 `..`/绝对路径/反斜杠穿越，无异常文件模式，
  无非法编码名，逐条目 CRC 读取零错误。`__pycache__` 零命中。
- public 包内 `.private/` 零命中（探针在包内跑完会生成它，打包前已剔除）。
- **抓到一条自己的打包缺陷**：第二轮交付的两个包里 `README.md` 权限位是 `0600`
  （其余全 `0644`）。`zip -r` 忠实携带源树权限位，而当时的审计只把
  setuid/可执行那类列进"异常位"判据，**没把"数据文件不该是 0600"当判据**，
  所以两轮都放过。后果是实打实的：解包后别的用户读不了 README，CI 直接
  Permission denied。判据改为"常规文件必须恰为 0644"，
  两侧同时落地（打包前 `find . -type f -exec chmod 644 {} +` /
  `-type d -exec chmod 755`，再由 `tools/release_check.py` 断言）。
  **根因**：母本 `src/` 里权限位本来就是混的（README `0600`、十余个文件 `0666`、
  其余 `0644`）—— 是编辑工具链写文件的默认行为，会随每次改动继续漂移，
  所以归一化必须每次打包都做，不能只修一次。归一化前后产物 md5 不变
  （`53b6ee5a…`），证明只动元数据。

## G. 三轮新发现（N6–N8 + 服务器 N9–N15）

- **N6 · 脱敏替换的级联碰撞（严重，B12 同类换层重现）**
  `_redact()` 对每个别名依次 `s.replace(old,new)`。语料里真有人叫 `P2` 时，
  `P20 → P2 → P1`：两个真人被并成同一个代号，与 B12 完全同一类缺陷，
  只是从"清洗姓名"挪到了"映射代号"。
  实测复现：`alias={'P2':'P1','P20':'P2','阿澈':'P3'}` → 三人脱敏后只剩 2 个代号，
  `T:P20|warm|日常` 被改成 `T:P10|warm|日常`（把 `P2` 从 `P20` 里挖走）。
  **修复**：新增 `_make_sub()`，用一次性交替正则做**单趟同时替换**
  （替换结果不再参与匹配），按长度降序保证 `李明华` 优先于 `李明`。
  顺带把 events/persons/themes/episodic/chains/timeline/recon_log 的逐字段映射
  全部删掉，统一交给那一次递归清洗 —— 代码更少，覆盖面更大。
  **回归**：`P-CASCADE`；且正常输入下产物与上一版**逐字节一致**
  （md5 `53b6ee5a…`/`f66516ca…` 未变），证明纯修复无行为漂移。

- **N7 · 外部数值污染产物（严重，浏览器侧崩盘）**
  `people.json` 的 `weight` 是用户手写的外部输入，被直接乘进强度：
  `inten * (0.75 + 0.05*weight)`。填 `-Infinity` 时（Python 的 `json.load`
  默认接受这个非标准字面量）intensity 变成 `-inf`，一路写进**发布版**
  `real.redacted.json`，产物里出现 `-Infinity` ——
  浏览器 `JSON.parse` 直接 `No number after minus sign` 报错，整个 viewer 白屏；
  而 Python 侧读得回去，所以生成阶段一声不响。典型"生成期静默、消费期崩盘"。
  **修复**（两道）：corpus 边界要求 weight 有限并夹紧到 [0,10]，
  非数值/NaN/Inf 回落 0；`_write()` 与 server `_send()` 统一 `allow_nan=False`，
  让任何来源的脏数值在写盘/响应边界炸出来，而不是带着坏产物发布。
  **回归**：`P-NFINITE` 覆盖 7 种脏 weight（-inf/nan/'abc'/None/1e999/999999/-50）
  全部落为有限值，并确认 `_write` 拒绝写出 NaN。
  **正常语料零漂移**：夹紧后演示语料仍逐字节一致。

- **N8 · 前端诊断串的潜在 XSS 汇点（纵深防御）**
  `renderDiag()` 把 `failures/warnings` 与 `hormone_extremes` 的键直接插进
  innerHTML。当前这些串由引擎常量拼成、不含语料可控字段，**打不出去**；
  但同一处一旦将来嵌入 bucket id / 语料文本就是下一个存储型 XSS。
  按 A2 的同样标准补 `esc()`，成本零，并把判断写进注释而非留白。

## H. 服务器层（与子代理独立复现交叉验证）
以下 N9–N12 由子代理先报，我在**自己的全新副本**上独立复现后才采信：

- **N9 · 口令落日志（中）**：token 支持 `?token=`，于是原样出现在请求行，
  而请求行被 access log 写进 stderr。实测 `GET /nope?token=s3cr3t` →
  nohup 日志里能看到明文口令。修复：日志视图过 `_mask_secrets()`，
  掩掉 token/access_token/auth/api_key/key。真实请求不受影响。
- **N10 · 口令比较非常量时间（低）**：`==` 在 `DATABRAIN_HOST=0.0.0.0` 部署下
  是可测量的字节前缀旁路。改 `hmac.compare_digest`，且**比 bytes**
  —— 第一版我写成 `compare_digest(str, str)`，非 ASCII token 会抛 TypeError
  变成 500，等于新引入一个崩溃点；改为两侧 encode 后实测非 ASCII token 回 401。
- **N11 · 缺 `Vary: Accept-Encoding`（低）**：响应随请求头不同而不同就必须声明。
  两处发送路径补齐。本服务自带 `no-store`，风险低，属正确性修正。
- **N12 · gzip 缓存可返回旧体（中）**：键只有 `(path, mtime(float), size)`，
  挡不住"同长度改写 + `os.utime` 把 mtime 调回去"。实测该情形下服务仍吐旧压缩体。
  修复：键扩为 `(path, ino, size, mtime_ns, ctime_ns)` —— ctime 由内核在写入时更新、
  `utime` 改不动它，inode 再堵住换文件对齐时间的路。修复后同一攻击实测返回新字节。

## I. 三轮新增的三件可重跑审计工具

前两轮"转义是否全覆盖""包干不干净"靠人工点数 + 一次性脚本，本轮把它们固化成
仓库里的工具，免得下次改前端或重新打包又靠记忆：

- **`tools/audit_esc.py`（静态）**：解析 `web/index.html`，
  对每个 `${...}` 模板插值做花括号配对，判断其中出现的**语料可控字段**
  （subject / stim / text / detail / hits / id / bucket_id / note / label /
  theme_key / bucket / name / action）是否都落在 `esc(...)` 的安全区内；
  另外断言不存在内联事件处理器里的插值。注释里的 `esc()` 不计入调用点，
  且注释替换保留换行 —— 报出来的行号与原文件一致。
  退出码 0=干净。**负向对照已验**：注入 3 处未转义 + 1 处 `onclick="go(${e.stim})"`
  → 报出 3 处未转义插值 + 1 处内联事件插值，退出码 1。
- **`tools/xss_render_test.js`（动态）**：抽出页面 `<script>` 块，
  套最小 DOM 桩在 Node 里**真实执行** `renderAll()`，
  夹具直接读线上产物 `web/real.redacted.json` 再把载荷塞进可控字段
  （手写夹具形状不对会让 renderAll 提前崩，"没泄露"就变成假阴性）。
  自带**防空转断言**：要求载荷以转义形态真实出现在 DOM 里（≥3 种），
  否则判 FAIL 而不是 PASS —— 因为"没原样出现"和"根本没画出来"用裸断言分不开。
  实测：9 处 innerHTML 写入、32 万字节，`&lt;script&gt;…` 形态出现 970 次，
  原样载荷 0 次。**负向对照已验**：去掉一处 `esc()` → 载荷原样进 DOM，退出码 1。
- **`tools/release_check.py`（容器 + 内容隐私，本轮新增）**：审的是 **zip 本体**
  而不是工作树。六类容器判据（危险路径形态、权限位必须恰为 0644、
  非 ASCII 名的 UTF-8 标志位、构建残渣、发布包多余条目、逐条目 CRC）
  + 四类内容判据（构建机路径、语料指纹、真名、`--mode public/private` 分级）。
  **人名与指纹判据一律写成字符类，名单只能从包外 `--names-file` 传入**：
  第一版我在注释里举例写了原值，文件进包后被自己判 FAIL；
  第二版把演示语料的虚构名内联成常量，结果 64 条假阳性 ——
  判据写死进被检查物等于既当裁判又当运动员，真名更不能内联。
  数据产物里的同值巧合按"两类以上指纹同时出现"才判，避免误伤引擎输出。
- 前两者由探针 `P-ESC` 串起来跑，互相交叉验证；node 缺失时动态侧记 **SKIP**
  （不是伪装成 PASS），套件末行同时打印 `FAIL=` 与 `SKIP=`。
  第三件由 `P-RELEASE` 验尺子本身（临时目录现造干净 zip + 毒 zip 双控）。

## J. 三轮追加发现（N13–N15）

- **N13 · 500 响应外带本机绝对路径（中）**：`_check_auth` 之外三处
  `self._send(500, {'error': str(e)})` 把原始异常文本发给客户端，
  `PermissionError` 的 `str()` 自带文件名。以**非 root** 身份
  （root 下 `chmod 000` 挡不住读，这条必须降权才复现得出来）实测：
  `{"error": "[Errno 13] Permission denied: '<构建机>/web/real.redacted.json'"}`。
  这与 `log_message` 里自己写的注释"不回显文件系统路径"直接矛盾 ——
  注释承诺了代码没实现的性质。修复：新增 `_safe_error()`，
  按长度**降序**替换 `HERE/WEB/WEB_REAL/父目录`（第一版没排序，输出叠了
  两层 `<path><path>/`），再用"至少两级"的绝对路径正则兜底；
  刻意不匹配单段路径，免得把 `JSONDecodeError` 这类正常错误也弄成不可读。
  正则灾难性回溯另测：`'/'*20000`、`'/'+'a/'*20000` 均 2.5ms 内返回。
- **N14 · 非回环监听 + 空口令 = 全量导出无人看守（高）**：`_check_auth` 的
  docstring 明写"绑到 0.0.0.0 必须设 DATABRAIN_TOKEN"，代码却不检查；
  `if not _AUTH_TOKEN: return True` 让"无口令"退化成"无鉴权"。实测
  `DATABRAIN_HOST=0.0.0.0` 无 token：`/api/data` **200 / 641 KB**（完整记忆导出）、
  `/api/run` **200 / 1.18 MB**（任何人可驱动重算）、`/api/config` 200。
  修复：`_open_bind_without_token()` + `main()` 前置闸门 —— 非回环且无口令
  **拒绝启动**并给三条出路（改回默认 / 设口令 / 显式 `DATABRAIN_ALLOW_OPEN=1`）。
  闸门放在跑模拟**之前**，否则要等约 20 秒才报错。四种组合逐一实测（见 review_v3 §3.4）。
  这条与 N7 同构：**安全前提只写在文字里、没写进代码里**。
- **N15 · 交付包自身泄露私人语料指纹（严重，隐私）**：只有"审交付包本体"这个
  视角才看得见。已发布的 public 包里，README / review_v2 / CHANGELOG /
  `web/index.html` 页面文案 / 三个引擎文件的注释，共 8 个文件印着
  只能从**原始私人语料**算出的那组数（跨度天数、事件数、社会化总分、认定区间）。
  这组数是指纹不是指标：与任何外部线索对上，脱敏就白做 ——
  而本轮同时证明了脱敏代号可 5/5 频率反推，两条叠加就是还原真名的第二把钥匙。
  修复：公开可见的每个字节改为尺度无关表述，精确数字只搬进
  `PRIVATE_README.md`（仅自用包）并在原位留指针；`config.py` 里连日常占比、
  salience 均值、被美化情节比例这类可反推的百分数一起换掉。
  复扫判据固化成 `tools/release_check.py`。

## K. 三轮验证汇总
`tools/probes_v2.py` 现为 **18 项**：17 PASS / 0 FAIL / 1 QUANT / 0 SKIP。
子代理独立审计结论：36 PASS / 4 FINDING（全部对应 N9–N12，已在我自己副本上复现才采信）。
容器层：本轮两包 36 / 42 常规文件全部 `0644`、零穿越、CRC 全通过、
真实人名零命中、构建机路径零命中、public 语料指纹零命中
（唯一剩项是产物里一个引擎生成的巧合浮点，已单独核对并写明判据）。
`release_check.py` 的判别力用**已知的第二轮坏包**验：它独立复现了我手工发现的
全部 15 条（含那条 0600），一条不漏；同一把尺子对本轮包给 PASS。
`P-RELEASE` 再验尺子本身：正例 rc=0、毒例 rc=1 且四类命中齐全，
把判据短路后探针报 `漏判=权限位`。
**关键回归证据**：N6/N7/N13/N14/N15 全部修复对正常演示语料
**逐字节无输出漂移**（real `53b6ee5a…`、compare `f66516ca…`、full `810fada6…`
三个 md5 全程不变）。

## L. 第四轮（针对交付包本身，2026-09-28）
报告见 `docs/review_v4.md`。新发现 5 项（N16–N20），全部已修：

- **N16 服务器**：绑定闸门的"拒绝启动"用 `return`，退出码是 **0**。
  被 systemd/Docker/CI 拉起时，安全拒绝与启动成功无法区分，编排层会判健康
  或无限重启并每次记成功。改为走 stderr + `raise SystemExit(2)`。
- **N17 前端/文档**：N14 推荐的补救（设 `DATABRAIN_TOKEN`）会让可视化整页 401 空白
  —— 前端无处交口令，也没有 401 分支。等于推荐了一条死路。修复：前端每个 `/api/*`
  带 `X-Databrain-Token` 头，401 时弹一次 prompt 收口令存 `sessionStorage`，
  口令绝不进 URL。`xss_render_test.js` 的 DOM 桩补了 `sessionStorage`/`window`。
- **N18 服务器**：①伪造 `Host:`（DNS rebinding）仍返 200 + 641 KB 全量记忆，
  回环监听时校验 Host，非白名单回 421；②`Server: BaseHTTP/0.6 Python/3.12.13`
  公示精确解释器小版本，改为 `Server: DataBrain`。
- **N19 服务器**：`/api/run` 是会改变状态的 GET（几十秒 CPU + 覆盖缓存），
  任意网页 `<img>` 即可借访客机器去跑。要求带自定义头，裸 GET 回 428。
- **N20 文档/前端**：公开包正文与前端标签写"真实语料"，但包内语料是**虚构演示数据**，
  开源读者会误以为仓库带着某人的真实聊天记录。用户可见标签统一改"语料"，
  README 树状说明标注"包内是虚构演示语料"，涉及真实数据的叙述只留在自用包。

验证：`tools/probes_v2.py` 现为 **19 项**，新增 `P-HTTP-R4`（起真实进程打真实 HTTP，
覆盖 N16/N17/N18/N19），末行 FAIL=0 SKIP=0。新探针做了反向对照：把四处修复还原成
缺陷态 → `P-HTTP-R4` FAIL 并逐项指名。**无输出漂移**：real `53b6ee5a…`、
compare `f66516ca…`、full `810fada6…`、det `b697bd61bf` 四个 md5 全程不变。
