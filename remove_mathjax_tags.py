#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除 WordPress 的 [mathjax][/mathjax] 标记
"""
import os
import glob

def remove_mathjax_tags(filepath):
    """删除文件中的 [mathjax][/mathjax] 标记"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for line in lines:
        # 跳过包含 [mathjax][/mathjax] 的行
        if r'\[mathjax\]\[/mathjax\]' in line or '[mathjax][/mathjax]' in line:
            modified = True
            continue
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    posts_dir = '/Users/kongfy/blog/_posts'
    
    modified_count = 0
    
    print("正在删除 WordPress [mathjax][/mathjax] 标记...\n")
    
    for filepath in glob.glob(os.path.join(posts_dir, '*.md')):
        if remove_mathjax_tags(filepath):
            modified_count += 1
            print(f"✓ 清理: {os.path.basename(filepath)}")
    
    print(f"\n清理完成！共处理了 {modified_count} 个文件")

if __name__ == '__main__':
    main()
