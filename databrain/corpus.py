# -*- coding: utf-8 -*-
"""
真实语料适配器

把 2 号记忆库里的 3,147 条真实事件（2021-12-29 → 2026-09-14，跨度 4.7 年）
转成能驱动 DataBrain 的刺激序列。

数据源：D:\\train\\memory\\mem2\\events.jsonl
  每行：{"date","month","peer","room","text","topics"}

为什么不直接用合成场景：
    合成的场景是我编的，它的"日常平淡"是我猜的。真实语料里
    大部分消息本来就是琐碎的 —— 这个分布本身就是最有价值的输入，
    因为"大部分时间很平淡"正是一个人不显得奇怪的关键。

分类方法：关键词规则 + 话题加权。规则来自原内分泌引擎的关键词表并做了扩展。
"""

import json
import os
import re
import sys
from datetime import datetime

# 语料路径（审查D1修复）：不再硬编码某台机器的 Windows 绝对路径。
# 优先级：环境变量 DATABRAIN_EVENTS > 包内 knowledge/events.jsonl > 老路径常量。
_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_EVENTS = os.environ.get(
    'DATABRAIN_EVENTS',
    os.path.join(_HERE, '..', 'knowledge', 'events.jsonl'))
DEFAULT_PEOPLE = os.environ.get(
    'DATABRAIN_PEOPLE',
    os.path.join(_HERE, '..', 'knowledge', 'people.json'))

# ------------------------------------------------------------
# 刺激分类规则：命中越靠前优先级越高
# ------------------------------------------------------------
RULES = [
    ('crisis',      ['想死', '不想活', '自杀', '活不下去', '结束算了', '没意思了']),
    ('betrayal',    ['背刺', '背叛', '骗我', '出卖', '背后说我', '两面三刀', '甩锅给我']),
    ('humiliation', ['丢人', '丢脸', '嘲笑', '笑话我', '看不起', '羞辱', '嘲讽', '菜鸡',
                     '就这水平', '废物一个']),
    ('rejection',   ['分手', '别联系了', '不想理你', '拉黑', '绝交', '别找我', '走开',
                     '不要你了', '不跟你']),
    ('loss',        ['走了', '去世', '离开我', '没了', '失去', '散了']),
    ('conflict',    ['吵架', '吵起来', '生气', '气死', '火大', '翻脸', '骂', '滚',
                     '你什么意思', '发火', '急眼', '闹']),
    ('criticism',   ['菜', '差劲', '不行啊', '太差', '废物', '垃圾', '没用', '失望',
                     '拉胯', '你不行', '水平不行']),
    ('neglect',     ['不理我', '已读不回', '不回我', '消失', '去哪了', '人呢',
                     '怎么不说话', '忙吗', '在吗']),
    ('loneliness',  ['一个人', '孤独', '没人', '好无聊', '没人陪', '空']),
    ('provocation', ['就这', '不过如此', '一般吧', '也不怎么样', '还行吧', '太弱',
                     '不够', '你敢吗', '吹牛']),
    ('reconciliation', ['和好', '不生气了', '没事了', '说开了', '解开', '误会解开',
                        '别往心里去', '翻篇']),
    ('apology',     ['对不起', '抱歉', '我错了', 'sorry', '不好意思', 'sorry啊',
                     '我的问题', '怪我']),
    ('gratitude',   ['谢谢', '感谢', '谢了', '多亏', '辛苦了', '谢谢你', '谢啦']),
    ('affection',   ['喜欢你', '爱你', '想你', '想你了', '抱', '亲', '离不开',
                     '舍不得', '在乎你', '在意你', '心疼']),
    ('shared_joy',  ['哈哈', '笑死', '太好笑', '好玩', '开心', '快乐', '赢了', '成了',
                     '厉害了', '绝了', '牛啊', '爽']),
    ('praise',      ['厉害', '优秀', '棒', '牛', '强', '赞', '不错', '可以的',
                     '好样的', '靠谱', '聪明', '厉害啊']),
    ('playful_neg', ['笨蛋', '傻瓜', '白痴', '讨厌', '臭', '哼', '切', '狗', '杂鱼',
                     '破防', '急了', '绷']),
    ('curiosity',   ['为什么', '怎么', '真的吗', '啥', '咋', '什么意思', '会不会',
                     '是不是', '能不能']),
]

