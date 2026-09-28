# -*- coding: utf-8 -*-
"""
跨时间 · 跨场景模拟 + 自检探针

跑这条命令：
  python3 -m databrain.simulate

模拟结构：
  180 天，步长 1 小时（4320 tick）
  每天按「时段 × 场景」注入经历；场景不同，刺激分布与强度分布都不同
  中间埋了脚本化关键事件（杰夫的汤姆剧本：一次重创 + 长期修复）

自检探针会逐 tick 检查数值健康度，任何异常都记进 warnings，
最后汇总 FAIL / WARN / PASS。
"""

import math
import sys
import json
from collections import defaultdict, Counter
from . import config as C
from .engine import DataBrain
from .state import clamp


# ============================================================
# 场景定义：不同场合发生不同性质的事
# ============================================================
SCENARIOS = {
    'morning': {
        'hours': [7, 8],
        'stims': [('neutral', .30), ('affection', .22), ('mundane', .28), ('praise', .20)],
        'intensity': (0.25, 0.55),
    },
    'work': {
        'hours': [9, 10, 11, 14, 15, 16, 17],
        'stims': [('neutral', .26), ('curiosity', .16), ('criticism', .16),
                  ('praise', .16), ('conflict', .10), ('provocation', .08), ('mundane', .08)],
        'intensity': (0.3, 0.8),
    },
    'evening': {
        'hours': [19, 20, 21],
        'stims': [('affection', .30), ('shared_joy', .18), ('playful_neg', .16),
                  ('conflict', .12), ('neutral', .14), ('reconciliation', .10)],
        'intensity': (0.4, 0.9),
    },
    'night': {
        'hours': [23, 0, 1],
        'stims': [('loneliness', .34), ('neutral', .28), ('neglect', .20), ('loss', .18)],
        'intensity': (0.3, 0.7),
    },
    'weekend': {
        'hours': [11, 13, 15, 17, 20],
        'stims': [('shared_joy', .28), ('affection', .26), ('curiosity', .18),
                  ('praise', .16), ('playful_neg', .12)],
        'intensity': (0.4, 0.85),
    },
}

# 每天的脚本化事件：day -> (hour, subject, stim, text, intensity)
SCRIPT = {
    2:   (20, '汤姆', 'betrayal',      '汤姆在所有人面前把责任推给了他',        1.0),
    3:   (21, '汤姆', 'humiliation',   '第二天有人当面拿这件事取笑他',          0.85),
    12:  (20, '汤姆', 'apology',       '汤姆私下道歉了，态度认真',              0.7),
    25:  (19, '汤姆', 'reconciliation','汤姆主动帮他解决了一个难题',            0.8),
    38:  (11, '汤姆', 'conflict',      '工作会议上汤姆再次抢功',                0.9),
    39:  (20, '汤姆', 'apology',       '汤姆当晚就来解释，说当时是误会',        0.75),
    60:  (19, '汤姆', 'affection',     '汤姆记得他提过的小事并做了安排',        0.8),
    75:  (20, '汤姆', 'shared_joy',    '一起完成了拖了很久的项目',              0.85),
    95:  (15, '莉莉', 'affection',     '莉莉一直在稳定地支持他',                0.7),
    110: (20, '汤姆', 'gratitude',     '汤姆公开感谢了他',                      0.75),
    145: (17, '汤姆', 'neglect',       '汤姆又一次临时爽约',                    0.6),
    146: (21, '汤姆', 'apology',       '汤姆立刻补救并解释了原因',              0.7),
    165: (19, '汤姆', 'reconciliation','两人把话说开了',                        0.85),
}


def pick_scenario(hour, weekday, rng):
    is_weekend = weekday >= 5
    if is_weekend and hour in SCENARIOS['weekend']['hours']:
        return 'weekend' if rng.random() < .7 else 'evening'
    for name, cfg in SCENARIOS.items():
        if name in ('weekend',):
            continue
        if hour in cfg['hours']:
            return name
    return None


