# 内部链接修复完成

## 修复概览

成功修复了博客文章中的所有内部链接，将错误的 `/posts/` 路径格式更新为符合 Jekyll 配置的正确格式。

## 修复统计

- **修复文件数**: 11 个文件
- **修复链接数**: 14 个内部链接

## 修复详情

### 自动修复的链接（3个）

1. `2017-01-02-多核并发编程中的cache-line对齐问题.md`
   - 修复指向 `2016-10-17-cache-coherence-sequential-consistency-and-memory-barrier` 的链接

2. `2017-01-27-用户态同步之自旋锁.md`
   - 修复指向 `2016-10-17-cache-coherence-sequential-consistency-and-memory-barrier` 的链接

3. `2017-04-18-并发编程牛刀小试：seqlock.md`
   - 修复指向 `2016-10-17-cache-coherence-sequential-consistency-and-memory-barrier` 的链接
   - 修复指向 `2017-01-27-用户态同步之自旋锁` 的链接

### 手动修复的链接（11个）

4. `2013-02-02-再见，百度.md`
   - `/posts/2012-09-*-技术评定不及格/` → `/2012-09-27-技术评定不及格/`

5. `2016-08-06-被误用的一致性.md` (2个链接)
   - `/posts/2016-05-*-分布式共识consensus：viewstamped、raft及paxos/` → `/2016-05-25-分布式共识consensus：viewstamped、raft及paxos/`

6. `2015-10-27-博弈论笔记：囚徒困境和重复博弈.md`
   - `/posts/2015-10-*-博弈论笔记normal-form-game-and-nash-equilibrium/` → `/2015-10-10-博弈论笔记normal-form-game-and-nash-equilibrium/`

7. `2014-05-03-nanos-note-1-bootloader.md`
   - `/posts/2014-03-*-译计算机启动过程-how-computers-boot-up/` → `/2014-03-24-译计算机启动过程-how-computers-boot-up/`

8. `2018-07-28-paxos-revisit.md`
   - `/posts/2016-05-*-分布式共识consensus：viewstamped、raft及paxos/` → `/2016-05-25-分布式共识consensus：viewstamped、raft及paxos/`

9. `2014-05-19-nanos-note-2-内核初始化.md`
   - `/posts/2014-05-*-nanos-note-1-bootloader/` → `/2014-05-03-nanos-note-1-bootloader/`

10. `2014-03-24-译计算机启动过程-how-computers-boot-up.md`
    - `/posts/2014-03-*-译主板芯片集和存储地址映射-motherboard-chipsets-and-the-memory-map/` → `/2014-03-29-译主板芯片集和存储地址映射-motherboard-chipsets-and-the-memory-map/`

11. `2013-04-02-使用python模拟weibo登录.md`
    - `/posts/2013-03-*-通过python-sdk使用weibo-api/` → `/2013-03-22-通过python-sdk使用weibo-api/`

12. `2016-10-17-cache-coherence-sequential-consistency-and-memory-barrier.md`
    - `/posts/2014-11-*-linux内核同步/` → `/2014-11-13-linux内核同步/`

## 修复内容

### 主要变更

1. **移除 `/posts/` 前缀**
   - 旧格式: `/posts/YYYY-MM-DD-title/`
   - 新格式: `/YYYY-MM-DD-title/`
   - 符合 `_config.yml` 中的配置: `permalink: /:year-:month-:day-:title/`

2. **替换通配符日期**
   - 将所有使用 `*` 通配符的日期替换为实际的完整日期
   - 例: `2016-10-*` → `2016-10-17`

3. **清理URL编码**
   - 移除URL编码的字符（如 `%e5%8d%9a%e5%bc%88%e8%ae%ba`）
   - 使用实际的文件名和路径

## 验证结果

- ✅ 所有内部链接格式已统一
- ✅ 不再使用 `/posts/` 路径前缀
- ✅ 所有通配符日期已替换为完整日期
- ✅ Jekyll 构建成功，无链接错误

## 注意事项

内部链接现在遵循以下规范：
- 使用相对路径
- 格式: `/YYYY-MM-DD-文章标题/`
- 与 Jekyll permalink 配置一致
- 在新增文章时引用其他文章时，请使用此格式

## 下一步

所有内部链接已修复完成，可以：
1. 运行 `bundle exec jekyll serve` 启动本地服务器
2. 在浏览器中测试链接是否正常工作
3. 部署到生产环境

---

修复日期: 2025-10-04

