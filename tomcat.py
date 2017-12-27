#!/usr/bin/python
##tomcat 8 and java 8 install and managment for multi user systems
##Apache proxy virtual hosts creation for tomcat

import subprocess
import random
import string
import argparse

######## Functions  ############

def base_install():
    subprocess.call(["yum","install","java-1.8.0-openjdk.x86_64", "-y"])
    subprocess.call(["yum","install","httpd","-y"])
    subprocess.call(["wget","http://apache.cbox.biz/tomcat/tomcat-8/v8.5.24/bin/apache-tomcat-8.5.24.tar.gz"],cwd="/opt/")
    subprocess.call(["tar","-xzf","apache-tomcat-8.5.24.tar.gz"],cwd="/opt/")
    subprocess.call(["mv","/opt/apache-tomcat-8.5.24","/opt/tomcat-base"])
    subprocess.call(["rm","-rf","/opt/apache-tomcat-8.5.24.tar.gz"])
    subprocess.call(["systemctl","enable","httpd"])


def pw_gen(size = 12, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def multi_user_install(user):

##### Instance Variables #######
    port = random.randint(8000,9000)
    parola = pw_gen(20)
    sslport = port + 10
    shport = port + 20
    ajport = port + 30
    null = open('/dev/null','w')
    home = "/opt/tomcat-" + user
    own = user + ':'
    shutdown_pass = '<user username="%s" password="%s" roles="admin-gui,manager-gui"/>' % (user,parola)
#### Make sure that there are no port conflicts ##
    rep = 'port="8080"'
    ssl = 'redirectPort="8443"'
    shp = 'port="8005"'
    ajp = 'port="8009"'
    tls = 'port="8443"'
    shut = 'shutdown="SHUTDOWN">'
    rep2 = 'port="%s"' % port
    ssl2 = 'redirectPort="%s"' % sslport
    shp2 = 'port="%s"' % shport
    ajp2 = 'port="%s"' % ajport
    tls2 = 'port="%s"' % sslport
    shut2 = 'shutdown="%s">' % parola
########## Deploy instance, create user, change owner

    subprocess.call(["cp","-rf","/opt/tomcat-base",home])
    subprocess.call(["useradd","-s","/sbin/nologin","-d",home,user],stdout=null,stderr=null)
    subprocess.call(["chown","-R",own,home])

    dirs = subprocess.check_output(["find",home,"-type","d"])
    files = subprocess.check_output(["find",home,"-type","f"])
    scripts = subprocess.check_output(["find",home + "/bin/","-name","*.sh"])

###########  Change permissions for the custom tomcat user instance
    for dir in dirs.split("\n"):
        subprocess.call(["chmod","750",dir],stdout=null,stderr=null)
    for file in files.split("\n"):
        subprocess.call(["chmod","640",file],stdout=null,stderr=null)
    for script in scripts.split("\n"):
        subprocess.call(["chmod","750",script],stdout=null,stderr=null)

#######  Modify the main config file server.xml and substitute conflicting ports

    with open(home + "/conf/server.xml", 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(rep,rep2)
    filedata = filedata.replace(ssl,ssl2)
    filedata = filedata.replace(shp,shp2)
    filedata = filedata.replace(ajp,ajp2)
    filedata = filedata.replace(tls,tls2)
    filedata = filedata.replace(shut,shut2)
    with open(home + "/conf/server.xml", 'w') as file:
        file.write(filedata)
    file.close()
    with open(home + '/conf/tomcat-users.xml','r') as file:
        cont = file.readlines()
    cont.insert(43,shutdown_pass)
    with open(home + '/conf/tomcat-users.xml','w') as file:
        for line in cont:
            file.write(line)

    data = "Instance created with home directory: %s \n \n User: %s\n Port: %s\n SSlPort: %s\n SHUTPort: %s\n AJPport: %s \n SHUTpass: %s\n AdminGUI user: %s \n AdminGUI pass: %s \n \nJava memory options by default: \n Xms=128m\n Xmx=512m\n PermSize=32m\n MaxPermSize=64m\n -server\n -XX:+UseParallelGC \n -Dfile.encoding=utf-8 \n If you want to increase or change modify the service file \n /usr/lib/systemd/system/tomcat-%s.service\n" % (home,user,port,sslport,shport,ajport,parola,user,parola,user)
    with open(home + "/tomi.info", 'w') as temp:
        temp.write(data)
    temp.close()
    print "Instance is created with home directory: %s" % home
    print "For info on ports check %s/tomi.info" % home
    return user,home


def make_user_service(user,home):
    content = """
    [Unit]
    Description=Apache Tomcat User Service
    After=syslog.target network.target
    [Service]
    Type=forking
    Environment=JAVA_HOME=/usr/lib/jvm/jre
    Environment=CATALINA_PID=%s/tomcat-%s.pid
    Environment=CATALINA_HOME=%s
    Environment=CATALINA_BASE=%s
    Environment='CATALINA_OPTS=-Xms128M -Xmx512M -XX:PermSize=32m -XX:MaxPermSize=64m -server -XX:+UseParallelGC -Dfile.encoding=utf-8'
    Environment='JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom'
    ExecStart=%s/bin/startup.sh
    ExecStop=/bin/kill -15 $MAINPID
    User=%s
    Group=%s
    [Install]
    WantedBy=multi-user.target
    """ % (home,user,home,home,home,user,user)

    service = '/usr/lib/systemd/system/tomcat-' + user + ".service"
    with open(service,'w') as file:
        file.write(content)
    file.close()
    subprocess.call(["systemctl","enable","tomcat-" + user])
    subprocess.call(["systemctl","start","tomcat-" + user])
    print "Systemd service file created for tomcat-%s.service" % user


def httpd_proxy(domain,install_port):
    proxy_file = '/etc/httpd/conf.d/' + domain + '.conf'
    proxy_set = """
    <VirtualHost *:80>
      ServerName %s

      ProxyRequests On
      ProxyPreserveHost      On
      ProxyPass / http://127.0.0.1:%s/
      ProxyPassReverse / http://127.0.0.1:%s/
    </VirtualHost>""" % (domain,install_port,install_port)

    with open(proxy_file,'w') as prfile:
        prfile.write(proxy_set)
    prfile.close()
    subprocess.call(["systemctl","restart","httpd"])
    print "Proxy Virtual Host is created for the domain %s \n if you want to point it to spesific context on this instance \n modify %s \n as follows: \n ProxyPass / http://127.0.0.1:your-port/your-context/" % (domain,proxy_file)


######### Argument Parser Declare ##############

parser = argparse.ArgumentParser(description='Apache tomcat 8 setup and management script')
parser.add_argument('--base_install','-b',action='store_true',help='Base install for java8 and tomcat8')
parser.add_argument('--user_install','-u',type=str,help='User instance install, provide username')
parser.add_argument('--vhost','-V',type=str,help='Install apache vhost, provide domain name and port for the user instance')
parser.add_argument('--port','-p',type=int,help='Port for the vhost install, this option can be used only with -V')
parser.add_argument('--version','-v',action='version',version='tomcat.py v2.0 for any bugs contact the developer of the script')
args = parser.parse_args()

######### Script Start ###############

if args.base_install:
    base_install()
elif args.user_install:
    usr = args.user_install
    acc,hom = multi_user_install(usr)
    make_user_service(acc,hom)
elif args.vhost:
    if args.port:
        dom = args.vhost
        por = args.port
        httpd_proxy(dom,por)
    else:
        print "Please provide port for the vhost with option --port or -p"
elif args.port:
    print "This option can be used only when you declare virtual host for apache..\ntomcat.py --help for more info."
else:
    print "Please provide valid options or try --help for more information."
