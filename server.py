# -*- coding: utf-8 -*-
"""
数据化大脑 · 可视化服务端

零依赖（只用标准库 http.server），不需要 pip install 任何东西。

启动：
  python3 server.py
然后浏览器打开 http://127.0.0.1:8777

接口：
  GET /                       前端页面
  GET /api/data               当前缓存的模拟结果
  GET /api/real               真实语料跑完的结果（web/real.json）
  GET /api/compare            真实语料 vs 合成场景 的对照（web/compare.json）
  GET /api/run?days&seed      重跑一次模拟（较慢，几十秒）
  GET /api/config             当前模型的全部可调参数
  GET /api/health             存活检查
"""

import gzip
import hmac
import json
import os
import re
import sys
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 用 pythonw（无控制台）自启时 sys.stdout/stderr 是 None，
# 任何 print 都会直接抛 AttributeError。重定向到空设备。
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

from databrain import config as C          # noqa: E402
from databrain.simulate import run         # noqa: E402

HOST = os.environ.get('DATABRAIN_HOST', '127.0.0.1')
# 端口可改：默认 8777 被别的东西占了的时候，
#   DATABRAIN_PORT=8778 python server.py
PORT = int(os.environ.get('DATABRAIN_PORT', '8777'))
HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, 'web')
WEB_REAL = os.path.realpath(WEB)

# 数据文件选取（审查A4修复配套）：
#   默认（发布/共享场景）走脱敏版；DATABRAIN_FULL=1 时优先 .private 未脱敏版（自用）。
#   老文件 real.json/compare.json 是修复前用真实原文生成的，只在两个新文件
#   都不存在时才回退，提示用户重跑。
_FULL_MODE = os.environ.get('DATABRAIN_FULL', '') == '1'

def _pick_data_file(full_path, redacted_path, legacy_path):
    if _FULL_MODE and os.path.isfile(full_path):
        return full_path
    if os.path.isfile(redacted_path):
        return redacted_path
    if os.path.isfile(legacy_path):
        return legacy_path
    return None

_lock = threading.Lock()
_cache = {'data': None, 'params': {'days': 180, 'seed': 42}, 'status': 'idle'}

# --- 节流：同时只允许一个 /api/run ---
_run_lock = threading.Lock()
_run_active = False

# --- 可选鉴权 ---
_AUTH_TOKEN = os.environ.get('DATABRAIN_TOKEN', '')

# 三轮审查 N14：把注释里的约定变成真正的闸门。
# 原版只在 docstring 里写"绑到 0.0.0.0 必须设 DATABRAIN_TOKEN"，代码并不检查：
# 实测 `DATABRAIN_HOST=0.0.0.0`（无 token）时 /api/data 直接吐 641 KB 全量记忆导出、
# /api/run 谁都能驱动 —— 一句文档约定挡不住一次误配置。
# 现在非回环地址且没口令 = 拒绝启动（可用 DATABRAIN_ALLOW_OPEN=1 明确知情放行）。
_LOOPBACK = ('127.0.0.1', 'localhost', '::1')


def _open_bind_without_token():
    """返回 (是否该拒绝启动, 打印给人看的说明)。

    该拒绝 = 监听在非回环地址 + 没口令 + 没有明确知情放行。
    """
    if _AUTH_TOKEN or HOST in _LOOPBACK:
        return False, ''
    if os.environ.get('DATABRAIN_ALLOW_OPEN') == '1':
        return False, (f'{HOST} 非回环监听且无口令，'
                       f'已按 DATABRAIN_ALLOW_OPEN=1 知情放行')
    return True, HOST

# --- 静态文件 gzip 缓存：key=(realpath, mtime, size) -> compressed bytes ---
_gzip_cache = {}
_gzip_cache_lock = threading.Lock()

# 审查（三轮 N9）：日志里要掩掉的敏感 query 参数
_SECRET_RE = re.compile(r'([?&])(?:token|access_token|auth|api_key|key)=[^&]*',
                        re.IGNORECASE)


