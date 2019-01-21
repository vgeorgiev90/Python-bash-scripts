#!/usr/bin/python

import argparse
from jinja2 import Template
import subprocess


### Parser declaration
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='+', help='Subcmd to execute')
    parser.add_argument('--options', '-o', nargs='+', help='Options to be passed')
    parser.add_argument('--ca', '-c',nargs='+' ,help='CA to be used')
    parser.add_argument('--hostnames', '-n', nargs=1, help='Hostnames for the certificate')
    return parser


### Get cfssl binaries
def cfssl():
    subprocess.call(['wget', 'https://pkg.cfssl.org/R1.2/cfssl_linux-amd64'])
    subprocess.call(['wget', 'https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64'])
    subprocess.call(['mv', 'cfssl_linux-amd64', '/usr/local/bin/cfssl'])
    subprocess.call(['mv', 'cfssljson_linux-amd64', '/usr/local/bin/cfssljson'])
    subprocess.call(['chmod', '+x', '/usr/local/bin/cfssl'])
    subprocess.call(['chmod', '+x', '/usr/local/bin/cfssljson'])


#### Templates for cfssl
ca_config_template = """
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "kubernetes": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
"""

cert_template = """
{
  "CN": "{{ common_name }}",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "BG",
      "L": "Sofia",
      "O": "{{ alternate_names }}",
      "OU": "CA",
      "ST": "Sofia"
    }
  ]
}
"""

def gen_ca(name):
    with open('config.json', 'w') as f:
        f.write(ca_config_template)

    temp = Template(cert_template)
    ready = temp.render(common_name=name , alternate_names=name )
    with open('ca.json', 'w') as c:
        c.write(ready)
    gen = subprocess.Popen(['cfssl','gencert','-initca','ca.json',], stdout=subprocess.PIPE)       
    subprocess.call(['cfssljson', '-bare', 'ca'], stdin=gen.stdout)
    subprocess.call(['rm','-rf','./ca.json'])
    subprocess.call(['rm','-rf','./ca.csr'])

def gen_cert(name, alt_names,hostnames , ca, ca_key):
    
    ### Generate cfssl config file
    with open('config.json', 'w') as f:
        f.write(ca_config_template)

    temp = Template(cert_template)
    ready = temp.render(common_name=name, alternate_names=alt_names)
    with open(name, 'w') as c:
        c.write(ready)

    c_auth = "-ca=%s" % ca
    c_key = "-ca-key=%s" % ca_key
    hostname = "-hostname=%s" % hostnames
    gen = subprocess.Popen(['cfssl','gencert',c_auth,c_key,'-config=config.json','-profile=kubernetes',hostname,name], stdout=subprocess.PIPE)    
    subprocess.call(['cfssljson', '-bare', name], stdin=gen.stdout)
    ### Some cleanup of files
    subprocess.call(['rm', '-rf', name + '.csr'])
    subprocess.call(['rm', '-rf', name ])



parser = Parser()
args = parser.parse_args()

if args.cmd[0] == 'cfssl':
    cfssl()

elif args.cmd[0] == 'ca' and args.options:
    name = args.options[0]
    gen_ca(name)
    
elif args.cmd[0] == 'cert' and args.options and args.ca:
    name = args.options[0]
    alt_names = args.options[1]

    if args.hostnames:
        hostnames = args.hostnames[0]
    else:
        hostnames = ""

    if args.ca[0] == 'local':
        gen_cert(name, alt_names, hostnames, './ca.pem', './ca-key.pem')
    elif args.ca[0] == 'remote':
        ca = args.ca[1]
        ca_key = args.ca[2]
        gen_cert(name, alt_names, hostnames, ca, ca_key)
    
else:
    print """
    Usage:
    ssl.py cfssl                                                                             --- Download and install cfssl binary (required)
    ssl.py ca -o NAME                                                                        --- Generate CA for certificate signing
    ssl.py cert -o NAME ALT_NAMES -c local/remote  (if remote: /path/to/ca /path/to/ca-key)  --- Generate certificate

    
    Example for certificate generation with existing CA and 2 IPs for hostnames
    ssl.py cert -o viktor system:node:viktor -c remote /var/lib/ca/ca.pem /var/lib/ca/ca-key.pem -n 127.0.0.1,10.0.11.120

    Example for certificate with newly generated CA and without hostnames (generate )
    ssl.py cert -o viktor alt-name-viktor -c local

    Notes:
    cfssl is mandatory , along with python jinja2 module run ssl.py cfssl before first time usage.
    """
