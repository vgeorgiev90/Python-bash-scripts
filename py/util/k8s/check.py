#!/usr/bin/python

import requests
import json
import argparse
import paramiko


def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='+', help="subcmd to be executed,  check.py help for more information on subcmd")
    return parser



class check():
    api_address='https://10.0.11.155:6443'
    headers =  { "Authorization" : "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJ2aWt0b3ItdG9rZW4tZzJnNDYiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoidmlrdG9yIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiOTlkZGYxZTItZmEyNi0xMWU4LTkyMWUtYTJjNjBhNTMzNWJlIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOnZpa3RvciJ9.FK9YEFFv1NLmOMaqn8ksaO9rNCX6t6azA6DldHB79WuAYGNl_5OsaM6mqjFYeTvUF229AImqGzltBRjTIm05AOIZKnK-yKn5SpYLTV1TfLMW4ZGrZzy0QQWHPmn3_XFOWCfHeTaDu8iJQsknAm_1TzwERblX_FpapzuZ3CtNo8AEQ0EemoD9_gQvzFC2ghuhazs89xYkZt38yr2djTWLoFjfeL4kK_k1tKo1Lv-5p2Lc4ieCbiI5K-1VEC6Dtrvv2vR-43AgX71Ely_OQE5D5bc1NyufgUgwfWwAfKgI4_fMw3EkCUs4jurxWQOe9zVW4NWbUU3TH2hXZZhS-vh6Sg" }
    ca_cert="ca-cert"

    def __init__(self):
        self.namespaces = []
        ns = requests.get(self.api_address + '/api/v1/namespaces', headers=self.headers, verify=self.ca_cert)
        ns = json.loads(ns.text)
        for n in ns['items']:
            self.namespaces.append(n['metadata']['name'])

    def list(self):
        for namespace in self.namespaces:
            print "--------------------------"
            print "Namespace: %s" % namespace
            print "--------------------------"
            pods_url = '%s/api/v1/namespaces/%s/pods' % (self.api_address, namespace)
            response = requests.get(pods_url, headers=self.headers, verify=self.ca_cert )
            res = json.loads(response.text)
            for item in res['items']:
                print item['metadata']['name'] + '    -----    ' + 'Pod IP: ' + item['status']['podIP']

    def logs(self,pod):
        p = pod.split("/")[1]
        ns = pod.split("/")[0]
        pod_log_url = '%s/api/v1/namespaces/%s/pods/%s/log' % (self.api_address, ns, p)
        response = requests.get(pod_log_url, headers=self.headers, verify=self.ca_cert )
        print response.text

    def proc(self,pod):
        p = pod.split("/")[1]
        ns = pod.split("/")[0]
        ## Find docker container id and host for the pod
        pod_url = '%s/api/v1/namespaces/%s/pods/%s' % (self.api_address, ns, p)
        response = requests.get(pod_url, headers=self.headers, verify=self.ca_cert )
        response = json.loads(response.text)
        host_ip = response['status']['hostIP']
        cont_id = response['status']['containerStatuses'][0]['containerID'].split("//")[1]
        ## Process checking depends on ssh connection to the host so passwordless login must be setup.
        port = '22'
        username = 'root'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, port, username=username)
        cmd = 'docker top %s' % cont_id
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print stdout.read()
        ssh.close()



############# Script ####################

parser = Parser()
args = parser.parse_args()

c = check()

if args.cmd[0] == 'list':
    c.list()

elif args.cmd[0] == 'logs':
    pod = args.cmd[1]
    c.logs(pod)

elif args.cmd[0] == 'proc':
    pod = args.cmd[1]
    c.proc(pod)

else:
    print """
    Usage: 

    check.py list   --->    List all pods and in all namespaces
    check.py logs   --->    List logs from a pod , pod with namespace must be provided in format:   check.py logs default/my-pod-name
    check.py proc   --->    List all processes in a pod , example:   check.py proc default/my-pod-name

    Note:
    For process checking ssh logins must be configured without password on all cluster nodes (including masters in pods there will be checked)
    Your Auth bearer token must be configured in headers class variable, cluster certificate authority in class variable ca_cert
    """