# 话题 → 可能涉及的刺激（弱信号，只在关键词没命中时兜底）
# 修复（审查C2）：原表映射到 'vulnerability' —— 一个不存在于
# STIMULUS_VA / STIMULUS_HORMONE 的刺激名，会静默退化成 (0.5,0.3)，
# 等于"健康话题 = 无情绪中性"，比承认未知更糟。改为显式可用类别。
TOPIC_HINT = {
    '情感': 'affection',
    '成绩考试': 'curiosity',
    '工作实习': 'neutral',
    '健康': 'neutral',       # 修复：不可知就不猜。原版映射 vulnerability(不存在)，
                             # 中途改 loneliness 又等于断言"生病=孤独"，同样是猜。
    '钱': 'neutral',
}

NEG_TAIL = ['不', '没', '难', '烦', '累', '崩', '输', '糟', '惨', '急', '怕', '慌']
POS_TAIL = ['好', '棒', '成', '行', '可以', '哈哈', '嘻嘻', '嘿嘿', '赢', '稳']


def classify(text, topics=None):
    """
    返回 (stim, intensity)。
    intensity 由文本的语气强度决定：感叹号、叠词、长度等。
    """
    t = (text or '').strip()
    if not t:
        return 'mundane', 0.2

    for stim, kws in RULES:
        for kw in kws:
            if kw in t:
                return stim, _intensity(t)
    # 兜底：按话题
    for tp in (topics or []):
        if tp in TOPIC_HINT:
            return TOPIC_HINT[tp], 0.35
    # 再兜底：看句尾情绪
    tail = t[-6:]
    if any(x in tail for x in NEG_TAIL):
        return 'neutral', 0.30
    if any(x in tail for x in POS_TAIL):
        return 'mundane', 0.30
    return 'mundane', 0.25


def _intensity(t):
    """语气强度：感叹号、重复、长度都会放大。"""
    s = 0.6
    s += 0.12 * min(3, t.count('！') + t.count('!'))
    s += 0.08 * min(3, t.count('？') + t.count('?'))
    # 叠字/重复（"好好好"）说明情绪强
    if re.search(r'(.)\1{2,}', t):
        s += 0.10
    if len(t) > 40:
        s += 0.08
    return max(0.25, min(1.0, round(s, 3)))


