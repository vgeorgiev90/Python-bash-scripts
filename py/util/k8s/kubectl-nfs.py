#!/usr/bin/python

import requests
import paramiko
from json import loads
from string import ascii_uppercase, digits
from random import choice
from argparse import ArgumentParser
from jinja2 import Template

pv_template = """
{
  "kind": "PersistentVolume",
  "apiVersion": "v1",
  "metadata": {
    "name": "{{ name }}",
    "labels" : {
      "name": "{{ name }}"
    }
  },
  "spec": {
    "capacity": {
      "storage": "{{ size }}"
    },
    "nfs": {
      "path": "/{{ path }}",
      "server": "{{ ip }}",
      "readOnly": false
    },
    "accessModes": [
      "ReadWriteMany"
    ],
    "persistentVolumeReclaimPolicy": "Delete",
    "volumeMode": "Filesystem"
  }
}
"""

pvc_template = """
{
  "kind": "PersistentVolumeClaim",
  "apiVersion": "v1",
  "metadata": {
     "name": "{{ name }}",
     "namespace": "{{ namespace }}"
  },
  "spec": {
    "accessModes": [ "ReadWriteMany" ],
    "resources": {
      "requests": { "storage": "{{ size }}" }
    },
    "selector": {
      "matchLabels": { "name": "{{ name }}" }
    },
    "storageClassName": ""
  }
}
"""

def Parser():
    parser = ArgumentParser()
    parser.add_argument('cmd', nargs=1, help="subcmd to be executed,  check.py help for more information on subcmd")
    parser.add_argument('--data', '-d',nargs='+',help='Name and size for the pv and pvc in format --name namespace/name (1...n)Gi')
    return parser


class Nfs():
    headers = { "Authorization": "Bearer YOUR-TOKEN-HERE" }
    api = "https://10.0.11.155:6443/api/v1/persistentvolumes"
    pvc_api = "https://10.0.11.155:6443/api/v1/namespaces/"

    def __init__(self):
        try:
            with open('.nfs.json', 'r') as f:
                data = f.read()
            self.config = loads(data)
        except:
            print "No .nfs.json config file found.."

    def provision(self, pvc, size):
        ## Provision nfs share and export
        host = self.config['server']
        ca = self.config['api-ca']
        port = '22'
        user = 'root'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username=user)
        exported_dir = ''.join(choice(ascii_uppercase + digits) for _ in range(16))
        cmd = "mkdir /%s; chown nobody: /%s ;echo '/%s    10.0.11.0/24(rw,sync,no_subtree_check,root_squash)' >> /etc/exports ; exportfs -arv" % (exported_dir, exported_dir, exported_dir)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        ssh.close()

        ## Create persistent volume with the share
        template = Template(pv_template)
        template2 = Template(pvc_template)

        namespace = pvc.split("/")[0]
        name = pvc.split("/")[1]

        ready_data = template.render(name=name, size=size, path=exported_dir, ip=host)
        pvc_ready_data = template2.render(name=name, size=size, namespace=namespace)

        api_response = requests.post(self.api, headers=self.headers, data=ready_data, verify=ca)
        pvc_api_response = requests.post(self.pvc_api + namespace + '/persistentvolumeclaims', headers=self.headers, data=pvc_ready_data, verify=ca)
        print "Created PersistentVolume: %s" % name
        print "Created PersistentVolumeClaim: %s" %  name


    def delete(self, pvc):
        ca = self.config['api-ca']
        host = self.config['server']
        port = '22'
        user = 'root'
        ## Delete the objects from k8s
        namespace = pvc.split("/")[0]
        pvc_name = pvc.split("/")[1]
        delete_response = requests.delete(self.pvc_api + namespace + '/persistentvolumeclaims/' + pvc_name, headers=self.headers, verify=ca)
        ## Get nfs hostpath from pv
        pv_response = requests.get(self.api + '/' + pvc_name, headers=self.headers, verify=ca)
        d = loads(pv_response.text)
        exported_dir = d['spec']['nfs']['path']
        del_dir = d['spec']['nfs']['path'].split("/")[1]

        ## Delete the pv
        delete = requests.delete(self.api + '/' + pvc_name, headers=self.headers, verify=ca)
        ## Clean the nfs server exports
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username=user)
        cmd = "rm -rf %s; sed -i '/%s/d' /etc/exports; exportfs -arv" % (exported_dir, del_dir)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        ssh.close()
        print "Deleted PersistentVolume: %s" % pvc_name
        print "Deleted PersistentVolumeClaim: %s" % pvc_name


parser = Parser()
args = parser.parse_args()

nfs = Nfs()

if args.cmd[0] == 'provision' and args.data:
    pv = args.data[0]
    size = args.data[1]
    nfs.provision(pv, size)

elif args.cmd[0] == 'delete' and args.data:
    pv = args.data[0]
    nfs.delete(pv)

else:
    print "Usage:  "
    print "This script is extension to kubectl place it in the same dir (/usr/local/bin) , it needs .nfs.json file created with content"
    print '{ "server": "nfs-server-ip", "api-ca": "/path/to/k8s/ca" }'
    print "Nfs server must be configured and ssh auth without password"
    print "Auth Bearer token must be configured in class variable headers"
    print "==========================================================================================================================================="
    print "kubectl nfs provision -d default/my-pv-vol 2Gi  --   This will create PV and PVC with name my-pv-vol in namespace default and size 2GB"
    print "kubectl nfs delete -d default/my-pv-vol         --   This will delete PV and PVC with name my-pv-vol and also corresponding exported shares"
