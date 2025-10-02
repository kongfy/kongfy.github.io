---
title: "Single Number"
date: 2014-06-05
categories: 
  - "algorithm"
tags: 
  - "leetcode"
---

> Given an array of integers, every element appears twice except for one. Find that single one. Note: Your algorithm should have a linear runtime complexity. Could you implement it without using extra memory?

题目链接在[这里](https://oj.leetcode.com/problems/single-number/)。

这是一道很有意思的题目，大意是说在一个整型数组中，所有的数字都出现了两次，只有一个数是例外，找出这个数。

乍一看感觉很简单啊，开个数组计数就好了~可惜题目还要求要在不使用额外空间的情况下找到解，这就有点蛋疼了...如果使用二分查找倒是不会用到额外空间，可是时间复杂度为O(nlogn)，又不符合题目要求的线性复杂度...

该怎么办呢？该怎么办呢？

<!--more-->

其实这个题目的解法非常的巧妙，也非常简单，主要用到了**异或**运算的性质： `a xor a = 0 0 xor a = a a xor b = b xor a` 非常非常简单...使用上面的性质可以很容易知道，把数组中所有的数异或起来，得到的结果就是仅出现了一次的数！！！！！

`class Solution { public: int singleNumber(int A[], int n) { int ans = 0; for (int i = 0; i < n; ++i) { ans ^= A[i]; } return ans; } };`