def weighted_pick(pairs, rng):
    tot = sum(p for _, p in pairs)
    r = rng.random() * tot
    acc = 0.0
    for s, p in pairs:
        acc += p
        if r <= acc:
            return s
    return pairs[-1][0]


# ============================================================
# 自检探针
# ============================================================
class Diagnostics:
    def __init__(self):
        self._tick_n = 0
        self.warnings = []
        self.failures = []
        self.info = {}
        self.hormone_extremes = {k: [1.0, 0.0] for k in C.HORMONES}
        self.saturated_ticks = Counter()      # 激素长期贴边计数
        self.importance_clamped = 0
        self.score_history = defaultdict(list)
        self.recon_trace = []
        self.drained_counter_evidence = 0
        self.max_counter_evidence = 0.0
        self.nan_count = 0

    def check_tick(self, t, engine, full_every=24):
        # 审查B11：桶级全量扫描 O(桶数) 每 tick 跑一次，长程模拟平方级变慢。
        # 激素/慢变量每 tick 查（便宜）；桶级深查降频（默认每 24 tick 一次）。
        full = (self._tick_n % full_every == 0)
        self._tick_n += 1
        # --- NaN / Inf ---
        for k, v in engine.hormones.h.items():
            if v is None or math.isnan(v) or math.isinf(v):
                self.nan_count += 1
                self.failures.append(f"t={t:.0f}h 激素 {k} 非法值 {v}")
            else:
                lo, hi = self.hormone_extremes[k]
                self.hormone_extremes[k] = [min(lo, v), max(hi, v)]
                cfg = C.HORMONES[k]
                # 贴边超过 0.5% 容差算饱和
                if v >= cfg['ceil'] - 0.01 or v <= cfg['floor'] + 0.01:
                    self.saturated_ticks[k] += 1
        # --- 慢变量 ---
        for k, v in engine.slow.v.items():
            if v is None or math.isnan(v) or math.isinf(v):
                self.failures.append(f"t={t:.0f}h 慢变量 {k} 非法值 {v}")
            elif not (0.0 <= v <= 1.0):
                self.failures.append(f"t={t:.0f}h 慢变量 {k} 越界 {v}")
        # --- 记忆桶（含三层）---
        for b in ((list(engine.person_buckets.values())
                  + list(engine.themes.values()) + engine.episodic) if full else []):
            for name in ('valence', 'arousal', 'counter_evidence', 'importance'):
                val = getattr(b, name)
                if val is None or math.isnan(val) or math.isinf(val):
                    self.failures.append(f"t={t:.0f}h 桶 {b.id} 的 {name} 非法值 {val}")
            s = b.score(t)
            if math.isnan(s) or math.isinf(s):
                self.failures.append(f"t={t:.0f}h 桶 {b.id} score 非法值 {s}")
            if not (0.0 <= b.valence <= 1.0) or not (0.0 <= b.arousal <= 1.0):
                self.failures.append(f"t={t:.0f}h 桶 {b.id} 效价/唤醒越界 "
                                     f"({b.valence}, {b.arousal})")
            self.max_counter_evidence = max(self.max_counter_evidence, b.counter_evidence)
            if b.importance >= 10 or b.importance <= 1:
                self.importance_clamped += 1

    def check_post(self, engine, total_ticks, days):
        # --- 长期饱和 ---
        for k, cnt in self.saturated_ticks.items():
            ratio = cnt / max(total_ticks, 1)
            if ratio > 0.15:
                self.warnings.append(
                    f"激素 {k} 有 {ratio:.1%} 的时间贴在边界上 —— 可能失去调节能力")
        # --- 情节遗忘（只对情节层报警）---
        # 注意：subject 级的"历史认定"本就不该被遗忘，那是设计意图而非 bug。
        epis = engine.episodic
        if epis:
            archived_ratio = sum(1 for b in epis if b.archived) / len(epis)
            self.info['episodic_archived_ratio'] = round(archived_ratio, 3)
            self.info['episodic_count'] = len(epis)
            # 弱情节记忆的归档周期理论值约 27 天，跑太短看不出来，
            # 所以在短程冒烟测试里跳过这条检查，避免误报。
            if days >= 60:
                if archived_ratio > 0.92:
                    self.warnings.append(
                        f"{archived_ratio:.0%} 的情节记忆被归档 —— 阈值过严或记忆强度过低")
                if archived_ratio < 0.05:
                    self.warnings.append(
                        f"只有 {archived_ratio:.0%} 的情节记忆被归档 —— 情节层遗忘机制失效")
        # --- 再巩固是否真的发生过 ---
        if not self.recon_trace:
            self.failures.append(
                "整个模拟期内发生 0 次再巩固 —— 门槛过高，旧判断永远无法更新")
        # --- 账本完整性 ---
        problems = engine.ledger.integrity_check()
        for p in problems:
            self.failures.append(f"账本完整性: {p}")
        # --- 反证据是否失控 ---
        if self.max_counter_evidence > 50:
            self.warnings.append(
                f"counter_evidence 峰值达到 {self.max_counter_evidence:.1f} —— 累积器可能失控")
        # --- NaN ---
        if self.nan_count:
            self.failures.append(f"共出现 {self.nan_count} 次 NaN/Inf")

    def report(self):
        lines = []
        lines.append("=" * 62)
        if self.failures:
            lines.append(f"❌ FAIL  ({len(self.failures)} 项)")
            for f in self.failures[:25]:
                lines.append(f"   - {f}")
        else:
            lines.append("✅ 无致命错误")
        lines.append("-" * 62)
        if self.warnings:
            lines.append(f"⚠️  WARN  ({len(self.warnings)} 项)")
            for w in self.warnings:
                lines.append(f"   - {w}")
        else:
            lines.append("✅ 无警告")
        lines.append("-" * 62)
        lines.append("激素极值范围:")
        for k, (lo, hi) in self.hormone_extremes.items():
            lines.append(f"   {k:<11} [{lo:.3f}, {hi:.3f}]")
        if self.recon_trace:
            lines.append("-" * 62)
            lines.append(f"再巩固事件 {len(self.recon_trace)} 次:")
            for r in self.recon_trace[:30]:
                lines.append(f"   D{r['day']:<6.1f} {r['detail']}")
        return "\n".join(lines)


