---
title: "Twisted和Reactor模式"
date: 2014-11-30
categories: 
  - "python"
tags: 
  - "python"
  - "twisted"
---

因为项目关系，接触学习了大名鼎鼎的Python网络编程框架Twised，Twisted是以高性能为目标的异步（event-driven）网络编程框架。

<figure style="text-align: center;">
  <img src="/assets/images/518wm5u3TjL.jpg" alt="Twisted book" width="379" height="500" />
  <figcaption>Twisted book</figcaption>
</figure>

图中是Twisted官方推荐的学习书籍的封面，我觉得封面设计的非常贴切：Twisted就是很多Python（蟒蛇）纠缠在一起。

很多人说Twisted太复杂了，不易于使用，而我**并不这么认为**。虽然代码流程和朴素的代码流程大相径庭，但复杂性源自于异步编程的思想，而Twisted通过优秀的封装已经极大了减轻了我们的工作量。如果你之前没有接触过异步编程模型，我认为从Twisted入手不失为一个很好的选择。

学习Twisted的最好方式就是阅读Twisted的[最新官方指南](http://twistedmatrix.com/documents/current/core/howto/index.html)，有详尽的解释和代码示例，网络上其他的教程都是浪费时间（包括本文，前提是如果本文算得上是教程的话...）。

<!--more-->

* * *

## 什么是异步？

异步编程模型在追求性能的服务器编程中大行其道，但异步编程并不等于高性能。下文中以I/O为例尝试分析异步的行为，但实际上异步的思想无处不在：信号、文件系统等等都是异步运行的例子。

异步编程为什么可以带来性能的提高？答案在于I/O。大体上我们可以把程序运行所消耗的时间分为两部分：占用CPU进行计算的时间和等待I/O操作完成的时间。同步和异步模型在前一种场景中的行为是相同的，区别在于后者，当用户进程执行I/O操作时，基于同步模型的程序被系统调用阻塞（内核态，操作系统执行进程切换），直到I/O操作完成，驱动程序通知内核，用户进程得以从内核态返回；而基于异步模型的用户进程执行非阻塞的I/O系统调用，直接从内核态返回，但这时I/O的数据并没有准备好，用户进程可以继续进行其他的计算工作，当I/O数据准备好时，用户进程通过异步通知（aio或I/O多路复用）的机制获取数据执行数据处理操作。

因此，异步编程利用等待I/O的时间去做其他的工作，更加充分的利用了CPU资源，有得必有失，使用异步编程模型意味着你需要把原本连续的流程切分为多个不被阻塞的小代码块，然后以一种非常反人类的逻辑流程编写代码来换取计算机执行的高性能。

顺便一提，另外一种常用的性能优化模型：多线程/多进程模型经常被拿来和异步模型做对比，实际上两者并不是一个概念。多线程/多进程模型使得程序可以更加有效的利用多核的优势，和同步、异步模型并不冲突。我们可以在使用多线程/多进程模型的基础上同时使用异步模型进行I/O：Nginx就是通过多进程+基于epoll的I/O多路复用才达到了如此优秀的性能。

* * *

## Reactor模式

在大量的实践中，似乎我们总是通过类似的方式来使用异步编程：

1. 监听事件
2. 事件发生执行对应的回调函数
3. 回调完成（可能产生新的事件添加进监听队列）
4. 回到1，监听事件

因此我们将这样的异步模式称为Reactor模式，例如在iOS开发中的Run Loop概念，实际上非常类似于Reactor loop，主线程的Run Loop监听屏幕UI事件，一旦发生UI事件则执行对应的事件处理代码，还可以通过GCD等方式产生事件至主线程执行。

<figure style="text-align: center;">
  <img src="/assets/images/event_model.png" alt="Event model" width="524" height="364" />
  <figcaption>Event model</figcaption>
</figure>

上图是[Boost](http://www.boost.org "boost")对Reactor模式的描绘，Twisted的设计就是基于这样的Reactor模式，Twisted程序就是在等待事件、处理事件的过程中不断循环。

```python
from twisted.internet import reactor
reactor.run()
```

reactor是Twisted程序中的单例对象。

* * *

## Twisted中的Factory和Protocol

有了Twisted的Reactor之后，我们只需要编写对应事件的事件处理过程即可。Twisted网络框架中通过Factory和Protocol对事件处理过程进行了抽象。

Factory如名字所暗示的，是抽象工厂。在Twisted中把一个工厂对象绑定到特定的端口中，当连接到来，Twisted使用该工厂创建工厂指定的Protocol对象，Protocol对象表明了连接的处理流程（协议），每个Protocol对象按照预定的协议处理连接，当连接关闭后销毁。

<figure style="text-align: center;">
  <img src="/assets/images/protocols-1.png" alt="Factory and Protocol" width="474" height="352" />
  <figcaption>Factory and Protocol</figcaption>
</figure>

因为Protocol仅处理一条连接，所以一些全局持久保存的数据都存储在Factory中，每个Protocol对象中都有一个指向创建自己的Factory对象的成员变量factory。

下面是官网指南中一个简单的例子，可以清楚的看到Factory和Protocol的关系。Protocol实例的transport成员变量表示对应的网络连接。

```python
# Read username, output from non-empty factory, drop connections

from twisted.internet import protocol, reactor
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        self.transport.write(self.factory.getUser(user)+"\r\n")
        self.transport.loseConnection()

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, **kwargs):
        self.users = kwargs

    def getUser(self, user):
        return self.users.get(user, "No such user")

reactor.listenTCP(1079, FingerFactory(moshez='Happy and well'))
reactor.run()
```

* * *

## 神奇的Deferred

Deferred是Twisted对Callback的实现方式，Deferred非常灵活，代表了“推迟”。下面的例子展示了Deferred对象的基本用法：

```python
from twisted.internet.defer import Deferred
 
def got_poem(res):
    print 'Your poem is served:'
    print res
 
def poem_failed(err):
    print 'No poetry for you.'
 
d = Deferred()
 
# add a callback/errback pair to the chain
d.addCallbacks(got_poem, poem_failed)
 
# fire the chain with a normal result
d.callback('This poem is short.')
 
print "Finished"
```

1. 创建Deferred对象
2. 将callback和errback函数添加到Deferred对象上
3. 在Deferred对象上执行回调

当我们想执行一个异步操作时，我们可以使用Deferred来代替数据立即返回。Deferred的含义是：你想要的数据还没有到，不过你可以告诉我你接下来想要执行的操作，当我得到数据以后会调用你想要执行的函数。

<figure style="text-align: center;">
  <img src="/assets/images/deferred-process.png" alt="Deferred process" width="240" height="382" />
  <figcaption>Deferred process</figcaption>
</figure>

如上图，我们把想要的回调函数添加到Deferred对象上，当数据准备好后会按我们设置好的回调函数链一层一层的进行回调。

回调函数链分为两条：正常回调链和错误回调链，方便我们进行错误处理。当然Deferred的强大之处远不止于此，还有包括DeferredList在内的很多有用的特性，按照你的使用方式不同，Deferred可以非常简单也可以极为复杂。这些东西作为Twisted初学者就不班门弄斧了。

* * *

## twistd

很多时候我们编写网络程序都需要程序可以作为[守护进程](http://en.wikipedia.org/wiki/Daemon_\(computing\) "守护进程")运行，在UNIX环境中这需要做2次fork的魔法（见APUE第13章），twist（注意，比Twisted少了一个字母e）为我们跨平台的封装了这一过程，通过编写Twisted Application Configuration文件（.tac）指定所运行的application，就可以通过twistd命令运行守护进程了！

```bash
root% twistd -ny finger11.tac # just like before
root% twistd -y finger11.tac # daemonize, keep pid in twistd.pid
root% twistd -y finger11.tac --pidfile=finger.pid
root% twistd -y finger11.tac --rundir=/
root% twistd -y finger11.tac --chroot=/var
root% twistd -y finger11.tac -l /var/log/finger.log
root% twistd -y finger11.tac --syslog # just log to syslog
root% twistd -y finger11.tac --syslog --prefix=twistedfinger # use given prefix
```

```python
# Read username, output from non-empty factory, drop connections
# Use deferreds, to minimize synchronicity assumptions
# Write application. Save in 'finger.tpy'

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        d = self.factory.getUser(user)

        def onError(err):
            return 'Internal error in server'
        d.addErrback(onError)

        def writeResponse(message):
            self.transport.write(message + '\r\n')
            self.transport.loseConnection()
        d.addCallback(writeResponse)

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, **kwargs):
        self.users = kwargs

    def getUser(self, user):
        return defer.succeed(self.users.get(user, "No such user"))

application = service.Application('finger', uid=1, gid=1)
factory = FingerFactory(moshez='Happy and well')
internet.TCPServer(79, factory).setServiceParent(
    service.IServiceCollection(application))
```

* * *

## 更多工具

除了这些优秀的特性，Twisted还为我们封装了大部分常用操作的非阻塞实现，如数据库查询（使用了线程池实现）、子进程、RPC等有力的工具。例子和文档都详细的列在官方文档中，我就不再继续搬运了。

* * *

## 参考资料

- [Twisted官方指南](http://twistedmatrix.com/documents/current/core/howto/index.html "Twisted")
- [Twisted introduction](http://krondo.com/?page_id=1327 "Twisted introduction")
