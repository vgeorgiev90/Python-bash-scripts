#!/usr/bin/python

## Example .config.json
# { "host": "10.0.11.100", "token": "token-from-server-conf" }


import requests
import argparse
import json

try:
    with open('.config.json', 'r') as f:
        conf = f.read()
    config = json.loads(conf)
except:
    print "No config.json found.."
    raise SystemExit

exec_url = "http://%s:5000/exec" % config['host']
config_url = "http://%s:5000/configs" % config['host']
token = config['token']

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd',nargs='+',help='Subcommand')
    parser.add_argument('--data','-d',nargs='+',help='post body')
    parser.add_argument('--headers','-s',nargs=1,help='headers')
    parser.add_argument('--file','-f',nargs=1,help='File with options')
    return parser

parser = Parser()
args = parser.parse_args()

headers = { 
    "token": token,
    }

if args.cmd[0] == 'configs':
    response = requests.get(config_url)
    for file in response.text.split("\\n"):
        print "--------"
        print file

elif args.cmd[0] == 'conf-view':
    config_file = args.cmd[1]
    response = requests.get(config_url + '/' + config_file)
    for line in response.text.split("\\n"):
        print line

elif args.cmd[0] == 'conf-delete':
    config_file = args.cmd[1]
    response = requests.delete(config_url + '/' + config_file, headers=headers)
    print response.text

elif args.cmd[0] == 'conf-change':
    config_file = args.cmd[1]
    if args.data:
        option = args.data[0]
        replace = args.data[1]
        response = requests.put(config_url + '/' + config_file, headers=headers , data = { 
            'option': option, 
            'replace': replace
            })
        print response.text
    else:
        print "Please provide: --data option_pair replace_pair"
elif args.cmd[0] == 'exec':
    config_file = args.cmd[1]
    if args.data and args.headers:
        provision = args.headers[0]
        data = args.data[0]
        headers['provision'] = provision
        response = requests.post(exec_url + '/' + config_file, headers=headers, data = { 
            "state": data 
            })
        print response.text
    else:
        print "get help  -  for help display"

elif args.cmd[0] == 'conf-create':
    config_file = args.cmd[1]
    if args.data:
        data = args.data[0]
        response = requests.post(config_url + '/' + config_file, headers=headers, data = { 
            "options": data 
            })
        print response.text
    elif args.file:
        with open(args.file[0], 'r') as f:
            data = f.read()
        response = requests.post(config_url + '/' + config_file, headers=headers, data = { 
            "options": data.decode("utf8") 
            })
        print response.text
    else:
        print "get help - for help display"

elif args.cmd[0] == 'help':
    print """
    Possible subcommands:
    conf-view   --  view conf file
    conf-change -- make changes in the file
    conf-create -- create new conf file
    exec        -- exec ansible play

    Usage:
    get conf-view file
    get conf-create file -f /path/to/json/data
    get conf-create file -d json-data
    get conf-change file -d option_pair replace_pair
    get exec file -s vginit/volume/mount -d present/absent
    """
else:
    print "Something got broken and i am too lazy to tell you what... maybe your spelling.. maybe missed argument..."
