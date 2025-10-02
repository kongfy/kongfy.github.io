---
title: "SRM657 DIV1 Problem Sets"
date: 2015-04-28
categories: 
  - "algorithm"
tags: 
  - "binary-search"
  - "srm"
  - "topcoder"
---

原题链接：[Problem Sets](http://community.topcoder.com/stat?c=problem_statement&pm=13771 "Problem Sets")

> Cat Snuke came up with some problems. He wants to construct as many problem sets as possible using those problems. Each problem set must contain exactly three problems: one for the Easy slot, one for the Medium slot, and one for the Hard slot. Each problem can only be assigned to a single slot in a single problem set. He came up with E + EM + M + MH + H problems in total. The distribution of the problems is as follows:
> 
> - E problems can only be used in the Easy slot.
> - EM problems can be used either in the Easy slot or the Medium slot.
> - M problems can only be used in the Medium slot.
> - MH problems can be used either in the Medium slot or the Hard slot.
> - H problems can only be used in the Hard slot.
> 
> Return the maximal number of problem sets he can construct.

<!--more-->

题目很好理解，不再赘述了。

这题在思路上还是有点意思的，按照题意直接从输入推到输出我感觉也是可以的，我想了一个自然的贪心策略（按照直觉推算Problem Sets的数量），但是Case太多了，编码起来太繁琐，故抛弃。

有意思的是如果把这个问题反转一下，提出判定问题：给定想要的Problem Sets的数量，能否用这些给定的题目来构成呢？不难发现，这个问题是非常简单解决的，只要所给的题目能够在E、M、H三个Slot中都放置目标数量个题目即可。那么，在判定问题的基础上，我们可以直接在long long的范围内做二分查找来寻找最终解，附上代码：

`class ProblemSets { private: bool check(long long cap, long long E, long long EM, long long M, long long MH, long long H) { if (H + MH < cap) return false; // check Hard problems if (E + EM < cap) return false; // check Easy problems  MH = H < cap ? MH - (cap - H) : MH; EM = E < cap ? EM - (cap - E) : EM; if (M + EM + MH < cap) return false; // check Medium problems return true; } public: long long maxSets(long long E, long long EM, long long M, long long MH, long long H) { long long l = 0, r = ~(1LL << 63);  while (l < r) { long long mid = (l + r + 1) / 2; if (check(mid, E, EM, M, MH, H)) { l = mid; } else { r = mid - 1; } }  return l; } };  `
