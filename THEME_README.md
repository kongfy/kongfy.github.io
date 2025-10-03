# Minimal Mistakes 主题使用指南

本博客使用了 [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) 主题，这是一个功能强大、灵活且美观的 Jekyll 主题。

## 🎨 主题特性

- ✅ 响应式设计，完美适配移动设备
- ✅ 支持多种皮肤主题切换
- ✅ 内置搜索功能
- ✅ 支持 Disqus、Discourse 等评论系统
- ✅ 代码高亮
- ✅ 文章目录（TOC）自动生成
- ✅ 分类、标签归档
- ✅ 社交链接
- ✅ SEO 优化
- ✅ Google Analytics 集成

## 📁 目录结构

```
blog/
├── _config.yml              # 主题配置文件
├── _data/
│   └── navigation.yml       # 导航栏配置
├── _pages/                  # 页面文件
│   ├── about.md            # 关于页面
│   ├── categories.md       # 分类页面
│   ├── tags.md             # 标签页面
│   └── year-archive.md     # 归档页面
├── _posts/                  # 博客文章
├── assets/
│   └── images/             # 图片资源
├── index.html              # 首页
└── Gemfile                 # Ruby 依赖
```

## 🎨 更换皮肤

编辑 `_config.yml` 文件，修改 `minimal_mistakes_skin` 配置：

```yaml
minimal_mistakes_skin: "default" 
```

可选的皮肤主题：
- `"default"` - 默认（白色背景）
- `"air"` - 空气感（浅色）
- `"aqua"` - 水蓝色
- `"contrast"` - 高对比度
- `"dark"` - 深色主题
- `"dirt"` - 泥土色
- `"neon"` - 霓虹色
- `"mint"` - 薄荷绿
- `"plum"` - 梅子色
- `"sunrise"` - 日出橙

## ⚙️ 重要配置

### 1. Disqus 评论

编辑 `_config.yml`：

```yaml
comments:
  provider: "disqus"
  disqus:
    shortname: "your-disqus-shortname"  # 替换为你的 shortname
```

### 2. 作者信息

```yaml
author:
  name: "Fanyu Kong"
  avatar: # 头像图片路径，如 "/assets/images/avatar.jpg"
  bio: "good good code, day day up!"
  location: "China"
  email: "njukongfy@gmail.com"
  links:
    - label: "GitHub"
      icon: "fab fa-fw fa-github"
      url: "https://github.com/yourusername"
    - label: "Twitter"
      icon: "fab fa-fw fa-twitter-square"
      url: "https://twitter.com/yourhandle"
```

### 3. 导航栏

编辑 `_data/navigation.yml`：

```yaml
main:
  - title: "首页"
    url: /
  - title: "分类"
    url: /categories/
  - title: "标签"
    url: /tags/
  - title: "归档"
    url: /archive/
  - title: "关于"
    url: /about/
```

### 4. 搜索功能

默认已启用 lunr 搜索，无需额外配置。

### 5. Google Analytics

编辑 `_config.yml`：

```yaml
analytics:
  provider: "google-gtag"
  google:
    tracking_id: "YOUR-TRACKING-ID"
    anonymize_ip: false
```

## 📝 文章 Front Matter

每篇文章的开头应包含以下 Front Matter：

```yaml
---
title: "文章标题"
date: 2025-10-02
categories: 
  - "分类名"
tags: 
  - "标签1"
  - "标签2"
layout: single           # 使用单栏布局
author_profile: true     # 显示作者信息
read_time: true          # 显示阅读时间
comments: true           # 启用评论
share: true              # 显示分享按钮
related: true            # 显示相关文章
toc: true                # 启用目录
toc_sticky: true         # 目录固定在侧边
---
```

### 可选的 Front Matter

```yaml
excerpt: "文章摘要，会显示在首页"
header:
  image: /assets/images/header.jpg          # 文章头图
  teaser: /assets/images/teaser.jpg         # 缩略图
  overlay_image: /assets/images/overlay.jpg # 覆盖图
  overlay_filter: 0.5                       # 图片遮罩
classes: wide # 使用宽屏布局
```

## 🚀 本地预览

```bash
bundle exec jekyll serve
```

访问 `http://localhost:4000` 查看效果。

### 实时刷新

```bash
bundle exec jekyll serve --livereload
```

保存文件后浏览器会自动刷新。

## 🎨 自定义样式

创建 `/assets/css/custom.scss` 文件：

```scss
---
---

// 你的自定义样式
.page__content {
  font-size: 16px;
}

// 自定义代码块样式
.highlight {
  border-radius: 5px;
}
```

然后在 `_config.yml` 中添加：

```yaml
sass:
  sass_dir: _sass
  style: compressed
```

## 📱 响应式设计

主题自带完美的响应式设计，会自动适配：
- 桌面端（宽屏）
- 平板（中屏）
- 手机（小屏）

## 🔧 常用自定义

### 1. 修改每页文章数

编辑 `_config.yml`：

```yaml
paginate: 10  # 每页显示10篇文章
```

### 2. 更改固定链接格式

```yaml
permalink: /:categories/:title/
# 或其他格式
# permalink: /:year/:month/:day/:title/
# permalink: /posts/:title/
```

### 3. 启用面包屑导航

```yaml
breadcrumbs: true
```

### 4. 设置默认缩略图

```yaml
teaser: /assets/images/default-teaser.jpg
```

## 📚 参考资源

- [Minimal Mistakes 官方文档](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/)
- [配置说明](https://mmistakes.github.io/minimal-mistakes/docs/configuration/)
- [布局说明](https://mmistakes.github.io/minimal-mistakes/docs/layouts/)
- [助手工具](https://mmistakes.github.io/minimal-mistakes/docs/helpers/)

## 💡 提示

1. **图片优化**：建议压缩图片以提高加载速度
2. **CDN 加速**：可以将图片托管到图床或 CDN
3. **主题更新**：定期运行 `bundle update` 更新主题
4. **备份配置**：修改配置前记得备份

## 🎯 下一步

1. ✅ 主题已安装并配置
2. 📝 更新 `_config.yml` 中的个人信息
3. 🎨 选择喜欢的皮肤主题
4. 📸 添加头像和站点 logo
5. 🔗 配置社交链接
6. 🚀 部署到生产环境

Happy Blogging! 🎉


