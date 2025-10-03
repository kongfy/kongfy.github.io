---
title: "Copy List with Random Pointer"
date: 2014-06-06
categories: 
  - "algorithm"
tags: 
  - "leetcode"
---

> A linked list is given such that each node contains an additional random pointer which could point to any node in the list or null. Return a deep copy of the list.

题目链接在[这里](https://oj.leetcode.com/problems/copy-list-with-random-pointer/)。

题目要求对链表进行复制，不过这个链表稍微有点特殊：在每一个节点中除了指向下一个节点的指针，还有一个指向链表中随机节点的指针，如下： 

```cpp
struct RandomListNode {
    int label;
    RandomListNode *next, *random;
    RandomListNode(int x) : label(x), next(NULL), random(NULL) {}
};
```

这个链表看起来大概是这个样子：

<figure style="text-align: center;">
  <img src="/assets/images/0.png" alt="带有随机指针的链表" />
  <figcaption>带有随机指针的链表</figcaption>
</figure>

这个随机指针对链表的拷贝造成了不小的麻烦...

<!--more-->

最朴素的做法是先按照next指针将链表主链复制出来，然后对每一个节点计算出random指针所处的索引，并根据索引给对应的新链表中的指针赋值。这个方法是显然的，同时也是低效的，时间复杂度为O(n2)。

基于朴素解法，对遍历做一定改进的算法是在复制主链表时使用散列表来记录两个链表对应节点地址之间的关联关系，这样通过查询散列表可以实现快速找到原链表节点random指针对应的新链表节点random指针值，将时间复杂度降为O(n)，使用了O(n)的额外空间用于散列表。

而最为巧妙的，也是不太容易想到的一种方法可以使用O(n)的时间复杂度，并且在不是用额外空间的情况下解决这个问题。步骤如下：

1. 对链表进行遍历，对每个节点，复制一个新节点，并将其插入到链表中该节点后面的位置上
<figure style="text-align: center;">
  <img src="/assets/images/1.png" alt="Step 1" />
  <figcaption>Step 1</figcaption>
</figure>3. 再次对链表进行遍历，k = 1...n，将2k节点的random指针指向(2k - 1)节点的random指针所指向节点的后继节点
<figure style="text-align: center;">
  <img src="/assets/images/2.png" alt="Step 2" />
  <figcaption>Step 2</figcaption>
</figure>5. 最后一次对链表进行遍历，k = 1...n，将2k节点顺序抽出组成新链表
<figure style="text-align: center;">
  <img src="/assets/images/3.png" alt="Step3" />
  <figcaption>Step3</figcaption>
</figure>

```cpp
class Solution
{
public:
    RandomListNode *copyRandomList(RandomListNode *head)
    {
        if (!head) {
            return NULL;
        }
        
        RandomListNode *p = head, *q = NULL;
        while (p) {
            q = new RandomListNode(p->label);
            q->next = p->next;
            p->next = q;
            p = q->next;
        }
 
        p = head;
        q = NULL;
        while (p) {
            q = p->next;
            if (p->random) {
                q->random = p->random->next;
            }
            p = q->next;
        }
 
        p = head;
        q = NULL;
        RandomListNode *new_head = NULL, *tail = NULL;
        while (p) {
            q = p->next;
            p->next = q->next;
            
            q->next = NULL;
            if (!new_head) {
                new_head = q;
            } else {
                tail->next = q;
            }
            tail = q;
            
            p = p->next;
        }
        
        return new_head;
    }
};
```
