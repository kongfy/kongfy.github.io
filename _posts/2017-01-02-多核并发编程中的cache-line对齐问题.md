---
title: "多核并发编程中的cache line对齐问题"
date: 2017-01-02
categories: 
  - "c-cpp"
tags: 
  - "多核"
  - "多线程"
mathjax: true
---

先看一段代码：

```
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <algorithm>

using namespace std;

static const int64_t MAX_THREAD_NUM = 128;

static int64_t n          = 0;
static int64_t loop_count = 0;

#pragma pack (1)
struct data
{
  int32_t pad[15];
  int64_t v;
};
#pragma pack ()

static data value __attribute__((aligned(64)));
static int64_t counter[MAX_THREAD_NUM];

void worker(int *cnt)
{
  for (int64_t i = 0; i < loop_count; ++i) {
    const int64_t t = value.v;

    if (t != 0L && t != ~0L) {
      *cnt += 1;
    }

    value.v = ~t;
    asm volatile("" ::: "memory");
  }
}

int main(int argc, char *argv[])
{
  pthread_t threads[MAX_THREAD_NUM];

  /* Check arguments to program*/
  if(argc != 3) {
      fprintf(stderr, "USAGE: %s <threads> <loopcount>\n", argv[0]);
      exit(1);
  }

  /* Parse argument */
  n          = min(atol(argv[1]), MAX_THREAD_NUM);
  loop_count = atol(argv[2]); /* Don't bother with format checking */

  /* Start the threads */
  for (int64_t i = 0L; i < n; ++i) {
    pthread_create(&threads[i], NULL, (void* (*)(void*))worker, &counter[i]);
  }

  int64_t count = 0L;
  for (int64_t i = 0L; i < n; ++i) {
    pthread_join(threads[i], NULL);
    count += counter[i];
  }

  printf("data size: %lu\n", sizeof(value));
  printf("data addr: %lX\n", (unsigned long)&value.v);
  printf("final: %016lX\n", value.v);

  return 0;
}

```

这段代码的逻辑很简单，开多个线程并行执行一个不断对全局变量取反的操作，你觉得最后的结果会是什么呢？

<!--more-->

简单理解似乎没什么可考虑的，不断取反即使并发产生冲突，但结果也只有两个情况：全0或者全1，运行一下看看结果（**一定要在多核机器上运行**）：

```
[jingyan.kfy@OceanBase224006 test]$ ./alignment 24 10000
data size: 68
data addr: 6016FC
final: FFFFFFFF00000000
```

最后的结构居然是一半1和一半0！是不是很神奇~

出现这种结果的原因其实很简单，我在程序中设置了特殊的对齐，把这个变量放在了跨越两个cacheline的位置（仔细看代码中高亮的部分）。这样的设置会引发一个反直觉的事实：**CPU的一条访存指令是分成两个访存操作执行的**。

如果你看过我的[前一篇文章](/posts/2016-10-*-cache-coherence-sequential-consistency-and-memory-barrier/)，那你应该会很容易理解这个现象：Cache-Coherence的基本单元就是cache line，为了写内存，CPU必须Exclusive的占有这个cache line，而如果一个变量分布在两个不同的cache line上，那么cache line的争用过程是没有原子性保证的。读的过程也是类似的。

这一点在Intel的文档[1](#fn-1610-intel)中也得到了验证：

> Intel 64 memory ordering guarantees that for each of the following memory-access instructions, the constituent memory operation appears to execute as a single memory access regardless of memory type:
> 
> 1. Instructions that read or write a single byte.
> 2. Instructions that read or write a word (2 bytes) whose address is aligned on a 2 byte boundary.
> 3. Instructions that read or write a doubleword (4 bytes) whose address is aligned on a 4 byte boundary.
> 4. Instructions that read or write a quadword (8 bytes) whose address is aligned on an 8 byte boundary.
> 
> All locked instructions (the implicitly locked xchg instruction and other read-modify-write instructions with a lock prefix) are an indivisible and uninterruptible sequence of load(s) followed by store(s) regardless of memory type and alignment. **Other instructions may be implemented with multiple memory accesses**. From a memory- ordering point of view, **there are no guarantees regarding the relative order in which the constituent memory accesses are made**. There is also no guarantee that the constituent operations of a store are executed in the same order as the constituent operations of a load.

可以看到Intel只保证了满足对齐规则的变量的访存操作原子性，这样的对齐规则保证变量不会跨越多个cache line。

那么我们该怎么办呢？其实很简单，Gcc默认的变量对齐是符合Intel的对齐要求的，所以正常情况下这种“异常”是完全不会发生的。但是当你自行操作内存的时候就一定要注意了：因为这个时候没有人会再来帮你对变量进行对齐了，You are on your own。

所以在进行底层系统编程的时候，一定要了解硬件的脾性，小心小心再小心。

## 参考资料

* * *

2. Intel® 64 Architecture Memory Ordering White Paper [↩](#fnref-1610-intel)
