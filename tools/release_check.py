#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布前自检：审 zip 容器本体，而不是审工作树。

第三轮的教训（见 docs/review_v3.md §1 与 N15）：前两轮审的是"代码跑起来
对不对"，而真正发出去的是 **zip**。发出去的东西有两类缺陷是代码审查在结构上
看不见的：

  1) 容器元数据 —— 权限位、文件名编码标志、路径形态、构建残渣；
  2) 内容里的隐私指纹 —— 只能从私人语料算出的那组数字。

这个脚本把这两类固定成可重跑的判据。

**判据一律写成字符类**（`17[2]0` 而不是那个四位数）。这条不是洁癖：
第一版我在注释里"举例说明"写了原值，结果这个检查文件自己进了包、
自己被自己判成 FAIL —— 一个自检工具如果自身的存在会污染它的结论，
它给出的"通过"就没有意义。同理，**真名列表不进发布包**（见 --names-file）。

用法：
    # 发布包
    python3 tools/release_check.py ../pkg/databrain_public_*.zip --mode public
    # 自用包（legacy 原始数据 / 一轮报告 / PRIVATE_README 允许含敏感内容）
    python3 tools/release_check.py ../pkg/databrain_private_*.zip --mode private \\
        --names-file /你的/私人名.txt

退出码 0 = 通过；1 = 有问题（逐条打印，不做静默过滤）。
"""
import argparse
import re
import sys
import zipfile

# --- 判据 -----------------------------------------------------------------
# 构建机/沙盒绝对路径。字符类写法，本文件不会匹配到自己。
PATH_PATTERNS = [
    r'/ap[p]/',
    r'/mn[t]/',
    r'/r[o]ot/',
    r'upl[o]ads/',
    r'r[e]view/(src|pkg)/',
    r'/t[m][p]/(probe|n13|r3)',          # 我这台机器上的临时验证目录
    r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]([Uu]sers|[Hh]ome)[\\/]',   # 盘符形态（含 MSYS 的 c:/）
]
# 最后一条是补漏：前六条只写 Unix 形态，Windows 构建机那种
# 「盘符 + 冒号 + 斜杠 + 用户目录」的绝对路径因此躲过了四轮审查
# （公开包里已清掉，但判据不补上，下一轮还会漏）。
# 前置 lookbehind 要求盘符字母左侧不是字母/数字，挡掉大写协议名这类
# 「字母紧邻冒号」的假阳性；盘符允许大小写，覆盖 Git-Bash 挂载形态。
# 注意：本条注释刻意不把泄露形态拼成一个完整的可匹配字符串 ——
# 判据文件的注释一旦写出实例，这个文件会把自己判成 FAIL。

# 私人语料指纹：跨度 / 事件数 / 社会化总分 / 认定区间。
# 数字护栏：产物里 17208.0 这种引擎生成的时刻不该算命中，
# prose 里"（那个四位数）天"必须算。
FINGER_CLASSES = [
    ('跨度', re.compile(r'(?<![\d.])17[2]0(?![\d.])')),
    ('事件数', re.compile(r'30[3]0\s*件')),
    ('社会化总分', re.compile(r'社会化\s*9[8](?:\.0|\.2)')),
    ('认定区间', re.compile(r'0\.48[3]1\s*~\s*0\.48[4]5')),
]

# 只有"散文/代码"类文件按单类命中就判泄露；
# 生成的 .json 数据体里同值巧合很多，要求**两类以上同时**出现才判，
# 因为指纹的威胁来自组合（跨度+事件数+人数足以框定一个人）。
PROSE_EXT = ('.md', '.py', '.js', '.html', '.jsonl', '.txt')

# 自用包里允许含敏感内容的位置（legacy 原始数据 / 一轮报告 / 自用说明）
PRIVATE_OK = ('.private/legacy/', 'review_v1', 'PRIVATE_README')

# 发布包条目黑名单
PUBLIC_FORBIDDEN = ('.private/', 'PRIVATE_README', 'review_v1',
                    '/web/real.json', '/web/compare.json')

# 人名判据：名单**只能**由 --names-file 从包外传入。
# 第二版的我在这一行里内联了演示语料的虚构名，结果这个工具自己进了包、
# 自己把自己判成 64 条 FAIL —— 判据写死进被检查物，等于既当裁判又当运动员。
# 真名更不可能内联：那等于把要保护的东西写进保护工具里发出去。


def _load_names(path):
    if not path:
        return []
    with open(path, encoding='utf-8') as f:
        return [x.strip() for x in f if x.strip() and not x.startswith('#')]


def check(zpath, mode, extra_names):
    problems, stats = [], {'files': 0, 'bytes': 0, 'text': 0, 'binary': 0,
                           'notes': []}
    zf = zipfile.ZipFile(zpath)
    infos = [i for i in zf.infolist() if not i.is_dir()]
    stats['files'] = len(infos)

    for i in infos:
        name = i.filename
        data = zf.read(name)              # 读全量 = 顺带校验 CRC
        stats['bytes'] += len(data)
        is_prose = name.endswith(PROSE_EXT)
        # 自用包里这几处位置本来就装私密数据，内容级判据对它们不适用
        exempt = mode == 'private' and any(a in name for a in PRIVATE_OK)

        # ---- 容器层（对两包、对所有文件都判）----
        if name.startswith('/') or '..' in name.split('/') or '\\' in name:
            problems.append(f'[容器/危险路径] {name}')
        bits = (i.external_attr >> 16) & 0o777
        if bits != 0o644:
            problems.append(f'[容器/权限位] {oct(bits)} != 0644：{name}')
        if not name.isascii() and not (i.flag_bits & 0x800):
            problems.append(f'[容器/编码] 非 ASCII 文件名缺 UTF-8 标志：{name}')
        if '__pycache__' in name or name.endswith(('.pyc', '.pyo')):
            problems.append(f'[容器/残渣] {name}')
        if mode == 'public':
            for f in PUBLIC_FORBIDDEN:
                if f in '/' + name:
                    problems.append(f'[发布/多余条目] 含 {f}：{name}')

        # ---- 内容层 ----
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            stats['binary'] += 1
            continue
        stats['text'] += 1

        for pat in PATH_PATTERNS:
            if re.search(pat, text) and not (exempt and not is_prose):
                if exempt:
                    stats['notes'].append(f'{name} 含构建机路径（自用包内，允许）')
                else:
                    problems.append(f'[泄露/构建机路径] {pat} → {name}')

        if not is_prose and not exempt:
            # 生成产物：要求两类以上指纹同时出现才判（见 FINGER_CLASSES 注释）
            hit = [lbl for lbl, rx in FINGER_CLASSES if rx.search(text)]
            if len(hit) >= 2:
                problems.append(f'[泄露/语料指纹组合] {hit} → {name}')
            elif hit:
                stats['notes'].append(f'{name}: 单类巧合值 {hit[0]}（产物内，已核对）')
        elif not exempt:
            for lbl, rx in FINGER_CLASSES:
                if rx.search(text):
                    problems.append(f'[泄露/语料指纹] {lbl} → {name}')

        for n in extra_names:
            if n and n in text and not exempt:
                problems.append(f'[泄露/人名] {n} → {name}')

    if zf.testzip() is not None:
        problems.append('[容器/CRC] testzip() 报错')
    return problems, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('zip_path')
    ap.add_argument('--mode', choices=['public', 'private'], default='public')
    ap.add_argument('--names-file', default='',
                    help='每行一个不得出现的真实人名；不写进包，只在检查时传入')
    a = ap.parse_args()
    extra = _load_names(a.names_file) if a.names_file else []
    problems, s = check(a.zip_path, a.mode, extra)
    print(f'release_check：{a.zip_path}（mode={a.mode}，'
          f'外部人名 {len(extra)} 个）')
    print(f'  常规文件 {s["files"]} 个 · 解压 {s["bytes"]:,} B · '
          f'文本 {s["text"]} / 二进制 {s["binary"]}')
    for n in s['notes']:
        print(f'  注：{n}')
    if problems:
        print(f'  结果：FAIL（{len(problems)} 条）')
        for p in problems:
            print('   ', p)
        return 1
    print('  结果：PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