def _safe_error(exc):
    """三轮审查 N13：错误信息回客户端前抹掉本机绝对路径。

    `str(e)` 里最常见的两类会直接暴露部署目录：
      FileNotFoundError/PermissionError → "[Errno 13] Permission denied:
        '/abs/path/web/real.redacted.json'"
      json 解析失败 → 不带路径，但 do_run 里的 OSError 带。
    服务端自己看日志时要留完整信息，所以这里只处理"发出去的那一份"。
    """
    msg = str(exc)
    # 先长后短，否则父目录先被换掉会让子路径匹配不上、留下叠两层占位符
    for p in sorted({HERE, WEB, WEB_REAL, os.path.dirname(HERE)},
                    key=len, reverse=True):
        if p:
            msg = msg.replace(p, '<path>')
    # 兜底：任何剩余的 "/xxx/" 形式绝对路径段都换成占位符
    msg = re.sub(r"(?<![\w])/(?:[A-Za-z0-9_.\-\u4e00-\u9fff]+/)+", '<path>/', msg)
    return msg


def _mask_secrets(text):
    """把 URL query 里的敏感参数值换成掩码，只用于日志输出。

    token 既支持 header 也支持 ?token=，所以它会原样出现在请求行里；
    请求行被 access log 写进 stderr（终端回滚、nohup.out、日志采集），
    等于把口令落盘。这里改的只是日志视图，真实请求不受影响。

    三轮审查（N9 的补漏）：只按原始文本匹配会被绕过 ——
    `?%74oken=xxx`（把 t 百分号编码）照样能通过鉴权，因为
    parse_qs 会先解码参数名；但日志里那条请求行不含字面 "token"，
    正则匹配不到，于是口令明文落进日志。实测确认后再修。
    现在对解码后的文本再掩一遍，并把口令明文本身兜底替换。
    """
    masked = _SECRET_RE.sub(r'\1token=<masked>', text)
    try:
        decoded = urllib.parse.unquote(text)
    except Exception:
        decoded = text
    if decoded != text:
        masked = _SECRET_RE.sub(r'\1token=<masked>', decoded)
    if _AUTH_TOKEN:
        for secret in {text, decoded}:
            if _AUTH_TOKEN in secret:
                masked = masked.replace(_AUTH_TOKEN, '<masked>')
    return masked


def _safe_int(val, default, lo=None, hi=None):
    """审查A3修复：外部数字参数一律容错 + 钳位，不再让 int('abc')
    的 ValueError 逃出 handler 把连接砸断；days 上限 365 防单请求造出
    多年逐小时模拟（原版 days=99999 就是一个免费 DoS）。"""
    """安全地把值转成 int，非法时回 default，然后 clamp 到 [lo, hi]。"""
    try:
        v = int(val)
    except (ValueError, TypeError):
        v = default
    if lo is not None and v < lo:
        v = lo
    if hi is not None and v > hi:
        v = hi
    return v


def do_run(days, seed):
    """跑一次模拟并缓存导出结果。"""
    brain, diag = run(int(days), int(seed), verbose=False)
    data = brain.export(180 * 24.0 if days is None else float(days) * 24.0)
    data['diagnostics'] = {
        'failures': diag.failures,
        'warnings': diag.warnings,
        'hormone_extremes': {k: [round(v[0], 4), round(v[1], 4)]
                             for k, v in diag.hormone_extremes.items()},
        'info': diag.info,
    }
    with _lock:
        _cache['data'] = data
        _cache['params'] = {'days': int(days), 'seed': int(seed)}
        _cache['status'] = 'ready'
    return data


def _check_static_path(rel):
    """检查静态文件路径是否安全（不越出 WEB 目录）。
    返回安全的绝对路径，或 None 表示拒绝。

    审查A1修复：原版用 `full_path.startswith(WEB)` 判前缀，
    而 WEB 未 realpath：`web/../../etc/passwd` 在**字符串层面**仍以 WEB 开头，
    检查放行，`open()` 才由文件系统解析出目录（实测可读 /etc/shadow）；
    同级兄弟目录名（`web.bak/`）同样能骗过前缀比较。
    现在两边都 realpath，再用 os.path.commonpath 判归属 ——
    符号链接、`..`、百分号编码穿越一并堵住。
    """
    target = os.path.realpath(os.path.join(WEB, rel))
    try:
        if os.path.commonpath([WEB_REAL, target]) != WEB_REAL:
            return None
    except ValueError:
        # 例如不同驱动器（Windows）
        return None
    return target


def _get_gzipped_body(raw_body, accept_encoding):
    """如果客户端接受 gzip 且 body 够大，返回压缩后的 bytes（带缓存）。
    否则返回 None 表示不压缩。
    """
    if len(raw_body) <= 4096 or 'gzip' not in accept_encoding.lower():
        return None
    # 缓存 key 用 body 的 id 不行（会被 GC），用内容 hash 太慢。
    # 对静态文件我们可以在 _send_file 里用 (path, mtime, size) 做 key。
    # 这里对非文件来源的 body 不做缓存，直接压缩。
    return gzip.compress(raw_body, 6)


