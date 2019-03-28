#!/usr/bin/python

import requests
import json
import sys
import argparse

mail = "cf-mail"
key = "cf-key"
url = "https://api.cloudflare.com/client/v4/zones/"

headers = {
   "X-Auth-Email": mail,
   "X-Auth-Key": key ,
   "Content-type": "application/json"
}


parser = argparse.ArgumentParser()
parser.add_argument('--file','-f', nargs=1, help='Domains file')
args = parser.parse_args()


file = args.file[0]

with open(file, 'r') as f:
    to_be_deleted = f.read()


response = requests.get(url + "&per_page=500", headers=headers)

zones = json.loads(response.text)


for domain in to_be_deleted.split("\n"):
    for zone in zones['result']:
        if domain == zone['name']:
            id = zone['id']
            records_response = requests.get(url + id + '/dns_records&per_page=500', headers=headers)
            records = json.loads(records_response.text)
            for rec in records['result']:
                delete = requests.delete(url + id + '/dns_records/' + rec['id'], headers=headers)
                print delete.text

choice = raw_input('Delete zones: yes/no\n')

if choice == "yes":
    for domain in to_be_deleted.split("\n"):
        for zone in zones['result']:
            if domain == zone['name']:
                id = zone['id']
                delete_zone = requests.delete(url + id, headers=headers)
                print delete_zone.text
else:
    print "No actual zones will be deleted"
