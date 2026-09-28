# -*- coding: utf-8 -*-
"""
对照实验：验证模型不是被某个随机种子喂出来的假象

三组对照：
  A. 种子扫描      —— 5 个不同随机种子跑同一剧本，看结论是否稳定
  B. 恶意-善意切换 —— 前 60 天持续伤害，60 天后持续善意。看曲线能否回升
  C. 单次赎回冲击  —— 一次超高显著性的正面事件，能否撬动一条深负性判断
                     （预期：能，但不能一步到位）

用法：
  python3 tools/validate.py
"""

import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databrain import DataBrain
from databrain import config as C
from databrain.simulate import sparkline, Diagnostics


def _make(seed):
    return DataBrain(seed=seed)


# ============================================================
# 通用推进器
# ============================================================
def drive(brain, plan, days, diag=None):
    """plan: {day: [(hour, subject, stim, text, intensity), ...]}"""
    for day in range(days):
        for hour in range(24):
            t = day * 24.0 + hour
            brain.tick(t, 1.0, hour=float(hour))
            for (h, subj, stim, text, inten) in plan.get(day, []):
                if h != hour:
                    continue
                brain.experience(t, subj, stim, text, inten, hour=float(hour))
            if diag:
                diag.check_tick(t, brain)
    return brain


# ============================================================
# A. 种子扫描
# ============================================================
def exp_seeds():
    print("=" * 70)
    print("A. 种子扫描（验证结论不依赖特定随机序列）")
    print("=" * 70)
    results = []
    for seed in (1, 7, 42, 99, 2024):
        brain, diag = _run_default(seed)
        tom = brain.person_buckets['汤姆']
        # 自检里的分区检查用 180 天
        fails = len([f for f in diag.failures])
        warns = len(diag.warnings)
        results.append((seed, tom.valence0, tom.valence, len(tom.appraisal_chain),
                        tom.impedance(180 * 24.0), fails, warns))
        print(f"  seed={seed:<5} 初值={tom.valence0:.3f}  终值={tom.valence:.3f}  "
              f"重评={len(tom.appraisal_chain):<3} 阻抗={tom.impedance(180*24.0):.2f}  "
              f"FAIL={fails} WARN={warns}")
    finals = [r[2] for r in results]
    print(f"\n  终值范围 [{min(finals):.3f}, {max(finals):.3f}]  "
          f"标准差 {(sum((x - sum(finals)/len(finals))**2 for x in finals)/len(finals))**0.5:.4f}")
    ok = len(set(r[6] for r in results)) == 1 and all(r[5] == 0 for r in results)
    print(f"  → {'✅ 全部种子零 FAIL 且行为一致' if ok else '❌ 种子间存在差异，需要检查'}")
    return results


def _run_default(seed):
    """复用主模拟的剧本，但不打印。"""
    rng = random.Random(seed)
    brain = DataBrain(seed=seed)
    diag = Diagnostics()
    from databrain.simulate import SCRIPT, SCENARIOS, pick_scenario, weighted_pick
    for day in range(180):
        weekday = day % 7
        script = SCRIPT.get(day)
        for hour in range(24):
            t = day * 24.0 + hour
            brain.tick(t, 1.0, hour=float(hour))
            if script and hour == script[0]:
                _, subject, stim, text, inten = script
                r = brain.experience(t, subject, stim, text, inten, hour=float(hour))
                if r['action'] == 'reconsolidated':
                    diag.recon_trace.append({'day': day, 'detail': r['detail']})
                diag.check_tick(t, brain)
                continue
            sc = pick_scenario(hour, weekday, rng)
            if sc is None:
                diag.check_tick(t, brain)
                continue
            p_event = 0.55 if sc == 'work' else 0.45
            if rng.random() > p_event:
                diag.check_tick(t, brain)
                continue
            cfg = SCENARIOS[sc]
            stim = weighted_pick(cfg['stims'], rng)
            lo, hi = cfg['intensity']
            inten = rng.uniform(lo, hi)
            subject = '汤姆' if rng.random() < 0.62 else '莉莉'
            r = brain.experience(t, subject, stim, '', inten, hour=float(hour))
            if r['action'] == 'reconsolidated':
                diag.recon_trace.append({'day': day, 'detail': r['detail']})
            diag.check_tick(t, brain)
    diag.check_post(brain, 180 * 24, 180)
    return brain, diag


