#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复斜体格式：将 _word_ 转换为 *word*
保护数学公式不被修改
"""
import re

filepath = '/Users/kongfy/blog/_posts/2016-05-25-分布式共识consensus：viewstamped、raft及paxos.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 保存原始数学公式，包括其中的下划线
# \\(...\\) 格式
math_inline = re.findall(r'\\\(.*?\\\)', content, re.DOTALL)
# $$...$$ 格式  
math_block = re.findall(r'\$\$.*?\$\$', content, re.DOTALL)
# $...$ 格式
math_simple = re.findall(r'\$[^\$\n]+?\$', content)

# 合并所有数学公式
all_math = []
math_map = {}

# 替换所有数学公式为占位符
for i, match in enumerate(re.finditer(r'(\\\(.*?\\\)|\$\$.*?\$\$|\$[^\$\n]+?\$)', content, re.DOTALL)):
    placeholder = f'___MATHFORMULA{i}___'
    math_map[placeholder] = match.group(0)
    content = content.replace(match.group(0), placeholder, 1)

# 现在转换 _word_ 格式，不会影响数学公式
# 匹配模式：_开头，中间是字母数字和连字符（可能有空格），_结尾
content = re.sub(
    r'(?<![_\\])_([a-zA-Z][a-zA-Z0-9\-]*(?:\s+[a-zA-Z0-9\-]+)*)_(?![_\\])',
    r'*\1*',
    content
)

# 恢复所有数学公式
for placeholder, formula in math_map.items():
    content = content.replace(placeholder, formula)

if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 统计修改
    underscore_count = original.count('_')
    asterisk_count = content.count('*')
    print(f"✓ 修复完成")
    print(f"原文下划线: {underscore_count}")
    print(f"修改后星号: {asterisk_count}")
else:
    print("无需修改")

