#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复斜体格式：将 _word_ 转换为 *word*
因为在某些情况下下划线格式的斜体可能无法正确渲染
"""
import os
import re
import glob

def fix_italic_in_file(filepath):
    """修复文件中的斜体格式"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 将 _word_ 格式转换为 *word*
    # 使用正则表达式匹配 _..._ 但避免匹配数学公式中的下标
    # 匹配条件：_ 前后不是字母数字，中间是字母、数字、连字符等
    # 排除在代码块、行内代码和数学公式中的情况
    
    # 先保护代码块和行内代码
    code_blocks = []
    inline_codes = []
    math_formulas = []
    
    # 保护三反引号代码块
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"
    
    content = re.sub(r'```[\s\S]*?```', save_code_block, content)
    
    # 保护行内代码
    def save_inline_code(match):
        inline_codes.append(match.group(0))
        return f"___INLINE_CODE_{len(inline_codes)-1}___"
    
    content = re.sub(r'`[^`]+?`', save_inline_code, content)
    
    # 保护数学公式
    def save_math(match):
        math_formulas.append(match.group(0))
        return f"___MATH_{len(math_formulas)-1}___"
    
    content = re.sub(r'\$\$[\s\S]*?\$\$', save_math, content)
    content = re.sub(r'\$[^\$]+?\$', save_math, content)
    
    # 现在转换 _word_ 为 *word*
    # 匹配 _..._ 其中 ... 不包含空格和换行符，且前后不是下划线
    content = re.sub(
        r'(?<![_\w])_([a-zA-Z0-9\-]+(?:\s+[a-zA-Z0-9\-]+)*)_(?![_\w])',
        r'*\1*',
        content
    )
    
    # 恢复代码块
    for i, block in enumerate(code_blocks):
        content = content.replace(f"___CODE_BLOCK_{i}___", block)
    
    # 恢复行内代码
    for i, code in enumerate(inline_codes):
        content = content.replace(f"___INLINE_CODE_{i}___", code)
    
    # 恢复数学公式
    for i, formula in enumerate(math_formulas):
        content = content.replace(f"___MATH_{i}___", formula)
    
    # 只有在内容有变化时才写入
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    posts_dir = '/Users/kongfy/blog/_posts'
    
    modified_count = 0
    
    print("正在修复斜体格式 (_word_ → *word*)...\n")
    
    for filepath in glob.glob(os.path.join(posts_dir, '*.md')):
        if fix_italic_in_file(filepath):
            modified_count += 1
            print(f"✓ 修复: {os.path.basename(filepath)}")
    
    print(f"\n修复完成！共处理了 {modified_count} 个文件")

if __name__ == '__main__':
    main()

