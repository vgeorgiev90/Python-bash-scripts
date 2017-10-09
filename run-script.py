#!/usr/bin/env python


import paramiko
#import sys
import pexpect
import time

########## List of available servers in dictionary ###########


d5 = {'server1': {'server': 'stefan', 'ip': '192.168.1.41', 'pass': 'viktor'}, 'server2': {'server': 'rusko', 'ip': '192.168.1.40', 'pass': 'viktor'}, 'server3': {'server': 'royal', 'ip': '192.168.1.17', 'pass': 'royalpass'}}


########## Iterate in the dictionary and set variables for server connection ######


A = raw_input("Please choose server: ")

parola = 0

for i in d5:
    var = d5[i]['server']
    if var == A:
        parola = d5[i]['pass']
        ip = d5[i]['ip']
        print(parola)
        print(ip)
        break
    elif var == A:
        parola = d5[i]['pass']
        ip = d5[i]['ip']
        print(parola)
        print(ip)
        break
    elif var == A:
        parola = d5[i]['pass']
        ip = d5[i]['ip']
        print(parola)
        print(ip)
        break


########### Rsync the script to be executed ###########


rs = pexpect.spawn('rsync -av test-script.sh root@' + ip + ':/root/')
var = rs.expect(['yes/no', 'password: '])
if var == 0:
    rs.sendline('yes')
    time.sleep(1)
    rs.sendline(parola)
elif var == 1:
    rs.sendline(parola)
rs.interact()


########### Execute the script via ssh connection ##########


username = "root"
port = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ip, port, username=username, password=parola)

stdin, stdout, stderr = ssh.exec_command("./test-script.sh")
print stdout.read()
print stderr.read()

ssh.close()
