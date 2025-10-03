---
title: "SRM656 DIV1 Random Pancake Stack"
date: 2015-04-17
categories: 
  - "algorithm"
tags: 
  - "srm"
  - "topcoder"
  - "动态规划"
mathjax: true
---

被虐了......这个题目其实不难，但是从一开始想法有个漏洞没有发现...一直没有转过弯来...还是需要训练训练...

原题链接：[Random Pancake Stack](http://community.topcoder.com/stat?c=problem_statement&pm=13747&rd=16416 "Random Pancake Stack")

> Charlie has N pancakes. He wants to serve some of them for breakfast. We will number the pancakes 0 through N-1. For each i, pancake i has width i+1 and deliciousness d\[i\].
> 
> Charlie chooses the pancakes he is going to serve using the following randomized process: He starts by choosing the first pancake uniformly at random from all the pancakes he has. He places the chosen pancake onto a plate. This pancake now forms the bottom of a future stack of pancakes. Then, Charlie repeats the following procedure:
> 
> 1. If there are no more pancakes remaining, terminate.
> 2. Choose a pancake uniformly at random from the pancakes that have not been chosen yet.
> 3. If the width of this pancake is greater than the width of the pancake on top of the stack, terminate without taking it.
> 4. Place the chosen pancake on top of the stack and go back to step 1.
> 
> You are given the vector d with N elements. The total deliciousness of a serving of pancakes is the sum of the deliciousness of all pancakes used in the serving. Compute and return the expected value of the total deliciousness of the pancakes chosen by Charlie.

<!--more-->

题目的意思就是在给定规则下求出得到的饼干美味值总和的期望。下面给出官方给的样例及解释：

> {1,1,1} Returns: 1.6666666666666667 The following scenarios may occur:
> 
> 1. With probability 1/3, Charlie chooses pancake 0 first. In this case he won't be able to add any more pancakes and the total deliciousness of his serving of pancakes will be 1.
> 2. With probability 1/3, Charlie chooses pancake 1 first. What happens in the second round? With probability 1/2 he will choose pancake 0 and with probability 1/2 it will be pancake 2. In the first case the total deliciousness of Charlie's pancakes will be 2, in the second case it will be 1.
> 3. With probability 1/3, Charlie chooses pancake 2 first. If he chooses pancake 0 next, the total deliciousness of his pancakes will be 2. If he happens to choose pancake 1 next (followed by pancake 0 in the third round), the total deliciousness will be 3.
> 
> Summing this up, we get the expected deliciousness to be 1/3 \* (1) + 1/3 \* (1/2 \* 1 + 1/2 \* 2) + 1/3 \* (1/2 \* 2 + 1/2 \* 3) = 5/3 = 1.666...

仔细分析规则，发现有子问题结构，令$f\[i,j\]$表示序列前$i$块饼干美味值总和的期望，而状态$j$表示剩余的饼干总数（$i \\le j \\le N$），不难写出如下的状态转移方程：

$\\displaystyle f\[i,j\] = \\frac{1}{i} \\sum\_{k=1}^{i}{\\left( (d\[k\]+f\[k-1,j-1\]) \\times \\frac{k-1}{j-1} + d\[k\] \\times \\frac{j-k}{j-1}\\right) }\\quad (1 \\le i \\le j \\le N)$

边界条件非常自然：

$\\displaystyle f\[1,i\] = d\[1\]\\qquad (1 \\le i \\le N)$

所求结果为：

$\\displaystyle f\[N,N\]$

有了状态转移方尺和边界条件后就可以非常轻松的写出动态规划代码了，如下（注意：上述方程中从1开始计数，在转换为C++程序时要留心）：

```cpp
#include <vector>

using namespace std;

class RandomPancakeStack
{
public:
    double expectedDeliciousness(vector <int> d)
    {
        int n = d.size();
        
        vector<vector<double> > f(n + 1, vector<double> (n + 1, 0));

        // base case
        for (int i = 1; i <= n; ++i) {
            f[1][i] = d[0];
        }
        
        // dp
        for (int i = 2; i <= n; ++i) {
            for (int j = i; j <= n; ++j) {
                double temp = 0;
                for (int k = 1; k <= i; ++k) {
                    temp += (d[k - 1] + f[k - 1][j - 1]) * (k - 1) / (double)(j - 1);
                    temp += d[k - 1] * (j - k) / (double)(j - 1);
                }
                
                temp *= 1.0 / i;
                f[i][j] = temp;
            }
        }

        return f[n][n];
    }
};
```

算法运行时间复杂度为$O(n^{2})$，空间复杂度为$O(n^{2})$，通过滚动数组可以将空间复杂度优化到$O(n)$（和背包问题一样）。房间里有一个Red(3000+)的俄罗斯大神写了时间复杂度为$O(n)$，空间复杂度为$O(1)$的方法...令人汗颜...

保持按时被虐的好习惯！