# ============================================================
# B. 前恶后善：判断能否被逆转
# ============================================================
def exp_reversal():
    print()
    print("=" * 70)
    print("B. 前 60 天持续伤害 → 后 120 天持续善意（看能否回升）")
    print("=" * 70)
    brain = _make(7)
    plan = {}
    # 前 60 天：隔天一次伤害
    for d in range(0, 60, 2):
        plan[d] = [(20, '凯文', 'betrayal', '又一次背叛', 0.9)]
    # 后 120 天：隔天一次善意
    for d in range(60, 180, 2):
        plan[d] = [(19, '凯文', 'affection', '持续的支持', 0.8)]

    trace = []
    for day in range(180):
        for hour in range(24):
            t = day * 24.0 + hour
            brain.tick(t, 1.0, hour=float(hour))
            for (h, s, st, tx, it) in plan.get(day, []):
                if h == hour:
                    brain.experience(t, s, st, tx, it, hour=float(hour))
        if day % 10 == 0 or day == 179:
            b = brain.person_buckets['凯文']
            trace.append((day, b.valence, b.impedance(t)))
    b = brain.person_buckets['凯文']
    print(f"  初始印象      {b.valence0:.3f}")
    print(f"  第 60 天      {trace[6][1]:.3f}  （伤害期结束）")
    print(f"  第 180 天     {b.valence:.3f}")
    print(f"  重评次数      {len(b.appraisal_chain)}")
    print(f"  曲线          {sparkline([x[1] for x in trace], 0, 1, width=70)}")
    recovered = b.valence > b.valence0
    print(f"  → {'✅ 旧判断确实被经历扭转了' if recovered else '❌ 判断没有被扭转'}")
    return b


# ============================================================
# C. 单次赎回冲击：一次大事件能撬动多少
# ============================================================
def exp_single_rescue():
    """
    真正要回答的问题是：**要攒够多少次经历，才能撬动一条深负性判断？**
    单次救济式的大事件确实不够 —— 这正是门槛存在的意义，
    但我们要把"不够"量化成"还差几次"，而不是笼统地说"没触发"。
    """
    print()
    print("=" * 70)
    print("C. 深负性判断需要多少次正面经历才能被撬动")
    print("=" * 70)

    # 先建立一条深负性判断（30 天持续伤害）
    def build_baseline():
        brain = _make(11)
        for d in range(0, 30, 2):
            for hour in range(24):
                t = d * 24.0 + hour
                brain.tick(t, 1.0, hour=float(hour))
                if hour == 20:
                    brain.experience(t, '马克', 'betrayal', '持续的伤害', 0.9, hour=20.0)
        return brain

    base = build_baseline()
    marker0 = base.person_buckets['马克']
    print(f"  基线：30 天持续伤害后 valence={marker0.valence:.3f}  "
          f"阻抗={marker0.impedance(30*24.0):.2f}")
    print()

    # --- 分组：不同程度的正面事件，每 3 天一次，看各需几次 ---
    for stim, intensity, label in [
        ('affection',      0.8, '日常善意       (affection i=0.8)'),
        ('shared_joy',     0.9, '深度共处       (shared_joy i=0.9)'),
        ('reconciliation', 1.0, '重大和解       (reconciliation i=1.0)'),
    ]:
        brain = build_baseline()
        m = brain.person_buckets['马克']
        start_v = m.valence
        hits = 0
        first_flip_at = None
        for rep in range(40):
            d = 30 + rep * 3
            for hour in range(24):
                t = d * 24.0 + hour
                brain.tick(t, 1.0, hour=float(hour))
                if hour == 19:
                    r = brain.experience(t, '马克', stim, '一次正面经历', intensity, hour=19.0)
                    hits += 1
                    if r['action'] == 'reconsolidated' and first_flip_at is None:
                        first_flip_at = hits
        # 处理一次都没撬动的情况
        print(f"  {label}")
        if first_flip_at:
            print(f"    第 {first_flip_at:>2} 次时首次撬动 → valence {start_v:.3f} → {m.valence:.3f}"
                  f"  (Δ{m.valence-start_v:+.4f}, 共重评 {len(m.appraisal_chain)} 次)")
        else:
            print(f"    40 次都没能撬动 → valence 停在 {m.valence:.3f}")
        print()


if __name__ == '__main__':
    # 中文 Windows 控制台默认 GBK；✅/⚠ 和 sparkline 的 ▁▂▃ 都编不进去，
    # 不显式改 UTF-8 会在打印那行崩（Linux/macOS 上 no-op）。
    sys.stdout.reconfigure(encoding='utf-8')
    exp_seeds()
    exp_reversal()
    exp_single_rescue()
    print("=" * 70)
    print("对照实验完成")
