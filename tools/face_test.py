# -*- coding: utf-8 -*-
"""
对照测试：把原「内分泌引擎 v2.0」跑一遍，把合并后的数据化大脑跑一遍，
同一段对话，两边各出一份 prompt_suffix，摆在一起看。

这不是为了证明谁分高 —— 是为了确认合并是真的合上了：
    · 原版该有的东西（语气、行为冲动、认知模式、对方状态、慢路径）有没有丢
    · 我们多出来的东西（对这个人的认定、模式、改写次数、分离焦虑按人算）有没有生效

用法：
  python tools/face_test.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from databrain import DataBrain                     # noqa: E402
from databrain.agentface import AgentFace           # noqa: E402

ORIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '_sources', 'orig_endocrine', '内分泌引擎_打包_20260921')

# 同一段对话，喂给两边
SCRIPT = [
    ('汤姆', 'betrayal',   '汤姆在会上把我们的成果说成他一个人做的，我当时气死了。'),
    ('汤姆', 'apology',    '汤姆下午私聊跟我道歉了，说当时脑子一热。'),
    ('莉莉', 'affection',  '莉莉说我最近状态比之前好多了，让我别太苛责自己。'),
    ('莉莉', 'neglect',    '给莉莉发消息一直没回，人呢去哪了。'),
    ('汤姆', 'criticism',  '汤姆说这个方案做得太差了，我好生气。'),
    ('莉莉', 'gratitude',  '谢谢莉莉一直陪着我，我好累但是很开心。'),
]

SEP = '─' * 62


def run_original():
    """直接 import 原包里的 endocrine.py 跑一遍，拿到它自己的 prompt_suffix。"""
    sys.path.insert(0, ORIG)
    try:
        import endocrine as E
    except ImportError as e:
        return None, f"无法载入原引擎：{e}"
    eng = E.EndocrineEngine()
    outs = []
    for who, stim, text in SCRIPT:
        eng.process_input(text)
        outs.append((who, stim, text, eng.generate_prompt_suffix()))
    return outs, None


def run_merged():
    """
    合并后的版本：同一段对话。
    **公平起见这里也只喂文本**，用我们自己的分类器（corpus.classify）判定刺激，
    不预先告诉它这句话是什么 —— 真实部署时就是这个样子。
    """
    from databrain.corpus import classify, _intensity
    brain = DataBrain(seed=7)
    outs = []
    for i, (who, stim, text) in enumerate(SCRIPT):
        t = i * 6.0
        brain.tick(t, 6.0, hour=t % 24.0)
        got, _ = classify(text)
        brain.experience(t, who, got, text, _intensity(text), hour=t % 24.0)
        # 让慢路径有机会释放
        brain.tick(t + 2.5, 2.5)
        outs.append((who, stim, text, brain.prompt_suffix(who)))
    return outs, brain


def main():
    print(SEP)
    print("同一段对话，两个引擎各自的 prompt_suffix")
    print(SEP)

    orig, err = run_original()
    merged, brain = run_merged()

    if err:
        print(err)
        orig = None

    for i, (who, stim, text) in enumerate(SCRIPT):
        print(f"\n\n【第 {i+1} 句】{who} · {stim}")
        print(f"  “{text}”")
        if orig:
            print(f"\n  ── 原内分泌引擎 v2.0 ──")
            for ln in orig[i][3].splitlines():
                print("   ", ln)
        print(f"\n  ── 合并后的数据化大脑 ──")
        for ln in merged[i][3].splitlines():
            print("   ", ln)

    print(f"\n\n{SEP}")
    print("机制覆盖对照")
    print(SEP)
    rows = [
        ('激素五项 + 昼夜节律',      '有', '有'),
        ('涌现情绪',                 '有', '有（人味层，带惯性/不应期）'),
        ('行为冲动 + 冷却',          '有', '有（原阈值移植）'),
        ('语气调制 + 惯性',          '有', '有（原文案移植）'),
        ('倒 U 认知门控',            '有', '有（原版 #31）'),
        ('对方状态识别',             '有（只打标签）', '有（还会带动激素）'),
        ('慢路径延迟反应',           '乘系数当场放', '排进时间轴，到点才放'),
        ('对话节奏感知',             '有', '有'),
        ('分离焦虑',                 '有（全局一份）', '有（按人计算，看在意程度）'),
        ('对某个人的长期认定',       '无', '有（含阻抗/改写次数/版本链）'),
        ('对所有曾说过话人的整体态度判断',        '无', '有（模式层）'),
        ('tell who when asked',      '做不到', '能说出"我认为他是什么样的人"'),
        ('哪些参考资料和原始时刻被 remember', '无（只有激素状态）', '有（append-only 账本）'),
    ]
    print(f"  {'能力':<26}{'原版 v2.0':<16}{'合并后'}")
    for a, b, c in rows:
        print(f"  {a:<26}{b:<16}{c}")

    print(f"\n{SEP}")
    print("验证：慢路径与分离焦虑是真的在跑吗")
    print(SEP)
    print(f"  延迟反应释放了 {len(brain.face.released)} 次")
    for r in brain.face.released[:4]:
        print(f"    t={r['at']:.1f}h  {r['reason']}  {r['effects']}")
    act = {k: v for k, v in brain.face.sep_level.items() if v}
    print(f"  分离焦虑档位：{act if act else '（这段对话太密，还没触发）'}")

    # 单独验一下久不联系的场景
    print(f"\n  单独验：莉莉之后消失 5 天")
    t2 = 40.0
    for step in range(5):
        brain.tick(t2 + step * 24.0, 24.0)
    t2 += 5 * 24.0
    print(f"    {brain.face.sep_level.get('莉莉')}")
    print(f"    {brain.prompt_suffix('莉莉')}")
    print(f"\n{SEP}")


if __name__ == '__main__':
    main()
