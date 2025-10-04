# 代码高亮主题配置指南

## 📝 概述

Jekyll 使用 Rouge 作为默认的语法高亮器。代码块的配色方案可以通过以下几种方式配置。

## 🎨 方法一：使用不同的主题皮肤（最简单）

代码块会自动继承主题皮肤的配色。编辑 `_config.yml`：

```yaml
minimal_mistakes_skin: "dark"  # 深色背景，代码高亮效果好
```

**推荐的皮肤选择：**
- **`"dark"`** - 深色主题，代码对比度高，适合长时间阅读
- **`"contrast"`** - 高对比度，代码非常醒目
- **`"default"`** - 传统浅色背景
- **`"neon"`** - 霓虹色，适合喜欢鲜艳色彩的读者

## 🎯 方法二：生成并使用 Rouge CSS 主题

### 1. 查看可用的 Rouge 主题

在终端运行：

```bash
rougify help style
```

可用的主题包括：
- **`base16`** - Base16 配色方案
- **`base16.dark`** / **`base16.light`** - Base16 深色/浅色
- **`base16.monokai`** - Monokai 风格
- **`base16.solarized`** - Solarized 配色
- **`colorful`** - 多彩配色
- **`github`** - GitHub 风格（最常见）
- **`gruvbox`** / **`gruvbox.light`** - Gruvbox 主题
- **`molokai`** - Molokai 配色
- **`monokai`** / **`monokai.sublime`** - Monokai 系列
- **`pastie`** - Pastie 风格
- **`thankful_eyes`** - 护眼配色

### 2. 生成主题 CSS 文件

选择一个主题（例如 `monokai`），生成 CSS：

```bash
# 进入项目目录
cd /Users/kongfy/blog

# 生成代码高亮 CSS（选择你喜欢的主题）
rougify style monokai > assets/css/syntax.css
```

**常用主题推荐：**

```bash
# GitHub 风格（浅色背景，适合白天阅读）
rougify style github > assets/css/syntax.css

# Monokai 风格（深色背景，经典编辑器配色）
rougify style monokai > assets/css/syntax.css

# Monokai Sublime（Sublime Text 编辑器配色）
rougify style monokai.sublime > assets/css/syntax.css

# Gruvbox（护眼配色）
rougify style gruvbox > assets/css/syntax.css
```

### 3. 在主题中引入 CSS

编辑 `assets/css/main.scss`，在文件末尾添加：

```scss
/* 导入自定义代码高亮主题 */
@import "syntax";
```

或者直接在文件中引入：

编辑 `_includes/head/custom.html`，添加：

```html
<!-- 自定义代码高亮主题 -->
<link rel="stylesheet" href="{{ '/assets/css/syntax.css' | relative_url }}">
```

## 🔧 方法三：自定义代码块样式

如果你想完全自定义，可以在 `assets/css/main.scss` 中添加自定义样式：

```scss
/* 自定义代码块样式 */
.highlight {
  background-color: #282c34;  /* 代码块背景色 */
  border-radius: 4px;         /* 圆角 */
  padding: 1em;               /* 内边距 */
  overflow-x: auto;           /* 横向滚动 */
  
  pre {
    margin: 0;
    background-color: transparent;
  }
  
  /* 关键字 */
  .k, .kd, .kn, .kp, .kr, .kt {
    color: #c678dd;  /* 紫色 */
  }
  
  /* 字符串 */
  .s, .s1, .s2, .sb, .sc, .sd, .se, .sh, .si, .sx {
    color: #98c379;  /* 绿色 */
  }
  
  /* 注释 */
  .c, .c1, .cm, .cp, .cs {
    color: #5c6370;  /* 灰色 */
    font-style: italic;
  }
  
  /* 函数名 */
  .nf, .fm {
    color: #61afef;  /* 蓝色 */
  }
  
  /* 数字 */
  .m, .mi, .mo, .mf, .mh {
    color: #d19a66;  /* 橙色 */
  }
}
```

## 📋 推荐配置

### 对于技术博客（当前推荐）：

1. **使用 `monokai.sublime` 主题**：
   ```bash
   rougify style monokai.sublime > assets/css/syntax.css
   ```

2. **或者使用 `github` 主题**（如果你喜欢浅色）：
   ```bash
   rougify style github > assets/css/syntax.css
   ```

3. **然后引入CSS**：在 `_includes/head/custom.html` 添加：
   ```html
   <link rel="stylesheet" href="{{ '/assets/css/syntax.css' | relative_url }}">
   ```

### 效果预览

不同主题在代码块中的效果：

**Monokai（深色）**：
- 背景：深灰色 (#272822)
- 关键字：粉色
- 字符串：黄色
- 注释：浅灰色

**GitHub（浅色）**：
- 背景：白色/浅灰
- 关键字：紫色
- 字符串：红色
- 注释：灰色

**Gruvbox（护眼）**：
- 背景：暖色调
- 整体配色柔和，适合长时间阅读

## 🔄 快速切换主题

创建一个脚本来快速切换代码高亮主题：

```bash
#!/bin/bash
# 保存为 switch-highlight-theme.sh

THEME=$1
if [ -z "$THEME" ]; then
  echo "Usage: ./switch-highlight-theme.sh [theme-name]"
  echo "Available themes: github, monokai, monokai.sublime, gruvbox, etc."
  exit 1
fi

rougify style "$THEME" > assets/css/syntax.css
echo "✅ Switched to $THEME theme"
```

使用方法：
```bash
chmod +x switch-highlight-theme.sh
./switch-highlight-theme.sh monokai
```

## 📖 更多资源

- Rouge 文档：https://github.com/rouge-ruby/rouge
- Minimal Mistakes 主题文档：https://mmistakes.github.io/minimal-mistakes/
- 在线预览 Rouge 主题：http://rouge.jneen.net/

## 💡 提示

1. 修改配置后记得重启 Jekyll 服务器：`bundle exec jekyll serve`
2. 清除缓存：`bundle exec jekyll clean`
3. 代码块记得指定语言以获得正确的语法高亮：
   ````markdown
   ```python
   def hello():
       print("Hello, World!")
   ```
   ````

