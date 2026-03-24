---
title: "拯救Openclaw微信插件"
date: 2026-03-24
categories:
  - "工具"
  - "AI"
tags:
  - "OpenClaw"
  - "weixin"
  - "Codex"
  - "插件"
  - "兼容性"
toc: false
toc_sticky: false
---

微信的龙虾插件在存活了一个周末以后，随着openclaw新版本升级挂了，先别急着删插件，在AI coding时代，最方便的做法是直接打开codex，用gpt-5.4模型要求他修复openclaw升级报错就可以了，后面附上稳定无情的bug修复机器codex给我的完整修复报告:

<!--more-->

## 背景

OpenClaw 升级后，`openclaw-weixin` 插件在新版本环境下无法正常加载。本文只记录 `openclaw-weixin` 本身的排查和修复过程，不涉及其他插件或配置问题。

## 现象

在插件加载阶段，`openclaw-weixin` 先后暴露出两类错误：

第一类错误：

```text
PluginLoadFailureError: plugin load failed: openclaw-weixin:
Error: Cannot find module 'openclaw/plugin-sdk'
```

第二类错误：

```text
TypeError: resolvePreferredOpenClawTmpDir is not a function
```

这说明问题并不是单一语法错误，而是插件与新版宿主 SDK 的运行时兼容性断裂。

## 调试目标

1. 让 `openclaw-weixin` 在当前 OpenClaw 版本下重新可加载。
2. 尽量少改插件逻辑，只修复宿主 SDK 兼容层。
3. 不改业务行为，不顺手重构。

## 第一阶段：确认插件为何找不到 `openclaw/plugin-sdk`

先检查 `openclaw-weixin` 源码，发现插件多处直接从：

```ts
import ... from "openclaw/plugin-sdk";
```

导入类型和运行时函数。

相关文件包括：

- [index.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/index.ts)
- [src/channel.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/channel.ts)
- [src/log-upload.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/log-upload.ts)
- [src/util/logger.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/util/logger.ts)
- [src/auth/accounts.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/accounts.ts)
- [src/auth/pairing.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/pairing.ts)
- [src/runtime.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/runtime.ts)
- [src/monitor/monitor.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/monitor/monitor.ts)
- [src/messaging/process-message.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/process-message.ts)
- [src/messaging/send.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/send.ts)

接着对比两个本地插件：

- `lossless-claw`
- `openclaw-weixin`

发现关键差异：

- `lossless-claw/node_modules` 中存在 `openclaw`
- `openclaw-weixin/node_modules` 中不存在 `openclaw`

这意味着 `openclaw-weixin` 被按本地扩展目录加载时，运行时模块解析无法在它自己的依赖树内找到宿主包，因此第一次失败是模块解析失败，而不是函数本身不存在。

## 第一处修复：补宿主包链接

为了让插件至少能解析宿主 SDK，在插件依赖目录下补了一个符号链接：

```text
/Users/kongfy/.openclaw/extensions/openclaw-weixin/node_modules/openclaw
-> /opt/homebrew/lib/node_modules/openclaw
```

这一步的作用很明确：

1. 不改插件源码
2. 不复制宿主包
3. 只让插件运行时能找到 `openclaw/plugin-sdk`

补完链接后，原来的 “Cannot find module `openclaw/plugin-sdk`” 错误消失了，但立刻暴露出下一层兼容性问题。

## 第二阶段：确认不是“模块缺失”，而是“SDK 导出面变化”

补完链接后再次测试，出现新的错误：

```text
TypeError: resolvePreferredOpenClawTmpDir is not a function
```

这说明：

- `openclaw/plugin-sdk` 模块已经能被找到
- 但插件依赖的某些顶层导出，在新版里已经不再从顶层导出

随后检查新版 `openclaw` 主包的 `exports`，确认：

- `./plugin-sdk` 入口还存在
- 但顶层导出已经非常少
- 许多原来可从顶层取到的运行时函数，被拆到新的公开子路径中

进一步核对后，发现 `openclaw-weixin` 依赖的函数分散到了这些模块：

- `openclaw/plugin-sdk/core`
- `openclaw/plugin-sdk/diffs`
- `openclaw/plugin-sdk/command-auth`
- `openclaw/plugin-sdk/matrix`
- `openclaw/plugin-sdk/msteams`
- `openclaw/plugin-sdk/text-runtime`

因此根因不是某一个函数被删除，而是：

`openclaw-weixin` 依赖了旧版 `openclaw/plugin-sdk` 的顶层导出面；升级后这些运行时能力仍存在，但公开入口已经迁移。

## 第二处修复：增加本地兼容桥接层

如果直接在每个文件里分别改成新版子路径，会让兼容性逻辑散落在整个插件中，后续维护成本很高。

因此采用了集中收口的方式：新增一个本地桥接文件。

新增文件：

