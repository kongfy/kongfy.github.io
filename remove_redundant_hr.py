#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除标题后面紧跟的 * * * 分割线
因为 Minimal Mistakes 主题会自动为标题添加样式，分割线是多余的
"""
import os
import re
import glob

def remove_redundant_hr(filepath):
    """移除标题后紧跟的分割线"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 匹配模式：## 标题\n\n* * *\n
    # 替换为：## 标题\n\n
    content = re.sub(
        r'(^#{1,6}\s+.+\n)\n\* \* \*\n',
        r'\1\n',
        content,
        flags=re.MULTILINE
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
    
    print("正在移除标题后的冗余分割线...\n")
    
    for filepath in glob.glob(os.path.join(posts_dir, '*.md')):
        if remove_redundant_hr(filepath):
            modified_count += 1
            print(f"✓ 修改: {os.path.basename(filepath)}")
    
    print(f"\n修改完成！共处理了 {modified_count} 个文件")

if __name__ == '__main__':
    main()

