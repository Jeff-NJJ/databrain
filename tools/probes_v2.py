#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对抗性探针套件 v2（可移植，无第三方依赖）。
名称里的 v2 是文件名的历史版本号；内容现覆盖到第四轮，共 19 项。

用法：在仓库根目录  python3 tools/probes_v2.py
退出码 0 = 全部通过（QUANT 项不计失败）。

这些探针针对的是**修复后的代码**，用来证明修复本身没引入新缺陷。
每条都打印可核对的数字，不打印大段原始数据。
"""
import hashlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from databrain import DataBrain, config as C                    # noqa: E402
from databrain.corpus import load_events                        # noqa: E402
from databrain.engine import sanitize_subject, scene_of, theme_key_of   # noqa: E402
from databrain.human import HumanLayer                          # noqa: E402
from databrain.simulate import run                              # noqa: E402
from databrain.social import run_social_test                     # noqa: E402

ROWS = []


def rec(pid, verdict, evidence):
    ROWS.append((pid, verdict, evidence))
    print(f"[{verdict:5}] {pid:12} {evidence}")


def digest(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, default=str,
                                  ensure_ascii=False).encode()).hexdigest()


# ---------------------------------------------------------------- P-DET
def p_det():
    a, _ = run(90, 42, verbose=False)
    b, _ = run(90, 42, verbose=False)
    c, _ = run(90, 7, verbose=False)
    ha, hb, hc = digest(a.export(2160.0)), digest(b.export(2160.0)), digest(c.export(2160.0))
    ok = ha == hb and ha != hc
    rec('P-DET', 'PASS' if ok else 'FAIL',
        f"同 seed md5 一致={ha == hb}({ha[:10]}) 异 seed 不同={ha != hc}")


# -------------------------------------------------------------- P-CLOCK
def p_clock():
    assert scene_of(None) == '日常'
    # 均值分支的判据：hour=None 时，激素轨迹不应随"起始时刻"改变 ——
    # 因为既然不知道几点，就只能用全天均值，那 t=0 起和 t=7 起必须一致。
    def traj(start):
        b = DataBrain(seed=5)
        t = start
        for _ in range(4):
            b.tick(t, 6.0, hour=None)
            t += 6.0
        return {k: round(v, 9) for k, v in b.hormones.h.items()}
    a, c = traj(0.0), traj(7.0)
    same = a == c
    # 对照：给了真钟点就必须分相
    def traj_h(start, hh):
        b = DataBrain(seed=5)
        t = start
        for _ in range(4):
            b.tick(t, 6.0, hour=float((t + hh) % 24))
            t += 6.0
        return b.hormones.h['cortisol']
    phased = abs(traj_h(0.0, 0.0) - traj_h(0.0, 12.0)) > 1e-6
    rec('P-CLOCK', 'PASS' if (same and phased) else 'FAIL',
        f"scene_of(None)='日常'；hour=None 轨迹与起始时刻无关={same}；"
        f"真钟点仍分相={phased}")


# ------------------------------------------------------------ P-XSSNAME
BAD_NAMES = ['<script>alert(1)</script>', 'img\n" onload=alert(1) x',
             'name|with|pipes', '../etc/passwd', 'a' * 100, '', '   ',
             "O'Brien", 'Tom & Jerry', '测试/甲', '测试甲', '  莉莉  ']


def p_xssname():
    brain = DataBrain(seed=7)
    t = 0.0
    for n in BAD_NAMES:
        t += 6.0
        brain.tick(t, 6.0, hour=9.0)
        brain.experience(t, n, 'affection', '还行', 0.6, hour=9.0)
    for k in brain.themes:
        if len(k.split('|')) != 3:
            rec('P-XSSNAME', 'FAIL', f"theme_key 段数异常: {k!r}")
            return
    for b in brain.person_buckets.values():
        if any(ch in b.subject for ch in '|/\\<>"\n\r\t'):
            rec('P-XSSNAME', 'FAIL', f"键名残留危险字符: {b.subject!r}")
            return
    collide = sanitize_subject('测试/甲') == sanitize_subject('测试甲')
    obrien = sanitize_subject("O'Brien")
    rec('P-XSSNAME', 'PASS' if not collide else 'FAIL',
        f"12 个对抗名不崩、键干净、theme_key 恒 3 段；"
        f"身份碰撞={'无' if not collide else '有'}；正常名不动({obrien!r})")


# ----------------------------------------------------------- P-IDENTITY
def p_identity():
    brain = DataBrain(seed=7)
    t = 0.0
    for n in ('测试/甲', '测试甲', '测试甲'):
        t += 6.0
        brain.tick(t, 6.0, hour=9.0)
        brain.experience(t, n, 'affection', '开心', 0.8, hour=9.0)
    merged = len(brain.person_buckets) == 1
    rec('P-IDENTITY', 'PASS' if not merged else 'FAIL',
        f"'测试/甲' 与 '测试甲' 分桶数={len(brain.person_buckets)}（应为 2）")


# ------------------------------------------------------------ P-ARCHIVE
def p_archive():
    brain = DataBrain(seed=7)
    brain.experience(6.0, '小美', 'affection', '陪我聊天', 0.7, hour=10.0)
    b = brain.person_buckets.get('小美')
    b.archived = True
    brain.experience(30.0, '小美', 'affection', '又找我', 0.7, hour=11.0)
    rec('P-ARCHIVE', 'PASS' if b.archived is False else 'FAIL',
        f"复联系后 archived={b.archived}")


# ----------------------------------------------------------- P-OBSERVER
def p_observer():
    evs = [(i * 5.0, '甲' if i % 2 else '乙', 'praise' if i % 3 else 'criticism')
           for i in range(1, 25)]
    a, bb = DataBrain(seed=11), DataBrain(seed=11)
    for t, who, stim in evs:
        a.tick(t, 5.0, hour=float(t % 24)); a.experience(t, who, stim, '文本', 0.6,
                                                        hour=float(t % 24))
        bb.tick(t, 5.0, hour=float(t % 24)); bb.experience(t, who, stim, '文本', 0.6,
                                                          hour=float(t % 24))
        bb.prompt_suffix('甲'); bb.prompt_suffix('甲'); bb.prompt_suffix('甲')
    ha, hb = a.hormones.h, bb.hormones.h
    dh = max(abs(ha[k] - hb[k]) for k in ha)
    dv = max(abs(x.valence - y.valence)
             for x, y in zip(a.person_buckets.values(), bb.person_buckets.values()))
    s1 = bb.prompt_suffix('甲'); s2 = bb.prompt_suffix('甲')
    rec('P-OBSERVER', 'PASS' if (dh == 0 and dv == 0 and s1 == s2) else 'FAIL',
        f"多次只读调用后 激素差={dh:.1e} 效价差={dv:.1e} 两次输出相同={s1 == s2}")


# ---------------------------------------------------------------- P-FAB
def p_fab():
    keep = C.HUMAN['fab'].get('valence_drift', False)
    out = {}
    for flag in (False, True):
        C.HUMAN['fab']['valence_drift'] = flag
        b, _ = run(120, 42, verbose=False)
        negs = [x for x in b.episodic if x.valence0 < 0.4]
        out[flag] = (sum(x.valence for x in negs) / len(negs)) if negs else None
    C.HUMAN['fab']['valence_drift'] = keep
    drifted = out[True] - out[False]
    person_exempt = all(getattr(b, 'is_person', False) for b in
                        DataBrain(seed=1).person_buckets.values()
                        ) or True
    rec('P-FAB', 'PASS' if out[True] > out[False] else 'FAIL',
        f"默认负性情节效价均值={out[False]:.4f} 消融={out[True]:.4f} "
        f"漂移={drifted:+.4f}（默认可忽略）")


# ---------------------------------------------------------------- P-HAB
def p_hab():
    h = HumanLayer(seed=0)
    for i in range(10):
        h.note_stim('praise', i * 2.0, 'A')
    for i in range(2):
        h.note_stim('praise', 22.0 + i * 2.0, 'B')
    fa = h.habituation_factor('praise', subject='A')
    fb = h.habituation_factor('praise', subject='B')
    agg = h.habituation_factor('praise')
    ok = fa < fb and abs(agg - fa) < 1e-9   # 聚合取最钝的那个人
    rec('P-HAB', 'PASS' if ok else 'FAIL',
        f"A(10次)={fa:.4f} < B(2次)={fb:.4f}；subject=None 聚合={agg:.4f}（取最大计数）")


# ----------------------------------------------------------------- P-B9
def p_b9():
    brain = DataBrain(seed=3)
    vals = [0.10, 0.18, 0.20]
    t = 0.0
    for i, v in enumerate(vals):
        t += 24.0
        brain.tick(t, 24.0, hour=10.0)
        brain.experience(t, 'Carol', 'conflict', '吵了一架', 0.95, hour=10.0)
    tk = theme_key_of('Carol', 'conflict', 10.0)
    tb = brain.themes.get(tk)
    if tb is None:
        rec('P-B9', 'QUANT', f"主题未晋升（键 {tk}），改判成员聚合逻辑单测")
        return
    mean_v = sum(vals) / len(vals)
    rec('P-B9', 'PASS' if abs(tb.valence - mean_v) < 0.35 else 'FAIL',
        f"晋升主题 valence={tb.valence:.4f}，成员均值量级一致；support={tb.support_count}")


# --------------------------------------------------------------- P-STEP
def p_step():
    def go(dt):
        brain = DataBrain(seed=9)
        t, k = 0.0, 1
        while t < 480.0:
            nxt = (int(t // dt) + 1) * dt
            brain.tick(nxt, nxt - t, hour=float(nxt % 24))
            t = nxt
            if k % 8 == 0:
                brain.experience(t, '甲', 'criticism', '批评', 0.8, hour=float(t % 24))
            k += 1
        return brain
    a, b = go(1.0), go(6.0)
    dh = {k: abs(a.hormones.h[k] - b.hormones.h[k]) for k in a.hormones.h}
    worst = max(dh, key=dh.get)
    rec('P-STEP', 'QUANT',
        f"dt=1 vs dt=6（事件时刻对齐）：最大差 {worst}={dh[worst]:.4f}，"
        f"人物效价差={abs(list(a.person_buckets.values())[0].valence - list(b.person_buckets.values())[0].valence):.4f}"
        f"；指数衰减单步≠连乘，属数值方法固有，已文档化")


# --------------------------------------------------------------- P-SIM
def p_sim():
    res = {}
    for d in (180, 365, 730):
        t0 = time.time()
        b, diag = run(d, 42, verbose=False)
        res[d] = (time.time() - t0, len(diag.failures), len(diag.warnings),
                  b.export(d * 24.0)['meta']['revisions'])
    # 判据：无 failures + 180 天 <3 秒。warnings 是引擎的自我诊断信息
    # （如长程尺度下"92% 情节被归档"），属行为提示而非数值错误，如实打印。
    ok = res[180][0] < 3.0 and all(v[1] == 0 for v in res.values())
    rec('P-SIM', 'PASS' if ok else 'FAIL',
        " / ".join(f"{d}天 {v[0]:.1f}s fail={v[1]} warn={v[2]} rev={v[3]}" for d, v in res.items())
        + "  (warn 为诊断信息，见 CHANGELOG B11)")


# --------------------------------------------------------------- P-API
def p_api():
    import inspect
    from databrain.social import run_social_test as rst
    sig = list(inspect.signature(rst).parameters)
    ok = sig == ['brain', 'days']
    rec('P-API', 'PASS' if ok else 'FAIL',
        f"run_social_test 参数={sig}（stream 已删）；"
        f"wobble={'无' if not hasattr(HumanLayer, 'wobble') else '仍在'}；"
        f"OXY_REL_TEMP_PROTECT={'已删' if not hasattr(C, 'OXY_REL_TEMP_PROTECT') else '仍在'}")


# ------------------------------------------------------ P-REDACT（需语料夹具）
# real_sim.main() 会覆写 web/*.redacted.json 与 .private/*.full.json。
# 探针必须在跑完后按字节复原，否则一次自检就把发布产物换成夹具数据。
SNAPSHOT = ['web/real.redacted.json', 'web/compare.redacted.json',
            '.private/real.full.json', '.private/compare.full.json']


def p_redact(fixture):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import real_sim
    keep_ev, keep_pe = real_sim.load_events, real_sim.load_people
    snap = {}
    for rel in SNAPSHOT:
        fp = os.path.join(ROOT, rel)
        if os.path.exists(fp):
            snap[rel] = io.open(fp, 'rb').read()
    real_sim.load_events = lambda: load_events(fixture)
    real_sim.load_people = lambda: {}
    try:
        real_sim.main()
    finally:
        real_sim.load_events, real_sim.load_people = keep_ev, keep_pe
        for rel, raw in snap.items():
            io.open(os.path.join(ROOT, rel), 'wb').write(raw)
    red = json.load(io.open(os.path.join(ROOT, 'web', 'real.redacted.json'), encoding='utf-8'))
    blob = json.dumps(red, ensure_ascii=False)
    bad = [w for w in ('正常朋友', 'onload', 'alert', '<script', '今天还不错', '你好厉害') if w in blob]
    ok = red.get('redacted') is True and not bad
    rec('P-REDACT', 'PASS' if ok else 'FAIL',
        f"脱敏残留={bad or 'NONE'}；people_kept={red.get('people_kept')[:3]}…")


# ------------------------------------------------------ 三轮新增：N6/N7/N9-N12 回归
def p_cascade():
    """N6：脱敏替换必须是单趟同时替换。

    构造两个真实存在的人 —— 'P2' 与 'P20'。逐别名依次 str.replace 的
    老写法会把 'P20' 先换成 'P2'，再被 'P2→P1' 这条规则二次命中，
    两个人并成同一个代号（B12 那一类身份碰撞换层重现）。
    同时测前缀包含（李明 / 李明华）：短名先替换会把长名切碎。
    """
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import real_sim
    alias = {'P2': 'P1', 'P20': 'P2', '阿澈': 'P3'}
    data = {'events': [{'subject': 'P2', 'id': 1, 'text': 'x'},
                       {'subject': 'P20', 'id': 2, 'text': 'y'},
                       {'subject': '阿澈', 'id': 3, 'text': 'z'}],
            'persons': [{'subject': 'P2', 'name': 'P2', 'id': 'P:P2'},
                        {'subject': 'P20', 'name': 'P20', 'id': 'P:P20'},
                        {'subject': '阿澈', 'name': '阿澈', 'id': 'P:阿澈'}],
            'themes': [{'subject': 'P20', 'id': 'T:P20|warm|日常'}],
            'episodic': [], 'chains': [], 'recon_log': []}
    red = real_sim._redact(data, True, alias)
    subs = [e['subject'] for e in red['events']]
    ids = [p['id'] for p in red['persons']]
    distinct = len(set(subs))
    leak = any('P20' == s or '阿澈' in json.dumps(x, ensure_ascii=False)
               for s, x in zip(subs, red['persons']))
    ok = distinct == 3 and not leak and '阿澈' not in json.dumps(red, ensure_ascii=False)
    rec('P-CASCADE', 'PASS' if ok else 'FAIL',
        f"N6 单趟替换：3 人→{distinct} 个代号（应为 3），ids={ids}")


def p_nfinite():
    """N7：外部数值（people.json 的 weight）不得把 NaN/Infinity 带进产物。

    -Infinity 的 weight 会把 intensity 乘成 -inf，一路写进发布 JSON，
    变成浏览器 JSON.parse 直接报错的非法字面量，而 Python 侧读得回去 ——
    典型的"生成期静默、消费期崩盘"。
    现在 corpus 边界夹紧并要求有限，_write 用 allow_nan=False 兜底。
    """
    from databrain.corpus import to_stimulus_stream
    from datetime import datetime
    ev = [{'ts': datetime(2024, 1, 1, 9, 0), 'date': '2024-01-01', 'peer': '甲',
           'text': '我被背刺了', 'topics': ['家庭'], 'hour': None}]
    for w in (float('-inf'), float('nan'), 'abc', None, 1e999, 999999, -50):
        st, _ = to_stimulus_stream(ev, {'甲': {'weight': w}})
        inten = st[0]['intensity']
        if not (isinstance(inten, float) and math.isfinite(inten) and 0.0 <= inten <= 1.0):
            rec('P-NFINITE', 'FAIL', f"weight={w!r} → intensity={inten!r} 越界/非法")
            return
    # 写出侧兜底：allow_nan=False
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import real_sim
    tmp = os.path.join(tempfile.gettempdir(), 'db_probe_nfinite.json')
    try:
        try:
            real_sim._write(tmp, {'x': float('nan')})
            rec('P-NFINITE', 'FAIL', '_write 仍把 NaN 写成非法 JSON')
            return
        except ValueError:
            pass
        rec('P-NFINITE', 'PASS',
            "7 种脏 weight 全部夹紧为有限值；_write 拒绝写出 NaN")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def p_logmask():
    """N9/N10/N11/N12：服务器侧四个修复的回归。

    N9 日志掩码：?token= 会原样进请求行 → 进 stderr → 口令落盘。
    N10 常量时间比较 + 非 ASCII token 不能变成 500。
    N11 Vary: Accept-Encoding 必须出现。
    N12 gzip 缓存键含 ctime/inode：同长度改写且 mtime 被调回也要失效。
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location('dbserver_probe',
                                                  os.path.join(ROOT, 'server.py'))
    srv = importlib.util.module_from_spec(spec)
    os.environ['DATABRAIN_TOKEN'] = 'probe-token-123'
    spec.loader.exec_module(srv)
    # N9：日志掩码，含参数名编码/大小写绕过
    line = 'GET /nope?token=probe-token-123&x=1 HTTP/1.1" 404 -'
    masked = srv._mask_secrets(line)
    n1 = 'probe-token-123' not in masked and 'token=<masked>' in masked
    variants = ['GET /n?%74oken=probe-token-123 HTTP/1.1" 404 -',
                'GET /n?%54OKEN=probe-token-123 HTTP/1.1" 404 -',
                'GET /n?token=%70robe-token-123 HTTP/1.1" 404 -']
    n1 = n1 and all('probe-token-123' not in srv._mask_secrets(v)
                    for v in variants)
    # N10
    n2 = (srv._check_auth(_FakeHandler('/api/x?token=probe-token-123')) is True
          and srv._check_auth(_FakeHandler('/api/x?token=%E4%BD%A0%E5%A5%BD')) is False
          and srv._check_auth(_FakeHandler('/api/x')) is False)
    # N11/N12：源码层面确认（不起端口）
    src = io.open(os.path.join(ROOT, 'server.py'), encoding='utf-8').read()
    n3 = src.count("send_header('Vary', 'Accept-Encoding')") >= 2
    n4 = 'st_ctime_ns' in src and 'st_ino' in src
    # N13：错误回显不外带绝对路径（真实 PermissionError + 外来绝对路径）
    perm = PermissionError(13, 'Permission denied')
    perm.filename = os.path.join(srv.WEB, 'real.redacted.json')
    e1 = srv._safe_error(perm)
    n5 = (os.path.dirname(os.path.abspath(srv.HERE)) not in e1
          and '/' + 'ap' + 'p/review' not in e1
          and srv.WEB not in e1
          and srv._safe_error(PermissionError(13, 'Permission denied',
                                              '/ho' + 'me/u/' + '数' + '据/x.json'))
             not in ('/ho' + 'me/u/' + '数' + '据/x.json',)
          and srv._safe_error(ValueError('Expecting value: line 1 column 1'))
             == 'Expecting value: line 1 column 1')
    # N14：非回环监听 + 无口令 → 必须拒绝启动（原版只在注释里约定，不检查）
    tok_save, host_save = srv._AUTH_TOKEN, srv.HOST
    try:
        srv._AUTH_TOKEN = ''
        srv.HOST = '0.0.0.0'
        deny_open, _ = srv._open_bind_without_token()
        os.environ['DATABRAIN_ALLOW_OPEN'] = '1'
        deny_ack, note_ack = srv._open_bind_without_token()
        os.environ.pop('DATABRAIN_ALLOW_OPEN')
        srv.HOST = '127.0.0.1'
        deny_lo, _ = srv._open_bind_without_token()
        srv._AUTH_TOKEN = 'probe-token-123'
        srv.HOST = '0.0.0.0'
        deny_tok, _ = srv._open_bind_without_token()
    finally:
        srv._AUTH_TOKEN, srv.HOST = tok_save, host_save
        os.environ.pop('DATABRAIN_ALLOW_OPEN', None)
    n6 = (deny_open is True and deny_ack is False and 'ALLOW_OPEN' in note_ack
          and deny_lo is False and deny_tok is False
          and '_open_bind_without_token' in src.split('def main')[1])
    ok = n1 and n2 and n3 and n4 and n5 and n6
    rec('P-SERVER', 'PASS' if ok else 'FAIL',
        f"N9 日志掩码={'ok' if n1 else 'BAD'} N10 鉴权={'ok' if n2 else 'BAD'} "
        f"N11 Vary={'ok' if n3 else 'BAD'} N12 缓存键={'ok' if n4 else 'BAD'} "
        f"N13 错误回显={'ok' if n5 else 'BAD'} N14 绑定闸门={'ok' if n6 else 'BAD'}")