def _get_cached_gzip_file(filepath, accept_encoding):
    """读取静态文件并返回 (body_bytes, is_gzipped)。

    审查（三轮 N12）：缓存键从 (path, mtime, size) 扩到
    (path, ino, size, mtime_ns, ctime_ns)。
    旧的 float mtime + size 挡不住「同长度改写 + 用 os.utime 把 mtime
    调回去」——实测这样服务会继续吐旧的压缩体。ctime 由内核在写入时
    更新、utime 改不了它，所以把它放进键里就能堵住这条路；
    inode 再堵住「换文件但故意对齐时间与长度」。
    """
    if 'gzip' not in accept_encoding.lower():
        with open(filepath, 'rb') as f:
            return f.read(), False

    try:
        st = os.stat(filepath)
    except OSError:
        return None, False

    cache_key = (filepath, st.st_ino, st.st_size,
                 st.st_mtime_ns, st.st_ctime_ns)

    with _gzip_cache_lock:
        cached = _gzip_cache.get(cache_key)
        if cached is not None:
            return cached, True

    # 未命中：读文件并压缩
    with open(filepath, 'rb') as f:
        raw = f.read()

    if len(raw) > 4096:
        compressed = gzip.compress(raw, 6)
        with _gzip_cache_lock:
            # 清理过期条目（简单策略：超过 32 条就清空）
            if len(_gzip_cache) > 32:
                _gzip_cache.clear()
            _gzip_cache[cache_key] = compressed
        return compressed, True
    else:
        return raw, False


