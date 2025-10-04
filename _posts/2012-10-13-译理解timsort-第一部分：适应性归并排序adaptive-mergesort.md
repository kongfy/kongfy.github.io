---
title: "[译]理解timsort, 第一部分：适应性归并排序(Adaptive Mergesort)"
date: 2012-10-13
categories: 
  - "algorithm"
tags: 
  - "算法"
---

Python2.3中开始使用的timsort应该说算是声名在外了，不管是在稳定性还是在速度上都十分的惊人。 前一段刚刚看了《Python CookBook》中的一些章节，对timsort产生了一些兴趣。于是在网上看到了这边文章，讲的相当清楚明了，于是产生了翻译的念头，也于是有了这篇文章。

这应该算是我翻译的第一篇技术文章，真正做一次才明白能看懂和能翻译出来还是有蛮大的差距的。翻译质量不可谓不差，诸位如果英文阅读无障碍，强烈建议移步原文：[Understanding timsort, Part 1: Adaptive Mergesort](http://www.drmaciver.com/2010/01/understanding-timsort-1adaptive-mergesort/)，如果你不幸看了下面的坑爹译文，欢迎留下各种吐槽！闲话少说，上主菜：

* * *

Python的timsort常常被认为是很复杂、可怕的。这是可以理解的，因为其中包含了太多的细节。但是，如果你真正的了解它，你会发现它其实只是对归并排序进行了一系列的改进。其中有一些是很聪明的，而也有一些是相当简单直接的。这些大大小小的改进聚集起来使得算法的效率变得十分的吸引人。

我将会通过一些例子告诉你如何从一个最基本的归并排序开始逐步得到timsort。在本文中我会讲述如何得到timsort的“核心”:基本的适应性归并排序。后续的文章会在此基础上讲述timsort中使用的其他特别的优化。 <!--more--> 为了简单起见，我将只考虑整数（integers）数组而不是更通用的情况（这使得代码更容易理解，并且当你理解之后，也很容易改写为更通用的算法）。另外，这只是一个概述，所以我会忽略很多细节（或许会有一些明显的错误），所以如果你想看到更多精确的细节，请参考[Tim Peters's description of the algorithm](http://svn.python.org/projects/python/trunk/Objects/listsort.txt)

噢，还有示例代码是使用C编写的，Sorry(Why?)。

我们将要从一个非常朴素的归并排序开始。

希望你已经了解归并排序的原理了（如果没有，你需要去了解一下），让我们来复习一下：长度为1的数组是已经排序好的。对长度为n>1的数组，将其分为2段(partition)（最常见的做法是从中间分开）。对两段数组递归进行归并排序，完成后将其合并（merge）：通过扫描个已排序的数组并总是挑出两者中较小数作为合并数组中的下一个元素，来将两个已排序数组合并形成一个更大的已排序数组。

下面是代码：

```cpp
#include "timsort.h"
#include <stdlib.h>
#include <string.h>
 
// 将两个长度分别为l1, l2的已排序数组p1, p2合并为一个
// 已排序的目标数组。
void merge(int target[], int p1[], int l1, int p2[], int l2);
 
void integer_timsort(int array[], int size){
    if(size <= 1) return;
 
    int partition = size/2;
    integer_timsort(array, partition);
    integer_timsort(array + partition, size - partition);
    merge(array, array, partition, array + partition, size - partition);
}
 
void merge(int target[], int p1[], int l1, int p2[], int l2){
    int *merge_to = malloc(sizeof(int) * (l1 + l2));
 
    // 当前扫描两数组的位置
    int i1, i2;
    i1 = i2 = 0;
 
    // 在合并过程中存放下一个元素的位置
    int *next_merge_element = merge_to;
 
    // 扫描两数组，将较小的元素写入
    // merge_to. 当两数相等时我们选择
    // 左边的, 因为我们想保证排序的稳定性
    // 当然对于integers这无关紧要，但这种想法是很重要的
    while(i1 < l1 && i2 < l2){
        if(p1[i1] <= p2[i2]){
            *next_merge_element = p1[i1];
            i1++;
        } else {
            *next_merge_element = p2[i2];
            i2++;
        }
        next_merge_element++;
    }
 
    // 如果有一个数组没有扫描完，我们直接拷贝剩余的部分
    memcpy(next_merge_element, p1 + i1, sizeof(int) * (l1 - i1));
    memcpy(next_merge_element, p2 + i2, sizeof(int) * (l2 - i2));
 
    // 现在我们已经将他们合并在了我们的额外的存储空间里了
    // 是时候转存到target了
    memcpy(target, merge_to, sizeof(int) * (l1 + l2));
 
    free(merge_to);
}
```

我不会总是贴出完整的代码，你可以在github上根据不同的版本来[查看他们](http://github.com/DRMacIver/understanding-timsort)

现在，如果你是一个C程序员，你可能已经在吐槽了：我在每次合并过程中都申请并释放了一次额外存储空间（你可能也会不爽于我没有检查返回值是否为null,请无视之...如果这能让你感觉好一点）

这个问题只要一点点的改动就可以修正： 

```cpp
void merge(int target[], int p1[], int l1, int p2[], int l2, int storage[]);
void integer_timsort_with_storage(int array[], int size, int storage[]);
 
void integer_timsort(int array[], int size){
    int *storage = malloc(sizeof(int) * size);
    integer_timsort_with_storage(array, size, storage);
    free(storage);
}
```

现在我们有了排序函数的最顶层，做了一些内存分配（setup）工作并将其传入调用中。这是我们将要开始优化工作的模版，当然最后实际可用的版本会更加复杂而不仅仅是优化一块内存空间。

现在我们有了基本的归并排序了，我们需要想想：我们能怎样来优化它？

一般来说我们不能指望对于每一种情况都能达到最优。归并排序的性能已经很接近比较排序的下界了。timsort的关键特性是极好的利用了数据中存在的规律。如果数据中存在普遍的规律，我们应该尽可能的利用他们，如果没有，我们的算法应该保证不会比普通的归并排序差太多。

如果你看过归并排序的实现，你会发现其实所有的工作都是在合并（merge）的过程当中完成的。所以优化的重点也就落在了这里。由此我们得出以下三点可能的优化途径：

1、能否使合并过程运行的更快？ 2、能否执行更少的合并过程？ 3、是否存在一些与其使用归并排序不如使用其他排序的情况？

以上三个问题的答案都是肯定的，并且这也是对归并排序进行优化最为普遍的途径。举例来说，递归的实现使得根据数组的规模使用不同的排序算法变的非常简单。归并排序是一个很好的通用性排序算法，（具有很好的渐进复杂度）但对小数组而言常数因子就显得愈发重要，当数组的大小小于某个值时（通常是7或者8左右）归并排序的性能频繁的低于插入排序。

这并不是timsort的原理，但是我们之后会用到插入排序，所以我们先开个小差。

最简单的：假设我们有一个具有n个元素的已排序数组，并且在尾端有第n+1个元素的位置。现在我们想要向里面添加一个新的元素并保持数组有序。我们需要为新元素找到一个合适的位置并将比它大的数向后移动。一种显而易见的做法是将新元素放到第n+1个位置上，然后从后向前两两交换直到到达正确的位置（对较大的数组这并不是最好的做法：你可能想要对数据进行二分查找（binary search）然后把剩下的元素不做比较的向后移动。但是对小数组来说这样的做法反而不是很好，due to cache effects）

这就是插入排序工作的方式：当你有了k个已排序的元素，将第k+1个元素插入其中，你就有了k+1个已排序的元素。反复如此直到整个数组有序。

下面是代码： 

```cpp
void insertion_sort(int xs[], int length){
    if(length <= 1) return;
    int i;
    for(i = 1; i < length; i++){
        // i之前的数组已经有序了，现在将xs[i]插入到里面
        int x = xs[i];
        int j = i - 1;
 
        // 将j向前移动直到数组头或者
        // something <= x, 并且其右边的所有的元素都已经
        // 右移了
        while(j >= 0 && xs[j] > x){
            xs[j+1], xs[j];
             j--;
        }   
        xs[j+1] = x;
    }
}
```

现在排序的代码会被修改为下面这样： 

```cpp
void integer_timsort_with_storage(int array[], int size, int storage[]){
    if(size <= INSERTION_SORT_SIZE){
        insertion_sort(array, size);
        return;
    }
}
```

你可以在[这里](http://github.com/DRMacIver/understanding-timsort/commit/57a91bd8c5383ffa1e0e5dc1df0849e16ec037bd)查看这个版本

好了，让我们回归正题：优化归并排序。

能否执行更少的合并过程？

对于一般的情况，不行。但是让我们考虑一些普遍存在的情况。

假设我们有一个已经排好序的数组，我们需要执行多少次合并过程？

原则上来说1次也不需要：数组已经排好序了，不需要做任何多余的工作。所以一个可行的选择是增加一个初始的检查来确定数组是否已经排好序了并在确认之后立刻退出。

但是那样会给排序算法增加很多额外的计算，虽然在判断成功的情况下带来很大的收益（将O(nlog(n))的复杂度下降到O(n)），但是如果判断失败了，会造成很多无用的计算。下面让我们看看我们该怎样实现这种检查并且无论其失败与否都能将检查的结果很好的利用起来。

假设我们遇到了下面的数组：

{5, 6, 7, 8, 9, 10, 1, 2, 3}

（现在暂且忽略我们会对小于n的数组使用不同的排序方法）

为了得到最好的合并策略，我们应该在哪里进行分段呢？

显然在这里有两个已经排好序的子数组：5到10和1到3，如果选择这两段作为分段必然可以获得很好的效果。

接下来提出一种片面的方法：

找出初始状态下最长的上升序列作为第一个分段（partition）,剩余部分作为第二个分段。

当数据是由不多的几个已排序的数组组成的情况下，这种方法表现的很好，但是这种方法存在十分糟糕的最差情况。考虑一个完全逆序的数组，每次分段的第一段都只有一个数，所以在每次递归中第一段只有一个数，而要对第二段的n-1个元素进行递归的归并排序。这造成了明显不令人满意的O(n^2)的性能表现。

我们也可以人工的将过短的分段修改为总长度一半的元素以避免这个问题，但是这同样也是不令人满意的：我们额外的检查工作基本没有什么收益。

但是，基本的思路已经明确了：利用已经有序的子序列作为分段的单位。

困难的是第二段的选择，为了避免出现糟糕的最差情况，我们需要保证我们的分段是尽可能的平衡的。

让我们退一步看看是否有办法改正它。考虑下面这种有些奇怪的对普通归并排序工作过程的逆向思考：

将整个数组切分成很多长度为1的分区。

当存在多个分区时，奇偶交替的两两合并这些分区（alternating even/odd）并用合并后的分区替代原先的两个分区。

{% raw %}
举例来说，如果我们有数组｛1, 2, 3, 4｝那么我们会这么做：  
{{1}, {2}, {3}, {4}}  
{{1, 2}, {3, 4}}  
{{1, 2, 3, 4}}  
{% endraw %}

很容易观察到这和普通归并排序的做法是相同的：我们只是将递归的过程变的明确并且用额外的存储空间取代了栈。但是，这样的方法更直观的展现了我们应该如何使用存在的已排序子序列：在第一步中，我们不将数组分割为长度为1的分段，而是将其分割成很多已排序的分段。然后对这些分段以相同的方法执行合并操作。

现在这个方法只有一个小问题了：我们使用了一些并不需要使用的额外空间。普通的归并排序使用了O(log(n))的栈空间。这个版本使用了O(n)的空间来存储初始的分段情况。

那么为什么我们“等价的”算法却有极为不同的空间消耗？

答案是我在他们的“等价”上面撒谎了。这种方法与普通的归并排序最大的不同在于：普通归并排序在分段操作上是“惰性”的，只有在需要生成下一级时才会生成足够的分段并且在生成了下一级之后就会立刻的丢弃这些分段。

换句话说，我们其实是在归并的过程中边合并边生成分段而不是事先就生成了所有的分段。 现在，让我们看看能否将这种想法转换成算法。

在每一步中，生成一个新的最低级的分段（在普通归并排序中这是一个单独的元素，在我们的上面叙述的版本中这是一个已排序的子序列）。把它加入到一个存储分段的栈中，并且不时的合并栈顶的两个分段以减小栈的大小。不停的重复这样的动作直到没有新的分段可以生成。然后将整个堆栈中的分段合并。

上面的算法还有一个地方没有具体说明：我们完全没有说明何时来执行合并操作。

到此为止已经有太多的文字而代码太少了，所以我打算给出一个暂时的答案：随便什么时候（好坑爹）。

现在，我们先写一些代码。 

```cpp
// 我们使用固定的栈大小，这个大小要远远大于任何合理的栈高度
// 当然，我们仍然需要对溢出进行检查
#define STACK_SIZE 1024
 
typedef struct {
    int *index;
    int length;
} run;
 
typedef struct {
    int *storage;
    // 存储已经得到的分段(runs,原文作者将得到分段叫做run)
    run runs[STACK_SIZE];
    // 栈顶指针，指向下一个待插入的位置
    int stack_height;
 
    // 保持记录我们已经分段到哪里里，这样我们可以知道在哪里开始下一次的分段
    // 数组中index < partioned_up_to 是已经分段并存储在栈上的, 而index >= partioned_up_to
    // 的元素是还没有存储到栈上的. 当partitioned_up_to == 数组长度的时候所有的元素都在栈上了
    int *partitioned_up_to;
 
    int *array;
    int length;
 
} sort_state_struct;
 
typedef sort_state_struct *sort_state;
```

我们将会给需要的所有函数传入`sort_state`的指针

这个排序的基础逻辑代码如下： 

```cpp
while(next_partition(&state)){
    while(should_collapse(&state)) merge_collapse(&state);
}
while(state.stack_height > 1) merge_collapse(&state);
```

`next_partition`函数如果还有未入栈的元素则将一个新的分段压入栈中并返回1，否则返回0。然后适当的压缩栈。最后当全部数组都分段完毕后将整个栈压缩。

现在我们有了第一个适应性版本的归并排序：如果数组中有很多有序的子序列，我们就可以走一个很好的捷径。如果没有，我们的算法依然有（期望）O(nlog(n))的时间效率。

这个“期望”的效率有点不靠谱，在随机的情况下我们需要一个好的策略来控制合并的过程。

我们来想一想是否有更好的限制条件。一个自然的想法来实现这个事情是在栈上维持一个不变式，不断的执行合并直到不变式满足为止。

更进一步，我们想要这个不变式来维持这个栈中最多只能有log(n)个元素

我们来考虑下面这个不变式：每个栈上的元素的长度必须>=两倍于其之下的元素长度，所以栈顶元素是最小的，第二小的是栈顶元素的下一个元素，并且至少是栈顶元素的两倍长度。

这个不变式确实保证了栈中log(n)个元素的要求，但是却造成了将每次栈的压缩变得很复杂的趋势，考虑栈中元素长度如下的情况：

64, 32, 16, 8, 4, 2, 1

假设我们将一个长度为1的分段放到栈上，就会产生如下的合并：  

64, 32, 16, 8, 4, 2, 1, 1  
64, 32, 16, 8, 4, 2, 2  
64, 32, 16, 8, 4, 4  
64, 32, 16, 8, 8  
64, 32, 16, 16  
64, 32, 32  
64, 64  
128 

在之后对合并过程做了更多的优化后，这种情况会显得愈发糟糕（basically because it stomps on certain structure that might be present in the array）。但是现在我们的合并过程还是很简单的，所以我们没有必要担心它，先暂时这样做就可以了。

有一件值得注意的事情：我们现在可以确定我们栈的大小了。假设栈顶元素的长度为1，第二个元素长度必然>=2，之后的必然>=4...所以栈中元素的总长度是2^n-1, 因为在64位机器中在数组中最多只会有2^64个元素（这是一个相当惊人的数组），所以我们的栈只需要最多65个元素，另外留出一个位置给新进栈的元素，则我们需要分配66的空间给栈以保证永远不会出现overflow的情况。

另外还有一点值得注意，我们只需要检查栈顶下面的一个元素长度>=2 \* 栈顶元素长度，因为我们在入栈过程中总是保持这个不变式的，并且合并过程只会影响到栈顶两个元素。

为了满足不变式，我们现在将`should_collapse`函数修改如下： 

```cpp
int should_collapse(sort_state state){
    if (state->stack_height <= 2) return 0;
 
    int h = state->stack_height - 1;
 
    int head_length = state->runs[h].length;
    int next_length = state->runs[h-1].length;
 
    return 2 * head_length > next_length;
}
```

现在，我们的适应性归并排序完成了，赞！

回过头看之前出过问题的一个例子现在会如何。

考虑下面的逆序数组：

5, 4, 3, 2, 1

当使用我们的适应性归并排序会发生什么？

栈的运行过程如下：  

{5}  
{5}, {4}  
{4, 5}  
{4, 5}, {3}  
{4, 5}, {3}, {2}  
{4, 5}, {2, 3}  
{2, 3, 4, 5}  
{2, 3, 4, 5}, {1}  
{1, 2, 3, 4, 5} 

这是一个足够清晰的合并策略了。

但是还有一个更好的办法来对逆序的数组进行排序：直接将其原地反转。

可以很简单的修改我们的算法来利用到这一点，我们已经寻找了递增的子序列，当找不递增的子序列的时候可以很简单的寻找一个递减的子序列，然后将其反转为一个递增的序列加入栈中。

根据上面的策略我们修改找序列的代码如下： 

```cpp
if(next_start_index < state->array + state->length){
    if(*next_start_index < *start_index){
        // We have a decreasing sequence starting here.
        while(next_start_index < state->array + state->length){
            if(*next_start_index < *(next_start_index - 1)) next_start_index++;
            else break;
        }
        // Now reverse it in place.
        reverse(start_index, next_start_index - start_index);
    } else {
    // We have an increasing sequence starting here.
        while(next_start_index < state->array + state->length){
            if(*next_start_index >= *(next_start_index - 1)) next_start_index++;
            else break;
        }
    }
}
```

和基本的逆序序列相同，我们的排序现在也可以很好的处理混合的情况了。比如下面这种数组：

{1, 2, 3, 4, 5, 4, 3, 2, 1}

执行排序过程如下：

{1, 2, 3, 4, 5}  
{1, 2, 3, 4, 5}, {1, 2, 3, 4}  
{1, 1, 2, 2, 3, 3, 4, 4, 5}  

这样的情况比我们之前的实现又要好上很多！

最后我们还要给算法加上一点优化：

在我们之前的归并排序中有存在一个临界点以便对于小数组转换为插入排序，但在目前我们的适应性版本中没有这样的设置，这意味着如果在没有很多特殊结构可利用的数组中我们的性能可能要低于普通的归并排序。

回头想想之前那个反转的归并排序的过程，将小数组改用插入排序的做法可以这样理解：比起从1的长度开始划分，我们从`INSERTION_SORT_SIZE`开始划分，并使用插入排序来确保这一段是有序的。

这提示了我们一个自然的思路来改进我们的适应性版本：当我们发现一个分段要小于一个设定值时，可以使用插入排序来将它增长到设定长度。

这使得我们更改了`next_partition`函数的最后面的代码如下： 

```cpp
if(run_to_add.length < MIN_RUN_SIZE){
    boost_run_length(state, &run_to_add);
}
state->partitioned_up_to = start_index + run_to_add.length;
```

boot\_run\_length函数如下：

```cpp
void boost_run_length(sort_state state, run *run){
    // Need to make sure we don't overshoot the end of the array
    int length = state->length - (run->index - state->array);
    if(length > MIN_RUN_SIZE) length = MIN_RUN_SIZE;
 
    insertion_sort(run->index, length);
    run->length = length;
}
```

这将算法应用在随机数据上时的性能表现提高到了一个和普通归并排序相比相当具有竞争力的程度。

到这里我们终于得到了一个适应性归并排序，一定程度上可以说是timsort的核心部分。timsort在此之上还添加了很多优化，这些优化也直接推动了它的成功，但是这个算法是所以其他优化的起点和基础。我希望并且计划可以在以后的文章中继续介绍其他的优化部分。
