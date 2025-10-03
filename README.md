# Kongfy's Blog - Jekyll 版本（Minimal Mistakes 主题）

这是从 WordPress 迁移到 Jekyll 的个人博客，使用了优秀的 [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) 主题。

## 📁 目录结构

```
blog/
├── _config.yml          # Jekyll 配置文件
├── _data/
│   └── navigation.yml   # 导航栏配置
├── _pages/              # 独立页面（关于、分类、标签等）
├── _posts/              # 63 篇博客文章 (Markdown 格式)
├── assets/
│   └── images/          # 193 张图片资源
├── backup/              # 原始 WordPress XML 备份
├── Gemfile              # Ruby 依赖管理
└── index.html           # 博客首页
```

## 🚀 快速开始

### 1. 配置个人信息

编辑 `_config.yml` 文件，更新以下内容：

```yaml
# 基本信息
title: "Kongfy's Blog"
url: "https://your-domain.com"  # 替换为你的域名

# Disqus 评论
comments:
  provider: "disqus"
  disqus:
    shortname: "your-disqus-shortname"  # 替换

# 作者信息
author:
  name: "Fanyu Kong"
  avatar: # 添加头像路径
  bio: "good good code, day day up!"
  email: "njukongfy@gmail.com"
```

### 2. 选择主题皮肤

在 `_config.yml` 中修改：

```yaml
minimal_mistakes_skin: "default"
```

可选：`default`, `air`, `aqua`, `contrast`, `dark`, `dirt`, `neon`, `mint`, `plum`, `sunrise`

### 3. 安装依赖

```bash
bundle install
```

### 4. 本地预览

```bash
bundle exec jekyll serve
```

访问 `http://localhost:4000` 查看博客。

### 5. 构建生产版本

```bash
bundle exec jekyll build
```

生成的静态文件在 `_site` 目录中。

## 📊 内容统计

- **文章数量**: 63 篇
- **图片数量**: 193 张
- **格式**: Markdown
- **评论系统**: Disqus
- **主题**: Minimal Mistakes
- **原始来源**: WordPress

## 🎨 主题特性

- ✅ 响应式设计
- ✅ 10+ 种皮肤主题
- ✅ 内置搜索功能
- ✅ 代码高亮
- ✅ 文章目录（TOC）
- ✅ 分类、标签归档
- ✅ 社交链接
- ✅ SEO 优化
- ✅ Google Analytics

## 📖 详细文档

- **主题使用**: 查看 [THEME_README.md](THEME_README.md)
- **快速入门**: 查看 [QUICKSTART.md](QUICKSTART.md)
- **迁移详情**: 查看 [MIGRATION_README.md](MIGRATION_README.md)

## 🌐 部署选项

可以部署到以下平台：

- **GitHub Pages**: 免费托管，推送到 GitHub 仓库即可
  ```bash
  # 添加到 _config.yml
  repository: username/repo-name
  ```

- **Netlify**: 自动构建部署
  - 构建命令: `bundle exec jekyll build`
  - 发布目录: `_site`

- **Vercel**: 快速部署，全球 CDN

- **自建服务器**: 部署 `_site` 目录到 Web 服务器

## 📝 添加新文章

在 `_posts` 目录下创建新文件，格式为 `YYYY-MM-DD-title.md`：

```markdown
---
title: "文章标题"
date: 2025-10-02
categories: 
  - "分类"
tags: 
  - "标签1"
  - "标签2"
layout: single
author_profile: true
read_time: true
comments: true
share: true
related: true
toc: true
toc_sticky: true
---

文章内容...
```

## 🎯 导航栏配置

编辑 `_data/navigation.yml` 文件自定义导航栏：

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

## 🔧 常见问题

### 如何更换主题皮肤？
编辑 `_config.yml`，修改 `minimal_mistakes_skin` 的值。

### 如何添加社交链接？
编辑 `_config.yml` 中的 `author.links` 部分。

### 如何启用 Google Analytics？
编辑 `_config.yml` 中的 `analytics` 部分。

### 如何自定义样式？
创建 `/assets/css/custom.scss` 文件并添加自定义 CSS。

## 📧 联系方式

- 作者: Fanyu Kong
- Email: njukongfy@gmail.com

## 🔗 相关链接

- [Minimal Mistakes 主题](https://mmistakes.github.io/minimal-mistakes/)
- [Jekyll 官方文档](https://jekyllrb.com/)
- [Markdown 指南](https://www.markdownguide.org/)

## 📄 许可证

博客内容版权归作者所有。

---

🎉 博客已成功配置 Minimal Mistakes 主题，enjoy！
