#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""前端转义静态审计（可重跑，替代"我数过了"这种口头保证）。

背景：语料里的人名/链条文本是对端可控字符串，直接进 innerHTML 就是存储型 XSS
（审查 A2 / N8）。人工点数会漂，所以这里用脚本断言两件事：

  1. 携带"语料可控字段"的模板插值 `${...}` 必须被 esc() 包裹；
  2. 不存在内联事件处理器（onclick=/onerror=…）里的插值。

"语料可控字段"取自 review_v2/v3 里逐条确认过的注入面：
subject / stim / text / detail / hits / id / bucket_id / note / label /
theme_key / bucket / name / action。

用法：
    python3 tools/audit_esc.py            # 打印审计结果
    python3 tools/audit_esc.py --quiet     # 只在有问题时无声退出非零

退出码 0 = 干净；1 = 发现未转义插值或内联事件插值。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'web', 'index.html')

# 语料可控字段名（这些值可能带人名/原文，进 DOM 前必须 esc()）
CONTROLLED = ('subject', 'stim', 'text', 'detail', 'hits', 'id',
              'bucket_id', 'note', 'label', 'theme_key', 'bucket',
              'name', 'action')

# 数字/布尔字段：来自引擎自己算出来的量，不是语料字符串。
# 为免误报，这些只在"直接 .字段 且没方法链"时才要求转义。
PURE_NUMERIC_HINTS = ('.length',)


def strip_comments(src):
    """去掉 /* */ 与 // 注释，避免把文档注释里讲的 esc() 也数进调用点。

    保留换行与行宽无关的空位，**行号必须与原文件一致**，
    否则报出来的 L 行号会误导人。
    """
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            j = n if j == -1 else j + 2
            out.append(''.join(ch if ch == '\n' else ' ' for ch in src[i:j]))
            i = j
        elif src.startswith('//', i):
            j = src.find('\n', i)
            j = n if j == -1 else j
            out.append(' ' * (j - i))
            i = j
        else:
            out.append(src[i]); i += 1
    return ''.join(out)


def find_interpolations(code):
    """返回 [(行号, 整段 ${...} 内容, 该行源码), ...]。

    模板字符串里 `${...}` 可以嵌套花括号（如三元、对象访问），
    用计数配对而不是贪婪正则来找闭合位置。
    """
    hits = []
    line = 1
    i = 0
    n = len(code)
    while i < n - 1:
        c = code[i]
        if c == '\n':
            line += 1
        if c == '$' and code[i + 1] == '{':
            depth = 0
            j = i
            start_line = line
            seg = []
            while j < n:
                ch = code[j]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        break
                seg.append(ch)
                j += 1
            body = ''.join(seg)[2:]  # 去掉起始 ${
            hits.append((start_line, body))
            line = code.count('\n', i, j + 1) + start_line
            i = j + 1
            continue
        i += 1
    return hits


def uses_controlled_field(body):
    for f in CONTROLLED:
        # 只认 ".field" 形式的属性访问，避免把 label 这种单词变量漏判
        if re.search(r'\.' + re.escape(f) + r'\b', body):
            return f
    return None


def wrapped_by_esc(body):
    """插值里凡是碰到受控字段的地方，是不是都落在某个 esc(...) 内部。

    简化但保守的判定：把插值里出现的每个 `esc(` 视为一段安全区，
    要求每个受控字段 `.field` 都出现在某个 esc( 与其配对 ) 之间。
    只要有一个受控字段在 esc( 之外，就判未转义。
    """
    fields = []
    for m in re.finditer(r'\.(' + '|'.join(CONTROLLED) + r')\b', body):
        fields.append(m.start())
    if not fields:
        return True
    safe = [False] * len(body)
    for m in re.finditer(r'(?<![\w$.])esc\(', body):
        depth = 0
        j = m.end() - 1
        k = j
        end = len(body)
        while k < end:
            ch = body[k]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        for p in range(m.start(), min(k + 1, end)):
            safe[p] = True
    return all(safe[p] for p in fields)


def main():
    quiet = '--quiet' in sys.argv
    src = io.open(HTML, encoding='utf-8').read()
    code = strip_comments(src)
    src_lines = src.split('\n')

    problems = []
    total_esc_calls = 0
    esc_lines = set()
    # 在"去掉注释后的代码"上数，注释里讲的 esc() 不算调用点。
    # strip_comments 保留换行，所以行号与原文件仍可对应。
    for i, l in enumerate(code.split('\n'), 1):
        c = len(re.findall(r'(?<![\w$.])esc\(', l))
        if c:
            total_esc_calls += c
            esc_lines.add(i)

    for ln, body in find_interpolations(code):
        f = uses_controlled_field(body)
        if f and not wrapped_by_esc(body):
            problems.append((ln, f, body.strip()[:70]))

    # 内联事件处理器里不许有插值：on<event>="${...}" 一律拒绝
    inline = []
    for m in re.finditer(r'\bon[a-z]+\s*=\s*"[^"]*\$\{', code, re.IGNORECASE):
        ln = code.count('\n', 0, m.start()) + 1
        inline.append((ln, m.group(0)[-40:]))

    if not quiet:
        print(f"审计对象：{HTML}")
        print(f"esc() 定义存在：{'是' if 'const esc' in code else '否'}")
        print(f"esc() 调用：{len(esc_lines)} 行 / {total_esc_calls} 处")
        print(f"语料可控字段清单：{', '.join(CONTROLLED)}")
        print("-" * 60)
        if problems:
            print(f"未转义插值：{len(problems)} 处")
            for ln, f, body in problems:
                print(f"  L{ln}: .{f} 在 esc() 之外 -> {body}")
        else:
            print("未转义插值：NONE")
        if inline:
            print(f"内联事件插值：{len(inline)} 处")
            for ln, frag in inline:
                print(f"  L{ln}: {frag}")
        else:
            print("内联事件插值：NONE")

    return 1 if (problems or inline) else 0


if __name__ == '__main__':
    sys.exit(main())
