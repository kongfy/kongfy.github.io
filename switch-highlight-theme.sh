#!/bin/bash
# 代码高亮主题快速切换脚本

THEME=$1

if [ -z "$THEME" ]; then
  echo "📚 使用方法: ./switch-highlight-theme.sh [主题名称]"
  echo ""
  echo "🎨 可用主题："
  echo ""
  echo "深色主题（推荐）："
  echo "  • monokai.sublime  - Sublime Text 经典配色 ⭐"
  echo "  • monokai         - Monokai 配色"
  echo "  • gruvbox.dark    - Gruvbox 深色（护眼）"
  echo "  • github.dark     - GitHub 深色模式"
  echo "  • base16.monokai.dark - Base16 Monokai"
  echo ""
  echo "浅色主题："
  echo "  • github          - GitHub 风格 ⭐"
  echo "  • github.light    - GitHub 浅色"
  echo "  • gruvbox.light   - Gruvbox 浅色"
  echo "  • base16.light    - Base16 浅色"
  echo ""
  echo "示例："
  echo "  ./switch-highlight-theme.sh monokai.sublime"
  echo "  ./switch-highlight-theme.sh github"
  exit 1
fi

# 检查主题是否存在
if ! rougify style "$THEME" > /dev/null 2>&1; then
  echo "❌ 错误: 主题 '$THEME' 不存在"
  echo "💡 运行 'rougify help style' 查看所有可用主题"
  exit 1
fi

# 生成CSS
echo "🎨 正在生成 $THEME 主题..."
rougify style "$THEME" > assets/css/syntax.css

if [ $? -eq 0 ]; then
  echo "✅ 成功切换到 $THEME 主题"
  echo "🔄 请重启 Jekyll 服务器以查看效果："
  echo "   bundle exec jekyll serve"
else
  echo "❌ 生成失败"
  exit 1
fi

