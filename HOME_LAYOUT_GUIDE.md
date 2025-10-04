# 主页 Layout 配置指南

## ✅ 已完成的配置

我已经为你创建了一个自定义的主页 layout，它能够正确识别并显示 `<!--more-->` 标记前的内容作为文章摘要。

### 📁 创建的文件

1. **`_layouts/home.html`** - 自定义主页布局
2. **`index.html`** - 主页配置（已更新）
3. **`assets/css/main.scss`** - 添加了主页样式（已更新）

## 🎨 主页功能特性

### 1. 文章摘要显示
- ✅ 自动识别 `<!--more-->` 标记
- ✅ 显示标记之前的完整内容（包括格式、加粗、链接等）
- ✅ 不会截断文字或破坏 Markdown 格式

### 2. 文章元信息
每篇文章显示：
- 📅 发布日期
- 📁 分类（可点击跳转到分类页面）
- 🏷️ 标签（可点击跳转到标签页面）

### 3. 阅读按钮
- 每篇文章摘要下方有"阅读全文"按钮
- 点击可跳转到完整文章页面

### 4. 分页功能
- 每页显示 10 篇文章（可在 `_config.yml` 中配置）
- 底部有分页导航（上一页/下一页）

## 📝 使用方法

### 在文章中添加 <!--more--> 标记

在你的文章中，在想要截断的位置添加 `<!--more-->` 标记：

```markdown
---
title: "我的文章标题"
date: 2024-01-01
categories: 
  - "技术"
tags:
  - "Jekyll"
---

这是文章的开头部分，会显示在主页的摘要中。

这段也会显示在摘要中。

<!--more-->

这是文章的详细内容，只有点击"阅读全文"后才能看到。

更多详细内容...
```

### 配置说明

#### 1. _config.yml 配置

```yaml
# 摘要分隔符（已配置）
excerpt_separator: "<!--more-->"

# 分页设置（已配置）
paginate: 10              # 每页显示的文章数
paginate_path: /page:num/ # 分页URL格式
```

#### 2. index.html 配置

```yaml
---
layout: home              # 使用自定义的 home layout
author_profile: true      # 显示作者信息侧边栏
entries_layout: list      # 列表布局（可选：grid）
pagination:
  enabled: true           # 启用分页
---
```

## 🎨 样式自定义

主页样式定义在 `assets/css/main.scss` 中，你可以根据需要调整：

### 调整文章标题大小

```scss
.archive__item-title {
  font-size: 1.5em;  // 修改这个值来调整标题大小
}
```

### 调整文章间距

```scss
.archive__item {
  margin-bottom: 2em;  // 修改文章之间的间距
}
```

### 调整摘要字体大小

```scss
.archive__item-excerpt {
  font-size: 1em;      // 修改摘要字体大小
  line-height: 1.7;    // 修改行高
}
```

### 修改"阅读全文"按钮样式

```scss
.archive__item-read-more {
  .btn {
    padding: 0.5em 1em;     // 按钮内边距
    font-size: 0.9em;       // 按钮字体大小
  }
}
```

## 🔧 高级配置

### 切换布局样式

在 `index.html` 中可以切换不同的布局样式：

```yaml
---
layout: home
entries_layout: list  # 选项：list（列表）或 grid（网格）
---
```

- **`list`**：传统的列表布局，显示完整摘要
- **`grid`**：网格布局，更紧凑的卡片式显示

### 修改每页文章数

在 `_config.yml` 中修改：

```yaml
paginate: 15  # 改为每页显示15篇文章
```

### 自定义摘要长度

如果不想使用 `<!--more-->` 标记，可以在文章的 Front Matter 中手动指定摘要：

```markdown
---
title: "文章标题"
excerpt: "这是手动指定的摘要内容"
---

文章正文...
```

## 📊 主页布局结构

```
主页 (index.html)
├── 使用 home layout (_layouts/home.html)
│   ├── 基于 archive layout
│   ├── 显示"最近文章"标题
│   ├── 文章列表循环
│   │   ├── 文章标题（链接）
│   │   ├── 元信息（日期、分类、标签）
│   │   ├── 文章摘要（<!--more--> 之前的内容）
│   │   └── "阅读全文"按钮
│   └── 分页导航
└── 样式 (assets/css/main.scss)
    ├── 文章列表项样式
    ├── 标题样式
    ├── 元信息样式
    ├── 摘要样式
    └── 按钮样式
```

## 🎯 效果预览

主页将显示如下结构：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
最近文章
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  分布式数据库事务故障恢复的原理与实践
  📅 2020-10-25  📁 关系型数据库, distributed-system
  
  关系数据库中的事务故障恢复并不是一个新问题，
  自70年代关系数据库诞生之后就一直伴随着数据库
  技术的发展...
  
  [阅读全文 »]
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  并发编程牛刀小试：seqlock
  📅 2017-04-18  🏷️ 并发编程
  
  在前文中介绍了用户态自旋锁的几种实现，
  本文将介绍一种读写场景下的无锁算法...
  
  [阅读全文 »]
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[← 上一页]  1  2  3  4  [下一页 →]
```

## 🔍 故障排查

### 问题1：摘要显示不正确

**检查：**
- 确认 `_config.yml` 中有 `excerpt_separator: "<!--more-->"`
- 确认文章中的标记是 `<!--more-->`（不要有空格）
- 重启 Jekyll 服务器：`bundle exec jekyll serve`

### 问题2：分页不工作

**检查：**
- 确认 `_config.yml` 中配置了 `paginate: 10`
- 确认 `plugins` 中包含 `jekyll-paginate`
- 确认主页文件名是 `index.html`（不是 `index.md`）

### 问题3：样式显示异常

**检查：**
- 清除 Jekyll 缓存：`bundle exec jekyll clean`
- 重新启动：`bundle exec jekyll serve`
- 检查浏览器控制台是否有 CSS 加载错误

## 🚀 启动网站

配置完成后，运行以下命令启动网站：

```bash
# 清除缓存
bundle exec jekyll clean

# 启动服务器（带热重载）
bundle exec jekyll serve --livereload

# 访问网站
# 打开浏览器访问：http://localhost:4000
```

## 📚 相关文档

- Jekyll 分页文档：https://jekyllrb.com/docs/pagination/
- Minimal Mistakes 主题文档：https://mmistakes.github.io/minimal-mistakes/
- Liquid 模板语法：https://shopify.github.io/liquid/

## 💡 提示

1. **所有文章都应该添加 `<!--more-->` 标记**，这样主页才能正确显示摘要
2. 建议在文章的前 2-3 段后添加标记，给读者足够的信息了解文章内容
3. 摘要部分可以包含 Markdown 格式（加粗、链接、代码等），都会正确渲染
4. 修改配置后记得重启 Jekyll 服务器

