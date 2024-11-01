#what can this version do
The crazy version2 which supports debugging the robots from different teams in the same time.

#how to use
1.最简单的方式是去群里的网盘或者u盘拷贝，在windows中直接用exe打开（不用配环境）<br/>
2.打开exe的时候windows会弹出一个类似防火墙的权限勾选 公用和专有网络都勾选 <br/>

#for people who bad luck
##1.exe没法使用就必须配环境用源码了 第一件事 确保你本机的ip在192.168.31网段下 如何判断方法比较多  讲两种<br/>
a.终端命令行 ifconfig（linux命令）or ipconfig（windows命令）<br/>
b.更精准一点的方法 因为a法的终端命令很有可能出现多个ip 比如翻墙或者连了网线的时候 所以用b法的python程序去看更合理一点<br/>
代码如下：
```python
import socket
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

local_ip=get_ip_address()
print("本机IP地址是:", get_ip_address()) 
```
##2.假如ip确实是在192.168.31网段下
1.windows端，确保给exe软件打开公用和专有网络的权限，再try一下<br/>
2.如果还是不行，在linux系统中跑源码吧 去github上clone一下 环境见environment.yml(创建一个虚拟环境即可)<br/>

##跑源码时注意 
1.python版本 库版本见environment.yml<br/>
2.proto版本 由于文件中用到了protobuf协议，需要将.proto文件编译成python模块 <br/>

###proto编译
下载proto编译器 我使用的是3.19.1版本 https://github.com/protocolbuffers/protobuf/releases/tag/v3.19.1<br/>
下载后编译
```bash
protoc --python_out=. zss_cmd.proto
protoc --python_out=. zss_cmd_type.proto
```

