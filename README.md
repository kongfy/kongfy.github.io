# Kongfy's Blog - Jekyll 版本

这是从 WordPress 迁移到 Jekyll 的个人博客。

## 📁 目录结构

```
blog/
├── _config.yml          # Jekyll 配置文件
├── _posts/              # 63 篇博客文章 (Markdown 格式)
├── _layouts/            # 页面布局模板
├── _includes/           # 可复用组件 (含 Disqus 评论)
├── assets/
│   └── images/          # 193 张图片资源
├── backup/              # 原始 WordPress XML 备份
├── Gemfile              # Ruby 依赖管理
├── index.html           # 博客首页
├── QUICKSTART.md        # 快速启动指南
└── MIGRATION_README.md  # 完整迁移文档

```

## 🚀 快速开始

### 1. 配置 Disqus 评论

编辑 `_config.yml` 文件：

```yaml
disqus:
  shortname: your-disqus-shortname  # 替换为你的 Disqus shortname

url: "https://your-domain.com"  # 替换为你的实际域名
```

### 2. 安装依赖

```bash
bundle install
```

### 3. 本地预览

```bash
bundle exec jekyll serve
```

访问 `http://localhost:4000` 查看博客。

### 4. 构建生产版本

```bash
bundle exec jekyll build
```

生成的静态文件在 `_site` 目录中。

## 📊 内容统计

- **文章数量**: 63 篇
- **图片数量**: 193 张
- **格式**: Markdown
- **评论系统**: Disqus
- **原始来源**: WordPress

## 📖 详细文档

- **快速入门**: 查看 [QUICKSTART.md](QUICKSTART.md)
- **迁移详情**: 查看 [MIGRATION_README.md](MIGRATION_README.md)

## 🌐 部署选项

可以部署到以下平台：

- **GitHub Pages**: 免费托管，推送到 GitHub 仓库即可
- **Netlify**: 自动构建部署，支持自定义域名
- **Vercel**: 快速部署，全球 CDN
- **自建服务器**: 构建后将 `_site` 目录部署到 Web 服务器

## 🔄 Git 管理

建议将以下目录添加到 `.gitignore`：

```
_site/
.jekyll-cache/
.sass-cache/
Gemfile.lock
```

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
---

文章内容...
```

## 📧 联系方式

- 作者: Fanyu Kong
- Email: njukongfy@gmail.com

## 📄 许可证

博客内容版权归作者所有。

