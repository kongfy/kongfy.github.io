# MathJax 数学公式配置说明

## ✅ 配置完成

已成功为博客配置 MathJax 支持，用于渲染 LaTeX 数学公式。

## 🔧 完成的工作

### 1. WordPress LaTeX 格式转换

已将所有文章中的 WordPress LaTeX 格式转换为标准 MathJax 格式：

**转换规则：**
- `\[latex\]formula\[/latex\]` → `$formula$` （块级公式）
- `$latex formula$` → `$formula$` （行内公式）
- 同时在包含数学公式的文章 front matter 中添加 `mathjax: true`

**转换的文章（共 24 篇）：**
1. 2015-04-17-srm656-div1-random-pancake-stack.md
2. 2014-11-09-广告慎入.md
3. 2014-11-18-machine-learning小结2：svm.md
4. 2014-11-13-linux内核同步.md
5. 2015-05-13-openstack网络迷宫：neutron以及lbaas.md
6. 2015-02-07-kargermincut.md
7. 2014-05-03-nanos-note-1-bootloader.md
8. 2014-11-14-apue杂记：解释器文件.md
9. 2014-05-19-nanos-note-2-内核初始化.md
10. 2015-08-03-探索c虚函数在g中的实现.md
11. 2014-11-25-machine-learning小结3：k-means.md
12. 2014-11-10-machine-learning小结1：线性回归、逻辑回归和神经网络.md
13. 2015-09-05-strict-aliasing，神坑？.md
14. 2014-11-28-machine-learning小结4：主成分分析（pca）.md
15. 2014-03-19-openstack-havana（ubuntu-13-10）安装笔记.md
16. 2014-12-06-machine-learning小结5：异常检测.md
17. 2015-10-10-博弈论笔记normal-form-game-and-nash-equilibrium.md
18. 2015-03-16-有向图强连通分支：kosarajus-algorithm.md
19. 2016-10-17-cache-coherence-sequential-consistency-and-memory-barrier.md
20. 2017-01-02-多核并发编程中的cache-line对齐问题.md
21. 2012-09-27-技术评定不及格.md
22. 2013-03-28-架设简单git服务器.md

**注：** 其中部分文章同时包含两种格式，已全部转换。

### 2. MathJax 配置

创建了 `_includes/head/custom.html` 文件，配置 MathJax 3：

```html
<!-- MathJax 配置 -->
{% if page.mathjax %}
<script>
  MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
    }
  };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
{% endif %}
```

## 📝 使用方法

### 在文章中启用 MathJax

在文章的 front matter 中添加 `mathjax: true`：

```yaml
---
title: "包含数学公式的文章"
date: 2025-10-02
categories: 
  - "algorithm"
tags: 
  - "数学"
mathjax: true
---
```

### 数学公式语法

#### 行内公式

使用单个 `$` 包围：

```markdown
这是行内公式 $E = mc^2$ 的例子。
```

渲染效果：这是行内公式 $E = mc^2$ 的例子。

#### 行间公式（独立成行）

使用双 `$$` 包围：

```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

渲染效果：
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

### 常用 LaTeX 语法

#### 希腊字母
```latex
$\alpha, \beta, \gamma, \Delta, \pi, \Omega$
```

#### 上下标
```latex
$x^2, x_i, x^{2n}, x_{i,j}$
```

#### 分数
```latex
$\frac{a}{b}, \dfrac{x+1}{y-1}$
```

#### 求和与积分
```latex
$\sum_{i=1}^{n} x_i, \int_a^b f(x)dx$
```

#### 矩阵
```latex
$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
$$
```

#### 方程组
```latex
$$
\begin{cases}
x + y = 1 \\
x - y = 0
\end{cases}
$$
```

## 🔍 示例文章

查看这些文章了解数学公式的实际效果：

- [全局最小割：Karger's Min Cut Algorithm](/_posts/2015-02-07-kargermincut.md)
- [Machine Learning小结1：线性回归、逻辑回归和神经网络](/_posts/2014-11-10-machine-learning小结1：线性回归、逻辑回归和神经网络.md)
- [博弈论笔记：Normal Form Game and Nash Equilibrium](/_posts/2015-10-10-博弈论笔记normal-form-game-and-nash-equilibrium.md)

## ⚠️ 注意事项

### 1. 特殊字符转义

如果你的公式中包含 `{` 和 `}` 等特殊字符，可能需要使用 `{% raw %}` 和 `{% endraw %}` 标签包围：

```markdown
{% raw %}
这是一个包含 ${{n}\choose{2}}$ 的公式。
{% endraw %}
```

### 2. Markdown 与 LaTeX 冲突

某些 Markdown 语法可能与 LaTeX 冲突，例如下划线 `_`。如果遇到问题：

- 使用反斜杠转义：`\_`
- 或者使用 `{% raw %}` 标签包围整个段落

### 3. 行内公式与文本

行内公式和文本之间建议保留空格：

```markdown
变量 $x$ 表示...   ✓ 推荐
变量$x$表示...     ✗ 不推荐
```

## 🚀 测试

### 本地预览

```bash
bundle exec jekyll serve
```

访问包含数学公式的文章，确认公式正确渲染。

### 检查公式

打开包含 `mathjax: true` 的文章页面，公式应该能够正常渲染。如果公式不显示：

1. 检查浏览器控制台是否有错误
2. 确认 front matter 中有 `mathjax: true`
3. 检查公式语法是否正确

## 📚 参考资源

- [MathJax 官方文档](https://docs.mathjax.org/en/latest/)
- [LaTeX 数学符号](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)
- [Minimal Mistakes MathJax 配置](https://mmistakes.github.io/minimal-mistakes/docs/configuration/#mathjax)

## 🔧 故障排除

### 公式不显示

**问题：** 页面加载后公式不显示

**解决方案：**
1. 检查文章 front matter 是否包含 `mathjax: true`
2. 检查浏览器开发者工具的网络选项卡，确认 MathJax 脚本加载成功
3. 清除浏览器缓存并刷新

### 公式渲染错误

**问题：** 公式显示不正确或出现错误

**解决方案：**
1. 检查 LaTeX 语法是否正确
2. 对于包含特殊字符的公式，使用 `{% raw %}` 标签包围
3. 确认公式中的反斜杠和花括号正确转义

### CDN 加载失败

**问题：** 在某些网络环境下 MathJax CDN 无法访问

**解决方案：**
修改 `_includes/head/custom.html` 中的 CDN 地址，使用国内镜像：

```html
<script src="https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
```

或者使用其他镜像：
- jsdelivr：`https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js`
- unpkg：`https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js`
- 中科大镜像：`https://mirrors.ustc.edu.cn/cdnjs/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js`

## ✅ 配置完成确认

- [x] WordPress LaTeX 格式已转换为标准格式
- [x] MathJax 配置文件已创建
- [x] 包含数学公式的文章已标记 `mathjax: true`
- [x] Jekyll 构建测试通过
- [x] 文档已创建

现在你的博客已经完全支持数学公式渲染了！🎉

