#!/usr/bin/python

import json
import argparse
from os import system
import logging
from datetime import datetime


help_message = """
#All Supported options
#Service

{
  "type": "service",
  "mode": "replicated/global",
  "image": "image name",
  "replicas": "replica number",
  "service_network": "Existing docker netowrk",
  "service_name": "Name for the service",
  "mounts": {"source": "/local/volume", "target": "/container/directory"},
  "ports": "80:80",
  "entry": "command to run the container",
  "dns": "8.8.8.8",
  "env_file": "/path/to/file",
}

#Network
{
  "type": "network",
  "network_name": "Name for the network",
  "driver": "overlay (default is bridge)",
  "subnet": "Subnet CIDR block",
}

#Delimiter between services definition is two new lines
#Required for service are: type, image, entry if image does not have ENTRYPOINT specified
"""

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build','-b',nargs=1,metavar='FILE',help='Build file containing json instructions')
    parser.add_argument('--options','-o',action='store_true',help='Display all available options')
    return parser

class Data():

    docker_options = {"dns": "--dns","env_file": "--env-file","driver": "--driver","subnet": "--subnet","replicas": "--replicas","mode": "--mode", "ports": "-p", "network": "--network", "name": "--name"}

    def __init__(self,data):
        self.config_data = json.loads(data)
        logging.basicConfig(filename='deploy.log',level=logging.DEBUG)

    def build_file(self):
        docker_command = []
        for opt in self.docker_options:
            for cfg in self.config_data:
                if opt == cfg:
                    docker_command.append(str(self.docker_options[opt]) + " " + str(self.config_data[cfg]))
        if self.config_data['type'] == 'service':
            docker_command.insert(0,'docker service create -d')
            if 'mounts' in self.config_data:
                docker_command.append('--mount target=%s,source=%s' % (self.config_data['mounts']['target'], self.config_data['mounts']['source']))
            else:
                pass
            docker_command.append(self.config_data['image'])
            if 'entry' in self.config_data:
                docker_command.append(self.config_data['entry'])
            else:
                pass
        elif self.config_data['type'] == 'network':
            docker_command.insert(0,'docker network create')
            remove = "--name %s" % self.config_data['name']
            docker_command.remove(remove)
            docker_command.append(self.config_data['name'])
        else:
            raise ValueError('There is no type defined or it is incorrect')
            logging.debug('%s -- Not exact type specified or there is none' % datetime.now())

        cmd = ' '.join(docker_command)
        system(cmd)

def deploy(file):
    with open(file,'r') as f:
        data = f.read()

    for deploy in data.split("\n\n"):
        try:
            conf = Data(deploy)
            conf.build_file()
            logging.debug('%s -- All services deployed successfully' % datetime.now())
        except ValueError:
            pass




############## Script  #########

parser = Parser()
args = parser.parse_args()

if args.build:
    file = args.build[0]
    deploy(file)
elif args.options:
    print help_message
