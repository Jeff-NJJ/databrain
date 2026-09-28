# -*- coding: utf-8 -*-
"""
数字再生成器（审查C6修复）：README/文档里的头条数字一律由本脚本现场跑出，
写入 docs/figures.md。手抄数字是上一版文档全部对不上的根因，
以后改行为后请重跑：  python3 tools/gen_figs.py
"""
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from databrain.simulate import run                      # noqa: E402
from databrain.social import run_social_test            # noqa: E402
from databrain.corpus import classify                   # noqa: E402
from databrain import config as C                        # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), 'docs', 'figures.md')


def synth_block(days=180, seed=42):
    t0 = time.time()
    brain, diag = run(days, seed, verbose=False)
    el = time.time() - t0
    exp = brain.export(days * 24.0)
    test = run_social_test(brain, days)
    lines = []
    lines.append(f"### 合成场景（{days} 天 / seed {seed}）\n")
    lines.append(f"- 运行耗时：**{el:.1f} 秒**（本机实测，{days} 天逐小时推进）")
    m = exp['meta']
    lines.append(f"- 事件 {m['events_total']} 条 / 人物 {m['persons']} / "
                 f"主题桶 {m['themes']} / 情节 {m['episodic']} / "
                 f"**改写 {m['revisions']} 次**")
    lines.append(f"- 诊断：failures={len(diag.failures)} warnings={len(diag.warnings)}")
    lines.append(f"- 社会化测试总分：**{test['total']} / 100**")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|---|---|")
    zh = {'emotion_std': '情绪波动幅度', 'switch_speed': '情绪切换速度',
          'calm_ratio': '平淡期占比', 'extreme_ratio': '极端情绪占比',
          'fab_decay': '负性记忆消退', 'habituation_drop': '重复刺激钝化',
          'spontaneous_rate': '自发回忆频率', 'ambivalence_max': '矛盾情感存在度'}
    for k, v in test['scores'].items():
        val = v['value']
        s = '—' if val is None else (f"{val:.4f}" if isinstance(val, float) else str(val))
        lines.append(f"| {zh.get(k, k)} | {s} |")
    lines.append("")
    return "\n".join(lines), m, test


def classifier_block():
    samples = [
        "今天还不错 哈哈",
        "周三下午开会讨论了下季度的排期",
        "这个合同条款需要法务再看一下",
        "我妈住院了，这几天不太舒服",
        "项目终于上线了，大家辛苦了",
        "晚上一起吃饭吗",
        "谢谢你一直陪着我",
        "他把我拉黑了",
    ]
    lines = ["### 关键词分类器现状（实测样本）\n",
             "| 输入 | classify() 判定 |", "|---|---|"]
    for s in samples:
        stim, conf = classify(s)
        lines.append(f"| {s} | `{stim}` (conf {conf:.2f}) |")
    lines.append("")
    lines.append("> 分类器是词表命中制，正常闲聊大量落到 neutral/miss；"
                 "这是规则法的固有上限，不是 bug。上 ML 分类器前请勿把"
                 "刺激构成当心理指标解读。")
    lines.append("")
    return "\n".join(lines)


def fab_block():
    old = C.HUMAN['fab'].get('valence_drift', False)
    lines = ["### FAB 消融（valence_drift 开关）\n"]
    res = {}
    for flag in (False, True):
        C.HUMAN['fab']['valence_drift'] = flag
        brain, _ = run(180, 42, verbose=False)
        # FAB 只作用于情节/主题桶，人物桶豁免（见 human.tick_fab）。
        # 所以这里测的是负性情节记忆的 valence，不是人物认定。
        negs = [b for b in brain.episodic if b.valence0 < 0.4]
        res[flag] = (sum(b.valence for b in negs) / len(negs)) if negs else None
        C.HUMAN['fab']['valence_drift'] = old
    lines.append(f"- 默认（valence_drift=False）：负性情节记忆效价均值 {res[False]:.4f}")
    lines.append(f"- 消融（valence_drift=True）：负性情节记忆效价均值 {res[True]:.4f}")
    lines.append("")
    lines.append("> 默认配置下 FAB 只衰减唤醒、不再把长期效价拉向中性目标；"
                 "旧行为保留为消融开关。这是方法论变更，详见 CHANGELOG。")
    lines.append("")
    return "\n".join(lines)


def main():
    parts = ["# 引擎现场数字（由 tools/gen_figs.py 生成，请勿手改）\n",
             f"生成时间：{time.strftime('%Y-%m-%d %H:%M')} · "
             f"Python {sys.version.split()[0]}\n"]
    synth, meta, test = synth_block()
    parts.append(synth)
    parts.append(classifier_block())
    parts.append(fab_block())
    io.open(OUT, 'w', encoding='utf-8').write("\n".join(parts))
    print(f"written: {OUT}")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