# ------------------------------------------------------------
# 载入
# ------------------------------------------------------------
def load_events(path=DEFAULT_EVENTS, max_events=None, min_year=None):
    """读出事件并按时间排序。返回 [{ts, date, peer, text, topics, hour}]

    修复（审查C1）：优先解析事件自带的时间（"time"/"datetime"/"hour" 字段），
    解析得到就 hour=真实钟点、并把 ts 精确到该时刻；解析不到 hour=None，
    下游一律按"时刻不可信"处理（昼夜调制取全天均值、不伪造场景归属）。
    原版用 `hour = int(delta) % 24` 把"第几小时的消息"当成钟点 ——
    那是编造的数据，而它驱动了节律、场景、分离焦虑全套机制。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到事件库: {path}")
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            d = e.get('date')
            if not d:
                continue
            if min_year and d[:4] < str(min_year):
                continue
            try:
                dt = datetime.strptime(d, '%Y-%m-%d')
            except ValueError:
                continue
            # 可选的日内时刻（有就信，没有就 None）
            hour = _extract_hour(e)
            if hour is not None:
                dt = dt.replace(hour=int(hour), minute=int(round((hour % 1) * 60)))
            out.append({'ts': dt, 'date': d, 'peer': e.get('peer') or '未知',
                        'text': e.get('text') or '', 'topics': e.get('topics') or [],
                        'hour': hour})
    out.sort(key=lambda x: x['ts'])
    if max_events:
        out = out[:max_events]
    return out


def _extract_hour(e):
    """从事件里尽力抠出一个 0-24 的真实钟点；抠不到返回 None（绝不编造）。"""
    dt = e.get('datetime') or e.get('timestamp') or e.get('time')
    if isinstance(dt, str):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M', '%H:%M:%S', '%H:%M'):
            try:
                p = datetime.strptime(dt.strip(), fmt)
                return p.hour + p.minute / 60.0
            except ValueError:
                continue
    h = e.get('hour')
    if isinstance(h, (int, float)) and 0 <= h < 24:
        return float(h)
    return None


def load_people(path=DEFAULT_PEOPLE):
    """返回 {姓名: {'relation':..., 'weight':..., 'msgs':...}}

    二轮审查补充：weight 直接乘在事件强度上
    （inten * (0.75 + 0.05 * weight)），所以这个文件读没读到、
    格式对不对，会显著改变情节记忆能不能成型。
    原版格式不对时静默返回 {}，等于把整条语料的强度统一削到 75%，
    跑出来的现象是"一个情节记忆都没有"，而日志里一句提示都没有。
    现在：兼容 {name: {...}} 扁平写法；解析失败/文件缺失都明确警告。

    ⚠ weight 的量纲是 **0~10**（不是 0~1）：乘数是 0.75 + 0.05*weight，
    weight=5 才等于"不缩放"，weight=10 是 1.25 倍。
    把它当 0~1 的归一化权重填（本项目踩过的坑），全体乘数落在 0.75~0.80，
    显著性门槛 0.42 就再也够不到 —— 现象是 episodic 恒为 0，
    社会化测试里"负性记忆消退"变成无数据。
    """
    if not os.path.exists(path):
        sys.stderr.write(f"[corpus] 警告：人物权重文件不存在：{path}"
                         f"（事件强度将统一按 0.75 计算）\n")
        return {}
    try:
        p = json.load(open(path, 'r', encoding='utf-8'))
    except Exception as e:
        sys.stderr.write(f"[corpus] 警告：人物权重文件解析失败：{e}\n")
        return {}
    # 扁平写法：{"阿澈": {"role": "friend", "weight": 0.7}}
    if isinstance(p, dict) and 'edges' not in p and 'nodes' not in p:
        return {k: {'relation': v.get('role', v.get('relation', '')),
                    'weight': v.get('weight', 0),
                    'msgs': v.get('msgs', 0)}
                for k, v in p.items() if isinstance(v, dict)}
    if not isinstance(p, dict):
        sys.stderr.write("[corpus] 警告：人物权重文件结构不是对象，已忽略\n")
        return {}
    rel = {}
    for e in p.get('edges', []):
        if e.get('from') == '本人':
            rel[e['to']] = {'relation': e.get('type', ''),
                            'weight': e.get('weight', 0),
                            'share': e.get('share', 0)}
    for n in p.get('nodes', []):
        if n.get('is_me'):
            continue
        rel.setdefault(n['id'], {'relation': n.get('relation', ''),
                                 'weight': n.get('weight', 0),
                                 'msgs': n.get('msgs', 0)})
    return rel


def to_stimulus_stream(events, people=None, top_peers=None):
    """
    转成引擎能吃的序列：[{t_hours, subject, stim, text, intensity, hour}]
    t_hours 是相对第一个事件的小时数（含一天内的时刻估计）。
    hour: 真实钟点或 None（审查C1 —— 原版伪造的 int(delta)%24 已删除，
    None 会让引擎走"均值昼夜 + 无场景"的可信分支）。
    """
    if not events:
        return [], 0.0
    t0 = events[0]['ts']
    stream = []
    for e in events:
        delta = (e['ts'] - t0).total_seconds() / 3600.0
        stim, inten = classify(e['text'], e['topics'])
        rel_w = 0.0
        if people and e['peer'] in people:
            rel_w = people[e['peer']].get('weight', 0)
        # 关系越亲近，同一句话的分量越重
        # 三轮审查（N7）：weight 来自用户手写的 people.json，是外部输入。
        # -Infinity 这类值会一路乘进 intensity，最终写进发布 JSON，
        # 变成浏览器 JSON.parse 直接报错的非法字面量。这里夹紧并要求有限。
        try:
            w = float(rel_w)
            if w != w or w in (float('inf'), float('-inf')):
                raise ValueError('non-finite')
            w = max(0.0, min(10.0, w))
        except (TypeError, ValueError):
            w = 0.0
        inten = min(1.0, inten * (0.75 + 0.05 * w))
        if inten != inten or inten in (float('inf'), float('-inf')):
            inten = 0.25
        stream.append({'t_hours': delta, 'subject': e['peer'], 'stim': stim,
                       'text': e['text'], 'intensity': round(inten, 3),
                       'hour': e.get('hour'), 'date': e['date'],
                       'topics': e['topics']})
    # 注意：秒 → 天要除 86400。写成了 /24 会算出 1.7 万年这种天文数字。
    return stream, (events[-1]['ts'] - t0).total_seconds() / 86400.0


def filter_top_peers(stream, n=5):
    """只保留最常出现的 n 个人，避免长尾把图弄乱。"""
    from collections import Counter
    c = Counter(s['subject'] for s in stream)
    keep = {k for k, _ in c.most_common(n)}
    return [s for s in stream if s['subject'] in keep], keep
