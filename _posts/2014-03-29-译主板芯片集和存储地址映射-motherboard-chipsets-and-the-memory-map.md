---
title: "[译]主板芯片组和存储地址映射 - Motherboard Chipsets and the Memory Map"
date: 2014-03-29
categories: 
  - "operating-system"
tags: 
  - "操作系统"
---

[原文在此](http://duartes.org/gustavo/blog/post/motherboard-chipsets-memory-map/ "Motherboard Chipsets and the Memory Map")，翻译仅供参考。

* * *

我计划写一些关于计算机内部的文章来解释现代的操作系统内核是如何运行的。我希望这些文章会对那些对此类东西感兴趣而没有相关经验的程序猿有所帮助，我会集中关注Linux、Windows和Intel处理器。探究计算机的内部运行原理是我的爱好,我已经写了一些内核态的代码但是还没有怎么写过相关的文章。我的第一篇文章将会对现代Intel系列的主板构造、CPU存储访问、存储地址映射进行描述。

作为开始，我们先来看一下现在的Intel体系的计算机是如何连接起来的。下图中包含了主板中的主要部件：

\[caption id="attachment\_142" align="aligncenter" width="668"\][![主板示意图，北桥和南桥构成了芯片组](/assets/images/6D264DDD-CB93-47A6-995E-B18F84AA12FC.jpg)](/assets/images/6D264DDD-CB93-47A6-995E-B18F84AA12FC.jpg) 主板示意图，北桥和南桥构成了芯片组\[/caption\]

当你在理解上图时，需要重点注意的一点是CPU并不知道它和什么东西连接在一起，它通过[引脚（pins）](http://en.wikipedia.org/wiki/Image:Intel_80486DX2_bottom.jpg "pins")和外部交流，但并不关心外部环境是什么：可能是主板，但也可能是烤面包机、路由器、植入大脑或者是CPU测试器。CPU主要通过三种方式与外部环境通信：存储地址空间、I/O地址空间和中断。现在我们只关注主板和存储。

<!--more-->

在一块主板中，CPU与外部通信的通道为连接在北桥（northbridge）上的前端总线（front-side bus），无论何时CPU需要读写数据，都需要通过前端总线。CPU使用一些引脚来传输它要读写的物理存储地址，还有一些引脚传送要写入的数据或是接受读取到的数据。一个Intel Core 2 QX6600有33个用来传送物理地址的引脚（所有有233个可以表示的地址）和64个用来传送和接受数据的引脚（所以被传输的数据为64位即8个字节），因此CPU可以使用64GB的物理地址空间（233个地址 \* 8字节）虽然大多数的芯片组只支持最大8GB的内存。

这里有一个可能会和你的认识冲突的事实：我们总是认为存储空间只是指内存（RAM），就是程序一直在读写的那个东西，实际上大部分处理器的读写请求也确实是被北桥转发给了内存模块，但并不是所有的。物理存储地址空间同时也被用来和一些主板上的其他设备通信（这种通信被称为[memory-mapped I/O](http://en.wikipedia.org/wiki/Memory-mapped_IO "memory-mapped I/O")），比如显卡和大部分的PCI设备（扫描仪、SCSI设备之类的），还有存储有BIOS的闪存。

当北桥接收到一个物理地址请求，北桥会决定这个请求该转向哪里：内存？还是显卡？北桥根据存储地址映射表来决定。对物理存储地址的每一个区域，存储地址映射表都知道究竟是哪一个设备拥有这些地址。大部分的地址都映射到内存中，但当地址不属于内存时，存储地址映射表会告诉芯片组哪个设备该响应这些地址的请求。这种将地址分配到其他设备的映射导致了在老式PC存储中640KB到1MB之间的空洞，而保留给显卡和PCI设备的地址又造城了一个更大的空洞，这也是为什么32位操作系统[不能完全使用4GB内存的原因](http://support.microsoft.com/kb/929605)。在Linux中/proc/iomem文件清楚的列出了这些被映射的地址。下图展示了Intel PC的前4GB地址空间中典型的映射关系：

\[caption id="attachment\_143" align="aligncenter" width="285"\][![Intel体系中前4GB存储空间的布局情况](/assets/images/1BD64BA1-2A96-4289-B293-9587881FE0AF.jpg)](/assets/images/1BD64BA1-2A96-4289-B293-9587881FE0AF.jpg) Intel体系中前4GB存储空间的布局情况\[/caption\]

实际的地址和范围取决于电脑中使用的主板和设备，不过大部分的Core 2系统和上图中展示的非常相似。所有棕色的区域都不属于内存，这里要明确一点，这里所说的地址是在主板总线中实际的物理地址，在CPU内部（例如程序中的运行、读写地址）使用的地址都是逻辑地址，并且在实际访问之前都必须被CPU转换成物理地址。

将逻辑地址转换成物理地址的规则十分复杂，并且依赖于CPU运行时处于的模式（实模式、32位保护模式以及64位保护模式）。抛开地址转换硬件不谈，CPU的运行模式决定了究竟能够访问多少物理地址。举例来说，如果CPU运行在32位保护模式中，则它最多只能够使用4GB的物理地址（有一个例外叫做[physical address extension](http://en.wikipedia.org/wiki/Physical_address_extension "PAE")，不过在这里我们先忽略它），因为最顶部的1GB地址空间被映射给了主板上的设备，CPU只能有效利用不到3GB的内存（有时候会更少-我有一台Vista机器只能使用2.4GB内存）；如果CPU运行在[实模式（real mode）](http://en.wikipedia.org/wiki/Real_mode "real mode")中，则它只能使用1MB的物理地址（实模式是早期Intel CPU唯一能够使用的模式）；而如果CPU运行在64位保护模式中，它可以使用64GB的物理地址（虽然仅仅只有少数芯片组支持这么多的内存），在64位模式中使用超过内存总容量的物理地址空间是可能的，系统通过对那些被主板设备偷走的存储地址对应的内存区域的访问来实现这点，这叫做内存回收（reclaiming memory），是在主板芯片组的支持下完成的。

以上就是在下一篇文章前我们需要的所有关于存储的知识了。下一篇文章将会讲解从计算机通电到boot loader即将跳转到内核之间的过程。如果你还想了解更多关于存储的知识，强烈推荐阅读Intel手册，Intel的手册写的很好，而且非常准确，下面给出一些：

- [Datasheet for Intel G35 Chipset](http://download.intel.com/design/chipsets/datashts/31760701.pdf)中给出了Core 2系列处理器具有代表性的芯片组的文档，是本文的主要参考。
- [Datasheet for Intel Core 2 Quad-Core Q6000 Sequence](http://download.intel.com/design/processor/datashts/31559205.pdf)是处理器的文档，详细的讲解了处理器的每一个引脚（实际上并没有那么多，并且在对它们分组之后更加没有多少了），虽然有些难懂，但还是非常赞。
- 广为人知的[Intel Software Developer’s Manuals](http://www.intel.com/products/processor/manuals/index.htm)，易于理解，非常优美的解释了很多体系结构上的问题。卷1和卷3A里有很多有用的东西（别被名字吓到了，“卷”其实并不长而且你也可以选择性的进行阅读）。
