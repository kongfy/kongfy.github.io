---
title: "Strict Aliasing，神坑？"
date: 2015-09-05
categories: 
  - "c-cpp"
---

先来看一段代码：

```
#include <cstdio>

void exchange(int input, int* output)
{
    short* pi = (short*)&input;
    short* po = (short*)output;
    po[1] = pi[0];
    po[0] = pi[1];
}

int main()
{
    int input = 0xffff0000;
    printf("input  : 0x%08x\n", input);

    int output = 0xababbaba;
    exchange(input, &output);
    printf("output : 0x%08x\n", output);

    return 0;
}
```

你觉得程序的输出是什么样的呢？

<!--more-->

代码很容易理解，只做了一件事情，把input变量储存的32位整数的高16位和低16位交换，存放在output变量中，并输出这两个变量。

相信很多人都写过这样的代码（至少我写过），虽然觉得有点怪，但应该不会有什么问题，于是编译运行：

```
[kongfy@kongfy-vps dev]$ g++ -g test.cpp -o test
[kongfy@kongfy-vps dev]$ ./test
input  : 0xffff0000
output : 0x0000ffff
```

结果完全符合预期，似乎没有任何问题啊！

别高兴的太早，让我们试试打开编译器优化选项\-O2重新编译运行：

```
[kongfy@kongfy-vps dev]$ g++ -O2 -g test.cpp -o test
[kongfy@kongfy-vps dev]$ ./test
input  : 0xffff0000
output : 0xababbaba
```

问题出现了，output变量居然不符合预期？什么鬼？！

PS:似乎有必要注明用来测试的g++版本，我测试用的版本是4.4.7，经测试高版本g++得到的结果会不同，但这个问题仍然是存在的。

## strict-aliasing

* * *

难道是编译器优化有问题么？但怀着对GNU的景仰...不，一定是我的使用方式有问题！

编译出现诡异问题怎么办？不要忘了使用\-Wall，编译器会给你线索：

```
[kongfy@kongfy-vps dev]$ g++ -Wall -O2 -g test.cpp -o test
test.cpp: In function ‘void exchange(int, int*)’:
test.cpp:7: warning: dereferencing pointer ‘pi’ does break strict-aliasing rules
test.cpp:5: note: initialized from here
test.cpp:8: warning: dereferencing pointer ‘<anonymous>’ does break strict-aliasing rules
test.cpp:8: note: initialized from here
test.cpp: In function ‘int main()’:
test.cpp:8: warning: dereferencing pointer ‘po’ does break strict-aliasing rules
test.cpp:6: note: initialized from here
test.cpp:7: warning: dereferencing pointer ‘pi’ does break strict-aliasing rules
test.cpp:5: note: initialized from here
test.cpp:7: warning: dereferencing pointer ‘<anonymous>’ does break strict-aliasing rules
test.cpp:7: note: initialized from here
test.cpp:8: warning: dereferencing pointer ‘<anonymous>’ does break strict-aliasing rules
test.cpp:8: note: initialized from here
```

编译器果然给出了警告：我们的指针操作破坏了strict-aliasing规则，新的问题来了，什么是strict-aliasing?严格别名（非准确翻译）？

在man g++中找到这样一段介绍：

```
-fstrict-aliasing
           Allow the compiler to assume the strictest aliasing rules applicable to the language being compiled.  For C (and C++), this activates optimizations based on the
           type of expressions.  In particular, an object of one type is assumed never to reside at the same address as an object of a different type, unless the types are
           almost the same.  For example, an "unsigned int" can alias an "int", but not a "void*" or a "double".  A character type may alias any other type.
           ...
           The -fstrict-aliasing option is enabled at levels -O2, -O3, -Os.

```

简单来说，如果在编译器中开启了\-fstrict-aliasing选项（\-O2优化级别默认开启这个选项），编译器会在“不同类型的变量一定存放在不同的内存空间中”的假定条件下对代码进行优化。

这实际是一个普通程序员和编译优化器编写者之间的约定：为了方便编译优化器的编写者写出更好的编译器优化功能，普通程序员在编写代码时要遵循这样的约定：“不同类型的变量一定存放在不同的内存空间中”。

反过来看看我们代码中的指针pi和po，他们是short \*类型，但他们指向的内存空间实际上是int类型的input变量，这就违反了strict-aliasing规则，但在开启\-O2优化时我们却告诉编译优化器我们遵守了strict-aliasing规则（默认开启），导致编译器做出了“错误”的优化。

## 来点汇编

* * *

明白了问题出现的原因，不妨看看编译器最终生成的汇编代码是怎样的：

```
080484a0 :
 80484a0:   55                      push   %ebp
 80484a1:   89 e5                   mov    %esp,%ebp
 80484a3:   83 e4 f0                and    $0xfffffff0,%esp
 80484a6:   83 ec 20                sub    $0x20,%esp
 80484a9:   c7 44 24 04 00 00 ff    movl   $0xffff0000,0x4(%esp)
 80484b0:   ff
 80484b1:   c7 04 24 b4 85 04 08    movl   $0x80485b4,(%esp)
 80484b8:   e8 e3 fe ff ff          call   80483a0 
 80484bd:   0f b7 44 24 18          movzwl 0x18(%esp),%eax
 80484c2:   c7 44 24 04 ba ba ab    movl   $0xababbaba,0x4(%esp)
 80484c9:   ab
 80484ca:   c7 04 24 c5 85 04 08    movl   $0x80485c5,(%esp)
 80484d1:   66 89 44 24 1e          mov    %ax,0x1e(%esp)
 80484d6:   0f b7 44 24 1a          movzwl 0x1a(%esp),%eax
 80484db:   66 89 44 24 1c          mov    %ax,0x1c(%esp)
 80484e0:   e8 bb fe ff ff          call   80483a0 
 80484e5:   31 c0                   xor    %eax,%eax
 80484e7:   c9                      leave
 80484e8:   c3                      ret

```

看不懂是正常的...\-O2级别的优化已经把代码搞的乱七八糟了。main函数中没有调用exchange函数的部分，进行了inline优化。

重要的是在调用第二个printf函数的传参部分，可以看到0x4(%esp)被直接赋予了$0xababbaba并且没有修改过。

让我们尝试从编译器的角度思考我们的代码：函数exchange中修改的内存都是short类型的，既然程序员承诺遵循strict-aliasing规则，那么函数exchange就不会修改int类型的变量output，所以可以优化一下直接输出初始值就可以了。

好聪明的编译器！好悲剧的程序猿...

## 怎么办？

* * *

那么这样的问题该如何避免呢？显然的，如果你告诉编译器遵循strict-aliasing规则，那在写代码的过程中就不应该尝试去打破这样的规则。但是我们在写C/C++代码的过程中常常需要编写这样一些打破规则的trick代码，与其让自己不自在，不如在编译时不要和编译器做这样的约定（使用\-fno-strict-aliasing编译参数），虽然不能让编译器做一些更加高效的优化，但安全总是第一位的，不是么？

## 参考资料

* * *

- [Understanding C/C++ Strict Aliasing](http://dbp-consulting.com/tutorials/StrictAliasing.html)
