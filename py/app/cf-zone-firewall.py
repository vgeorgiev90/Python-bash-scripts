#!/usr/bin/python

import requests
import json
import argparse
import os

mail = "your-cf-mail"                                                      #### Provide your cloudflare mail address
key = "your-cf-key"                                                        #### Provide your Cloudflare API key
url1 = "https://api.cloudflare.com/client/v4/zones/9eeff1b8950ac2697e66560e19a199b5/firewall/lockdowns?&per_page=20"
url2 = "https://api.cloudflare.com/client/v4/zones/9eeff1b8950ac2697e66560e19a199b5/firewall/lockdowns"


h1 = "\"X-Auth-Email: %s\"" % mail
h2 = "\"X-Auth-Key: %s\"" % key
h3 = "\"Content-type: application/json\""


headers = {
   "X-Auth-Email": mail,
   "X-Auth-Key": key ,
   "Content-type": "application/json"
}


def Parser():
    parser = argparse.ArgumentParser(description='Cloudflare firewall script')
    parser.add_argument('cmd',help='Sub-cmd for the script')
    parser.add_argument('--data','-d',nargs='+',help='User instance install, provide username')
    return parser



class firewall():

    def __init__(self):
        self.response = requests.get(url1, headers=headers)
        self.dict = json.loads(self.response.text)

    def get_all(self):
        for list in self.dict['result']:
            print ""
            print "Name: %s " % list['description']
            print "ID: %s " % list['id']
            print "Total: %s" % len(list['configurations'])
            print "=================="
            print ""
            for ip in list['configurations']:
                print ip['value']

    def create_rule(self, name):

        cmd = "curl -XPOST %s -H %s -H %s -H %s --data '{\"paused\": false, \"configurations\": [{\"target\":\"ip\",\"value\":\"192.168.1.1\"}] , \"urls\": [\"admim.finte.co/*\",\"admin.finte.co/*\"], \"description\": \"%s\" }'" % (url2, h1, h2, h3, name)
        response = os.system(cmd)
        print response

    def add_ip(self, rule_id, ip):
        self.response3 = requests.get(url2 + '/' + rule_id, headers=headers)
        config = json.loads(self.response3.text)
        for dict in config['result']['configurations']:
            if dict['value'] == ip:
                print "%s is already in the list %s" % (ip, config['result']['description'])
                raise SystemExit

        data = config['result']
        del data['id']
        data['configurations'].append({ "target": "ip", "value": ip})


        rep = str(data['configurations'])
        rep2 =  rep.replace("u'", "'")
        confs = rep2.replace("'", "\"")

        lock_url = url2 + '/' + rule_id
        cmd = "curl -XPUT %s -H %s -H %s -H %s --data '{\"paused\": false, \"configurations\": %s , \"urls\": [\"admim.finte.co/*\",\"admin.finte.co/*\"], \"description\": \"%s\" }'" % (lock_url, h1, h2, h3, confs, data['description'])
        response = os.system(cmd)
        print response



parser = Parser()
args = parser.parse_args()

fw = firewall()

if args.cmd == 'list':
    fw.get_all()

elif args.cmd == 'create-rule' and args.data:
    name = args.data[0]
    fw.create_rule(name)

elif args.cmd == 'add-ip' and args.data:
    rule_id = args.data[0]
    ip = args.data[1]
    fw.add_ip(rule_id, ip)

else:
    print """
        Sub-commands:

        list        ---  List all rules and associated IPs
        create-rule ---  Create new rule in firewall zone
        add-ip      ---  Add Ip address to existing rule

        Usage:

        cf-firewall.py list
        cf-firewall.py create-rule -d NAME
        cf-firewall.py add-ip -d RULE-ID IP-ADDRESS
    """
