# 第四轮对抗性审查报告（2026-09-28）

审查对象：**已交付的两个 zip 本身**（`databrain_public_20260928_r3.zip` /
`databrain_private_20260928_r3.zip`），全新解压后逐字节核。这一轮不重读
源码找逻辑问题，而是把交付物当成"别人拿到手会怎样"来打。

结论：找到 **5 个新缺陷**（N16–N20），全部已修复并加了动态探针；
**无输出漂移**；两包重建、复验通过。

## 0. 汇总

| 编号 | 层 | 缺陷 | 严重度 | 状态 |
|---|---|---|---|---|
| N16 | 服务器 | 安全拒绝退出码是 **0** —— 编排层看不出启动被拒 | 高 | 已修，`P-HTTP-R4` 复验 |
| N17 | 前端/文档 | N14 推荐的补救（设口令）会让可视化**整页 401 空白**，前端无处交口令 | 高 | 已修，前端 prompt + `sessionStorage` |
| N18 | 服务器 | ①伪造 `Host:` 仍返 200（DNS rebinding 可读本机全部记忆）②`Server:` 头公示精确 Python 小版本 | 中 | 已修，421 + 自定义 `server_version` |
| N19 | 服务器 | `/api/run` 是**会改变状态**的 GET，任意网页 `<img>` 即可借你的机器跑几十秒 CPU | 中 | 已修，要求自定义头，裸 GET 回 428 |
| N20 | 文档 | 公开包正文说"含真实人名"、README 提"真实语料结果"，但**包内语料是虚构的** —— 描述与实际交付物不符，会误导开源读者 | 低（但发布即错） | 已修，措辞统一为"演示语料"，真名说法只留在自用包 |

> N20 是这一轮唯一"不是安全洞、但发到开源社区就是错"的问题，
> 详见 §2.5。

## 1. 交付容器审计（全新解压后）

- 权限位：public `0o100644 ×37 / 0o40755 ×7`；private `0o100644 ×43 / 0o40755 ×9`。
  上一轮那个 `0600` README 没有复发。
- zip 中央目录：**无**绝对路径、无 zip comment、无 extra 字段泄漏构建机信息。
- 顶层目录名规范（`databrain_public/` / `databrain_private/`），解压不会洒一地文件。
- `__pycache__/*.pyc` **在 zip 里不存在**（只在解压后跑代码时生成），干净。
- private 独有 6 项：`.private/{real.full.json, compare.full.json, legacy/*}`、
  `PRIVATE_README.md`、`docs/review_v1_20260928.md` —— 与文档声明一致。

## 2. 逐项

### 2.1 N16 · 安全拒绝的退出码是 0

上一轮加的绑定闸门（`0.0.0.0` 无口令就拒绝启动）用的是 `return`：

```text
$ DATABRAIN_HOST=0.0.0.0 python3 server.py; echo rc=$?
拒绝启动：…
rc=0        ← 三轮遗留
```

一个"我不干了"的进程用成功码退出。systemd / Docker / CI / 计划任务里，
这和"启动成功"无法区分：编排层会判健康，或者干脆无限重启并每次都记一次成功。
安全拒绝必须失败。

修复：走 stderr + `raise SystemExit(2)`。

```text
$ DATABRAIN_HOST=0.0.0.0 python3 server.py; echo rc=$?
rc=2
$ grep -c 拒绝启动 /tmp/n16.err
1        ← 走 stderr，不再进 stdout
```

`DATABRAIN_ALLOW_OPEN=1` 的知情放行仍能正常启动（探针 `n16b` 断言进程活着）。

### 2.2 N17 · N14 给的补救办法是死路

N14 的拒绝信息里第 2 条建议是"设口令：`DATABRAIN_TOKEN='…' python server.py`"。
照做之后：

```text
$ DATABRAIN_TOKEN=abc123 python3 server.py     # 端口 18102
UI /                    -> 200
api/data 无 token       -> 401
api/data 带 token       -> 200
```

而 `web/index.html` 里**没有任何地方能交出这个口令** —— 前端只有
`fetch('/api/data?_t=…')`，没有 token 入口，也没有 401 分支（401 的 JSON
会被当成"解析失败"报成 `SyntaxError` 风格的重试提示）。结果：照建议设了口令，
可视化整页空白，用户会以为程序坏了。

修复（前端）：
- 每个 `/api/*` 请求带 `X-Databrain-Token` 头；
- 收到 401 弹一次 `prompt` 收口令，存 `sessionStorage`（关标签页即清，
  不写 `localStorage`，不跟备份/漫游走）；
- 口令**绝不进 URL** —— `?token=` 会落到浏览器历史、Referer 和访问日志，
  等于把 N9 的日志掩码白做；
