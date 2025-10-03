---
title: "Nanos note 1 : bootloader"
date: 2014-05-03
categories: 
  - "operating-system"
tags: 
  - "nanos"
  - "操作系统"
mathjax: true
---

Nanos是JYY大神为南大计算机系操作系统课程专门设计的实验用操作系统。出于对操作系统的好奇和对JYY大神的敬仰，我又再次踏上了DIY玩具内核的道路。和本科时候不同，这次希望能对操作系统有更深的理解，而不是仅仅局限于完成实验，也希望能留下一些笔记作为积淀。这是第一篇note，从分析Nanos的bootloader开始再好不过了。

Nanos的框架代码都可以在github上找到([点我](https://github.com/NJUOS "NJUOS"))，为了方便起见，一份打包的仅包含bootloader的代码在[这里](/assets/images/bootloader.tar.gz)。

* * *

正如[之前](/posts/2014-03-*-%e8%af%91%e8%ae%a1%e7%ae%97%e6%9c%ba%e5%90%af%e5%8a%a8%e8%bf%87%e7%a8%8b-how-computers-boot-up/ "[译]计算机启动过程 – How Computers Boot Up")提到的，在计算机的启动过程中当完成了POST之后，BIOS会从可启动磁盘中读出头512个字节(MBR)并将其载入内存地址0x7c00的位置并开始执行，MBR中的代码通常被称为bootloader，负责将操作系统内核载入到内存中。在Nanos中，bootloader极其简单，仅由MBR中的512字节组成(即仅包含stage 1)，麻雀虽小五脏俱全，Nanos的bootloader完成了bootloader所需要做的所有基本任务：为操作系统内核设置运行环境、载入内核到内存、跳转到内核开始执行。

下面具体分析一下Nanos的bootloader是如何完成的。首先看一下bootloader的源文件目录结构： `. ├── Makefile ├── asm.h ├── boot.h ├── genboot.pl ├── main.c └── start.S`

<!--more-->

我们从Makefile文件入手： `bootblock: start.S main.c asm.h boot.h gcc -c -m32 start.S gcc -c -m32 -O1 main.c ld -melf_i386 -e start -Ttext 0x7C00 start.o main.o -o bootblock.o @objcopy -S -O binary -j .text bootblock.o bootblock @./genboot.pl bootblock  clean: rm -rf bootblock *.o` 从Makefile中我们可以明白bootloader是如何编译生成的，在编译目标bootblock中：

1. 首先编译了start.S和main.c文件(注意此处并没有执行链接)
2. 在链接过程中通过-e start指定了可执行文件的入口为符号start(这个符号出现start.S中，我们之后会看到)，通过-Ttext 0x7c00指定了代码段的起始位置(实际运行的bootloader并不是一个ELF格式的文件，所以这里指定的起始位置仅用来指导链接程序做地址的解析使用)，最终生成bootblock.o文件
3. 运行objcopy指令将上一步中生成的bootblock.o文件中的text代码段拷贝出来，生成bootblock，至此脱离了ELF格式
4. 运行genboot.pl脚本，该脚本只是很简单的将bootblock拓展到512字节，并将末尾两个字节改写为魔数0x55aa

了解了bootloader是如何生成的之后，接下来我们跟随程序的入口，从start.S看起： `# 从此开始是16位代码 .code16 .globl start start: cli # 关闭外部中断  # 设置正确的段寄存器 xorw %ax, %ax # %AX = 0 movw %ax, %ds # %DS = AX (data segment) movw %ax, %es # %ES = AX (extra segment) movw %ax, %ss # %SS = AX (stack segment)  # 打开A20地址线 movw $0x2401, %ax int $0x15  lgdt gdtdesc # 设置GDT(段描述符表地址为$gdt) movl %cr0, %eax # %CR0 |= PROTECT_ENABLE_BIT orl $0x1, %eax movl %eax, %cr0 # 设置PE bit  # 长跳转进入保护模式，设置%CS为GDT中的第一项，%EIP为start32所对应地址 ljmp $GDT_ENTRY(1), $start32` 在start.S的一开始就是我们在Makefile中看到的程序入口标记start。当计算机将512个字节载入到内存后，代码就是从这里开始运行的。

当计算机开始运行bootloader时，计算机仍处于实模式，所以start中为16位代码。在一开始，首先关闭外部中断，然后将段寄存器都设置为0、打开A20地址线(如果你不明白这是什么，请移步[这里](http://wiki.osdev.org/A20_Line "A20地址线"))、利用lgdt命令设置GDT(同样，请移步[这里](http://wiki.osdev.org/GDT_Tutorial "GDT"))、设置控制寄存器的PE位，打开保护模式(你懂的，[这里](http://wiki.osdev.org/Protected_Mode "保护模式"))，最后执行一个ljmp指令，跳转到start32开始执行保护模式中的代码。

在这里我们稍微停留一下，来仔细的研究一下Nanos是如何设置GDT的。假定你已经大致理解了GDT是如何工作的，我们把注意力集中到下面这行代码上： `lgdt gdtdesc # 设置GDT(段描述符表地址为$gdt)` lgdt指令实际上设置了gdtr寄存器，指明了GDT在内存中的位置。lgdt命令需要GDT描述符的地址作为操作数，GDT描述符的结构如下：

<figure style="text-align: center;">
  <img src="/assets/images/Gdtr.png" alt="GDT描述符" />
  <figcaption>GDT描述符</figcaption>
</figure>

其中offset字段为GDT起始位置的线性地址，size字段为GDT的大小减1(注：之所以要减去1是因为GDT的最大长度为65536，而不存在长度为0的GDT)，在Nanos中lgdt的操作数gdtdesc详细定义： `# GDT .p2align 2 # 对齐 gdt: # 确保段选择子不能为0 SEG_NULLASM # GDT第一项必须为空 # type 0xA 代表设置了Ex&Rw，表示代码段可执行&可读 SEG_ASM(0xA, 0x0, 0xffffffff) # 代码段描述符 # type 0x2 代表设置了Rw，表示数据段可写 SEG_ASM(0x2, 0x0, 0xffffffff) # 数据段描述符 # 参见 http://wiki.osdev.org/Global_Descriptor_Table  gdtdesc: # GDT描述符 .word (gdtdesc - gdt - 1) # GDT长度，留意地址运算 .long gdt # GDT地址` 可以看到gdtdesc起始的内存中存放了GDT描述符，而具体的段描述符表则存放在标号gdt开始的内存单元中。每一个段描述符占8字节，其结构如下：

<figure style="text-align: center;">
  <img src="/assets/images/GDT_Entry.png" alt="段描述符" />
  <figcaption>段描述符</figcaption>
</figure>

段描述符中Base字段表示该段的段基址(32位线性地址)，Limit字段表示该段可寻址的最大单元(注意：这里的单元可能是1byte，也可能是一个页，见Gr位)。Flags和Access Byte要稍微复杂些：

<figure style="text-align: center;">
  <img src="/assets/images/Gdt_bits.png" alt="Flags & Access Byte" />
  <figcaption>Flags & Access Byte</figcaption>
</figure>

对这些位的解释引自[OSDev](http://wiki.osdev.org/GDT "GDT"):

- **Pr :** 保护位，总是为**1**
- **Privl :** 2位的权限位(ring)，0为最高，3为最低
- **Ex :** 执行位，如果该位为**1**代表该段中的代码可以被执行，该段是一个代码段，如果该位为**0**则该段是一个数据段
- **DC :** 方向/适应位：
    - 对数据段来说该位为方向位：**0**代表数据段从低地址向高地址增长，**1**代表数据段从高地址向低地址增长
    - 对代码段来说该位为适应位：
        - 如果该位为**1**则该段中的代码可以由相等或更低的权限执行。例如：ring 3中的代码可以far-jump到设置了适应位的ring 2代码段中执行，privl位表示了可以执行该代码段的最高权限
        - 如果该位为**0**则该段中的代码只能由privl中标明的权限执行
- **RW :** 可读/可写位：
    - 对代码段来说该位为可读位：代表当前段是否可读，代码段不具有写权限
    - 对数据段来说该位为可写位：代表当前段是否可写，数据段总是可读的
- **Ac :** Accessed bit. 设置为**0**即可，CPU访问该段时将其改写为**1**
- **Gr :** Granularity bit. 如果该位为**0**则Limit表示的单元为1byte，否则为4KB(一页)
- **Sz :** 如果该位为**0**则该段为16位保护模式，如果该位为**1**表示该段为32位保护模式

在Nanos中通过asm.h中的相关宏来实现GDT条目的定义： `/* 参考：i386手册 */ #define GDT_ENTRY(n) \ ((n) << 3)  #define SEG_NULLASM \ .word 0, 0; \ .byte 0, 0, 0, 0  #define SEG_ASM(type,base,lim) \ .word (((lim) >> 12) & 0xffff), ((base) & 0xffff); \ .byte (((base) >> 16) & 0xff), (0x90 | (type)), \ (0xC0 | (((lim) >> 28) & 0xf)), (((base) >> 24) & 0xff)` 我们可以看到Nanos实际上定义了2个段，并将GDT条目0留空以确保段选择子为0是非法的。第一个段为代码段，具有可执行、可读权限；第二个段为数据段，具有可写权限(对于GDT更详细的描述，参考[这里](http://wiki.osdev.org/Global_Descriptor_Table "GDT"))。两个段的段基址都是0x0，长度也都是0xffffffff，实际上是共用了相同的线性地址空间。

回到主线，现在我们已经切换到了保护模式，并跳转到start32处开始执行。这里值得注意的一点是最后执行的ljmp指令，宏GDT\_ENTRY只是简单的将参数n左移三位，这是因为在保护模式中段寄存器中并不像实模式那样直接存放段基址，而是存放了一个叫做段选择子的结构来指出选择的段，段选择子结构如下：

<figure style="text-align: center;">
  <img src="/assets/images/selector.jpg" alt="段选择子" />
  <figcaption>段选择子</figcaption>
</figure>

结构中TI位用于标识该段是GDT还是LDT中的段(0为GDT，1为LDT)、RPL表示运行的权限等级(0-3，0为最高权限)、高13位表示段描述符的标号。因此ljmp的操作数$GDT\_ENTRY(1)表示选择了GDT中的第一个段描述符，并具有最高权限。跳转成功后执行的start32中32位代码如下： `.code32 start32: # 设置数据访问所用的段寄存器(%DS, %ES, %SS) movw $GDT_ENTRY(2), %ax movw %ax, %ds # %DS = %AX movw %ax, %es # %ES = %AX movw %ax, %ss # %SS = %AX  # 设置栈位置。栈从此没有切换过，请注意栈的大小！ movl $0x8000, %esp # %ESP = $0x8000 call bootmain # 跳转到C代码执行，此处不会返回` 这段代码所做的事情非常简单，首先设置了ds、es、ss段寄存器，使其指向GDT中的第二项——数据段，然后设置栈顶指针为0x8000，最后跳转到C函数bootmain执行。

之后的事情相对来说就简单多了，我们已经为内核运行布置了良好的环境，现在只要将内核载入到内存中就可以了，值得庆幸的是这部分代码可以用C来完成，Nanos的bootmain函数如下: `void bootmain(void) { struct ELFHeader *elf; struct ProgramHeader *ph, *eph; unsigned char *pa, *i;  /* 因为引导扇区只有512字节，我们设置了堆栈从0x8000向下生长。 * 我们需要一块连续的空间来容纳ELF文件头，因此选定了0x8000。 */ elf = (struct ELFHeader*)0x8000;  /* 读入ELF文件头 */ readseg((unsigned char*)elf, 4096, 0);  /* 把每个program segement依次读入内存 */ ph = (struct ProgramHeader*)((char *)elf + elf->phoff); eph = ph + elf->phnum; for(; ph < eph; ph ++) { pa = (unsigned char*)ph->paddr; /* 获取物理地址 */ readseg(pa, ph->filesz, ph->off); /* 读入数据 */ for (i = pa + ph->filesz; i < pa + ph->memsz; *i ++ = 0); }  ((void(*)(void))elf->entry)(); // 离开bootloader }` 因为Nanos的内核被编译成ELF格式，所以bootloader所做的事情就是将ELF格式的内核按照ELF规定的描述载入到内存中(如果你不清楚ELF是什么，请移步[这里](http://en.wikipedia.org/wiki/Executable_and_Linkable_Format "ELF"))。C语言代码很容易理解，整体的bootmain流程如下：

1. 将内核的ELF头读入0x8000起始的内存空间中(0x8000向下为栈空间，在start.S中设置的)
2. 按照ELF头的描述依次将每一个段拷贝到对应的内存空间中
3. 跳转到ELF头所规定的程序入口(即内核入口)开始执行

运行到这里，bootloader终于完成了使命，功成身退了。

* * *

### 参考资料

- [OSDev Wiki](http://wiki.osdev.org/Main_Page "OSDev")
- 《深入理解Linux内核》
