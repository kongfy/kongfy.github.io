---
title: "通过python SDK使用weibo API"
date: 2013-03-22
categories: 
  - "python-2"
tags: 
  - "python"
---

之前做JAVA课大作业的时候曾经用过weibo的API，weibo的API采用OAuth2的认证方法进行认证，也就是避免开发者知晓用户密码的一种手段。不过这样对于开发一些简单使用的客户端程序就不太友好了，可以通过程序模拟授权过程来跳过这一步骤。之前是用JAVA做的，现在用Python再做一次...

<!--more-->

Python的weibo SDK是第三方开发的[weibopy](http://michaelliao.github.com/sinaweibopy/)，主要是封装了OAuth2的认证和weibo API接口的访问和JSON解析。下载之后文件夹里主要的文件是weibo.py，将这个文件直接拷贝到工程目录下即可。当然也可以通过 

```bash
python setup.py install
```

来安装到python目录中。

装好后按照[weibo上的指导](http://open.weibo.com/wiki/%E6%96%B0%E6%89%8B%E6%8C%87%E5%8D%97)创建应用，然后就可以愉快的使用weibo API了。

代码如下：

**config.py** 

```python
# -*- coding: utf-8 -*-
 
config = {'APP_KEY' : '********',
          'APP_SECRET' : '****************************',
          'CALLBACK_URL' : 'www.kongfy.com',
          'WEIBO_USER' : '******',
          'WEIBO_PWD' : '**********',
          }
```          

**main.py**

```python
# -*- coding: utf-8 -*-
 
from weibo_toy import Toy
from config import config
 
 
if __name__ == '__main__':
    try:
        toy = Toy(config['APP_KEY'],
                  config['APP_SECRET'],
                  config['CALLBACK_URL'],
                  config['WEIBO_USER'],
                  config['WEIBO_PWD'],
                  )
    except Exception, e:
        print "Error while Oauth2 with sina api..."
        print e
        exit()
 
 
    client = toy.client
    print client.get.statuses__public_timeline()
```

**weibo\_toy.py** 

```python
# -*- coding: utf-8 -*-
 
from weibo import APIClient
import urllib2, urllib
 
class Toy(object):
    def __init__(self, app_key, app_secret, app_redirect_uri, username, password):
        self.__client = APIClient(app_key, app_secret, app_redirect_uri)
        self.__app_key = app_key
        self.__app_secret = app_secret
        self.__username = username
        self.__password = password
        self.__callback = app_redirect_uri
        
        client = self.__client
        code = self.__get_code() #获取新浪认证code
    
        #新浪返回的token，类似abc123xyz456，每天的token不一样
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in # token过期的UNIX时间
 
        #设置得到的access_token
        client.set_access_token(access_token, expires_in)
    
    def __get_code(self):
        login_url = 'https://api.weibo.com/oauth2/authorize'
        params = urllib.urlencode({'action' : 'submit', #login不能授权,submit可以
                                   'response_type' : 'code',
                                   'redirect_uri' : self.__callback,
                                   'client_id' : self.__app_key,
                                   'userId' : self.__username,
                                   'passwd' : self.__password,
                                   })
        client = self.__client
        url = client.get_authorize_url()
        headers = {'Referer' : url}
        request = urllib2.Request(login_url, params, headers)
        f = urllib2.urlopen(request)
        return f.geturl().split('=')[1]
    
    def __getattr__(self, name):
        if name == 'client':
            return self.__client
```

代码中的 

```python
client.get.statuses__public_timeline()
```

就是使用weibo的statuses/public\_timeline的API,get代表使用GET方法提交数据，用"\_\_"代替"/"。完整的API文档在[这里](http://open.weibo.com/wiki/API%E6%96%87%E6%A1%A3_V2)。

**Have fun!**
