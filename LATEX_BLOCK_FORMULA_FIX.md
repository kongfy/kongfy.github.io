# LaTeX 块级公式格式修复总结

## 🎯 问题与解决方案

### 原始问题
- 使用 `$\displaystyle ...$` 格式的公式虽然显示为展示样式，但**不会居中**
- 改用 `$$...$$` 后公式**显示不正确**（转义字符处理问题）

### 最终解决方案 ✅
使用 `\[...\]` 格式：
- ✅ 公式独占一行
- ✅ 公式居中显示
- ✅ 转义字符处理稳定（保持原有的 `\\` 和 `\_`）
- ✅ 在主页摘要中也能正确渲染

## 📝 修复的文章列表

### 1. `2015-03-16-有向图强连通分支：kosarajus-algorithm.md`
**修复公式数：2**
```latex
\[\max_{v\in C_1}f(v) < \max_{v\in C_2}f(v)\]
\[\min_{v\in C_1}f(v) > \min_{v\in C_2}f(v)\]
```

### 2. `2015-04-17-srm656-div1-random-pancake-stack.md`
**修复公式数：3**
- 状态转移方程
- 边界条件
- 所求结果

### 3. `2014-11-10-machine-learning小结1：线性回归、逻辑回归和神经网络.md`
**修复公式数：4**
- Hypothesis 函数
- Cost function
- Regularization 后的线性回归 Cost function
- Regularization 后的逻辑回归 Cost function（多行公式）

### 4. `2014-12-06-machine-learning小结5：异常检测.md`
**修复公式数：3**
- 高斯分布概率密度函数
- 单变量高斯模型参数拟合（包含两个公式）
- 样本概率计算公式

### 5. `2014-11-28-machine-learning小结4：主成分分析（pca）.md`
**修复公式数：7**
- 数据预处理（均值和标准化）
- 数据维度转换（投影和逆投影）
- SVD 分解公式
- 选择 k 的方差保留公式
- 简化计算公式

## 📊 统计

- **总修复文章数**：5 篇
- **总修复公式数**：19 个
- **格式转换**：`$\displaystyle ...$` → `\[...\]`

## 🔍 三种格式对比

| 格式 | 居中 | 独占行 | 转义稳定性 | 使用场景 |
|------|------|--------|-----------|---------|
| `$...$` | ❌ | ❌ | ✅ | 行内公式 |
| `$\displaystyle ...$` | ❌ | ❌ | ✅ | 行内展示样式 |
| `$$...$$` | ✅ | ✅ | ⚠️ | 块级公式（Jekyll 中可能有问题） |
| `\[...\]` | ✅ | ✅ | ✅ | **块级公式（推荐）** ⭐ |

## 📖 MathJax 配置

在 `_includes/head/custom.html` 中的配置支持这些格式：

```javascript
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],          // 行内公式
    displayMath: [['$$', '$$'], ['\\[', '\\]']],       // 块级公式
    processEscapes: true,
    processEnvironments: true
  }
}
```

## ✨ 修复示例

### 修复前
```markdown
该算法正确性证明的核心在于...可以证明：

$\displaystyle \max_{v\in C_1}f(v) < \max_{v\in C_2}f(v)$

\(f(v)\)代表点在...
```
**问题**：公式不居中，左对齐

### 修复后
```markdown
该算法正确性证明的核心在于...可以证明：

\[\max_{v\in C_1}f(v) < \max_{v\in C_2}f(v)\]

\(f(v)\)代表点在...
```
**效果**：公式居中显示，独占一行 ✅

## 💡 写作建议

在编写新文章时：

```markdown
# 行内公式（文字段落中）
文字中的公式 $f(x) = x^2$ 继续文字

# 块级公式（独立居中显示）
重要的数学公式：

\[f(x) = \int_0^1 x^2 dx\]

继续下一段文字。

# 多行公式（使用 aligned 环境）
\[\begin{aligned}
  J(\theta) &= -\frac{1}{m}\sum_{i=1}^{m}[\cdots] \\
            &+ \frac{\lambda}{2m}\sum_{j=1}^{n}\theta_j^2
\end{aligned}\]
```

## ✅ 验证结果

所有修复后的公式：
- ✅ 在文章页面中居中显示
- ✅ 在主页摘要中正确渲染
- ✅ 转义字符正确处理
- ✅ 数学符号显示正确

## 🔧 技术说明

### 为什么 `\[...\]` 比 `$$...$$` 更好？

1. **更标准的 LaTeX 语法**
   - `\[...\]` 是 LaTeX 原生的块级公式语法
   - `$$...$$` 是 TeX 的语法，不是标准 LaTeX

2. **在 Jekyll + Kramdown 中更稳定**
   - Kramdown 对 `\[...\]` 的处理更一致
   - `$$...$$` 在某些情况下会与 Markdown 语法冲突

3. **转义字符处理更可靠**
   - `\[...\]` 保持原有的转义（`\\`、`\_`）
   - `$$...$$` 可能需要额外的转义调整

## 📚 参考资源

- MathJax 文档：https://docs.mathjax.org/
- LaTeX 数学公式：https://en.wikibooks.org/wiki/LaTeX/Mathematics
- Kramdown 语法：https://kramdown.gettalong.org/syntax.html#math-blocks

## 🎉 完成状态

**所有需要居中显示的数学公式已全部修复完成！**

- 修复方法：`$\displaystyle ...$` → `\[...\]`
- 修复文章：5 篇
- 修复公式：19 个
- 状态：✅ 全部完成

