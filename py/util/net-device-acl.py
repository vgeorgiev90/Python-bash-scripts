#!/usr/bin/python

import netmiko
import argparse
import sys

exceptions = (netmiko.ssh_exception.NetMikoTimeoutException, netmiko.ssh_exception.NetMikoAuthenticationException)

def parser():
    parser = argparse.ArgumentParser(description='Tool for managing Cisco devices and access-lists')
    parser.add_argument('--list','-l',metavar='LIST NAME',help='List all ACEs in the access-list provided\n --list all for all acl entries')
    parser.add_argument('--version','-v',action='version',version='cisco.py 1.0 alpha')
    parser.add_argument('--deny','-d',nargs=3,metavar=('RuleID','Protocol','HOST'),help='Provide ruleid,host and protocol for deny ACE to be placed')
    parser.add_argument('--remove','-r',action='store_true',help='This option can be used only with --deny to remove the ACE from the list')
    parser.add_argument('--acl','-a',type=str,metavar=('ACL-NAME'),help='This option is used to provide acl name for list or deny commands')
    return parser


class Automate():
    def __init__(self):
        device = {
            'device_type': 'cisco_ios',
            'ip': '172.16.1.1',
            'username': 'admin',
            'password': 'viktor',
            'secret': 'viktor123'
        }
        self.connect = netmiko.ConnectHandler(**device)

    def prompt(self):
        print self.connect.find_prompt()

    def enable(self):
        self.connect.enable()

    def config(self):
        self.connect.config_mode()

    def send(self,cmd):
        result = self.connect.find_prompt()
        result += self.connect.send_command(cmd)
        print result

    def send_set(self,cmd):
        output = self.connect.send_config_set(cmd)
        print output

    def exit(self):
        self.connect.disconnect()
        print "Disconecting from the host..."

def block_or_remove(acl,rule,prot,host,mode):
    if acl == 'INT-Filter' or acl == 'BG-Filter':
        router = Automate()
        router.enable()
        cmd = [ 'ip access-list extended %s' % acl ]
        if mode == 'deny':
            deny = "%s deny %s any host %s" % (rule,prot,host)
            cmd.append(deny)
            router.send_set(cmd)
        elif mode == 'remove':
            deny = "no %s deny %s any host %s" % (rule,prot,host)
            cmd.append(deny)
            router.send_set(cmd)
    else:
        print "Possible --acl options are: INT-Filter , BG-Filter.."

sc = parser()
args = sc.parse_args()
try:
    if args.list:
        router = Automate()
        router.enable()
        list = args.list
        if list == 'all':
            cmd = 'show ip access-list'
        else:
            cmd = 'show ip access-list %s' % list
        router.send(cmd)
    elif args.deny:
        if args.acl:
            acl = args.acl
            if args.remove:
                mode = 'remove'
                block_or_remove(acl,args.deny[0],args.deny[1],args.deny[2],mode)
            else:
                mode = 'deny'
                block_or_remove(acl,args.deny[0],args.deny[1],args.deny[2],mode)
        else:
            print "Provide also acl name with --acl"
    elif args.remove:
        print "This option can be used only with --deny..."
    elif args.acl:
        print "This option is intended to be used only with --deny"
    else:
        print "Provide arguments or -h,--help for more info..."
except exceptions as exception_type:
    print "Time out occured while trying to establish connection..."
    print exception_type
finally:
    try:
        router.exit()
    except NameError:
        pass
