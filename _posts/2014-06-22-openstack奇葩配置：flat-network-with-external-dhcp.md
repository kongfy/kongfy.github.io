---
title: "OpenStack奇葩配置：Flat network with external DHCP"
date: 2014-06-22
categories: 
  - "cloud-computing"
tags: 
  - "openstack"
---

最近对实验室的实验用OpenStack环境进行调整，遇到的最大的阻力来自于系楼网络的特殊性：系楼网络采用强制DHCP的模式，这就意味着我没有办法通过手工设定IP地址的方式来使用虚拟机——即使这个IP地址是可用的。

OpenStack似乎没有针对这种情况的网络模式（即使FlatManager也不行），因为所有的网络模式都需要在虚拟机创建时就可以确定虚拟机的IP，这一点在系楼的网络中是做不到的，同时在系楼中也不能做到拥有可以自己管理的预留IP，所以floating IP的概念也拜拜了。

折腾了一段时间以后总算是找到了一种非常规的解决方案：在FlatManager的基础上通过合并内部网和外部网来达到把虚拟机和物理服务器置于同一网络中的目的。

**注：下文中所有配置均针对icehouse版本。**

<!--more-->

* * *

## 网络配置

首先我们要按照标准的Flat网络模型配置计算节点网络：

<figure style="text-align: center;">
  <img src="/assets/images/generic-bridge-config-2.png" alt="Flat网络模型" />
  <figcaption>Flat网络模型</figcaption>
</figure>

在Flat模式中需要手工建立Linux网桥，网上这方面的资料很多了，在此不进行赘述。值得注意的一点是如果创建的网桥名称不是默认的br100，那么在配置的过程中仅仅按照文档描述的修改配置文件中的 

```bash
flat_network_bridge=vmbr
```

 是不够的，还需要在创建网络时指定网桥的名字才可以...（所以说还是按照默认的br100比较好）

进行了上面的配置之后虚拟机已经可以通过系楼DHCP获取到IP了，但是仍然不能正常的进行网络通信...经过一段时间的挣扎（抓包抓包抓包），发现似乎虚拟机的ARP报文被什么东西拦截了，原来这是OpenStack的防火墙机制，因为DHCP获取到的IP和OpenStack认为的IP不同，所以被判断为IP欺诈报文！So...干掉防火墙： 

```bash
firewall_driver = nova.virt.firewall.NoopFirewallDriver
```

因为OpenStack的防火墙实际上是使用了libvirt的nwfilter机制，如果已经创建的规则关闭防火墙后没有失效，你可能需要在virsh中手动undefine对应的nwfilter才可以。

到这一步配置已经全部完成了，网络也可以正常访问了，完整的网络配置如下： 

```bash
network_manager = nova.network.manager.FlatManager
firewall_driver = nova.virt.firewall.NoopFirewallDriver
multi_host = True
flat_network_bridge = vmbr
allow_same_net_traffic = true
```

* * *

## 有得有失

做这样类似于trick的配置必然是有得有失的，**优点**在于：

- 完成了特别的需求，将所有虚拟机置于了与物理服务器相同的网络中
- 因为没有了内外网的区别，节省了一个网口（如果这能算是优点的话...）

这样的配置也带来了很多**缺点**：

- 最严重的一点：metadata-api不能使用了（因为虚拟机的网关不再是计算节点，因此169.254.169.254的IP不能正常访问了），这带来的直接麻烦就是虚拟机中cloud-init也不能使用了...
- OpenStack记录的IP地址与真实的IP地址不一致，这个主要是不方便，可以忍
- 没有内部网和外部网的隔离，虚拟机安全性下降，且网络流量会互相影响，增大了带宽压力
- ...

所以说这样奇葩的配置虽然满足了最初的诡异需求，但也造成了不小的副作用，一般不建议使用这样的配置，不过为了适应系楼的特殊网络环境，似乎我也没有什么别的选择了...

* * *

## 参考资料

[OpenStack Networking – FlatManager and FlatDHCPManager](http://www.mirantis.com/blog/openstack-networking-flatmanager-and-flatdhcpmanager/http:// "OpenStack Networking – FlatManager and FlatDHCPManager")