# ============================================================
# ASCII 迷你图
# ============================================================
BLOCKS = '▁▂▃▄▅▆▇█'

def sparkline(vals, lo=None, hi=None, width=None):
    if not vals:
        return ''
    vals = list(vals)
    lo = min(vals) if lo is None else lo
    hi = max(vals) if hi is None else hi
    if hi - lo < 1e-9:
        return BLOCKS[0] * len(vals)
    if width and len(vals) > width:
        step = len(vals) / width
        vals = [vals[int(i * step)] for i in range(width)]
    out = []
    for v in vals:
        idx = int((v - lo) / (hi - lo) * (len(BLOCKS) - 1))
        out.append(BLOCKS[max(0, min(len(BLOCKS) - 1, idx))])
    return ''.join(out)


# ============================================================
# 主模拟
# ============================================================
def run(days=180, seed=42, verbose=True):
    import random
    rng = random.Random(seed)
    brain = DataBrain(seed=seed)
    diag = Diagnostics()

    total_ticks = 0
    act_map = Counter()

    for day in range(days):
        weekday = day % 7
        # ---- 脚本事件 ----
        script = SCRIPT.get(day)
        for hour in range(24):
            t = day * 24.0 + hour
            brain.tick(t, 1.0, hour=float(hour))
            total_ticks += 1

            if script and hour == script[0]:
                _, subject, stim, text, inten = script
                r = brain.experience(t, subject, stim, text, inten, hour=float(hour))
                act_map[r['action']] += 1
                if r['action'] == 'reconsolidated':
                    diag.recon_trace.append({'day': day, 'detail': r['detail']})
                if verbose:
                    print(f"  [脚本] D{day:<3} {hour:02d}:00 {stim:<15} "
                          f"v={r['v']:.3f} a={r['a']:.3f} → {r['action']}")
                continue

            # ---- 常规场景 ----
            sc = pick_scenario(hour, weekday, rng)
            if sc is None:
                diag.check_tick(t, brain)
                continue
            # 不是每个时段都发生值得一提的事
            p_event = 0.55 if sc == 'work' else 0.45
            if rng.random() > p_event:
                diag.check_tick(t, brain)
                continue

            cfg = SCENARIOS[sc]
            stim = weighted_pick(cfg['stims'], rng)
            lo, hi = cfg['intensity']
            inten = rng.uniform(lo, hi)
            # 主体：汤姆占多数，莉莉偶尔出现（跨多个 social 客体）
            subject = '汤姆' if rng.random() < 0.62 else '莉莉'
            r = brain.experience(t, subject, stim, '', inten, hour=float(hour))
            act_map[r['action']] += 1
            if r['action'] == 'reconsolidated':
                diag.recon_trace.append({'day': day, 'detail': r['detail']})

            diag.check_tick(t, brain)

        # ---- 每天记录一次快照指标 ----
        t_end = day * 24.0 + 23.0
        brain.record_timeline(t_end)
        snap = brain.snapshot(t_end)
        diag.score_history['mood_valence'].append(snap['slow']['mood_valence'])
        diag.score_history['cortisol'].append(snap['hormones']['cortisol'])
        diag.score_history['rel_temp'].append(snap['slow']['rel_temp'])
        diag.score_history['tom_valence'].append(
            brain.person_buckets['汤姆'].valence if '汤姆' in brain.person_buckets else 0.5)
        diag.score_history['tom_arousal'].append(
            brain.person_buckets['汤姆'].arousal if '汤姆' in brain.person_buckets else 0.3)
        diag.score_history['tom_impedance'].append(
            brain.person_buckets['汤姆'].impedance(t_end) if '汤姆' in brain.person_buckets else 0.0)

    diag.check_post(brain, total_ticks, days)

    if verbose:
        print()
        print("=" * 62)
        print(f"模拟完成：{days} 天 / {total_ticks} tick / "
              f"{len(brain.ledger)} 条事件 / {len(brain.episodic)} 个情节桶")
        print("=" * 62)
        print(f"行为分布: {dict(act_map)}")
        print()
        print(f"--- 汤姆的历史认定轨迹（{days}天）---")
        print(f"valence   {sparkline(diag.score_history['tom_valence'], 0, 1, width=90)}")
        print(f"arousal   {sparkline(diag.score_history['tom_arousal'], 0, 1, width=90)}")
        print(f"阻抗      {sparkline(diag.score_history['tom_impedance'], 0, 3, width=90)}")
        print()
        print(f"心境效价  {sparkline(diag.score_history['mood_valence'], 0, 1, width=90)}")
        print(f"皮质醇    {sparkline(diag.score_history['cortisol'], 0, 1, width=90)}")
        print(f"关系温度  {sparkline(diag.score_history['rel_temp'], 0, 1, width=90)}")
        print()

        tom = brain.person_buckets.get('汤姆')
        if tom:
            print("--- 汤姆这条记录的详细状态 ---")
            d = tom.to_dict(days * 24.0)
            for k, v in d.items():
                print(f"   {k:<20} {v}")
            print(f"   重评次数           {len(tom.appraisal_chain)}")
            for c in tom.appraisal_chain:
                print(f"      D{c['day']:<6.1f} {c['from_v']:.3f} → {c['to_v']:.3f}  "
                      f"触发: {c['trigger_stim']:<14} 移动 {c['shift']:+.4f} "
                      f"阻抗 {c['impedance']:.2f}")
            print(f"   关联原始事件数     {len(tom.event_ids)}")
        print()
        print(diag.report())

    return brain, diag


if __name__ == '__main__':
    # 中文 Windows 控制台默认 GBK；✅/⚠ 和 sparkline 的 ▁▂▃ 都编不进去，
    # 不显式改 UTF-8 会在打印那行崩（Linux/macOS 上 no-op）。
    sys.stdout.reconfigure(encoding='utf-8')
    run(180, 42)
