    ==============================
    |--\ \  / |\  /|  /----  |----
    |--/  \/  | \/ |  |---\  |----
    |     ||  |    |  ____|  |
    ==============================
                   made by s0m30ne
    ------------------------------

    Usage: python msf_python.py [options] 

    Options:  
        -h, --help            show this help message and exit  
        -n, --normal          normal mode  
        -s SEARCH, --search=SEARCH  
                              chose a search engine, for example: censys, zoomeye or shodan  
        -f FILE_NAME, --file=FILE_NAME  
                              the poc file you want to run  
        -t THREAD_NUM, --threads=THREAD_NUM  
                              set the thread num

##准备工作：
（1）安装Python的msgpack类库，MSF官方文档中的数据序列化标准就是参照msgpack。

    root@kali:~# apt-get install python-setuptools
    root@kali:~# easy_install msgpack-python
 
（2）创建createdb_sql.txt:

    create database msf;
    create user msf with password 'msf123';
    grant all privileges on database msf to msf;
 
（3）在PostgreSQL 执行上述文件：

    root@kali:~# /etc/init.d/postgresql start
    root@kali:~# sudo -u postgres /usr/bin/psql < createdb_sql.txt
 
（4）创建setup.rc文件

    db_connect msf:msf123@127.0.0.1/msf
    load msgrpc User=msf Pass='abc123'
 
（5）启动MSF并执行载入文件

    root@kali:~# msfconsole -r setup.rc
    *SNIP*
    [*] Processing setup.rc for ERB directives.
    resource (setup.rc)> db_connect msf:msf123@127.0.0.1/msf
    [*] Rebuilding the module cache in the background...
    resource (setup.rc)> load msgrpc User=msf Pass='abc123'
    [*] MSGRPC Service: 127.0.0.1:55552
    [*] MSGRPC Username: msf
    [*] MSGRPC Password: abc123
    [*] Successfully loaded plugin: msgrpc
 
（6）安装msfrpc

    root@kali:~# git clone git://github.com/SpiderLabs/msfrpc.git msfrpc
    root@kali:~# cd msfrpc/python-msfrpc
    root@kali:~# python setup.py install

（7）在config.txt中配置你的token信息

后面每次使用时都需要先使用`msfconsole -r setup.rc`启动msf

##使用方法
使用`python msf_python.py -n`或者直接使用`python msf_python.py`进入普通模式，使用`python msf_python.py -s [censys,shodan,zoomeye]`选择相应的搜索引擎，默认选择的是`censys`。

![](http://7xp22c.com1.z0.glb.clouddn.com/welcome.PNG)

启动脚本后的使用方式和msf基本相同，支持msf的所有命令，不同之处在于你没必要设置`RHOST`或者`RHOSTS`，后面的扫描过程中程序会自己进行设置。额外需要你设置的是`QUERY`和`PAGE`选项，`QUERY`是你选择的搜索引擎下的搜索条件，`PAGE`则是你想要搜索的页数（默认为10）。

![](http://7xp22c.com1.z0.glb.clouddn.com/options.PNG)

通过`python msf_python.py -f FILENAME`命令用户可以使用自定义的漏洞poc文件，但是编写poc文件时请提供IP参数接口，比如说你可以按照如下格式编写poc：

    import sys
    def poc(ip):
        manage with the ip
        ...
    if __name__ == "__main__":
        poc(sys.argv[1])

通过`-f`参数指定poc文件后，设置好`QUERY`和`PAGE`参数就可以通过exploit命令执行了。

你可以通过`-t`参数指定线程数。