#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换 WordPress 行内 LaTeX 格式
$latex formula$ -> $formula$
"""
import os
import re
import glob

def convert_inline_latex(filepath):
    """转换文件中的行内 LaTeX 格式"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 转换 $latex ...$ 为 $...$
    # 使用非贪婪匹配，避免跨多个公式匹配
    content = re.sub(
        r'\$latex\s+([^$]+?)\$',
        r'$\1$',
        content
    )
    
    # 确保文章有 mathjax: true 设置
    if '$' in content:
        front_matter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if front_matter_match:
            front_matter = front_matter_match.group(1)
            if 'mathjax:' not in front_matter:
                # 在 front matter 末尾添加 mathjax: true
                new_front_matter = front_matter.rstrip() + '\nmathjax: true\n'
                content = re.sub(
                    r'^---\n(.*?)\n---\n',
                    f'---\n{new_front_matter}---\n',
                    content,
                    count=1,
                    flags=re.DOTALL
                )
    
    # 只有在内容有变化时才写入
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    posts_dir = '/Users/kongfy/blog/_posts'
    
    modified_count = 0
    
    print("正在转换 WordPress 行内 LaTeX 格式 ($latex ...$)...\n")
    
    for filepath in glob.glob(os.path.join(posts_dir, '*.md')):
        if convert_inline_latex(filepath):
            modified_count += 1
            print(f"✓ 转换: {os.path.basename(filepath)}")
    
    print(f"\n转换完成！共处理了 {modified_count} 个文件")

if __name__ == '__main__':
    main()

