# GitHub Pages 部署指南

## 🚀 快速部署到 GitHub Pages

### 步骤 1：创建 GitHub 仓库

1. 访问 [https://github.com/new](https://github.com/new)
2. 创建一个新仓库，有两种选择：

   **选项 A：个人站点（推荐）**
   - 仓库名：`你的用户名.github.io`（例如：`kongfy.github.io`）
   - 访问地址：`https://你的用户名.github.io`
   - 优点：URL 简洁，无需配置 baseurl

   **选项 B：项目站点**
   - 仓库名：任意名称（例如：`blog`）
   - 访问地址：`https://你的用户名.github.io/blog`
   - 需要设置 baseurl: "/blog"

3. 设置为 Public（公开）
4. 不要初始化 README、.gitignore 等文件（因为本地已有）

### 步骤 2：更新配置文件

**如果使用选项 A（个人站点）**，编辑 `_config.yml`：

```yaml
url: "https://你的用户名.github.io"
baseurl: ""
repository: "你的用户名/你的用户名.github.io"
```

**如果使用选项 B（项目站点）**，编辑 `_config.yml`：

```yaml
url: "https://你的用户名.github.io"
baseurl: "/blog"
repository: "你的用户名/blog"
```

### 步骤 3：推送到 GitHub

```bash
# 添加 GitHub 远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送代码
git push -u origin main

# 如果提示需要设置用户信息
git config user.name "你的名字"
git config user.email "你的邮箱"
```

### 步骤 4：配置 GitHub Pages

1. 进入 GitHub 仓库页面
2. 点击 **Settings** → **Pages**
3. 在 **Source** 中选择：
   - Branch: `main`
   - Folder: `/ (root)`
4. 点击 **Save**

### 步骤 5：等待部署

- GitHub Actions 会自动构建和部署
- 通常需要 1-3 分钟
- 可以在 **Actions** 标签查看构建进度
- 构建完成后访问你的网站

## 📋 完整命令示例

假设你的 GitHub 用户名是 `kongfy`，创建个人站点：

```bash
# 1. 更新 _config.yml（手动编辑或运行以下命令）
sed -i '' 's|url: "https://your-domain.com"|url: "https://kongfy.github.io"|' _config.yml
sed -i '' 's|repository: # GitHub username/repo-name|repository: "kongfy/kongfy.github.io"|' _config.yml

# 2. 提交更改（如果有修改）
git add _config.yml
git commit -m "Update config for GitHub Pages"

# 3. 添加远程仓库并推送
git remote add origin https://github.com/kongfy/kongfy.github.io.git
git push -u origin main
```

## ⚙️ GitHub Actions 配置（可选）

如果需要自定义构建流程，创建 `.github/workflows/pages.yml`：

```yaml
name: Deploy Jekyll site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## 🔍 故障排查

### 1. 构建失败

查看 GitHub Actions 日志：
- 进入仓库的 **Actions** 标签
- 点击失败的 workflow
- 查看详细错误信息

常见问题：
- `Gemfile.lock` 版本不匹配：删除本地的 `Gemfile.lock`，重新 `bundle install`
- 主题未找到：确保 `Gemfile` 中包含 `minimal-mistakes-jekyll`

### 2. 页面 404

- 检查 `_config.yml` 中的 `url` 和 `baseurl` 是否正确
- 确保 GitHub Pages 设置中选择了正确的分支和目录
- 等待几分钟让 GitHub Pages 完成部署

### 3. 样式丢失

如果是项目站点（非用户名.github.io），确保：
- `_config.yml` 中设置了 `baseurl: "/仓库名"`
- 重新推送并等待重新构建

### 4. Disqus 评论不显示

- 登录 Disqus 后台，更新网站 URL 为你的 GitHub Pages 地址
- 在 **Trusted Domains** 中添加你的 GitHub Pages 域名

## 🌐 自定义域名（可选）

如果你有自己的域名：

1. 在 GitHub 仓库 Settings → Pages → Custom domain 中输入你的域名
2. 在你的域名提供商处添加 DNS 记录：
   ```
   CNAME记录: www.yourdomain.com → 你的用户名.github.io
   A记录: yourdomain.com → 185.199.108.153
   A记录: yourdomain.com → 185.199.109.153
   A记录: yourdomain.com → 185.199.110.153
   A记录: yourdomain.com → 185.199.111.153
   ```
3. 等待 DNS 生效（可能需要几小时）
4. 在 GitHub Pages 设置中启用 "Enforce HTTPS"

## 📱 验证部署

部署完成后检查：
- ✅ 首页能正常访问
- ✅ 文章列表显示正常
- ✅ 文章内容和图片加载正常
- ✅ 导航菜单工作正常
- ✅ 搜索功能可用
- ✅ Disqus 评论显示（需要在 Disqus 后台配置）

## 🔄 后续更新

每次修改后更新网站：

```bash
# 1. 提交更改
git add .
git commit -m "描述你的更改"

# 2. 推送到 GitHub
git push

# 3. 等待 GitHub Actions 自动部署（1-3分钟）
```

## 🎉 完成！

现在你的博客应该已经在线了！访问 `https://你的用户名.github.io` 查看效果。

