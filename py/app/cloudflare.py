#!/bin/python
## dependencies: python-cloudflare


import CloudFlare
import argparse
import json
import os


################ CloudFlare functions and parser ####################

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dns','-d',nargs=1,metavar='ID',help='Check the zone for the particular domain')
    parser.add_argument('--purge','-p',nargs=1,metavar='ID',help='Purge the cache for a zone')
    return parser

class cloudflare():
    def __init__(self):
        self.mail = ""                                                       #### Provide your cloudflare mail address
        self.key = ""                                                        #### Provide your Cloudflare API key
        self.zones_url = "https://api.cloudflare.com/client/v4/zones/"
        self.cf = CloudFlare.CloudFlare(self.mail,self.key)

    def list(self):
        zones = self.cf.zones.get(params={'per_page': 150})
        for zone in zones:
            zone_name = zone['name']
            zone_id = zone['id']
            print zone_name + " ---- " + zone_id

    def dns(self,id):
        records = self.cf.zones.dns_records.get(id)
        for elem in records:
            record = json.dumps(elem, indent=4, sort_keys=True)
            dict = json.loads(record)
            print ""
            print "%s --- %s --- %s" % (dict['name'], dict['type'], dict['content'])

    def purge_cache(self,id):
        purge_url = self.zones_url + id + "/purge_cache"
        h1 = "\"X-Auth-Email: %s\"" % self.mail
        h2 = "\"X-Auth-Key: %s\"" % self.key
        h3 = "\"Content-Type: application/json\""
        cmd = "curl -X POST %s -H %s -H %s -H %s --data '{\"purge_everything\": true}'" % (purge_url,h1,h2,h3)
        response =  os.system(cmd)


############### Script #####################


parser = Parser()
args = parser.parse_args()

cloud = cloudflare()

if args.dns:
    id = args.dns[0]
    cloud.dns(id)

elif args.purge:
    id = args.purge[0]
    cloud.purge_cache(id)

else:
    cloud.list()
