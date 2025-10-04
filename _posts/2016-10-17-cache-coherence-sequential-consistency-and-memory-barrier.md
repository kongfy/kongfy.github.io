---
title: "Sequential Consistency，Cache-Coherence及Memory barrier"
date: 2016-10-17
categories: 
  - "c-cpp"
  - "linux"
tags: 
  - "memory-barrier"
  - "多核"
  - "多线程"
mathjax: true
---

如今多核CPU在服务器中已经是标配，如何更好的发挥多核CPU进行并行计算相信是每个后端开发都会遇到的难题。这篇文章主要是梳理一下我最近学习的一些关于C++多线程编程的知识。

## 并发 VS 并行


提到并发编程，有很多不同的编程模型，如多进程、多线程、协程，还可以结合使用I/O多路复用技术来进行异步并发编程，由此产生了很多不同类型的并发编程技巧来解决各类场景下的问题。

其中，协程模型也称为“用户态线程”，在用户态对程序流进行切换，避免了系统上下文切换的开销，属于**并发**而不是**并行**的（协程也可以和多进程、多线程模型结合，此处不做探讨），多进程和多线程的编程模型是真正**并行**的，即多个程序流是真正同时运行的，因此可以更好的利用多核优势，由于多线程之间共用进程地址空间，所以多线程模型相对多进程模型而言可以减少一些进程间的通信开销。

## 多线程同步