- 弹窗重试上限 5 次，避免反复输错变成死循环。

`xss_render_test.js` 的 DOM 桩相应补了 `sessionStorage` / `window`（否则页面脚本
在装载阶段就 `ReferenceError`，退出码 2，那是假失败）。

### 2.3 N18 · 伪造 Host 可读全部记忆 + Server 头版本公示

```text
$ curl -H 'Host: evil.com' http://127.0.0.1:8777/api/data
-> 200, 641136 字节        ← 三轮遗留
```

浏览器同源策略只看 URL。攻击者把 `evil.com` 的 A 记录指到 `127.0.0.1`，
用户访问那个网站，页面里的 JS 就能读到本机 DataBrain 的**整个记忆导出**
（响应体不带 CORS 头不影响：读取被同源策略挡住的前提是 Origin 不同，
而 rebinding 场景下 Origin 就是 evil.com 自己）。本机服务没有口令（默认配置）时，
这是唯一一道门，而它当时不存在。

修复：回环监听时校验 `Host`，非白名单回 `421 Misdirected Request`；
显式绑到非回环地址时放行（此时 N14 已强制要求口令，且浏览器发的是机器名/LAN IP，
白名单只会误伤）。

```text
Host: evil.com          -> 421
Host: 127.0.0.1:18110   -> 200
```

顺带：`Server: BaseHTTP/0.6 Python/3.12.13` 对外公示精确解释器小版本，
攻击者可直接比对已知 CVE。改为 `server_version='DataBrain'` / `sys_version=''`，
现在只发 `Server: DataBrain`。

### 2.4 N19 · 状态改变的 GET 无跨站防护

`/api/run?days=365` 跑几十秒 CPU 并覆盖 `_cache`。它是 GET，于是：

```html
<img src="http://127.0.0.1:8777/api/run?days=365">
```

任意网页都能借访客的机器去跑，且 `_run_lock` 的"同时只允许一个"反而让
攻击者能持续占用（后续请求全 409），把服务卡死。Host 校验挡不住这个 ——
浏览器发出的 `Host` 就是合法的 `127.0.0.1:8777`。

修复：要求带自定义头 `X-Databrain-Token`（前端已自动带）。跨站请求要加自定义头
必须先过 CORS 预检，而本服务不发任何 `Access-Control-Allow-*`，预检必然失败。

```text
GET /api/run                    -> 428 Precondition Required
GET /api/run  (带自定义头)       -> 200
```

### 2.5 N20 · 公开包的描述与实际内容不符

包内语料是**虚构演示数据**（`knowledge/events.jsonl` 792 条、6 个假人物；
最长文本 14 字，全部来自模板句）。但公开包正文里仍留着真实数据时代的措辞：

| 文件 | 原文 | 问题 |
|---|---|---|
| `README.md` | "`web/real.redacted.json` 是**真实语料**跑出来的结果" | 开源读者会以为仓库里带着某个人的真实聊天记录 |
| `docs/review_v2.md` / `v3.md` | "含真实人名"、"真实语料那组指纹" | 同上，且暗示存在一份未发布的真实数据 |

`docs/review_v3.md:366` 甚至写着 private 侧 27 处命中"集中在 `.private/legacy/*`、
`review_v1`、`PRIVATE_README`"—— 那是**自用包**的事实，公开包里这几个文件不存在，
读者按图索骥会找不到东西。

这不是安全漏洞（`release_check.py` 判 PASS 是对的：没有真实指纹泄漏），
但开源发布即错：描述不实会让读者对数据来源产生错误预期，也可能让人
误以为公开仓库里含隐私。

修复：公开侧措辞统一为"演示语料/包内虚构语料"，涉及真实数据的叙述只在
自用包保留；`README.md` 明确 `web/real.redacted.json` 是**包内虚构演示语料**的结果。
核对后公开包内已无"真实语料 = 某人真实聊天"的暗示。

## 3. 证据

### 3.1 探针套件（`tools/probes_v2.py`，19 项）

新增 `P-HTTP-R4`，**起真实进程打真实 HTTP**（N16 是退出码、N18/N19 是路由行为，
只读源码判不出来）：

```text
[PASS ] P-SERVER     N9 日志掩码=ok N10 鉴权=ok N11 Vary=ok N12 缓存键=ok N13 错误回显=ok N14 绑定闸门=ok
[PASS ] P-RELEASE    正例 rc=0 毒例 rc=1 命中=权限位,指纹,真名,多余条目
[PASS ] P-ESC        静态 clean(18 行 / 22 处) 动态 0 泄漏 | 4 （要求 ≥3）
[PASS ] P-HTTP-R4    N16 拒绝码=ok 放行仍启动=ok N18 Host=ok Server头='DataBrain '
                     N19 run防CSRF=ok N17 前端交口令=ok
----------------------------------------------------------------------
总计 19 项：FAIL=0 SKIP=0
```

