# -*- coding: utf-8 -*-
"""
真实语料模拟 + 因果链追踪 + 与合成场景的对比

用法：
  python tools/real_sim.py            # 跑真实语料并生成 web/real.json
  python tools/real_sim.py --compare  # 同时跑合成场景做对比

因果链要回答的五问（这是杰夫要的那条主线）：
  发生了什么 → 引起了什么 → 结果怎么样 → 短期如何 → 长期如何

所以每条重大事件都会被记下：即时冲击、写入了什么、7 天后的状态、90 天后的状态。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databrain import DataBrain                      # noqa: E402
from databrain.corpus import (load_events, load_people,   # noqa: E402
                              to_stimulus_stream, filter_top_peers)
from databrain.social import run_social_test, report    # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'web', 'real.json')
# 审查A4修复：未脱敏版永远只留在本机（.private/ 目录随包分发时剔除）；
# 发布版输出 web/real.redacted.json —— 人名映射为 P1..Pn、聊天原文清空。
PRIVATE_DIR = os.path.join(HERE, '.private')
OUT_FULL = os.path.join(PRIVATE_DIR, 'real.full.json')
CMP_FULL = os.path.join(PRIVATE_DIR, 'compare.full.json')
REDACT_OUT = os.path.join(HERE, 'web', 'real.redacted.json')
REDACT_CMP = os.path.join(HERE, 'web', 'compare.redacted.json')
CMP = os.path.join(HERE, 'web', 'compare.json')

# 值得追踪因果链的事件类型
TRACK_STIMS = {'betrayal', 'humiliation', 'rejection', 'conflict', 'crisis',
               'criticism', 'loss', 'neglect', 'reconciliation', 'apology',
               'affection', 'shared_joy'}
MARKS = [7, 30, 90]      # 短期 / 中期 / 长期（天）


def run_real(top_peers=5, seed=7):
    events = load_events()
    people = load_people()
    stream, days = to_stimulus_stream(events, people)
    stream, keep = filter_top_peers(stream, top_peers)

    brain = DataBrain(seed=seed)
    t = 0.0
    pending = []          # 待观察后续影响的重大事件
    chains = []

    print(f"真实语料：{len(stream)} 条事件 / {days:.0f} 天 / 人物 {sorted(keep)}")

    for i, s in enumerate(stream):
        th = s['t_hours']
        # ---- 按天推进（事件驱动，不做逐小时 tick）----
        # 审查C1修复：不再喂伪造的小时。24h 步进走"均值昼夜"分支；
        # 事件自带真实钟点时（s['hour'] is not None）才传给 experience。
        while th - t >= 24.0:
            t += 24.0
            brain.tick(t, 24.0)
            brain.record_timeline(t)
            _collect_marks(brain, pending, chains, t)
        if th > t:
            brain.tick(th, th - t)
            t = th

        # ---- 事前快照 ----
        before = {
            'h': dict(brain.hormones.h),
            'emo_v': brain.human.emo_v, 'emo_a': brain.human.emo_a,
        }
        pb = brain.person_buckets.get(s['subject'])
        before['pv'] = pb.valence if pb else None

        r = brain.experience(t, s['subject'], s['stim'], s['text'], s['intensity'],
                             hour=s.get('hour'))

        # ---- 事后快照 ----
        after = {
            'h': dict(brain.hormones.h),
            'emo_v': brain.human.emo_v, 'emo_a': brain.human.emo_a,
        }
        pb2 = brain.person_buckets.get(s['subject'])
        after['pv'] = pb2.valence if pb2 else None

        # ---- 判定是否值得追踪 ----
        if s['stim'] in TRACK_STIMS or r['salience'] >= 0.38:
            ev_id = len(brain.ledger)
            pending.append({
                't0': t, 'ev_id': ev_id, 'subject': s['subject'],
                'stim': s['stim'], 'text': s['text'], 'date': s['date'],
                'intensity': s['intensity'], 'salience': r['salience'],
                'before': before, 'after': after,
                'action': r['action'], 'detail': r['detail'],
                'hits': r['hits'], 'mod': r['mod'],
                'bucket_before': before['pv'], 'bucket_after': after['pv'],
                'marks': {},
            })

    # 收尾：把还没到观察点的补上
    _collect_marks(brain, pending, chains, t, final=True)

    test = run_social_test(brain, days)
    return brain, chains, test, days, keep


def _collect_marks(brain, pending, chains, t_now, final=False):
    """
    到达 7/30/90 天观察点时，把当时状态补进因果链。

    注意：靠近结尾的事件凑不满 90 天，不能拿"最后一天"硬填成 90 天后的状态——
    那会让人以为长期影响已经稳定了。凑不满就如实标 None，并记下 truncated。
    """
    still = []
    for p in pending:
        for mk in MARKS:
            if mk in p['marks']:
                continue
            reached = (p['t0'] + mk * 24.0) <= t_now
            if reached:
                pb = brain.person_buckets.get(p['subject'])
                p['marks'][mk] = {
                    'pv': round(pb.valence, 4) if pb else None,
                    'pa': round(pb.arousal, 4) if pb else None,
                    'imp': round(pb.impedance(t_now), 3) if pb else None,
                    'score': round(pb.score(t_now), 2) if pb else None,
                    'revisions': len(pb.appraisal_chain) if pb else 0,
                    'emo_v': round(brain.human.emo_v, 4),
                }
            elif final:
                # 观察窗不够长：留 None，但记下实际经过了多少天
                pb = brain.person_buckets.get(p['subject'])
                p['marks'][mk] = None
                p['truncated_days'] = round((t_now - p['t0']) / 24.0, 1)
                p.setdefault('_final_pv',
                             round(pb.valence, 4) if pb else None)
        if len(p['marks']) < len(MARKS):
            still.append(p)
        else:
            chains.append(p)
    pending[:] = still


# ============================================================
def _num(x, nd=4):
    """审查B3修复：round(None) 会崩。None 原样传，数字正常舍入。"""
    return None if x is None else round(x, nd)


def _alias_of(data):
    """人名 → P1..Pn。必须全工程唯一一份：real 里叫 P3 的人，
    在 compare 里也得是 P3，否则两份发布产物互相指错人。"""
    names = set()
    for e in data.get('events', []):
        names.add(e.get('subject'))
    for key in ('persons', 'themes', 'episodic'):
        for b in data.get(key, []):
            names.add(b.get('subject'))
    for c in data.get('chains', []):
        names.add(c.get('subject'))
    names.discard(None)
    return {n: 'P%d' % (i + 1) for i, n in enumerate(sorted(names))}


def _make_sub(alias):
    """三轮审查（N6）：脱敏替换必须**单趟同时**完成。

    旧写法是对每个别名依次 `s.replace(old,new)`，会把上一步刚写进去的
    代号再匹配一遍。语料里真有人叫 `P2` 时，`P20 → P2 → P1`，
    于是 `P2` 和 `P20` 两个不同的人被并成同一个代号 ——
    这正是 B12（清洗导致身份碰撞）那一类缺陷，只是换了层。
    这里用一次性的交替正则：全文只扫一遍，替换结果不再参与匹配。
    按长度降序排列，保证 `李明华` 优先于 `李明` 命中。
    """
    import re
    # 空表也要返回可用的替换函数（否则 scrub 调用 None 直接崩）；
    # 空键会让交替正则退化成"每次都匹配"，一并滤掉。
    keys = [k for k in alias if k]
    if not keys:
        return lambda s: s
    pat = re.compile('|'.join(re.escape(k) for k in
                              sorted(keys, key=lambda x: (-len(x), x))))
    return lambda s: pat.sub(lambda m: alias[m.group(0)], s)


def _redact(data, enabled, alias=None):
    """审查A4修复：发布版脱敏。原文剔除、人名映射为代号、链条文本隐去。

    结构级字段（subject / id / theme_key / bucket）统一交给一次递归清洗，
    不再逐字段多次 replace —— 见 _make_sub 的 N6 说明。
    """
    if not enabled:
        return data
    if alias is None:
        alias = _alias_of(data)
    sub = _make_sub(alias)

    for e in data.get('events', []):
        e['text'] = ''
    for c in data.get('chains', []):
        c['text'] = ''
        c.pop('date', None)          # 连日期一起隐去，防交叉定位
    for r in data.get('recon_log', []):
        if isinstance(r, dict):
            r.pop('detail', None)    # 改写详情里可能引用原文

    def scrub(o):
        if isinstance(o, dict):
            # 键同样可能携带人名（如 social_test._ambivalence_all）
            return {scrub(k): scrub(v) for k, v in o.items()}
        if isinstance(o, list):
            return [scrub(v) for v in o]
        if isinstance(o, str):
            return sub(o)
        return o

    data = scrub(data)
    data['redacted'] = True
    return data


def build_payload(brain, chains, test, days, keep, redact=False, alias=None):
    t_end = brain.t
    data = brain.export(t_end)
    data['source'] = 'real'
    data['span_days'] = round(days, 1)
    # people_kept 存的是语料原始名（未经引擎 sanitize），alias 键是清洗后的
    # 名字 —— 两者可能不同源。这里先按引擎同一规则过一遍再映射，堵住漏网。
    from databrain.engine import sanitize_subject
    data['people_kept'] = sorted({sanitize_subject(n) for n in keep})
    data['social_test'] = test
    # 因果链按冲击力排序，只带最重的若干条给前端
    chains_sorted = sorted(chains, key=lambda c: -c['salience'])[:40]

    def side(d):
        # 审查B3残留修复：新人物首条事件的 before['pv'] 是 None，
        # 嵌套 dict 推导也要能吞掉 None，否则整条管线在这里崩。
        if not isinstance(d, dict):
            return d
        return {k: (_num(v) if isinstance(v, float) else
                    ({kk: _num(vv) for kk, vv in v.items()}
                     if isinstance(v, dict) else v))
                for k, v in d.items()}

    data['chains'] = [{
        'date': c['date'], 'subject': c['subject'], 'stim': c['stim'],
        'text': c['text'][:80], 'salience': _num(c['salience'], 3),
        'intensity': c['intensity'], 'action': c['action'],
        'detail': c['detail'], 'hits': c['hits'], 'mod': _num(c['mod'], 3),
        'before': side(c['before']),
        'after': side(c['after']),
        'marks': {m: ({kk: _num(vv) for kk, vv in mv.items()}
                      if isinstance(mv, dict) else None)
                  for m, mv in c['marks'].items()},
    } for c in chains_sorted]
    return _redact(data, redact, alias)


NAMES = {
    'emotion_std': '情绪波动幅度', 'switch_speed': '情绪切换速度',
    'calm_ratio': '平淡期占比', 'extreme_ratio': '极端情绪占比',
    'fab_decay': '负性记忆消退', 'habituation_drop': '重复刺激钝化',
    'spontaneous_rate': '自发回忆频率', 'ambivalence_max': '矛盾情感存在度',
}

VALENCE = {'warm', 'affection', 'support', 'shared_joy', 'reconciliation',
           'apology', 'praise', 'humor', 'trust'}
NEGATIVE = {'betrayal', 'humiliation', 'rejection', 'conflict', 'crisis',
            'criticism', 'loss', 'neglect', 'pressure'}


def _dist(stims):
    """把刺激序列归成 正/中/负 三类占比。"""
    n = len(stims) or 1
    p = sum(1 for s in stims if s in VALENCE)
    g = sum(1 for s in stims if s in NEGATIVE)
    return {'pos': round(p / n, 4), 'neg': round(g / n, 4),
            'neutral': round((n - p - g) / n, 4), 'total': len(stims)}


def build_compare(brain_r, test_r, days_r, stims_r,
                  brain_s, test_s, days_s, stims_s, redact=False, alias=None):
    rows = []
    for k, label in NAMES.items():
        a = test_r['scores'][k]
        b = test_s['scores'][k]
        va, vb = a['value'], b['value']
        if va is not None and vb is not None:
            d = round(va - vb, 4)
        else:
            d = None
        rows.append({'key': k, 'label': label,
                     'real': va, 'synth': vb, 'diff': d,
                     'real_score': a['score'], 'synth_score': b['score']})

    def snap(brain, days):
        pb = list(brain.person_buckets.values())
        vs = [b.valence for b in pb]
        return {
            'days': round(days, 1),
            'events': len(brain.ledger),
            'persons': len(pb),
            'revisions': sum(len(b.appraisal_chain)
                             for b in list(brain.person_buckets.values())
                             + list(brain.themes.values())),
            'valence_mean': round(sum(vs) / len(vs), 4) if vs else None,
            'valence_min': round(min(vs), 4) if vs else None,
            'valence_max': round(max(vs), 4) if vs else None,
            'dist': _dist(stims_r if brain is brain_r else stims_s),
            'people': sorted([{'id': b.subject, 'v': round(b.valence, 3),
                               'imp': round(b.impedance(brain.t), 2),
                               'rev': len(b.appraisal_chain)}
                              for b in pb], key=lambda x: -x['v']),
        }

    payload = {
        'social': rows,
        'real_total': test_r['total'],
        'synth_total': test_s['total'],
        'real': snap(brain_r, days_r),
        'synth': snap(brain_s, days_s),
    }
    # 审查（二轮）补漏：对照载荷的 real.people[].id 直接取自真实语料人名，
    # 第一版脱敏漏了这里（而且 full/redacted 写的是同一个对象引用）。
    # 合成侧的 莉莉/汤姆 来自仓库里的脚本（simulate.py），本就是公开虚构名，
    # 脱敏它们只会让对照页更难读，因此只映射真实侧。
    if redact:
        if alias is None:
            names = sorted(b.subject for b in brain_r.person_buckets.values())
            alias = {n: 'P%d' % (i + 1) for i, n in enumerate(names)}
        for item in payload['real']['people']:
            item['id'] = alias.get(item['id'], item['id'])
        payload['redacted'] = True
    return payload


def _write(path, obj):
    """三轮审查（N7）：allow_nan=False —— Python 默认会把 NaN/Infinity
    写成 JSON 里没有的字面量，浏览器 JSON.parse 直接报错，而生成阶段
    一声不响。放在写盘这一道边界上拦，任何来源的脏数值都只能在这里
    炸出来，不会带着坏了的产物去发布。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, allow_nan=False)
    except ValueError as e:
        raise ValueError(f'{path} 含非有限数值（NaN/Infinity），拒绝写出：{e}') from e


