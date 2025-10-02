---
title: "使用python模拟weibo登录"
date: 2013-04-02
categories: 
  - "python-2"
tags: 
  - "python"
---

之前写过在python中使用weibo API的方法，见[这里](/posts/2013-03-*-%e9%80%9a%e8%bf%87python-sdk%e4%bd%bf%e7%94%a8weibo-api/)，但是因为weibo API有频率限制，不够目前需求使用，所以通过爬虫模拟登录weibo进行直接抓取还是很有必要的，第一步要做的事情就是模拟登录过程。

weibo的登录方法一直在变，不知道现在的方法还能使用多久。 目前登录使用的是RSA加密的方式，总体来看步骤分为三步：

1. 访问预登录地址，获取servertime、nonce和RSA公钥
2. 访问认证地址，发送编码后的用户名和RSA加密过的密码，获得跳转地址
3. 访问获得的地址，获取到登录cookie，登录完成

<!--more-->

代码如下，注释比较少，主要是\_\_login()函数内的过程，需要安装rsa包，easy\_install即可 `# -*- coding: utf-8 -*- import urllib2, urllib, cookielib import re, json, base64 import rsa, binascii  url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625' url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'  class Toy(object): def fecth_page(self, url = 'http://weibo.com', data = None): return self.__opener.open(url, data) def __init__(self, username, password): self.__username = username self.__password = password cj = cookielib.CookieJar() opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20100101 Firefox/19.0')] self.__opener = opener self.__login() def __encode_passwd(self, pwd, servertime, nonce, pubkey): rsaPublickey = int(pubkey, 16) key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥 message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)#拼接明文 js加密文件中得到 passwd = rsa.encrypt(message, key)#加密 passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。 return passwd  def __encode_username(self, username): username = urllib.quote(username) username = base64.encodestring(username)[:-1] return username def __prelogin(self): html = self.__opener.open(url_prelogin).read() json_data = re.search('\((.*)\)', html).group(1) data = json.loads(json_data) servertime = data['servertime'] nonce = data['nonce'] pubkey = data['pubkey'] rsakv = data['rsakv'] return servertime, nonce, pubkey, rsakv def __login(self): (servertime, nonce, pubkey, rsakv) = self.__prelogin() sp = self.__encode_passwd(self.__password, servertime, nonce, pubkey) su = self.__encode_username(self.__username) postdata = { 'entry': 'weibo', 'gateway': '1', 'from': '', 'savestate': '7', 'userticket': '1', 'ssosimplelogin': '1', 'vsnf': '1', 'vsnval': '', 'su': su, 'service': 'miniblog', 'servertime': servertime, 'nonce': nonce, 'pwencode': 'rsa2', 'sp': sp, 'encoding': 'UTF-8', 'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack', 'returntype': 'META', 'rsakv' : rsakv, }  postdata = urllib.urlencode(postdata) html = self.__opener.open(url_login, postdata).read() url_final = re.search('location\.replace\(\"(.*?)\"\)', html).group(1) self.__opener.open(url_final)`
