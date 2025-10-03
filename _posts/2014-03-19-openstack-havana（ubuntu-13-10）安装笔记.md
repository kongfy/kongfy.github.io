---
title: "OpenStack Havana（Ubuntu 13.10）安装笔记"
date: 2014-03-19
categories: 
  - "cloud-computing"
tags: 
  - "openstack"
---

安装配置OpenStack最好的资料是OpenStack的[官方安装指南](http://docs.openstack.org/havana/install-guide/install/apt/content/)，我就是按照官方指南一步一步进行的，虽然基于的操作系统版本不同（指南中使用的是Ubuntu 12.04），所幸没有遇到什么诡异的问题，不废话了，整个过程记录如下。

* * *

## 安装环境

> 操作系统：Ubuntu 13.10 配置机器数：1（单点安装） 机器网卡数量：2 Hypervisor类型：KVM

<!--more-->

* * *

## 安装顺序

OpenStack主要包括Identity Service、Image Service、Compute Service、Dashboard、Block Storage等几部分组成，OpenStack Havana的整体结构图如下（图片出自官方安装指南）：

<figure style="text-align: center;">
  <img src="/assets/images/F263D492-D28B-468D-87BB-C1A5860E0FCC.jpg" alt="OpenStack基本结构概况" />
  <figcaption>OpenStack基本结构概况</figcaption>
</figure>

我没有安装图中全部的模块，仅选择了主要的几部分，按照下面的顺序进行安装：

1. 基础服务
2. Identity Service(keystone)
3. Compute Service(nova)
4. Dashboard(horizon)
5. Block Storage(cinder)

* * *

## 一些约定

- 由于本文是按照单节点的结构进行安装的，所以文中多使用localhost（127.0.0.1）来进行配置。如果需要在多节点环境中进行安装，将localhost改为对应的节点即可。
- 下文中将不包含安装配置中具体使用的密码，所有使用到的密码如下：

| **密码** | **描述** |
| --- | --- |
| RABBIT\_PASS | RabbitMQ的guest用户密码 |
| KEYSTONE\_DBPASS | keystone使用的数据库密码 |
| ADMIN\_PASS | admin用户密码 |
| GLANCE\_DBPASS | glance使用的数据库密码 |
| GLANCE\_PASS | glance用户密码 |
| NOVA\_DBPASS | nova使用的数据库密码 |
| NOVA\_PASS | nova用户密码 |
| CINDER\_DBPASS | cinder使用的数据库密码 |
| CINDER\_PASS | cinder用户密码 |

**干掉弱密码：**一种好用的随机密码生成： `$ openssl rand -hex 5`

* * *

## 基础服务

安装ntp，作为OpenStack集群的时钟同步服务。如果为多节点安装，修改除Controller以外其他所有节点的/etc/ntp.conf将server指向Controller节点以同步时钟。 `$ apt-get install ntp` 安装MySQL并初始化 `$ apt-get install python-mysqldb mysql-server $ mysql_install_db $ mysql_secure_installation` 添加OpenStack的Ubuntu源 `$ apt-get install python-software-properties $ add-apt-repository cloud-archive:havana $ apt-get update && apt-get dist-upgrade  $ reboot` 安装消息队列服务rabbitmq，并修改rabbitmq guest用户的密码供OpneStack使用 `$ apt-get install rabbitmq-server $ rabbitmqctl change_password guest RABBIT_PASS`

* * *

## 安装Identity Service

`$ apt-get install keystone` 修改keystone配置文件/etc/keystone/keystone.conf `[DEFAULT] # 替换一个随机的admin token admin_token = ADMIN_TOKEN  [sql] # 配置keystone数据库，如果为多节点安装，把localhost替换为数据库所在节点 connection = mysql://keystone:KEYSTONE_DBPASS@localhost/keystone` 在MySQL中为keystone创建数据库和用户 `$ mysql -u root -p mysql> CREATE DATABASE keystone; mysql> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \ IDENTIFIED BY 'KEYSTONE_DBPASS'; mysql> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \ IDENTIFIED BY 'KEYSTONE_DBPASS’;` 初始化keystone数据表 `$ keystone-manage db_sync` 重启服务 `$ initctl restart keystone` 创建初始用户、角色等 `$ export OS_SERVICE_TOKEN=ADMIN_TOKEN $ export OS_SERVICE_ENDPOINT=http://localhost:35357/v2.0 $ keystone tenant-create --name=admin --description="Admin Tenant" $ keystone tenant-create --name=service --description="Service Tenant" $ keystone user-create --name=admin --pass=ADMIN_PASS --email=admin@example.com $ keystone role-create --name=admin $ keystone user-role-add --user=admin --tenant=admin --role=admin` 为keystone注册服务和endpoint `$ keystone service-create --name=keystone --type=identity \ --description="Keystone Identity Service" $ keystone endpoint-create \ --service-id=keystone \ --publicurl=http://localhost:5000/v2.0 \ --internalurl=http://localhost:5000/v2.0 \ --adminurl=http://localhost:35357/v2.0` [验证keystone是否可以正常工作](http://docs.openstack.org/havana/install-guide/install/apt/content/keystone-verify.html)

* * *

## 安装Image Service

镜像存储直接使用本地file system作为存储后端，所以不需要额外安装Object Storage等存储服务 `$ apt-get install glance python-glanceclient` 修改glance配置文件/etc/glance/glance-api.conf和/etc/glance/glance-registry.conf `[DEFAULT] # 设置数据库 sql_connection = mysql://glance:GLANCE_DBPASS@localhost/glance  # 设置keystone验证信息 [keystone_authtoken] auth_host = localhost auth_port = 35357 auth_protocol = http admin_tenant_name = service admin_user = glance admin_password = GLANCE_PASS  [paste_deploy] flavor = keystone` 创建数据库和用户 `$ mysql -u root -p mysql> CREATE DATABASE glance; mysql> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' \ IDENTIFIED BY 'GLANCE_DBPASS'; mysql> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' \ IDENTIFIED BY 'GLANCE_DBPASS’;` 初始化glance数据库 `$ glance-manage db_sync` 在/etc/glance/glance-api-paste.ini和/etc/glance/glance-registry-paste.ini中添加keystone验证信息 `[filter:authtoken] paste.filter_factory=keystoneclient.middleware.auth_token:filter_factory auth_host=localhost admin_user=glance admin_tenant_name=service admin_password=GLANCE_PASS` 为glance创建用户 `$ keystone user-create --name=glance --pass=GLANCE_PASS \ --email=glance@example.com $ keystone user-role-add --user=glance --tenant=service --role=admin` 为glance注册服务和endponit `$ keystone service-create --name=glance --type=image \ --description="Glance Image Service" $ keystone endpoint-create \ --service-id=glance \ --publicurl=http://localhost:9292 \ --internalurl=http://localhost:9292 \ --adminurl=http://localhost:9292` 重启服务 `$ initctl restart glance-registry $ initctl restart glance-api` [验证glance是否正常工作](http://docs.openstack.org/havana/install-guide/install/apt/content/glance-verify.html)

* * *

## 安装Compute Service(Controller部分)

`$ apt-get install nova-novncproxy novnc nova-api \ nova-ajax-console-proxy nova-cert nova-conductor \ nova-consoleauth nova-doc nova-scheduler \ python-novaclient` 修改nova配置文件/etc/nova/nova.conf `# 设置数据库 sql_connection = mysql://nova:NOVA_DBPASS@localhost/nova  # 设置keystone验证信息 auth_strategy = keystone auth_host = localhost auth_port = 35357 auth_protocol = http admin_tenant_name = service admin_user = nova admin_password = NOVA_PASS  # 设置消息队列 rpc_backend = nova.rpc.impl_kombu rabbit_host = localhost rabbit_password = RABBIT_PASS  # 设置VNC # 修改为自己的public_ip my_ip=114.221.83.138 vncserver_listen=114.221.83.138 vncserver_proxyclient_address=114.221.83.138` 创建数据库和用户 `$ mysql -u root -p mysql> CREATE DATABASE nova; mysql> GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' \ IDENTIFIED BY 'NOVA_DBPASS'; mysql> GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' \ IDENTIFIED BY 'NOVA_DBPASS’;` 初始化nova数据表 `$ nova-manage db sync` 在/etc/nova/api-paste.ini中添加keystone验证信息 `[filter:authtoken] paste.filter_factory = keystoneclient.middleware.auth_token:filter_factory auth_host = localhost auth_port = 35357 auth_protocol = http auth_uri = http://localhost:5000/v2.0 admin_tenant_name = service admin_user = nova admin_password = NOVA_PASS` 为nova创建用户 `$ keystone user-create --name=nova --pass=NOVA_PASS --email=nova@example.com $ keystone user-role-add --user=nova --tenant=service --role=admin` 为nova创建服务和endpoint `$ keystone service-create --name=nova --type=compute \ --description="Nova Compute service" $ keystone endpoint-create \ --service-id=nova \ --publicurl=http://localhost:8774/v2/%\(tenant_id\)s \ --internalurl=http://localhost:8774/v2/%\(tenant_id\)s \ --adminurl=http://localhost:8774/v2/%\(tenant_id\)s` 重启服务 `$ initctl restart nova-api $ initctl restart nova-cert $ initctl restart nova-consoleauth $ initctl restart nova-scheduler $ initctl restart nova-conductor $ initctl restart nova-novncproxy`

* * *

## 安装Compute Service(Compute Node部分)

这一部分内容安装的是nova运行在compute node上的部分，如果为单节点安装，需要跳过与Controller重复的部分 `$ apt-get install nova-compute-kvm python-guestfs $ apt-get install nova-network nova-api-metadata` **注意**：nova-api-metadata只在独立的compute node安装，与nova-api冲突，如果部署为单节点已经安装了nova-api，则不需要安装nova-api-metadata。 修改nova配置文件/etc/nova/nova.conf `[DEFAULT] # 设置验证方式为keystone auth_strategy=keystone  # 设置数据库 connection = mysql://nova:NOVA_DBPASS@localhost/nova  # 设置消息队列 rpc_backend = nova.rpc.impl_kombu rabbit_host = localhost rabbit_password = RABBIT_PASS  # 设置VNC # 修改为你的public_ip my_ip=114.221.83.138 vnc_enabled=True vncserver_listen=0.0.0.0 vncserver_proxyclient_address=114.221.83.138 novncproxy_base_url=http://114.221.83.138:6080/vnc_auto.html  # 设置Image Service地址 glance_host=localhost  # 设置网络  network_manager=nova.network.manager.FlatDHCPManager firewall_driver=nova.virt.libvirt.firewall.IptablesFirewallDriver network_size=254 allow_same_net_traffic=False multi_host=True send_arp_for_ha=True share_dhcp_address=True force_dhcp_release=True flat_network_bridge=br100 flat_interface=wlan0 public_interface=eth0` 注意在上面的网络设置中，flat\_interface和public\_interface最好能够区分开，否则可能会影响虚拟机通过NAT连接外网，见后文。

在/etc/nova/api-paste.ini中添加keystone验证信息 `[filter:authtoken]paste.filter_factory = keystone client.middleware.auth_token:filter_factory auth_host = localhost auth_port = 35357 auth_protocol = http admin_tenant_name = service admin_user = nova admin_password = NOVA_PASS` 创建虚拟网络 `$ nova network-create vmnet --fixed-range-v4=10.0.0.0/24 \ --bridge=br100 --multi-host=T`

* * *

## 安装Dashboard

安装apache2 `$ apt-get install apache2` 安装horizon `$ apt-get install memcached libapache2-mod-wsgi openstack-dashboard $ apt-get remove --purge openstack-dashboard-ubuntu-theme # 删除ubuntu的horizon主题  $ a2enmod wsgi $ a2enconf openstack-dashboard` 修改horizon配置文件中OPENSTACK\_HOST为Identity Service所在节点 `OPENSTACK_HOST = "localhost"` 一切顺利的话现在就可以通过访问 http://localhost/horizon 使用OpenStack了

* * *

## 安装Block Storage

安装进行到这里OpenStack的基本功能已经可以正常使用了。但是目前为止的安装中instance只能使用Ephemeral Storage来进行存储，当instance被terminate后所有的存储会丢失。如果想要有可持久的存储，接下来需要安装block storage，也就是OpenStack的Cinder模块。 `$ apt-get install cinder-api cinder-scheduler` 修改cinder配置文件/etc/cinder/cinder.conf `# 设置消息队列 rpc_backend = cinder.openstack.common.rpc.impl_kombu rabbit_host = localhost rabbit_port = 5672 rabbit_userid = guest rabbit_password = RABBIT_PASS  # 设置数据库连接 [database] connection = mysql://cinder:CINDER_DBPASS@localhost/cinder` 在/etc/cinder/api-paste.ini中添加keystone验证信息 `[filter:authtoken] paste.filter_factory=keystone client.middleware.auth_token:filter_factory auth_host=localhost auth_port = 35357 auth_protocol = http auth_uri = http://localhost:5000 admin_tenant_name=service admin_user=cinder admin_password=CINDER_PASS` 创建数据库和用户 `# mysql -u root -p mysql> CREATE DATABASE cinder; mysql> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' \ IDENTIFIED BY 'CINDER_DBPASS'; mysql> GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' \ IDENTIFIED BY 'CINDER_DBPASS’;` 初始化cinder数据表 `$ cinder-manage db sync` 为cinder创建用户 `$ keystone user-create --name=cinder --pass=CINDER_PASS --email=cinder@example.com $ keystone user-role-add --user=cinder --tenant=service --role=admin` 为cinder注册服务和endpoint `$ keystone service-create --name=cinder --type=volume \ --description="Cinder Volume Service" $ keystone endpoint-create \ --service-id=cinder \ --publicurl=http://localhost:8776/v1/%\(tenant_id\)s \ --internalurl=http://localhost:8776/v1/%\(tenant_id\)s \ --adminurl=http://localhost:8776/v1/%\(tenant_id\)s $ keystone service-create --name=cinderv2 --type=volumev2 \ --description="Cinder Volume Service V2" $ keystone endpoint-create \ --service-id=cinderv2 \ --publicurl=http://localhost:8776/v2/%\(tenant_id\)s \ --internalurl=http://localhost:8776/v2/%\(tenant_id\)s \ --adminurl=http://localhost:8776/v2/%\(tenant_id\)s` 重启服务 `$ initctl restart cinder-scheduler $ initctl restart cinder-api` Cinder需要选择一种存储方案作为存储后端，可选的有LVM、Ceph、NFS、ZFS等，这里我选择LVM/iSCSI作为存储后端选择。 如果你也选择LVM作为cinder存储后端，你需要至少一个完整的磁盘分区来配置LVM，你可以选择使用完整的磁盘分区或者[使用普通文件创建loop设备](http://www.linuxcommand.org/man_pages/losetup8.html)（仅限于实验用）来配置LVM，[这里](https://wiki.archlinux.org/index.php/LVM_%28%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87%29)有一篇对于LVM的介绍。 `$ apt-get install lvm2` 我用来配置LVM的分区是/dev/sda9，根据你的情况进行设置 `$ pvcreate /dev/sda9 # 创建逻辑卷 $ vgcreate cinder-volumes /dev/sda9 # 创建卷组` 安装cinder-volume `$ apt-get install cinder-volume` 重启服务 `$ initctl restart cinder-volume $ initctl restart tgt`

* * *

## 虚拟机的ping和SSH

刚安装完成OpenStack后启动instance，你会发现在宿主机上也无法ping通虚拟机ip，并且无法使用ssh登录虚拟机。这是因为OpenStack的安全组设置默认不允许非虚拟机局域网内的input流量，可以通过在Horizon中修改instance所属的安全组（默认为default组）设置或是执行下面的命令来允许icmp和ssh流量进入虚拟机： `$ nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0 $ nova secgroup-add-rule default tcp 22 22 0.0.0.0/0` 其实质上是OpenStack在宿主机上增加了如下iptables规则: `$ iptables -A nova-compute-inst-9 -p icmp -j ACCEPT $ iptables -A nova-compute-inst-9 -p tcp -m tcp --dport 22 -j ACCEPT`

* * *

## 外网访问

OpenStack文档中给出的外网和私有网的连通方式是绑定floating ip和fixed ip的方法，实际上在没有绑定floating ip的情况下虚拟机也可以通过NAT的方式访问外网。 在/etc/nova/nova.conf中添加下面的规则即可（仅限FlatDHCP和VLAN模式）。 `routing_source_ip=114.221.83.138 # public_interface对应的ip地址` 这条配置实质上是在宿主机上增加了如下iptables规则: `$ iptables -A nova-network-snat -s 10.0.0.0/24 -o eth0 \ -j SNAT --to-source 114.212.83.138` 另外别忘了打开Linux的ip转发功能 `$ echo 1 > /proc/sys/net/ipv4/ip_forward` 重启nova-network `$ initctl restart nova-network`
