# -*- coding: utf-8 -*-
"""
社会化测试：把"像不像人"变成可量化的指标

一个问题必须先回答：**什么叫做"相处久了不觉得奇怪"？**
下面是八个可测量的反常信号。每一个都对应一种"露馅"方式。

  1. 情绪方差        太大=躁狂，太小=麻木
  2. 情绪切换速度    相邻事件间的跳变幅度；太大=瞬变，没有惯性
  3. 平淡期占比      真实生活大部分时间是平淡的；太低=持续戏剧化
  4. 极端化          长期停在极端情绪 = 不正常
  5. 记仇检测        负性记忆的情绪强度该随时间消退（FAB）；不消退=记仇
  6. 钝化检测        重复刺激该越来越不管用；不钝化=假
  7. 自发回忆        静默期该会主动想起人；完全没有=太被动，像工具
  8. 矛盾情感        该存在又爱又恨的关系；完全没有=态度单一，显假

评分区间 0-100，>=75 视为"能长期相处不露馅"。
"""

import math
import statistics


# 每个指标的合理区间（下界, 上界）
BANDS = {
    'emotion_std':      (0.05, 0.28),    # 情绪标准差
    'switch_speed':     (0.0,  0.16),    # 相邻事件平均跳变
    'calm_ratio':       (0.55, 0.98),    # 平淡期占比
    'extreme_ratio':    (0.0,  0.12),    # 极端情绪占比
    'fab_decay':        (0.15, 1.0),     # 负性记忆情绪消退比例
    'habituation_drop': (0.15, 0.85),    # 重复刺激的钝化程度
    'spontaneous_rate': (0.05, 1.6),     # 每天自发想起的次数（有上限防止太黏人）
    'ambivalence_max':  (0.20, 1.0),     # 最矛盾关系的矛盾度
}


def _score(name, value):
    lo, hi = BANDS[name]
    if value is None:
        return 0.0, '无数据'
    if lo <= value <= hi:
        return 100.0, '正常'
    # 偏离多少
    if value < lo:
        dev = (lo - value) / max(lo, 1e-9)
    else:
        dev = (value - hi) / max(hi, 1e-9)
    s = max(0.0, 100.0 - dev * 160.0)
    tag = '偏低' if value < lo else '偏高'
    return round(s, 1), tag


def run_social_test(brain, days):
    """
    brain: 跑完的 DataBrain
    days: 模拟跨度（天）
    （审查B6：原 stream 参数从未被函数体使用，已删除）
    """
    res = {}

    # ---------- 1/2/3/4: 情绪动力学 ----------
    trace = brain.human.emo_trace
    vs = [p['v'] for p in trace if p['event']]
    if len(vs) > 2:
        res['emotion_std'] = round(statistics.pstdev(vs), 4)
        # 切换速度：只在"有事件"的相邻点之间算
        ev_tr = [p for p in trace if p['event']]
        jumps = [abs(ev_tr[i]['v'] - ev_tr[i - 1]['v'])
                 for i in range(1, len(ev_tr))]
        res['switch_speed'] = round(sum(jumps) / len(jumps), 4) if jumps else None
    else:
        res['emotion_std'] = None
        res['switch_speed'] = None

    # 平淡期：整条轨迹（含静默）里低唤醒的比例
    allpts = trace
    if allpts:
        calm = sum(1 for p in allpts if p['a'] < 0.35)
        res['calm_ratio'] = round(calm / len(allpts), 4)
        ext = sum(1 for p in allpts if p['v'] < 0.15 or p['v'] > 0.85)
        res['extreme_ratio'] = round(ext / len(allpts), 4)
    else:
        res['calm_ratio'] = None
        res['extreme_ratio'] = None

    # ---------- 5: FAB ----------
    negs = [b for b in brain.episodic if b.valence0 < 0.4]
    if negs:
        drops = []
        for b in negs:
            a0 = b.arousal0
            a1 = b.arousal
            if a0 > 1e-6:
                drops.append((a0 - a1) / a0)
        res['fab_decay'] = round(sum(drops) / len(drops), 4) if drops else None
    else:
        res['fab_decay'] = None

    # ---------- 6: 钝化 ----------
    # 审查B8 修复后 habit 的键是 (stim, subject)：这里按"刺激在所有人身上的
    # 最大计数"评估钝化程度，聚合口径与引擎一致。
    hs = brain.human.habit
    if hs:
        top = max(hs.values())
        top_key = max(hs, key=hs.get)          # (stim, subject)
        res['habituation_drop'] = round(1.0 - brain.human.habituation_factor(
            top_key[0], top_key[1]), 4)
        res['_habit_top'] = round(top, 1)
    else:
        res['habituation_drop'] = None

    # ---------- 7: 自发回忆 ----------
    n_sp = len(brain.human.spontaneous_log)
    res['spontaneous_rate'] = round(n_sp / max(days, 1), 4)
    res['_spontaneous_total'] = n_sp

    # ---------- 8: 矛盾情感 ----------
    from .human import HumanLayer
    ambs = [HumanLayer.ambivalence(b) for b in brain.person_buckets.values()]
    res['ambivalence_max'] = round(max(ambs), 4) if ambs else None
    res['_ambivalence_all'] = {b.subject: round(HumanLayer.ambivalence(b), 3)
                               for b in brain.person_buckets.values()}

    # ---------- 汇总评分 ----------
    scores = {}
    for k in BANDS:
        s, tag = _score(k, res.get(k))
        scores[k] = {'value': res.get(k), 'score': s, 'tag': tag}
    total = round(sum(v['score'] for v in scores.values()) / len(scores), 1)
    return {'metrics': res, 'scores': scores, 'total': total}


def report(test, title='社会化测试'):
    lines = [f"=== {title} ===", ""]
    names = {
        'emotion_std': '情绪波动幅度',
        'switch_speed': '情绪切换速度',
        'calm_ratio': '平淡期占比',
        'extreme_ratio': '极端情绪占比',
        'fab_decay': '负性记忆消退',
        'habituation_drop': '重复刺激钝化',
        'spontaneous_rate': '自发回忆频率',
        'ambivalence_max': '矛盾情感存在度',
    }
    for k, label in names.items():
        s = test['scores'][k]
        v = s['value']
        vs = '—' if v is None else f'{v:.4f}'
        bar = '█' * int(s['score'] / 10)
        lines.append(f"  {label:<10} {vs:>9}  {s['score']:>5.0f}  {bar:<10} {s['tag']}")
    lines.append("")
    lines.append(f"  总分  {test['total']} / 100   "
                 f"{'✅ 可以长期相处' if test['total'] >= 75 else '⚠️ 仍有露馅风险'}")
    return "\n".join(lines)