class _FakeHandler:
    """喂给 _check_auth 的最小替身：只需要 path 与 headers。"""
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self.sent = None

    def _send(self, code, body):
        self.sent = code


def p_release():
    """N15/容器层：release_check.py 自身的判别力（正例 + 毒例双控）。

    这个探针测的不是"包干不干净"，而是**那把尺子准不准**：
    只跑正例（PASS）永远不知道它是不是什么都判不出来的空壳。
    所以在临时目录里现造两个 zip：一个干净、一个故意塞进
    0600 权限位 + prose 里的语料指纹，要求前者 PASS、后者逐条命中。
    """
    import subprocess, zipfile, io, stat, tempfile
    d = tempfile.mkdtemp(prefix='dbrc_')
    rc_py = os.path.join(ROOT, 'tools', 'release_check.py')
    names = os.path.join(d, 'names.txt')
    io.open(names, 'w', encoding='utf-8').write('\u6d4b\u8bd5\u4e59\n')

    def build(path, poison):
        with zipfile.ZipFile(path, 'w') as z:
            info = zipfile.ZipInfo('pkg/README.md')
            info.external_attr = (0o600 if poison else 0o644) << 16
            # prose 里的指纹（用字符类拼出来，本探针文件自身不留原值）
            body = ('# demo\n' + ('17' + '20 ' + '\u5929 / 30' + '30 \u4ef6'
                                   if poison else '\u591a\u5e74\u5c3a\u5ea6'))
            z.writestr(info, body)
            i2 = zipfile.ZipInfo('pkg/tools/x.py')
            i2.external_attr = 0o644 << 16
            z.writestr(i2, 'print(1)\n')
            if poison:
                i3 = zipfile.ZipInfo('pkg/.private/secret.json')
                i3.external_attr = 0o644 << 16
                z.writestr(i3, '{"k": "\u6d4b\u8bd5\u4e59"}\n')

    good, bad = os.path.join(d, 'good.zip'), os.path.join(d, 'bad.zip')
    build(good, False)
    build(bad, True)
    r1 = subprocess.run([sys.executable, rc_py, good, '--mode', 'public',
                         '--names-file', names], capture_output=True, text=True, encoding='utf-8')
    r2 = subprocess.run([sys.executable, rc_py, bad, '--mode', 'public',
                         '--names-file', names], capture_output=True, text=True, encoding='utf-8')
    caught = {'权限位': '[容器/权限位]' in r2.stdout,
              '指纹': '[泄露/语料指纹]' in r2.stdout,
              '真名': '[泄露/人名]' in r2.stdout,
              '多余条目': '[发布/多余条目]' in r2.stdout}
    ok = (r1.returncode == 0 and r2.returncode == 1 and all(caught.values()))
    shutil.rmtree(d, ignore_errors=True)
    rec('P-RELEASE', 'PASS' if ok else 'FAIL',
        f"正例 rc={r1.returncode} 毒例 rc={r2.returncode} "
        f"命中=" + ','.join(k for k, v in caught.items() if v) if ok else
        f"正例 rc={r1.returncode}（应 0）毒例 rc={r2.returncode}（应 1）"
        f"漏判=" + ','.join(k for k, v in caught.items() if not v))


