---
title: "[paper note]Consensus on Transaction Commit"
date: 2018-07-28
categories: 
  - "关系型数据库"
  - "distributed-system"
tags: 
  - "paxos"
disqus_identifier: "1703 http://blog.kongfy.com/?p=1703"
---

这篇论文的作者实在太吓人了，Jim Gray和Leslie Lamport，两个领域的扛把子。论文介绍的内容叫Paxos Commit，是用分布式共识算法解决分布式事务的原子提交问题，不愧是这两位大佬写出来的文章哈哈。

PS：这篇文章是我的paper note，主要是帮助自己理解和记忆，与其说是文章，其实更像是简单的笔记。

## 解决了什么问题


事务的属性是ACID，A代表原子性，事务要么全部提交，要么全部失败，不能出现提交了一半的情况。单机事务的原子性通过日志系统来保证，而在分布式事务里，通常的做法是两阶段提交（Tow Phase Commit，2PC）。

两阶段提交的一个重要问题是协调者宕机问题，参与者执行完Prepare状态后，参与者处于“未决”状态，意味着参与者自己无法决定事务状态，而如果此时协调者宕机，事务的状态将无法推进下去。

Paxos Commit希望解决这个问题，即在事务提交过程中，能够容忍F个副本失败而不会导致事务无法推进。

另外，论文中还提到了其他尝试解决此问题的方法（三阶段提交），并表示不屑一顾……....（三阶段提交实际上并没有改善提交过程的容灾）

<!--more-->

## Paxos Commit


实际上，分布式事务问题的核心也是一个分布式共识问题，即多个事务参与者要就事务提交还是回滚这个决定上达成共识。Lamport老爷子自然想到了用自己大名鼎鼎的Paxos算法来解决这个问题。

算法的基本思路是**用2F+1个acceptor来替代2PC中单一的协调者节点**，并将原本记录在参与者本地的Prepare/Abort日志改为Paxos的一个instance，记录在acceptor上。

[![](/assets/images/paxos-commit.png)](/assets/images/paxos-commit.png)

Paxos Commit算法还是非常清楚的，但要特别注意一些理解上容易出现的问题：**上图中的Leader并不是Paxos算法中的leader**（Paxos本身不需要leader，用来避免live lock），而是专门负责推动事务状态的一个角色。

当事务提交发起时，Leader会向所有参与者（RM）发起事务的Prepare请求（区别于Paxos的prepare），参与者收到请求后，根据本地情况决定Prepare还是Abort，并将该决定通过Paxos的accept消息发送给acceptors。这一步中省略了Paxos算法的prepare步骤，而是**直接使用proposal number 0发送accept消息**，本质上执行完整的Paxos是没有任何问题的，这样做是为了让整体的事务提交时延和2PC保持一致。

acceptor将Paxos的acceptAck消息直接返回给事务的Leader（为了优化消息数，没有回复参与者），当Leader得知所有的参与者对应的Paxos instance都就Prepare达成一致后，向参与者发出Commit请求。

考虑异常情况，Paxos保证在2F+1个acceptors可以容忍F个acceptor宕机；而如果参与者在没有把状态“写”到对应的Paxos instance里之前宕机，则Leader在达到事务超时后会使用**更大的proposal number**在这些Paxos instance上执行标准Paxos算法，并以Abort作为value，达到事务回滚的目的；由于事务的状态完全存储在acceptor上，Leader并不保存任何状态，因此Leader宕机可以重新选一个即可。

## 和2PC比较


Paxos算法在本质上和2PC的思想是一样的，只是有一些设计上的区别。

2PC的协调者在收到所有参与者的Prepare回复后要写Commit日志，而Paxos Commit没有。在2PC中，即使所有参与者都回复Prepare，协调者依然可以选择Abort，然而Paxos Commit中事务的状态只取决于参与者的状态。但是实际上，如果所有参与者都Prepare，协调者没有理由选择Abort，协调者写日志的主要原因还是出于容灾考虑（参与者宕机，请自行思考），而在Paxos Commit中，参与者的状态是由多个acceptors共同保存的，并不需要担心参与者宕机。

另外就是2PC的参与者将Prepare/Abort的决定写在本地，而Paxos Commit则是由多个acceptors共同保存的，实际上，如果F=0（没有acceptor，参与者日志仍然写在本地），则Paxos Commit算法就会退化成协调者不写日志的2PC：

[![](/assets/images/2pc-paxos-commit.png)](/assets/images/2pc-paxos-commit.png)

## 一点想法


当前业界分布式事务所使用的方案，大多是使用Paxos来实现协调者的高可用副本，属于2PC+Paxos的组合方案，对比Paxos Commit，前者在逻辑分层上更为清晰，后者实际上打破了事务和日志的边界，做了很多前者无法做的优化。

在系统设计中常常会有这样的trade off，分层清晰的方案复杂度低，开发难度低，从设计上来说更为优雅，但融合的方案可以利用到很多分层结构无法使用的信息，难分高下。

## 参考文献


\[1\] Gray J, Lamport L. Consensus on transaction commit\[J\]. ACM Transactions on Database Systems (TODS), 2006, 31(1): 133-160.