def _check_auth(handler):
    """检查鉴权。返回 True 表示通过，False 表示已发送 401。

    审查A3/D1配套：本服务只应监听 127.0.0.1；若要放到别的机器或
    局域网（DATABRAIN_HOST=0.0.0.0），必须设 DATABRAIN_TOKEN，
    否则任何人都能免密驱动你的 /api/run 与读取全部记忆导出。
    /api/health 豁免，方便探活。"""
    if not _AUTH_TOKEN:
        return True
    # 三轮审查（N10）：口令比较改用 hmac.compare_digest。
    # 服务只监听 127.0.0.1 时这是纸面问题，但 README 允许
    # DATABRAIN_HOST=0.0.0.0 —— 放到网络上，`==` 的短路行为
    # 就成了可测量的旁路（第几字节开始不一致 → 口令前缀）。
    def ok(candidate):
        # 比 bytes 而不是 str：compare_digest 对含非 ASCII 的 str 会抛
        # TypeError（=500），攻击者只要塞一个非 ASCII token 就能触发。
        if candidate is None:
            return False
        try:
            return hmac.compare_digest(str(candidate).encode('utf-8'),
                                       _AUTH_TOKEN.encode('utf-8'))
        except Exception:
            return False
    # 从 query string 查 token
    parsed = urllib.parse.urlparse(handler.path)
    qs = urllib.parse.parse_qs(parsed.query)
    token_qs = qs.get('token', [None])[0]
    if ok(token_qs):
        return True
    # 从 header 查 token
    if ok(handler.headers.get('X-Databrain-Token')):
        return True
    handler._send(401, {'error': 'unauthorized'})
    return False


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    # 四轮审查 N18：不覆盖的话 BaseHTTPRequestHandler 会把
    # `Server: BaseHTTP/0.6 Python/3.12.13` 发给每个请求，
    # 等于对外公示精确解释器小版本，攻击者可直接比对已知 CVE。
    server_version = 'DataBrain'
    sys_version = ''

    # 允许的 Host 头（DNS rebinding 防护）：浏览器同源策略只看 URL，
    # 而 evil.com 的 DNS 可以指向 127.0.0.1 —— 于是任意网页都能读到
    # /api/data（实测 Host: evil.com 时仍返回 200 + 641 KB 全量记忆）。
    # 校验 Host 就能把这类"看起来跨站其实是本机"的请求挡掉。
    def _host_allowed(self):
        if HOST not in _LOOPBACK:
            # 非回环监听本来就是对整个网卡开放（且 N14 要求有口令），
            # 用 Host 做白名单在这里只会误伤：浏览器发来的是机器名/LAN IP，
            # 不是字面 0.0.0.0。放行。
            return True
        raw = self.headers.get('Host', '') or ''
        host = raw.rsplit(':', 1)[0].strip('[]').lower()
        # 空 Host（curl/脚本常不带）与 IPv6 括号写法都算本机
        return host in {'127.0.0.1', 'localhost', '::1', ''}

    def log_message(self, fmt, *args):
        # 安静一点，只在出错时说话；不回显文件系统路径
        msg = fmt % args
        if '404' in msg or '500' in msg:
            msg = _mask_secrets(msg)   # 三轮审查 N9：别让 ?token= 落进日志
            # 过滤掉可能的文件系统路径（以 WEB 目录开头的部分）
            safe_msg = msg.replace(WEB_REAL, '<web>')
            safe_msg = safe_msg.replace(WEB, '<web>')
            sys.stderr.write("  %s - %s\n" % (self.address_string(), safe_msg))

    # ---------- helpers ----------
    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, (dict, list)):
            # N7：写出侧同样拒绝 NaN/Infinity —— 服务端是最后一道边界，
            # 宁可回 500，也不能把浏览器 JSON.parse 打不开的响应发出去。
            body = json.dumps(body, ensure_ascii=False,
                              allow_nan=False).encode('utf-8')
        elif isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        # 大 JSON 走 gzip：/api/real 有 2.5MB，压完不到 200KB，
        # 传输被中间层截断的概率也小得多
        ae = self.headers.get('Accept-Encoding', '')
        if len(body) > 4096 and 'gzip' in ae.lower():
            body = gzip.compress(body, 6)
            self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(body)))
        # 三轮审查 N11：响应会因 Accept-Encoding 不同而不同，就必须声明 Vary，
        # 否则共享缓存（反代/CDN）可能把 gzip 体发给不支持的客户端，
        # 或把明文发给期待压缩的客户端。本服务自带 no-store，风险很低，
        # 但这是正确性问题，补上。
        self.send_header('Vary', 'Accept-Encoding')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, ctype):
        try:
            ae = self.headers.get('Accept-Encoding', '')
            body, is_gzipped = _get_cached_gzip_file(path, ae)
            if body is None:
                self._send(404, {'error': 'not found'})
                return
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            if is_gzipped:
                self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self._send(404, {'error': 'not found'})

    # ---------- routes ----------
    def do_GET(self):
        # 四轮审查 N18：先挡 Host 头伪造，再谈路由
        if not self._host_allowed():
            return self._send(421, {'error': 'misdirected request'})
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # /api/health 豁免鉴权
        if path == '/api/health':
            return self._send(200, {'ok': True, 'status': _cache['status'],
                                    'params': _cache['params']})

        # 其他 /api/* 需要鉴权
        if path.startswith('/api/'):
            if not _check_auth(self):
                return

        if path in ('/', '/index.html'):
            return self._send_file(os.path.join(WEB, 'index.html'),
                                   'text/html; charset=utf-8')

        if path == '/favicon.ico':
            # 浏览器每次都会要，回个空响应省得刷 404
            return self._send(204, b'', 'image/x-icon')

        if path == '/api/data':
            if _cache['data'] is None:
                return self._send(202, {'status': 'running',
                                        'msg': '首次模拟进行中，请稍候再试'})
            return self._send(200, _cache['data'])

        if path == '/api/real':
            # 真实语料结果由 tools/real_sim.py 预生成（跑一次约 1 分钟，不宜实时跑）。
            # 默认读发布安全的脱敏版；DATABRAIN_FULL=1 时读 .private 下的未脱敏版（自用）。
            f = _pick_data_file(os.path.join(HERE, '.private', 'real.full.json'),
                                os.path.join(WEB, 'real.redacted.json'),
                                os.path.join(WEB, 'real.json'))
            if not f:
                return self._send(404, {'error': '还没有真实语料结果，先跑 tools/real_sim.py'})
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    return self._send(200, json.load(fh))
            except Exception as e:
                return self._send(500, {'error': _safe_error(e)})

        if path == '/api/compare':
            # 真实语料 vs 合成场景 的对照结果（跑 tools/real_sim.py --compare 生成）
            f = _pick_data_file(os.path.join(HERE, '.private', 'compare.full.json'),
                                os.path.join(WEB, 'compare.redacted.json'),
                                os.path.join(WEB, 'compare.json'))
            if not f:
                return self._send(404, {'error': '还没有对照结果，先跑 tools/real_sim.py --compare'})
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    return self._send(200, json.load(fh))
            except Exception as e:
                return self._send(500, {'error': _safe_error(e)})

        if path == '/api/run':
            global _run_active
            # 四轮审查 N19：/api/run 是会改变状态的（跑一次 365 天模拟，
            # 几十秒 CPU + 覆盖 _cache）。它是 GET，所以任何网页塞一个
            # <img src="http://127.0.0.1:8777/api/run?days=365"> 就能让
            # 访客的机器替它跑 —— Host 校验挡不住，因为浏览器发的 Host
            # 是合法的 127.0.0.1。
            # 要求带一个自定义头：跨站请求要加自定义头必须先过 CORS 预检，
            # 本服务不发任何 Access-Control-Allow-*，预检必然失败。
            if self.headers.get('X-Databrain-Token') is None:
                return self._send(428, {'error': 'run 需要带 X-Databrain-Token 头（前端会自动带）'})
            days = _safe_int(qs.get('days', ['180'])[0], 180, 1, 365)
            seed = _safe_int(qs.get('seed', ['42'])[0], 42, -10**9, 10**9)
            # 节流：同时只允许一个 run
            with _run_lock:
                if _run_active:
                    return self._send(409, {'error': 'run already in progress'})
                _run_active = True
            try:
                data = do_run(days, seed)
                return self._send(200, data)
            except Exception as e:
                import traceback
                traceback.print_exc()
                # N13：完整异常只进本机 stderr，回客户端的要抹掉绝对路径
                return self._send(500, {'error': _safe_error(e)})
            finally:
                with _run_lock:
                    _run_active = False

        if path == '/api/config':
            return self._send(200, {
                'hormones': C.HORMONES,
                'antagonism': C.ANTAGONISM,
                'reconsolidation': C.RECONSOLIDATION,
                'theme': C.THEME,
                'decay': C.DECAY,
                'encoding': C.ENCODING,
                'slow_var': C.SLOW_VAR,
                'dispositions': C.DISPOSITIONS,
            })

        # 静态资源（安全路径检查）
        rel = path.lstrip('/')
        if rel.startswith('api/'):
            return self._send(404, {'error': 'unknown api'})

        safe_path = _check_static_path(rel)
        if safe_path is not None and os.path.isfile(safe_path):
            ext = os.path.splitext(safe_path)[1]
            ct = {'.js': 'application/javascript; charset=utf-8',
                  '.css': 'text/css; charset=utf-8',
                  '.svg': 'image/svg+xml'}.get(ext, 'application/octet-stream')
            return self._send_file(safe_path, ct)

        self._send(404, {'error': 'not found'})


