---
title: "EXC_BAD_ACCESS : UIScrollView crash on iOS7"
date: 2014-08-23
categories: 
  - "ios-development"
tags: 
  - "ios"
---

在我的应用运行在iOS7上时，当用户点击后退退出一个列表时，有可能会导致应用崩溃，错误信息是：EXC\_BAD\_ACCESS。

其实这个问题存在很久了，但一直不能稳定复现所以放着没管。这一次版本更新似乎出现概率大了很多，所以追了一下终于找到了原因。

[![EXC_BAD_ACCESS](/assets/images/B3EEA236-8C70-4CED-BFA6-6FECD7C1DDA5.jpg)](/assets/images/B3EEA236-8C70-4CED-BFA6-6FECD7C1DDA5.jpg)

<!--more-->

## EXC\_BAD\_ACCESS

**EXC\_BAD\_ACCESS**这个错误应该是相当普遍也很让人头疼的问题了，按照字面意思理解就是说代码访问了不应该访问的内存地址，类似于C中的悬空指针，即使设置了All Exceptions BreakPoint，也没办法定位到错误的位置——这很合理，毕竟错误发生的地址是"Bad"...

观察发生错误发生错误的线程的stack trace如下： [![objc_msgSend](/assets/images/A1F21BB4-2A5E-4386-848C-492A0653A8FA.jpg)](/assets/images/A1F21BB4-2A5E-4386-848C-492A0653A8FA.jpg)

有进展！看来导致应用Crash的罪魁祸首就是这个objc\_msgSend函数！这个函数是Objective-C中的runtime消息发送实现，我们所使用的 \[MyClass function\] 这样的“函数调用”在Objective-C中实际上都是在运行时由Objective-C使用消息传递来实现的，就像这样： objc\_msgSend(MyClass, @selector(function)) 。也就是说我的问题是由于在运行时给一个不存在的对象发送了消息所以导致了Crash。

那么该怎么找到这个不存在的对象呢？很简单，使用Zombie Objects！Apple的命名还是很形象的，如果你在build时开启了这个选项，那么运行时释放的对象都不会被完全释放，而是留在内存中，就像Zombie一样~ 在"Product"-"Scheme"-"Edit Scheme"中打开Zombie Objects: [![Zombie](/assets/images/7517BBB0-8A1A-4D00-B8FF-E3FEFCA15276.jpg)](/assets/images/7517BBB0-8A1A-4D00-B8FF-E3FEFCA15276.jpg)

再次运行调试，观察控制台输出： `-[CommentTableViewController scrollViewDidScroll:]: message sent to deallocated instance 0x19397130`

OK，这个不存在的对象终于被我们找到了！

## Why UIScrollView?

接下来就要好好分析一下错误的原因了，上面的输出告诉我们Crash是因为scrollViewDidScroll消息发送给了已经被释放的对象，但这怎么会发生嘞？一番Google之后发现遇到这个问题的人为数不少，在iOS7中确实存在这个问题，但也没有说明为什么出现，只是给出了[解决方法](http://stackoverflow.com/questions/15216245/uicollectionview-calling-scrollviewdidscroll-when-popped-from-the-navigation-st "解决方法")，在对象dealloc时，一定将scrollView delegate置为nil：

`- (void)dealloc { // iOS7中 EXC_BAD_ACCESS // message sent to deallocated instance // http://stackoverflow.com/questions/15216245/uicollectionview-calling-scrollviewdidscroll-when-popped-from-the-navigation-st self.tableView.delegate = nil; }`

再次运行，问题解决。

## 原因

这个问题的根本原因应该是因为我没有使用UITableViewController，而是自己基于UIViewController在其中添加UITableView“山寨”了一个UITableViewController，这样做的原因是因为UITableViewController中仅有一个UITableView类型的self.view，而我更需要一个作为Container的UIView，相信这样的需求不仅仅是我一个人遇到过。

但是我这样的山寨就会出现种种问题，总是会出现一些小问题。比如这次的Crash，当我的山寨版UITableViewController退出后，在dealloc的过程中是先释放View Controller和self.view，之后由于引用计数为0，原先作为self.view的subview的UITableView才会被释放，就在这两次释放之间scrollViewDidScroll消息由UITableView发送给了作为delegate的已释放的山寨版UITableViewController...所以...而在UIKit中UITableViewController可以正确处理这些问题。

作为建议：不要自己山寨UITableViewController，更好的实践是将UITableViewController作为Child View Controller加入到自己的View Controller中，血的教训...在[objc.io](http://www.objc.io/issue-1/table-views.html "ojbc.io")中也提到了这个问题。