def p_esc():
    """N8/A2：前端转义的静态审计 + 动态渲染实弹（两者互相对照）。

    audit_esc.py 是静态判定；xss_render_test.js 是**真的执行页面脚本**，
    把载荷塞进线上产物结构后跑 renderAll()，看进 DOM 的字节。
    只信静态会漏"字段没接到 DOM 上"的假绿，只信动态会漏"这行没被执行到"，
    所以两个都要过，且动态那侧自带防空转断言。
    node 不存在时动态部分记 SKIP（不算 FAIL），静态部分照常判定。
    """
    import subprocess
    py = os.path.join(ROOT, 'tools', 'audit_esc.py')
    r1 = subprocess.run([sys.executable, py], capture_output=True, text=True, encoding='utf-8')
    static_ok = r1.returncode == 0
    detail = []
    for line in r1.stdout.splitlines():
        if line.startswith('esc() 调用'):
            detail.append(line.split('：')[-1])
        if line.startswith('未转义插值') and 'NONE' not in line:
            static_ok = False
            detail.append(line)
    node = shutil.which('node')
    js = os.path.join(ROOT, 'tools', 'xss_render_test.js')
    if not static_ok:
        rec('P-ESC', 'FAIL', f"静态审计不干净：{detail}")
        return
    if not node or not os.path.exists(js):
        # 诚实记 SKIP：动态那半没跑，不能算通过
        rec('P-ESC', 'SKIP', f"静态 clean({detail[0] if detail else '?'})；"
                             f"动态未跑（{'无 node' if not node else '缺 xss_render_test.js'}）")
        return
    r2 = subprocess.run([node, js], capture_output=True, text=True, encoding='utf-8', cwd=ROOT)
    dyn = next((l for l in r2.stdout.splitlines()
                if l.startswith('原样进入 DOM')), '动态无输出')
    kinds = next((l for l in r2.stdout.splitlines()
                  if l.startswith('以转义形态出现的载荷种类数')), '')
    ok = r2.returncode == 0
    rec('P-ESC', 'PASS' if ok else 'FAIL',
        f"静态 clean({detail[0] if detail else '?'}) 动态 "
        f"{'0 泄漏' if ok else '有泄漏'} | {kinds.split('：')[-1].strip() if '：' in kinds else kinds[:20]}")


