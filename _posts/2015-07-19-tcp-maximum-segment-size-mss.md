---
title: "TCP Maximum Segment Size (MSS)"
date: 2015-07-19
categories: 
  - "network"
tags: 
  - "ip"
  - "tcp"
---

这篇是一个小小的查缺补漏，还记得大三网络实验最后助教检查实验问过这个问题：“MSS是干什么的？”，当时背了个定义蒙混过去了，没有仔细理解，现在又遇到了，补上~

## MSS是什么？

下图中看到的是TCP连接发送和接收的过程示意图，最大报文段长度（MSS）的作用是限制在TCP层产生的报文段的最大长度（当然要在滑动窗口允许的前提下）。

<figure style="text-align: center;">
  <img src="/assets/images/ipov.fig88.epsi_.gif" alt="TCP发送接收过程图" />
  <figcaption>TCP发送接收过程图</figcaption>
</figure>

比如如果MSS为1000个字节，每个TCP报文的最大长度为1020字节（附加20字节TCP头部），之后传递到IP层加装20字节IP头部封装成为IP报文利用链路层发送。

<!--more-->

## 为什么要有MSS？

知其然更要知其所有然，知道了MSS的作用，那么为什么我们需要MSS的功能呢？难道不能生成一个任意大的TCP报文传递给IP层么？

要理解这个问题，就一定要牵扯到MTU的概念。[MTU（最大传输单元）](https://en.wikipedia.org/wiki/Maximum_transmission_unit)是链路层的概念，指的是一条路径上的允许传输的最大单元的大小。比如以太网的MTU为1500，这意味着以太网中通信的双方能够交互的最大单个报文的大小不能超过1500字节，在IP层由于有20字节的IP头部，则IP载荷不能超过1480。也就是说超过这个大小的IP报文必须经过分段才能够发送。

那么MTU和MSS又有什么必然联系呢？虽然MTU限制了IP层的报文大小，但分层网络模型本来不就是为了对上层提供透明的服务么？即使一个很大的TCP报文传递给IP层，IP层也应该可以经过分段等手段成功传输报文才对。

理论上来说是没错的，UDP中就不存在MSS，UDP生成任意大的UDP报文，然后包装成IP报文根据底层网络的MTU分段进行发送。MSS存在的本质原因就是TCP和UDP的根本不同：TCP提供**稳定**的连接。假设生成了很大的TCP报文，经过IP分段进行发送，而其中一个IP分段丢失了，则TCP协议需要重发整个TCP报文，造成了严重的网络性能浪费，而相对的由于UDP无保证的性质，即使丢失了IP分段也不会进行重发。所以说，MSS存在的核心作用，就是避免由于IP层对TCP报文进行分段而导致的性能下降。

## 如何挑选合适的MSS？

从上面的分析我们可以看到，挑选MSS的关键在于在避免IP层对TCP报文进行分段的基础上尽可能的提高传输效率。所谓传输效率，即数据载荷占整个报文大小的比重，比如如果MSS设置为40，则80字节长的IP报文中最多只有40字节的数据，传输效率仅为50%，因此，通常将MSS设置为MTU-40（20字节IP头部+20字节TCP头部）。

这一过程是在TCP连接建立时由连接双方商定的，需要注意的是：双方所得到的MSS可能并不相同。另外，建立MSS所基于的MTU的值基于[路径MTU发现](https://en.wikipedia.org/wiki/Path_MTU_Discovery)机制获取，这又是另外一个晦涩的主题了。

## 参考资料

- [TCP Maximum Segment Size (MSS) and Relationship to IP Datagram Size](http://www.tcpipguide.com/free/t_TCPMaximumSegmentSizeMSSandRelationshiptoIPDatagra-2.htm)