- [src/openclaw-bridge.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/openclaw-bridge.ts)

这个文件负责两件事：

1. 统一重新导出插件需要的类型
2. 从新版公开子路径重新导出运行时函数

桥接层导出的主要内容如下。

类型：

- `ChannelAccountSnapshot`
- `ChannelPlugin`
- `OpenClawConfig`
- `OpenClawPluginApi`
- `PluginRuntime`
- `ReplyPayload`

运行时函数：

- `buildChannelConfigSchema`
- `normalizeAccountId`
- `resolvePreferredOpenClawTmpDir`
- `resolveDirectDmAuthorizationOutcome`
- `resolveSenderCommandAuthorizationWithRuntime`
- `createTypingCallbacks`
- `withFileLock`
- `stripMarkdown`

这些符号分别从新版的公开子路径重新导出。

## 第三处修复：把插件源码统一切到桥接层

建立桥接层后，把所有原来直接从 `openclaw/plugin-sdk` 顶层读取内容的文件，统一改成从本地桥接模块读取。

修改文件如下：

- [index.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/index.ts)
- [src/log-upload.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/log-upload.ts)
- [src/util/logger.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/util/logger.ts)
- [src/channel.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/channel.ts)
- [src/auth/accounts.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/accounts.ts)
- [src/auth/pairing.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/pairing.ts)
- [src/runtime.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/runtime.ts)
- [src/monitor/monitor.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/monitor/monitor.ts)
- [src/messaging/process-message.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/process-message.ts)
- [src/messaging/send.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/send.ts)

这一步之后，插件代码不再直接耦合新版宿主的顶层导出面，而是通过桥接层与宿主交互。

## 中途遇到的小问题

桥接层接入后，还修过一次小路径问题：

- [src/util/logger.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/util/logger.ts)

这里最初桥接路径写得不一致，后来统一调整为稳定的相对路径写法，避免不同文件层级下的引用歧义。

这一步没有改变业务逻辑，只是把桥接引用路径修正到正确位置。

## 为什么没有直接“逐个函数热修”

这次没有采用“哪里报错修哪里”的方式，而是先把根因归类后统一收口，原因有三个：

1. 插件依赖的旧顶层导出不止一个
2. 如果只按报错逐个修，很容易每修一处再暴露下一处
3. 兼容层集中后，未来再升级 OpenClaw 时只需要改一个桥接文件

换句话说，这次改动的重点不是重写插件，而是把插件对宿主 SDK 的依赖入口做了一次兼容封装。

## 最终验证

修复完成后，重启网关服务，让新插件代码生效。之后通过 `openclaw status` 验证插件状态。

最终状态中，`openclaw-weixin` 显示为：

- `Enabled: ON`
- `State: OK`

这说明：

1. 插件已经成功被宿主发现
2. 插件已经完成加载
3. 旧版顶层 SDK 依赖导致的崩溃已被修复

同时，最新启动日志中已不再出现：

- `Cannot find module 'openclaw/plugin-sdk'`
- `resolvePreferredOpenClawTmpDir is not a function`

## 本次修改清单

新增：

- [src/openclaw-bridge.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/openclaw-bridge.ts)

修改：

- [index.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/index.ts)
- [src/log-upload.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/log-upload.ts)
- [src/util/logger.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/util/logger.ts)
- [src/channel.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/channel.ts)
- [src/auth/accounts.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/accounts.ts)
- [src/auth/pairing.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/auth/pairing.ts)
- [src/runtime.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/runtime.ts)
- [src/monitor/monitor.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/monitor/monitor.ts)
- [src/messaging/process-message.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/process-message.ts)
- [src/messaging/send.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/messaging/send.ts)

运行时补充：

```text
/Users/kongfy/.openclaw/extensions/openclaw-weixin/node_modules/openclaw
-> /opt/homebrew/lib/node_modules/openclaw
```

## 最终根因总结

`openclaw-weixin` 的问题本质上是两层：

1. 插件自身依赖树里缺少宿主包入口，导致运行时无法解析 `openclaw/plugin-sdk`
2. 插件仍按旧版方式依赖 `openclaw/plugin-sdk` 顶层导出，而新版 SDK 已把这些运行时 API 拆分到公开子模块

对应修复也分两层：

1. 先让插件运行时能找到宿主包
2. 再通过桥接层把旧依赖方式迁移到新版公开子路径

## 后续建议

1. 如果 `openclaw-weixin` 后续继续维护，保留 [src/openclaw-bridge.ts](/Users/kongfy/.openclaw/extensions/openclaw-weixin/src/openclaw-bridge.ts) 作为唯一宿主兼容入口。
2. 如果未来再升级 OpenClaw，优先检查桥接层是否仍覆盖所有被插件使用的 SDK 符号。
3. 如果插件未来发布正式版本，最好在包层面明确宿主 SDK 兼容策略，而不是继续依赖本地软链接。
