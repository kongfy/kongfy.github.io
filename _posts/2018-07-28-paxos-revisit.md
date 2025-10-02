---
title: "Paxos revisit"
date: 2018-07-28
categories: 
  - "distributed-system"
tags: 
  - "consensus"
  - "paxos"
---

前一段时间借着组里的实习生学习交流的机会，又重新讨论了一次Paxos算法，颇有收获。本文整理记录几个我个人觉得比较有意义的问题，希望通过思考这几个问题，能够加深你对Paxos算法的理解。

本文假定读者已经对Paxos算法有一定了解（包括原理、正确性证明、执行流程），如果你还不了解Paxos，请移步[这里](/posts/2016-05-*-%e5%88%86%e5%b8%83%e5%bc%8f%e5%85%b1%e8%af%86consensus%ef%bc%9aviewstamped%e3%80%81raft%e5%8f%8apaxos/)。

## Paxos算法流程

* * *

在思考问题之前，首先重温一下Paxos算法的流程，同时统一变量名称，方便后文讨论。

**Prepare阶段：**

1. Proposer选择proposal number n，并向acceptors发送Prepare(n)消息
2. Acceptor收到Prepare(n)：if n > minProposal then minProposal = n; return (acceptedProposal, acceptedValue)

**Accept阶段：**

1. 如果Proposer收到了超过多数派acceptors对于Prepare(n)的回复，如果回复中有包含acceptedValue，则选择acceptedProposal值最大的作为value，否则Proposer可以自行选择value
2. Proposer向所有acceptors发出Accept(n, value)消息
3. Acceptor收到Accept(n, value)：if n >= minProposal then acceptedProposal = n; acceptedValue = value，并回复AcceptAck(n)
4. Proposer收到来自多数派acceptors的AcceptAck消息，value已达成决议(chosen)

## 问题

* * *

在上述Paxos算法流程的基础上，仔细思考下面几个问题：

1. 为了保证算法在容灾（节点故障重启）场景下的正确性，Acceptor上需要持久化哪些信息？
    
2. 如果Acceptor不持久化acceptedProposal，在Prepare阶段的第2步中minProposal代替，有没有问题？
    
3. Accept阶段，Proposer不用n覆盖acceptedProposal，仍将其发送给Acceptor，Acceptor收到Accept(n, acceptedProposal, value)之后使用消息中的acceptedProposal而不是n来作为acceptedProposal，有没有问题？
    
4. 在5个节点的情况下，如果修改流程为Proposer要收到4个acceptor对Prepare(n)的回应才可以发送Accept消息，要收到2个acceptor对Accept(n, value)的回应才能确认决议，有没有问题？
    
5. 论文中提到Proposer选择proposal number要递增且不重复，这个要求是不是必要的？如果把Prepare阶段第2步中的>改为>=呢？
    

**WARNING： 强烈建议花一些来仔细思考上面的问题，在得出自己的答案之后再继续往下看**

<!--more-->

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  

## 解

* * *

免责声明：我并不能保证这里给出的答案一定是正确的，如果你发现了问题，欢迎一起讨论。

**1\. 为了保证算法在容灾（节点故障重启）场景下的正确性，Acceptor上需要持久化哪些信息？**

(minProposal, acceptedProposal, acceptedValue)

**2\. 如果Acceptor不持久化acceptedProposal，在Prepare阶段的第2步中minProposal代替，有没有问题？**

有问题，会导致已经形成决议的value被推翻，如下图例：

[![](/assets/images/paxos.png)](/assets/images/paxos.png)

注意在中间过程中blue已经达成了决议，但是后面由于prepare误认为red是之前的决议，而错误的把red重新达成决议。

**3\. Accept阶段，Proposer不用n覆盖acceptedProposal，仍将其发送给Acceptor，Acceptor收到Accept(n, acceptedProposal, value)之后使用消息中的acceptedProposal而不是n来作为acceptedProposal，有没有问题？**

有问题，会导致已经形成决议的value被推翻，如下图例：

[![](/assets/images/paxos2.png)](/assets/images/paxos2.png)

同样，在中间过程中red已经达成了决议，但是后面由于prepare误认为blue是之前的决议，而错误的把blue重新达成决议。

仔细分析这个问题，不难联想到Raft的做法：Raft更高Term的Leader会把自己的日志复制给其他人，但并没有修改这些日志的Term值，对比Paxos的做法，这就相当没有修改acceptedProposal。那么Raft算法为什么没有问题呢？因为Raft正确性保证的很重要的一点就是：更高Term的Leader不能按照多数派原则直接提交更低Term的日志，而依赖于后续使一条本Term的日志形成决议一起提交。

**4\. 在5个节点的情况下，如果修改流程为Proposer要收到4个acceptor对Prepare(n)的回应才可以发送Accept消息，要收到2个acceptor对Accept(n, value)的回应才能确认决议，有没有问题？**

从正确性来说是没有问题的，因为只要prepare和accept所需的副本个数之和超过总数，就可以保证只要一个值形成了决议，那么Prepare消息的回复中一定包含这个值。

问题在于容错性，Paxos算法保证的是容忍F个节点宕机，需要2F+1个节点。也就是说5节点可以容忍2节点宕机，上面提到的修改显然无法做到。

**5\. 论文中提到Proposer选择proposal number要递增且不重复，这个要求是不是必要的？如果把Prepare阶段第2步中的>改为>=呢？**

如果只需要保证协议的正确性，那么递增是不需要的，如果取的proposal number更小，则一定会被拒绝。选择递增只是为了效率的考虑。同样，不重复也不是必须的，重复的proposal number在Prepare阶段同样会被拒绝。

但是出于实现考量，我们总是希望如果出现网络消息丢失，可以进行重试，也就是说，需要把Prepare阶段的第2步中的>改为>=。这样一来，不重复就是必须的了，如果不同节点选择了相同的proposal number，就可能导致多个Proposer同时在同一个proposal number上发起Accept。

不重复是必要的，否则会出现错误：

[![](/assets/images/paxos3.png)](/assets/images/paxos3.png)

S1宕机恢复后如果重新用相同的proposal number执行Paxos，可能会收到过去的prepare ok消息（没有包含acceptedValue），导致覆盖决议。

一个更直接的反例是Fast Paxos论文中提到的方法，当使用相同的proposal number执行Paxos时，必须修改多数派的数量，才能保证协议的正确性。

## 写在最后

* * *

理解Paxos算法的关键还是要完全理解论文中的正确性证明，尤其是P1a和P2c两个条件。前者保证了proposal number更小的proposal无法干扰后续的决议，后者保证了已经达成的决议绝对不会被推翻。而前面2、3两个问题讨论的协议修改，就是违背了P2c，所以是不正确的。