然而，凡事有利必有弊，共用进程地址空间带来了性能上的提高必然也会产生一些复杂的问题，及引入了线程间同步的问题。多个线程如果不加保护的访问共享的变量，必然会引发严重问题，这些在线程间共享的变量被称为“[临界区](https://en.wikipedia.org/wiki/Critical_section)”，最为经典的例子就是多个线程同时对单变量执行递增操作，相信诸位都已经听到耳朵起茧，就不再展开了。

在多线程编程中，常用的同步方式是使用pthread库中提供的线程同步手段（暂不考虑C++11中提供的线程库），如互斥锁、自旋锁、信号量、条件变量等等，但这些方法不是本文的主要内容，因此也不做展开，有兴趣的同学可以自行阅读《UNIX环境高级编程》中关于多线程同步的章节。

PS：在Linux内核中由于内核线程共用内核地址空间，所以内核线程之间也需要使用线程同步机制进行保护，Linux内核中所使用的几种常见同步机制分析见我[之前的文章](/2014/11/linux内核同步/)。

<!--more-->

## Lockless


到这里一切都很好，我们可以使用多线程作为并行编程手段，并且使用pthread提供的同步机制对临界区进行保护，pthread库为我们屏蔽了底层的复杂性，在我们看来多核CPU是透明的计算资源，而不需要特别为多核CPU进行太多的考虑。

然而，随着对性能的要求进一步提高，当我们需要达到更大的并发度时，pthread库提供的同步手段将成为瓶颈，因此在需要高性能的程序中往往会借助于一些lock-free的编程技术来提高程序的性能，这样的程序中不再使用pthread所提供的保护元语，必须自行处理多核CPU环境中产生的各种问题，这样不显式使用底层锁同步机制的程序我们成为是lockless的（注：lockless不是lock-free，比如常见的使用CAS操作做循环等待是lockless的，但是却不是lock-free的，lock-free是另一个重要的概念，本文中不涉及）。

## 什么是Cache-Coherence


那么，多核环境和单核究竟有什么不同？实际上，问题的来源是cache。我们都知道，因为CPU的运行速度比内存访问速度快很多(百倍的量级差距)，所以每个CPU都有自己的cache来加速对内存的访问（局部性原理），如下图：

[![](/assets/images/perf3_9.png)](/assets/images/perf3_9.png)

这样造成的一个问题是同一份数据有可能会分布在各个CPU的cache中，和分布式系统一样，数据的副本会带来一致性问题，事实上，在同一时间，同一变量在不同的CPU上会有不同的值，如下图：

[![](/assets/images/perf14_5.png)](/assets/images/perf14_5.png)

举个例子，当CPU 0刚刚修改了内存中某处的值时，最新的值是先写入到CPU 0的局部cache中，等待cache line淘汰才会被写回内存，如果此时另一个CPU（如CPU 7）想要访问内存中同一位置的值，则不论是CPU 7的局部cache中还是内存中都没有最新值，最新值只存在于CPU 0的局部cache中，因此我们需要一个机制来保证cache在不同CPU间的一致性，这个机制就是Cache-Coherence Protocal。

MESI是一种使用最广泛的Cache-Coherence Protocal，Intel使用的MESIF就是在MESI协议基础上改进而来。为了理解原理的目的，我们只需要了解MESI协议就可以了。

MESI这四个字母分别代表了每一个cache line可能处于的四种状态：“Modified”、“Exclusive”、“Shared”和“Invalid”：

- **Modified**：处于该状态的cache line刚刚被该CPU修改过，且该修改还没有同步到其他的CPU及内存中，这个状态的cache line是被这个CPU所“拥有”的，所以这个CPU必须负责将这个cache line写回内存或是交给其他的CPU。
- **Exclusive**：和Modified状态很接近，区别在于CPU已经“拥有”了这个cache line，但还没有修改cache line的值，可以在任意时刻修改并不需要询问其他的CPU。
- **Shared**：处于该状态的cache line被多个CPU所共享，所以CPU无法直接修改该cache line，只可以读取其上的值。
- **Invalid**：这个状态是所有cache line的初始状态，表明该cache line为空，没有存储数据。

当CPU对cache line进行操作时，就会导致cache line的状态发生变化，这样的变化往往需要通过在CPU之间传递消息来完成，MESI的状态转换图如下：

[![](/assets/images/mesi-1.png)](/assets/images/mesi-1.png)

图中所列出的状态变化都值得仔细考量，为了下文叙述方便，我在这里重点描述其中一种情况：多个CPU都持有同一cache line，初始状态为“Shared”，当其中一个CPU想要修改该cache line的内容时，它向其他所有CPU发送“Invalidate”消息，其他CPU收到消息以后必须将该cache line的状态修改为“Invalid”，随后回复“Invalidate Acknowledge”消息给发送方CPU，当发送方CPU收到所有的“Invalidate Acknowledge”消息后，就可以将该cache line修改为“Exclusive”状态并执行数据修改了。

上述过程实际是一次cache line"所有权"的获取过程，其他的状态过程切换见RCU一哥书中的表述[^perfbook]。

### False sharing

在这里我们先开个小差，讨论下另外一个问题——False sharing。

如我们所见，这个cache line“所有权”的获取过程涉及到了多个CPU之间的消息通信，相比起直接在单核上进行操作一定是低效的，然而此处有一个陷阱：在我们编程时通常是以变量为思考单元的，但这里CPU之间争夺“所有权”的单元是cache line(通常为64字节)，那么就会下图中的一种情况：在一个并行的程序中，一个线程不断写入变量X，另一个线程不断写入变量Y，本来是没有冲突的，但是两个变量在内存中落在了同一cache line上，这就是导致执行过程中在两个CPU之间不断发生该cache line“所有权”的争夺，导致性能的下降，这个问题就叫False sharing(名字也很直观)。

[![](/assets/images/false_share.png)](/assets/images/false_share.png)

知道了问题发生的原因，解决起来就不难了，既然是因为多个本不相干的变量落在同一cache line上产生的冲突，那么我们只要在这些变量之间添加适当的padding，使得他们落在不同的cache line上就可以了，这在GNU C中可以通过设置变量属性 \_\_attribute\_\_((aligned(64))) 解决。

让我们写个代码来实际验证这个问题：

```cpp
/*
 * Demo program for showing the drawback of "false sharing"
 *
 * Use it with perf!
 *
 * Compile: g++ -O2 -o false_share false_share.cpp -lpthread
 * Usage: perf stat -e cache-misses ./false_share  
 */

#include <sys/time.h>
#include <cstdio>
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <cstdlib>

#define CACHE_ALIGN_SIZE 64
#define CACHE_ALIGNED __attribute__((aligned(CACHE_ALIGN_SIZE)))

int gLoopCount;

inline int64_t current_time()
{
  struct timeval t;
  if (gettimeofday(&t, NULL) < 0) {
  }
  return (static_cast(t.tv_sec) * static_cast(1000000) + static_cast(t.tv_usec));
}

struct value {
  int64_t val;
};
value data[2] CACHE_ALIGNED;

struct aligned_value {
  int64_t val;
} CACHE_ALIGNED;
aligned_value aligned_data[2] CACHE_ALIGNED;

void* worker1(int64_t *val)
{
  printf("worker1 start...\n");

  volatile int64_t &v = *val;
  for (int i = 0; i < gLoopCount; ++i) {
    v += 1;
  }

  printf("worker1 exit...\n");
}

// duplicate worker function for perf report
void* worker2(int64_t *val)
{
  printf("worker2 start...\n");

  volatile int64_t &v = *val;
  for (int i = 0; i < gLoopCount; ++i) {
    v += 1;
  }

  printf("worker2 exit...\n");
}

int main(int argc, char *argv[])
{
  pthread_t race_thread_1;
  pthread_t race_thread_2;

  bool is_aligned;

  /* Check arguments to program*/
  if(argc != 3) {
    fprintf(stderr, "USAGE: %s  \n", argv[0]);
    exit(1);
  }

  /* Parse argument */
  gLoopCount = atoi(argv[1]); /* Don't bother with format checking */
  is_aligned = atoi(argv[2]); /* Don't bother with format checking */

  printf("size of unaligned data : %d\n", sizeof(data));
  printf("size of aligned data   : %d\n", sizeof(aligned_data));

  void *val_0, *val_1;
  if (is_aligned) {
    val_0 = (void *)&aligned_data[0].val;
    val_1 = (void *)&aligned_data[1].val;
  } else {
    val_0 = (void *)&data[0].val;
    val_1 = (void *)&data[1].val;
  }

  int64_t start_time = current_time();

  /* Start the threads */
  pthread_create(&race_thread_1, NULL, (void* (*)(void*))worker1, val_0);
  pthread_create(&race_thread_2, NULL, (void* (*)(void*))worker2, val_1);

  /* Wait for the threads to end */
  pthread_join(race_thread_1, NULL);
  pthread_join(race_thread_2, NULL);

  int64_t end_time = current_time();

  printf("time : %d us\n", end_time - start_time);

  return 0;
}

```

代码很简单，不需要太多解释，重点看下perf结果：

```bash
[jingyan.kfy@OceanBase224006 work]$ perf stat -e cache-misses ./false_share 100000000 0
size of unaligned data : 16
size of aligned data   : 128
worker2 start...
worker1 start...
worker1 exit...
worker2 exit...
time : 452451 us

 Performance counter stats for './false_share 100000000 0':

         3,105,245 cache-misses

       0.455033803 seconds time elapsed

[jingyan.kfy@OceanBase224006 work]$ perf stat -e cache-misses ./false_share 100000000 1
size of unaligned data : 16
size of aligned data   : 128
worker1 start...
worker2 start...
worker1 exit...
worker2 exit...
time : 326994 us

 Performance counter stats for './false_share 100000000 1':

            27,735 cache-misses

       0.329737667 seconds time elapsed

```

可以看出在进行了aligned之后减少了非常多cache-misses，运行速度也加快了很多。

PS：这个代码只能定性的说明False sharing对性能是有影响的，如果想要定量的分析False sharing对性能的影响，那就需要结合所使用CPU的架构来做具体分析。

## Reorder


回到正题，在有了Cache-Coherence协议之后，似乎一切看上去都很完美，即使在多核环境下，cache之间仍然维持了一致，似乎我们并不需要考虑什么？

可惜的是，事实并非如此...

CPU的设计者实在是太聪明了，为了提高CPU的性能，CPU设计者做出了非常多的优化，以至于在外界看来，似乎CPU在以完全不可理喻的方式运行...CPU是不是疯了？为了解释这一点，我们首先需要明白CPU对执行顺序的约定是怎样的.

### 美好的Sequential Consistency

在程序员的直觉里，不论多核与否，所有线程的执行顺序（内存读写顺序）都应该和我们源码中所写的保持一致，并且所有核看到的某个线程的执行顺序（内存读写顺序）都应该是一致的，这就是Sequential Consistency。

然而，现在的多核CPU由于性能发展的要求，采用了各种各样的手段来加快运算速度，Sequential Consistency对CPU性能的提高是一个很强的阻碍，因此现在的CPU大都选择不同程度的违背Sequential Consistency的要求来达到提高执行速度的目的，CPU所提供保障的底线是：**在单核看来，线程的内存读写顺序要和源码中所写的一致。**

### CPU重排

那CPU为什么要对指令进行重排呢？回到我们对Cache-Coherence协议的分析，我们会发现一些比较慢的操作。

首先一点，当CPU需要写入一个“Shared”状态的cache line时，它向其他CPU发出“Invalidate”消息，而在收到其他CPU“Invalidate Acknowledge”回复之前都必须等待，这就对内存写入操作造成了一个阻塞，如下图：

[![](/assets/images/perfc_4.png)](/assets/images/perfc_4.png)

为了避免这个阻塞，聪明的CPU设计者在CPU和cache之间加入了一个缓冲Store Buffer，当执行store操作时，CPU无需阻塞等待其他CPU的回复，而是直接将该store操作缓冲在Store Buffer中，然后继续执行后续操作，当收到其他所有CPU的回复后再把数据从Store Buffer中移入cache，和cache一样，Store Buffer也是CPU局部的，一个CPU不能访问除自己以外的Store Buffer，如下图：

[![](/assets/images/perfc_6.png)](/assets/images/perfc_6.png)

对执行store操作的CPU本身来说这是一个绝妙的点子，因为CPU对内存的读取也会先查询Store Buffer中缓存的store指令，所以在执行store指令的CPU自己看来是维持了指令的执行顺序的，然而对其他CPU来说就没有那么幸运了...试想如下场景：

1. CPU 0先修改cache line c1上的数据，c1处于“Shared”状态，CPU 0发出“Invalidate c1”消息后将store指令存入Store Buffer
2. CPU 0修改cache line c2上的数据，c2处于“Exclusive”状态，则直接写入到cache中
3. CPU 1从CPU 0获取了c2（通过“Read”消息）
4. CPU 1在还没有收到“Invalidate c1”消息时从cache读出了处于“Shared”状态的c1

这样在CPU 1看来CPU 0的两次修改操作就出现了重排，即CPU1看到了CPU0后做的修改c2却没有看到先做的修改c1。

情况看上去是不是很糟，然而这还不算完...CPU设计者很快又注意到另一个问题：Store Buffer的大小是有限的，如果“Invalid Acknowledge”回复到达的速度不够快，Store Buffer将会很快被填满，CPU就又必须阻塞等待store指令完成了，于是乎他们在每个CPU上又加了一个Invalidate Queue，它的作用很简单，就是加速“Invalidate”消息的处理速度，当cache收到“Invalidate”消息后不马上执行cache line的invalidate操作（有些耗时），而是把这个消息缓存在Invalidate Queue之后直接回复“Invalidate Acknowledge”消息，之后cache再异步的处理Invalidate Queue中的消息，如下图：

[![](/assets/images/perfc_7.png)](/assets/images/perfc_7.png)

这样的设计使得多个CPU之间的关系更加复杂了，由于Invalidate Queue导致“Invalidate”消息的处理被延迟，所以CPU先发出的load操作有可能读出已经被确认“Invalidate”但在本地状态还没有切换的cache line，导致CPU的load操作好像也是会乱序的。

### 编译器重排

更加雪上加霜的是...不光是CPU，编译器也会在更高层次上进行优化，只要编译器认为不会有影响的，编译器会把对变量的操作顺序重新排列，甚至直接消除。

## 如何写正确的程序


看到这里是不是觉得CPU和编译器的设计者简直都是疯子，在这样的平台上还如何能够愉快的写代码？简直寸步难行有木有...

庆幸的是，CPU和编译器的设计者除了做出这些优化之外，也给我们留下了后路，让我们能够在需要时使用这些工具来抑制CPU和编译器的优化功能，保证程序的正确性，这就是memory barrier和编译器屏障。

PS：回顾前文，为什么使用pthread库的程序就不需要考虑这些复杂的情况呢？这些库在CPU和编译器看来也并没有什么特别的，原因在于库的编写者已经仔细的考虑了这些情况，并且在库的代码中加入了适当的memory barrier，减轻了库使用者的负担。

### memory barrier

对于编译器来说，编译器屏障即程序中插入的asm volatile("" ::: "memory"); ，其作用是告诉编译器，不管怎么优化，程序的读写操作影响不能跨过这个“屏障”，通俗的说就是告诉编译器不要自作聪明，在屏障后的读写都老老实实去内存位置上读写，不能偷懒使用“屏障”之前的临时结果。

CPU针对可能出现的重排给出三种memory barrier（不同体系结构的CPU都不太一样，这里给出通常的定义）：

- **写屏障（store fence）**：维持屏障前后的store操作的偏序关系，即屏障后的store一定发生在屏障前的store之后，结合之前所讲的CPU优化机制，写屏障的作用在于在Store Buffer，实现上既可以等待Store Buffer清空，也可以在Store Buffer中写入一个标记，并禁止后续的store指令直接写入cache，转而写入Store Buffer中，直到Store Buffer中没有标记才恢复正常
- **读屏障（load fence）**：维持屏障前后的load操作的偏序关系，即屏障后的load一定发生在屏障前的load之后，结合之前所讲的CPU优化机制，读屏障的作用在于Invalidate Queue，读屏障会强制等待Invalidate Queue清空才继续执行，这样可以消除其引发的读乱序问题
- **全屏障（full fence）**：作用相当于前两者加起来

关于memory barrier，还有几点是必须要明确的：

1. **memory barrier并不提供时间保障**：即使是非常有经验的程序员，也总会使用“刷cache”这样的说法来形容store fence，意思是使用store fence指令后就可以确保数据进入cache中了，实际上这种描述是不稳妥的，memory barrier并没有提供时间上的保障，store fence指令执行结束并不代表Store Buffer已经清空写入了cache中（所谓的“全局可见”），memory barrier只是提供了barrier前后指令的偏序关系保证
2. **memory barrier没有办法对其他CPU产生影响**：在某一CPU上执行的memory barrier指令并没有办法对其他CPU的cache和执行产生直接影响，只会改变其他CPU看到的本CPU的内存访问顺序。
3. **memory barrier需要成对使用**：即使使用了store fence维持了屏障前后的store操作偏序关系，由于Invaliate Queue的影响，其他CPU可能仍无法看到正确的顺序，因此往往在程序中store fence要和load fence成对使用。

Tips：不管是编译器屏障还是CPU屏障，其真实的作用都是抑制优化，是对性能有损的。所以，在使用这些机制时一定要慎之又慎，仔细考量方可。即使在Linux内核的编程中，也是不建议直接使用这些底层工具的，而总是首选一些易用的封装好的同步机制（如RCU）。

### 慎用volatile

C/C++的程序员应该对volatile都很熟悉了，但volatile在多线程并行编程中实际实际上也是最容易被误用的。在变量声明前加上volatile表示该变量“可能被意外的修改（当前流程之外）”，要求编译器在每次使用该变量时都要从内存地址中读出最新值。

这意味着对编译器优化的抑制，也就是性能的降低。更糟的是，通常程序中对volatile的使用都无法达到你想要的效果。

这是因为单单保证编译器不优化掉读操作**并不能保证CPU不会产生乱序行为**，如果读操作被提前，即使没有被优化掉也可能读出你意料之外的值，让我们看个例子，下面是一种[Dekker算法](https://en.wikipedia.org/wiki/Dekker%27s_algorithm)的实现：

```cpp
/*
 * Dekker's algorithm, implemented on pthreads
 *
 * To use as a test to see if/when we can make
 * memory consistency play games with us in
 * practice.
 *
 * Compile: gcc -O2 -o dekker dekker.c -lpthread
 * Source: http://jakob.engbloms.se/archives/65
 */

#include <cstdio>
#include <stdio.h>
#include <time.h>
#include <cstdlib>

static volatile int flag1 = 0;
static volatile int flag2 = 0;
static volatile int turn  = 1;
static volatile int gSharedCounter = 0;
int gLoopCount;
int gOnePercent;

void dekker1(void) {
  flag1 = 1;
  turn = 2;
  // __sync_synchronize();
  while((flag2 == 1) && (turn == 2)) ;
  // Critical section
  gSharedCounter++;
  // Let the other task run
  flag1 = 0;
}

void dekker2(void) {
  flag2 = 1;
  turn = 1;
  // __sync_synchronize();
  while((flag1 == 1) && (turn == 1)) ;
  // critical section
  gSharedCounter++;
  // leave critical section
  flag2 = 0;
}

//
// Tasks, as a level of indirection
//
void *task1(void *arg) {
  int i,j;
  printf("Starting task1\n");
  // Do the dekker very many times
#ifdef PRINT_PROGRESS
  for(i=0;i<100;i++) {
    printf("[One] at %d%%\n",i);
    for(j=gOnePercent;j>0;j--) {
      dekker1();
    }
  }
#else
  // Simple basic loop
  for(i=gLoopCount;i>0;i--) {
    dekker1();
  }
#endif
}

void *task2(void *arg) {
  int i,j;
  printf("Starting task2\n");
#ifdef PRINT_PROGRESS
  for(i=0;i<100;i++) {
    printf("[Two] at %d%%\n",i);
    for(j=gOnePercent;j>0;j--) {
      dekker2();
    }
  }
#else
  for(i=gLoopCount;i>0;i--) {
    dekker2();
  }
#endif
}

int
main(int argc, char ** argv)
{
  int loopCount = 0;
  pthread_t dekker_thread_1;
  pthread_t dekker_thread_2;
  void * returnCode;
  int result;
  int expected_sum;

  /* Check arguments to program*/
  if(argc != 2)
    {
      fprintf(stderr, "USAGE: %s \n", argv[0]);
      exit(1);

    }

  /* Parse argument */
  loopCount = atoi(argv[1]); /* Don't bother with format checking */
  gLoopCount = loopCount;
  gOnePercent = loopCount/100;
  expected_sum = 2*loopCount;

  /* Start the threads */
  result = pthread_create(&dekker_thread_1, NULL, task1, NULL);
  result = pthread_create(&dekker_thread_2, NULL, task2, NULL);

  /* Wait for the threads to end */
  result = pthread_join(dekker_thread_1,&returnCode);
  result = pthread_join(dekker_thread_2,&returnCode);
  printf("Both threads terminated\n");

  /* Check result */
  if( gSharedCounter != expected_sum ) {
    printf("[-] Dekker did not work, sum %d rather than %d.\n", gSharedCounter, expected_sum);
    printf("%d missed updates due to memory consistency races.\n", (expected_sum-gSharedCounter));
    return 1;

  } else {
    printf("[+] Dekker worked.\n");
    return 0;
  }
}

```

在这个例子中我们可以看到关键变量flag1、flag2和turn已经声明为volatile了，如果就此认为线程总能读到这三个变量的“最新值”，那Dekker算法已经被理论证明是正确的（可以尝试推导看看），那么结果如何呢？我在多核x86机器上（关于体系结构的说明见后文）运行了该程序：

```
➜  test git:(master) ✗ ./dekker 10000000
Starting task2
Starting task1
Both threads terminated
[-] Dekker did not work, sum 19999915 rather than 20000000.
85 missed updates due to memory consistency races.

```

显然结果是不正确的，问题就在于volatile并不能保证能够读到“最新”的值，它只保证了编译器每一次都生成load操作，而CPU所产生的乱序却使得该load操作读到了“旧值”，导致了混乱。在代码中合适的位置添加memory barrier即可防止这种异常（去掉注释即可）。

上面的例子说明单独使用volatile很有可能无法得到你想要的结果。所以，当你要使用volatile时，一定要思考清楚究竟为什么要用它？是否需要使用memory barrier？是不是对编译器优化产生了无谓的抑制？

[Linux内核社区对volatile的思考](https://www.kernel.org/doc/Documentation/volatile-considered-harmful.txt)中提到，在Linux内核中使用volatile的场景绝大部分都是错误使用，这也足以证明随意使用volatile的危险性：即使对聪明的Linux内核开发人员来说，也常常难以正确的使用volatile。

我的想法是：存在即有道理，volatile的存在一定是有其使用场景的，但volatile也确实是一个非常危险的关键字，在想要使用volatile时一定要谨记在心：“volatile**只是**对编译器起作用，让编译器老老实实的按照程序描述生成变量store/load指令”，然后再问自己一个问题：这真的是你想要的效果么？

## x86体系结构


即使有了这些用来抑制优化的工具，是不是仍然感觉难以写出正确的代码...可能发生乱序的情况如此之多，似乎在任何时候都需要考虑要不要使用memory barrier，实在是太复杂了。

没错，在多核环境并行编程就是这么复杂，但前提是你要写的是**可移植**的代码。因为不同体系结构的CPU实现有很大差别，所以他们所提供的顺序保证也一定是不同的。x86平台作为目前最为流行的体系结构，实际上已经为我们提供了很强的顺序性保证了，如下图：

[![](/assets/images/perfc_5.png)](/assets/images/perfc_5.png)

可以看到x86体系结构中只会发生一种乱序(忽略图中最后一列，最后一列的含义是指令cache的一致性，不在讨论范围内)：store-load乱序，举个例子，如下图在两个CPU上并行执行代码：

[![slreorder](/assets/images/slreorder.png)](/assets/images/slreorder.png)

在CPU代码中，两个线程都是先执行store操作（x和y的初始值都是0），然后再执行load操作，按照这个逻辑，我们可以确认执行完毕后后r1和r2的值至少有一个是1。然而在x86体系结构中由于会出现store-load乱序，所以两个线程的store-load执行顺序都有可能产生变化，如下图：

[![slreorder2](/assets/images/slreorder2.png)](/assets/images/slreorder2.png)

所以可能会产生r1和r2都为0的执行结果，这是不符合程序执行逻辑的。下面让我们通过程序实际验证这种乱序行为（上文中的Dekker算法也是一个例子）：

```cpp
/*
 * Demo program for catching cpu reorder behaviors
 *
 * Compile: g++ -O2 -o reorder reorder.cpp -lpthread
 * Usage: ./reorder 
 */

#include <sys/time.h>
#include <cstdio>
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <cstdlib>

int gLoopCount;
int A, B, X, Y;

inline int64_t current_time()
{
  struct timeval t;
  if (gettimeofday(&t, NULL) < 0) {
  }
  return (static_cast(t.tv_sec) * static_cast(1000000) + static_cast(t.tv_usec));
}

void* worker1(void *arg)
{
  X = 1;
  asm volatile("" ::: "memory");
  A = Y;
}

void* worker2(void *arg)
{
  Y = 1;
  asm volatile("" ::: "memory");
  B = X;
}

int main(int argc, char *argv[])
{
  pthread_t race_thread_1;
  pthread_t race_thread_2;

  int64_t count = 0;

  /* Check arguments to program*/
  if(argc != 2) {
    fprintf(stderr, "USAGE: %s \n", argv[0]);
    exit(1);
  }

  /* Parse argument */
  gLoopCount = atoi(argv[1]); /* Don't bother with format checking */

  for (int i = 0; i < gLoopCount; ++i) {
    X = 0;
    Y = 0;

    /* Start the threads */
    pthread_create(&race_thread_1, NULL, (void* (*)(void*))worker1, NULL);
    pthread_create(&race_thread_2, NULL, (void* (*)(void*))worker2, NULL);

    /* Wait for the threads to end */
    pthread_join(race_thread_1, NULL);
    pthread_join(race_thread_2, NULL);

    if (A == 0 && B == 0) {
      printf("reorder caught!\n");
      count++;
    }

  }

  printf("%d reorder cought in %d iterations.\n", count, gLoopCount);

  return 0;
}

```

在多核x86机器上运行该程序会发现冲突：

```bash
➜  test git:(master) ✗ ./reorder 100000
reorder caught!
reorder caught!
reorder caught!
...
164 reorder cought in 100000 iterations.

```

在store-load操作之间加上memory barrier指令（例如使用GNU C的 \_\_sync\_synchronize(); )后可以消除这种异常。

Trade off无处不在，对CPU设计人员也是一样，如果使用更多的Trick，虽然可以达到更高的指令执行速度，但却要为上层程序开发人员带来更大的负担。一般来说，如果你只是编写在x86平台上运行的代码，那么只需要考虑store-load乱序就可以了，这也是x86体系结构为我们提供的巨大便利。

## What's next


这篇文章概要性的介绍了一些在多核环境中并行编程所需要注意的几个基本问题，还有很多问题没有展开探讨，以后可能会写基于一些细节展开进行分析，以及lock-free数据结构、内存回收技术相关的文章。

## 参考资料

[^perfbook]: Is Parallel Programming Hard, And, If So, What Can You Do About It?
