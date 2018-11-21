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

exec_url = "https://%s:5000/exec" % config['host']
config_url = "https://%s:5000/check" % config['host']
token = config['token']

headers = {
    "token": token,
    }

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd',nargs='+',help='Subcommand')
    parser.add_argument('--data','-d',nargs='+',help='post body')
    return parser

parser = Parser()
args = parser.parse_args()

if args.cmd[0] == 'pods':
    response = requests.get(config_url + '/pods', headers=headers, verify=False)
    print response.text

elif args.cmd[0] == 'configs':
    response = requests.get(config_url + '/configs', headers=headers, verify=False)
    print response.text

elif args.cmd[0] == 'template' and args.data:
    website = args.cmd[1]
    domain = args.data[0]
    response = requests.post(config_url + '/' + website , headers=headers, data={ "domain": domain }, verify=False)
    print response.text

elif args.cmd[0] == 'new-wl':
    website = args.cmd[1]
    response = requests.get(exec_url + '/' + website, headers=headers, verify=False)
    print response.text

elif args.cmd[0] == 'deploy' and args.data:
    pod_name = args.cmd[1]
    data = {
           "domain": args.data[0],
           "website": args.data[1]
        }
    response = requests.post(exec_url + '/' + pod_name, headers=headers, data=data, verify=False)
    print response.text

else:
       print """
    Possible subcommands:
    pods     -- Check running pods
    configs  -- Check config files for deployment
    template -- Create new template for deployment
    new-wl   -- Deploy new Rc from conf file
    deploy   -- Deplot or Redeploy the website


    Usage:
    get pods
    get configs
    get template example -d example.com
    get new-wl example
    get deploy pod-name -d example.com example
    """
