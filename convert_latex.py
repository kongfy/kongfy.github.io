#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换 WordPress LaTeX 格式为标准 MathJax 格式
\[latex\]formula\[/latex\] -> $formula$ (行内)
\[latex\]\\displaystyle formula\[/latex\] -> $$formula$$ (行间)
"""
import os
import re
import glob

def convert_latex_in_file(filepath):
    """转换文件中的 LaTeX 格式"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 转换 WordPress LaTeX 格式为标准格式
    # \[latex\]...\[/latex\] -> $...$
    content = re.sub(
        r'\\\[latex\\\](.*?)\\\[/latex\\\]',
        r'$\1$',
        content
    )
    
    # 检查是否有数学公式，如果有，确保 front matter 中启用 mathjax
    has_math = bool(re.search(r'\$[^\$]+\$|\$\$[^\$]+\$\$', content))
    
    if has_math:
        # 检查 front matter 中是否已经有 mathjax 设置
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
    
    print("正在转换 WordPress LaTeX 格式到标准 MathJax 格式...\n")
    
    for filepath in glob.glob(os.path.join(posts_dir, '*.md')):
        if convert_latex_in_file(filepath):
            modified_count += 1
            print(f"✓ 转换: {os.path.basename(filepath)}")
    
    print(f"\n转换完成！共处理了 {modified_count} 个文件")
    print("\n注意：请检查转换后的文章，确保数学公式显示正常。")

if __name__ == '__main__':
    main()

