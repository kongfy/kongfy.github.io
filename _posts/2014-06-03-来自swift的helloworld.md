---
title: "来自Swift的hello,world!"
date: 2014-06-03
categories: 
  - "ios-development"
tags: 
  - "ios"
  - "swift"
---

一觉醒来，所有的新闻媒体都充斥着**Swift**，不过这个Swift可不是那个女歌手[Swift](http://en.wikipedia.org/wiki/Taylor_Swift)，而是apple在WWDC2014上刚刚发布的新编程语言：[Swift](https://developer.apple.com/swift/)。

\[caption id="attachment\_277" align="aligncenter" width="1024"\][![WWDC2014推出Swift编程语言](/assets/images/rdn_538cc786563e1.jpg)](/assets/images/rdn_538cc786563e1.jpg) WWDC2014推出Swift编程语言\[/caption\]

### Swift是什么？

突然冒出一个新语言，这感觉...还是先来看看苹果怎么说：

> Swift is an innovative new programming language for Cocoa and Cocoa Touch. Writing code is interactive and fun, the syntax is concise yet expressive, and apps run lightning-fast. Swift is ready for your next iOS and OS X project — or for addition into your current app — because Swift code works side-by-side with Objective-C.

是不是有一种不明觉厉的感觉！简单来说Swift是一个运行效率高、并且具有多种现代语言特性、可以和Objective-C一起使用的用来开发iOS和OS X应用的新语言。

<!--more-->

### Swift是不是运行效率很低？

很多人在看到Swift的动态解释特性的时候很自然的认为Swift运行效率很低。但这并说不通，因为Swift并不是一个脚本语言，虽然在apple新推出的playground中，你可以像一个脚本语言一样来运行它，但是它却不是一个脚本语言。_Using the high-performance LLVM compiler, Swift code is transformed into optimized native code._Swift和Objective-C一样，是由LLVM编译成native code运行的。同时，Swift在内存管理方面依然沿用了ARC机制，并没有垃圾回收造成的效率损失。在WWDC上展示了其运行效率甚至已经超越了其前辈Objective-C！(不过这个...我感觉只能信一半)

\[caption id="attachment\_285" align="aligncenter" width="580"\][![Swift运行效率](/assets/images/wwdc-31.jpg)](/assets/images/wwdc-31.jpg) Swift运行效率\[/caption\]

### 大明湖畔的Objective-C

\[caption id="attachment\_304" align="aligncenter" width="416"\][![长江后浪推前浪，前浪死在沙滩上](/assets/images/538d0f1cdec3c.jpg)](/assets/images/538d0f1cdec3c.jpg) 长江后浪推前浪，前浪死在沙滩上\[/caption\]

相信不止我一个人在第一次看到的Swift的时候心中一声咆哮：“我\*，这Objective-C是白学了么！”

Objective-C作为Swift的大哥，而Swift作为Objective-C官方出品的继任者，我相信在未来很有可能会取代Objective-C现在的地位，但是不是现在，在未来一段时间内也不会替代Objective-C。毕竟现在如此众多基于Objective-C的项目还是要继续维护和发展的，而另一方面，Swift也远远还没有成熟到足够取代老大哥的地步。不过Swift的特性确实足够出色，相信取代Objective-C也只是时间上的问题。

不过apple对Swift和Objective-C的关系也比较模糊，似乎并没有明确的表态，而更像是试探性的发布Swift来试探开发者的反应。也就是说，目前情况下apple并不认为Swift已经足以取代Objective-C，一个比较靠谱的说法是：如果有一天apple用Swift重写了iOS内置应用，那才算得上是apple对Swift官方语言身份的认可。

### hello, world!

看了半天热闹，也该上手感受感受了。apple同时放出了Xcode 6 beta来支持Swift的开发，所以首先安装Xcode 6 beta（同时放出的还有OS X Yosemite，这个如果不是急需建议还是先等等，笔者上次太早更新Maverick导致发生了一些不愉快的体验）。

\[caption id="attachment\_288" align="aligncenter" width="611"\][![安装Xcode 6 beta](/assets/images/8DCE2F8B-8BC5-4B2E-9B5D-168A9EFEEFE8.jpg)](/assets/images/8DCE2F8B-8BC5-4B2E-9B5D-168A9EFEEFE8.jpg) 安装Xcode 6 beta\[/caption\]

打开Xcode，还是熟悉的感觉，创建一个项目，选择语言为Swift:

\[caption id="attachment\_291" align="aligncenter" width="730"\][![使用Swift创建项目](/assets/images/8AA06695-5ED4-43D5-A5EC-D7F0DA81CC66.jpg)](/assets/images/8AA06695-5ED4-43D5-A5EC-D7F0DA81CC66.jpg) 使用Swift创建项目\[/caption\]

看的出来apple对待Swift还是很认真的，UIKit的文档全部都针对Swift做了重写：

\[caption id="attachment\_293" align="aligncenter" width="1400"\][![UIView文档中的Swift部分](/assets/images/5AED08BC-3C28-4AFC-B735-BD695D1F8426.jpg)](/assets/images/5AED08BC-3C28-4AFC-B735-BD695D1F8426.jpg) UIView文档中的Swift部分\[/caption\]

找准位置，写下helloworld代码~

`override func viewDidLoad() { super.viewDidLoad() println("hello, world") }`

运行后就可以看到华丽丽的hello, world输出了~

### 官方教程

目测现在已经有一大批人要开始Swift语言入门教程的写作工作了...不过目前能看到最好的教程还是apple自己的文档：

- [The Swift Programming Language](https://itunes.apple.com/us/book/the-swift-programming-language/id881256329?mt=11)
- [Welcome to Swift](http://itunes.apple.com/cn/book/swift-programming-language/id881256329?mt=11)

抽空看看，虽然只是一个半吊子iOS开发，也得跟得上潮流不是~
