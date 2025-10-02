# Jekyll 博客快速启动指南

## 快速开始

### 1. 配置 Disqus (重要!)

编辑 `_config.yml` 文件，更新以下内容：

```yaml
# 替换为你的 Disqus shortname
disqus:
  shortname: your-disqus-shortname

# 替换为你的实际域名
url: "https://your-domain.com"
```

### 2. 安装依赖

确保你已经安装了 Ruby 和 Bundler：

```bash
# 检查 Ruby 版本 (需要 2.5.0 或更高)
ruby -v

# 安装 Bundler (如果还没有)
gem install bundler

# 安装 Jekyll 和依赖
cd jekyll-blog
bundle install
```

### 3. 本地预览

```bash
bundle exec jekyll serve
```

打开浏览器访问: `http://localhost:4000`

### 4. 构建生产版本

```bash
bundle exec jekyll build
```

生成的静态文件在 `_site` 目录中。

## 快速部署

### GitHub Pages

1. 创建一个 GitHub 仓库
2. 推送代码到仓库
3. 在仓库设置中启用 GitHub Pages
4. 选择分支和目录（通常是 `main` 分支的根目录）

### Netlify

1. 登录 Netlify
2. 点击 "New site from Git"
3. 连接你的 Git 仓库
4. 构建命令: `bundle exec jekyll build`
5. 发布目录: `_site`

### Vercel

1. 登录 Vercel
2. 导入项目
3. Vercel 会自动检测 Jekyll 并配置构建设置

## 迁移完成的内容

✅ **63 篇文章** - 全部转换为 Markdown 格式  
✅ **193 张图片** - 已保存到 `assets/images/`  
✅ **Disqus 评论** - 已集成到文章模板  
✅ **内部链接** - 已修复为相对路径  
✅ **SEO 优化** - 已配置 Jekyll SEO 插件  

## 常见问题

### Q: 如何添加新文章？

在 `_posts` 目录下创建新的 Markdown 文件，文件名格式为：
```
YYYY-MM-DD-title.md
```

文章开头需要包含 YAML front matter：
```yaml
---
title: "文章标题"
date: 2025-10-02
categories: 
  - "分类名"
tags: 
  - "标签1"
  - "标签2"
---
```

### Q: Disqus 评论没有显示？

1. 确认已在 `_config.yml` 中设置正确的 Disqus shortname
2. Disqus 在本地开发环境 (localhost) 可能不会显示
3. 部署到生产环境后等待几分钟让 Disqus 加载

### Q: 如何迁移原有的 Disqus 评论？

1. 登录 Disqus 管理后台
2. 进入 Tools > Migration Tools > URL Mapper
3. 上传 CSV 文件映射旧 URL 到新 URL
4. 格式: `旧URL, 新URL`

### Q: 图片显示不正常？

确保：
1. 图片已复制到 `assets/images/` 目录
2. 文章中的图片路径为 `/assets/images/图片名`
3. 运行 `bundle exec jekyll serve` 时检查控制台错误

### Q: 如何自定义样式？

1. 创建 `assets/css/style.css`
2. 在 `_layouts/default.html` 中添加：
   ```html
   <link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
   ```

## 下一步建议

1. 🎨 **选择主题**: 浏览 [Jekyll Themes](https://jekyllthemes.io/) 选择喜欢的主题
2. 📊 **添加分析**: 集成 Google Analytics 或其他分析工具
3. 🔍 **搜索功能**: 添加站内搜索（如 Algolia）
4. 📱 **移动优化**: 确保网站在移动设备上显示良好
5. ⚡ **性能优化**: 压缩图片、使用 CDN

## 有用的资源

- [Jekyll 官方文档](https://jekyllrb.com/docs/)
- [Jekyll 中文文档](http://jekyllcn.com/)
- [Liquid 模板语言](https://shopify.github.io/liquid/)
- [Markdown 语法](https://www.markdownguide.org/)

## 需要帮助？

查看完整的迁移文档: `MIGRATION_README.md`