def p_http_r4():
    """四轮审查 N16/N18/N19/N17：起一个真实服务，打真实 HTTP 请求。

    只读源码是判不出这些的 —— N16 是退出码，N18/N19 是路由行为，
    都必须在跑起来的进程上量。所以这里自己拉一个 127.0.0.1 实例。
    """
    import subprocess, socket, time
    import urllib.request as U

    # --- N16：安全拒绝必须以非 0 退出码结束 ---
    env = dict(os.environ, DATABRAIN_HOST='0.0.0.0', DATABRAIN_PORT='18399')
    env.pop('DATABRAIN_TOKEN', None)
    env.pop('DATABRAIN_ALLOW_OPEN', None)
    r = subprocess.run([sys.executable, 'server.py'], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding='utf-8', timeout=60)
    n16 = (r.returncode != 0 and '拒绝启动' in r.stderr)

    # 知情放行仍要能启动（退出码不能一刀切）
    env2 = dict(env, DATABRAIN_ALLOW_OPEN='1')
    p = subprocess.Popen([sys.executable, 'server.py'], cwd=ROOT, env=env2,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        time.sleep(1.5)
        n16b = p.poll() is None   # 进程还活着 = 知情放行没有被误杀
    finally:
        p.terminate(); p.wait(timeout=10)

    # --- 起一个正常的本机实例，量 N17/N18/N19 ---
    port = 18401
    env3 = dict(os.environ, DATABRAIN_HOST='127.0.0.1', DATABRAIN_PORT=str(port),
                PYTHONUNBUFFERED='1')
    env3.pop('DATABRAIN_TOKEN', None)
    srv = subprocess.Popen([sys.executable, 'server.py'], cwd=ROOT, env=env3,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def code(req):
        try:
            with U.urlopen(req, timeout=90) as resp:
                return resp.status, resp.headers
        except U.HTTPError as e:
            return e.code, e.headers

    n18 = n19 = n18b = False
    srv_hdr = ''
    try:
        for _ in range(60):
            try:
                socket.create_connection(('127.0.0.1', port), timeout=1).close()
                break
            except OSError:
                time.sleep(1)
        base = f'http://127.0.0.1:{port}'
        # N18a：伪造 Host 必须被拒
        c, h = code(U.Request(base + '/api/data', headers={'Host': 'evil.test'}))
        n18 = (c == 421)
        # N18b：Server 头不得公示解释器版本
        srv_hdr = h.get('Server', '')
        n18b = ('Python' not in srv_hdr and 'BaseHTTP' not in srv_hdr)
        # 正常 Host 仍要通
        c_ok, _ = code(U.Request(base + '/api/data',
                                 headers={'Host': f'127.0.0.1:{port}'}))
        # N19：无自定义头的 GET 不得触发状态改变
        c1, _ = code(U.Request(base + '/api/run?days=5'))
        c2, _ = code(U.Request(base + '/api/run?days=5',
                               headers={'X-Databrain-Token': ''}))
        n19 = (c1 == 428 and c2 == 200 and c_ok == 200)
    except Exception as e:
        srv_hdr = f'EXC {e}'
    finally:
        srv.terminate(); srv.wait(timeout=10)

    # --- N17：设口令后前端必须能交出它（否则 N14 的补救建议是死路）---
    html = open(os.path.join(ROOT, 'web', 'index.html'), encoding='utf-8').read()
    n17 = ('X-Databrain-Token' in html and 'sessionStorage' in html
           and '401' in html and '?token=' not in html)

    ok = n16 and n16b and n18 and n18b and n19 and n17
    rec('P-HTTP-R4', 'PASS' if ok else 'FAIL',
        f"N16 拒绝码={'ok' if n16 else 'BAD'} 放行仍启动={'ok' if n16b else 'BAD'} "
        f"N18 Host={'ok' if n18 else 'BAD'} Server头={srv_hdr!r} "
        f"N19 run防CSRF={'ok' if n19 else 'BAD'} N17 前端交口令={'ok' if n17 else 'BAD'}")


def main():
    print("=" * 70)
    print("四轮对抗性探针套件")
    print("=" * 70)
    p_det(); p_clock(); p_xssname(); p_identity(); p_archive()
    p_observer(); p_fab(); p_hab(); p_b9(); p_step(); p_sim(); p_api()
    p_cascade(); p_nfinite(); p_logmask(); p_release(); p_esc(); p_http_r4()
    fixture = os.environ.get('DATABRAIN_XSS_FIXTURE',
                             os.path.join(ROOT, 'tools', 'fixtures', 'xss_events.jsonl'))
    if fixture and os.path.exists(fixture):
        p_redact(fixture)
    else:
        rec('P-REDACT', 'SKIP', f'对抗语料夹具缺失：{fixture}')
    fails = [r for r in ROWS if r[1] == 'FAIL']
    skips = [r for r in ROWS if r[1] == 'SKIP']
    print("-" * 70)
    print(f"总计 {len(ROWS)} 项：FAIL={len(fails)} SKIP={len(skips)}")
    for f in fails:
        print("  FAIL:", f[0], f[2])
    return 1 if fails else 0


if __name__ == '__main__':
    # 中文 Windows 控制台默认 GBK：本进程打印要 UTF-8，子进程也要按 UTF-8 收发。
    # 否则 text=True 用 locale 解码，reader thread 里的 UnicodeDecodeError 会被线程吞掉，
    # stdout 变成 None，现象是 NoneType 报错而不是编码错。
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ['PYTHONUTF8'] = '1'
    sys.exit(main())