def main():
    os.makedirs(WEB, exist_ok=True)
    # N14：先做绑定检查，再花时间跑模拟 —— 配置错了要立刻说话，
    # 不能等 20 秒模拟跑完才拒绝，那时终端里已经刷了一堆输出。
    danger, note = _open_bind_without_token()
    if danger:
        print(f"拒绝启动：DATABRAIN_HOST={note} 是非回环地址，但没有设 DATABRAIN_TOKEN。\n"
              f"这个服务会把全部记忆导出（/api/data、/api/real）交给任何能连到 {PORT} 的人，\n"
              f"并且 /api/run 可以被任意驱动。\n"
              f"三选一：\n"
              f"  1) 只用本机：去掉 DATABRAIN_HOST（默认 127.0.0.1）\n"
              f"  2) 设口令：DATABRAIN_TOKEN='一段长随机串' python server.py\n"
              f"  3) 你清楚风险并要这么跑：DATABRAIN_ALLOW_OPEN=1 ...",
              file=sys.stderr)
        # 四轮审查 N16：原来这里 return，进程退出码是 0。
        # 被 systemd / Docker / CI / 计划任务拉起来时，
        # "拒绝启动"和"启动成功"在退出码上完全一样 —— 编排层会认为服务健康，
        # 甚至无限重启并每次都记成功。安全拒绝必须是失败。
        raise SystemExit(2)
    if note:
        print(f"提示：{note}。")
    # 端口被占（比如已经有一个实例在跑）就安静退出，
    # 不报错 —— 这样它可以被计划任务放心地反复拉起
    try:
        srv = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f"端口 {PORT} 已被占用（{e}），说明已有一个实例在跑，本次退出。")
        return
    print(f"数据化大脑 · 可视化服务")
    print(f"目录: {HERE}")
    print(f"先跑一次默认模拟（180 天 / seed 42），完成后再开浏览器…")
    do_run(180, 42)
    print(f"模拟完成。打开 http://{HOST}:{PORT}")
    print(f"重跑：http://{HOST}:{PORT}/api/run?days=365&seed=7")
    print(f"Ctrl+C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        srv.shutdown()


if __name__ == '__main__':
    main()