def main():
    compare = '--compare' in sys.argv
    brain, chains, test, days, keep = run_real()
    print()
    print(report(test, f'社会化测试 · 真实语料（{days:.0f} 天）'))
    print()
    print(f"因果链追踪到 {len(chains)} 条重大事件")

    # 双写（审查A4修复）：未脱敏版进 .private/（自用、不进发布包），
    # 脱敏版进 web/（发布、可开源）。默认两个都写，避免误发原文。
    full = build_payload(brain, chains, test, days, keep, redact=False)
    _write(OUT_FULL, full)
    alias = _alias_of(full)          # real 与 compare 共用同一张代号表
    red = build_payload(brain, chains, test, days, keep, redact=True, alias=alias)
    _write(REDACT_OUT, red)
    print(f"未脱敏（自用）: {OUT_FULL}  ({os.path.getsize(OUT_FULL)/1024:.0f} KB)")
    print(f"脱敏（发布）  : {REDACT_OUT}  ({os.path.getsize(REDACT_OUT)/1024:.0f} KB)")

    if compare:
        print()
        from databrain.simulate import run as run_synth
        print("合成场景重跑中…")
        b2, _d = run_synth(180, 42, verbose=False)
        t2 = run_social_test(b2, 180)
        print(report(t2, '社会化测试 · 合成场景（180 天）'))
        print()
        print("  对照：")
        for k in t2['scores']:
            a = test['scores'][k]['value']
            b = t2['scores'][k]['value']
            fa = '—' if a is None else f'{a:.4f}'
            fb = '—' if b is None else f'{b:.4f}'
            print(f"    {k:<18} 真实 {fa:>9}   合成 {fb:>9}")

        _write(CMP_FULL, build_compare(
            brain, test, days, [e.stim for e in brain.ledger.events],
            b2, t2, 180, [e.stim for e in b2.ledger.events], redact=False))
        _write(REDACT_CMP, build_compare(
            brain, test, days, [e.stim for e in brain.ledger.events],
            b2, t2, 180, [e.stim for e in b2.ledger.events],
            redact=True, alias=alias))
        print(f"\n对照（自用）: {CMP_FULL}")
        print(f"对照（发布）: {REDACT_CMP}")


if __name__ == '__main__':
    # 中文 Windows 控制台默认 GBK；✅/⚠ 和 sparkline 的 ▁▂▃ 都编不进去，
    # 不显式改 UTF-8 会在打印那行崩（Linux/macOS 上 no-op）。
    sys.stdout.reconfigure(encoding='utf-8')
    main()