### 3.2 新探针的反向对照（证明它不是空壳）

把四处修复逐一还原成缺陷态，`P-HTTP-R4` 必须 FAIL 并指名：

```text
[FAIL ] P-HTTP-R4  N16 拒绝码=BAD 放行仍启动=ok N18 Host=BAD
                   Server头='BaseHTTP/0.6 ' N19 run防CSRF=BAD N17 前端交口令=ok
```

（`放行仍启动` 保持 ok 是对的：那个子断言在缺陷态下也应通过，
它测的是"知情放行没被误杀"。`N17 前端交口令=ok` 也正确，因为那次只回退了 server.py。）
`xss_render_test.js` 同样做了反向对照：把一处 `esc()` 摘掉 → 退出码 1；
恢复 → 退出码 0。

### 3.3 攻击面对照表（四轮前 → 四轮后）

| 攻击 | 三轮包 | 四轮包 |
|---|---|---|
| 网页 rebinding 读 `/api/data` | 200 + 641 KB | **421** |
| 网页 `<img>` 触发 `/api/run` | 200（跑几十秒 CPU） | **428** |
| 指纹精确 Python 版本 | `BaseHTTP/0.6 Python/3.12.13` | `DataBrain` |
| 编排层误判"拒绝启动"为成功 | rc=0 | **rc=2 + stderr** |
| 照建议设口令后打不开页面 | 整页 401 空白 | prompt 收口令，`X-Databrain-Token` 头 |

### 3.4 无输出漂移

引擎一行未动，只改了服务器路由与前端取数方式。四轮前后逐一比对：

```text
P-DET                   同 seed md5 一致=True(b697bd61bf) 异 seed 不同=True
web/real.redacted.json  53b6ee5a3cddc11727ea0cc7c7cbd656   （不变）
web/compare.redacted.json f66516ca34143a5fc99e4421e8526b43 （不变）
.private/real.full.json 810fada6c4b1b47fa8ee84f33331f375   （不变）
```

## 4. 这一轮我自己写出的缺陷（记录在案）

1. `p_http_r4` 初版留了一行垃圾代码 `'知情放行' in ''`（永远 False）
   和一行未使用的 `src = open(...)`。反向对照时才暴露，已删。
2. `xss_render_test.js` 的 DOM 桩没有 `sessionStorage`，加完 N17 之后
   页面脚本装载即 `ReferenceError` → 退出码 2。这是**我改了产物没同步改测试桩**
   造成的假失败，已补桩并验证 clean rc=0 / poisoned rc=1 / restored rc=0。
3. N18 的 Host 白名单初版对非回环监听也生效，会把 LAN 访问误判成 421
   （浏览器发的 Host 是机器名，不是字面 `0.0.0.0`）。已改成"仅回环监听时校验"。
4. 曾把"另外两件四轮加固"写进 README，实际列了三条。已改。

## 5. 仍然存在的风险（不隐瞒）

1. **仓库无 LICENSE** —— 开源发布前必须由你决定，我不替你选。
2. **口令是全局一个**，无按人区分、无失败次数限制。本机自用足够，
   真放到公网应换成正经反代 + 认证。
3. `sessionStorage` 里的口令对**同源的其它脚本**可见。本仓库前端无第三方脚本
   （无 CDN、无 npm），这是有意的设计约束，别往里加外部 JS。
4. `421` 依赖客户端诚实发送 `Host`。命令行工具可以不带（本实现把空 Host 视为本机），
   所以这道门防的是浏览器/rebinding，不是防本地提权。
5. `days` 上限 365、`seed` 上限 1e9 是既有节流，但**没有并发配额** ——
   带口令的用户仍可连续触发长任务。本机场景可接受。

## 6. 发布流程（四道检查）

```bash
# 1) 语料/结构自检
python3 tools/validate.py

# 2) 行为探针：19 项，末行 FAIL=0 SKIP=0
python3 tools/probes_v2.py

# 3) 前端转义：静态 + 动态实弹
python3 tools/audit_esc.py && node tools/xss_render_test.js

# 4) 发布容器审计（人名清单不进包，只在这里传）
python3 tools/release_check.py <发布版 zip> --mode public  --names-file /你的/私人名.txt
python3 tools/release_check.py <自用版 zip> --mode private --names-file /你的/私人名.txt
```

`release_check.py` 判据全部写成字符类（`17[2]0`）或从 `--names-file` 外部读入，
**工具自身不含被检字面量** —— 否则打包进 zip 后它会匹配到自己，
上一轮为此栽了两次（写进注释 / 内联演示人名常量，后者一次造成 64 处误报）。
