import kubernetes
import kopf
import yaml
import boto3
from botocore.exceptions import ClientError
import requests
import json
import base64


### Get aws credentials from the kubernetes secret
def get_creds(aws_key):
    token_file = '/var/run/secrets/kubernetes.io/serviceaccount/token'
    with open(token_file, 'r') as f:
        token = f.read()
    secret_name = aws_key['valueFrom']['secretKeyRef']['name']

    headers = { "accept": "application/json"}
    headers['Authorization'] = "Bearer %s" % token

    url = "https://kubernetes/api/v1/secrets"

    response = requests.get(url, headers=headers, verify='/var/run/secrets/kubernetes.io/serviceaccount/ca.crt')
    secrets = json.loads(response.text)['items']

    for item in secrets:
        name = item['metadata']['name']
        if name == secret_name:
            akey = item['data']['awsKey']
            asecret = item['data']['awsSecret']

    aws_key = base64.b64decode(akey)
    aws_secret = base64.b64decode(asecret)
    return aws_key.decode("utf8"), aws_secret.decode("utf8")



@kopf.on.create('kubernetes.io', 'v1', 'workers')
def create_worker(body, spec, **kwargs):
    aws_key = body['spec']['awsKey']
    aws_secret = body['spec']['awsSecret']
    node_name = body['spec']['nodeName']
    aws_region = body['spec']['awsRegion']
    node_type = body['spec']['nodeType']
    join_command = body['spec']['joinCommand']
    aws_key, aws_secret = get_creds(aws_key)

    creds = """
[default]
aws_access_key_id = %s
aws_secret_access_key = %s """ % (aws_key, aws_secret)

    config = """
[default]
region = eu-central-1
    """

    with open('/root/.aws/credentials', 'w') as f:
        f.write(creds)

    with open('/root/.aws/config', 'w') as w:
        w.write(config)

    tags = [{ 'ResourceType': 'instance' , 'Tags': [{ 'Key': 'Name', 'Value': node_name}] }]

    script = """#!/bin/bash
sleep 120
%s """ % join_command

    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(
                ImageId = 'ami-0592b9d1aed542a30',
                MinCount = 1,
                MaxCount = 1,
                SecurityGroupIds = [ 'sg-02a86d13e8ab4e4d0' ],
                SubnetId = 'subnet-17c15c5a',
                KeyName = 'k8s-workers',
                UserData = script,
                TagSpecifications = tags
            )
   


@kopf.on.delete('kubernetes.io', 'v1', 'workers')
def delete_worker(body, spec, **kwargs):
    aws_key = body['spec']['awsKey']
    aws_secret = body['spec']['awsSecret']
    node_name = body['spec']['nodeName']

    aws_key, aws_secret = get_creds(aws_key)

    creds = """
    [default]
    aws_access_key_id = %s
    aws_secret_access_key = %s """ % (aws_key, aws_secret)

    config = """
    [default]
    region = eu-central-1
    """

    with open('/root/.aws/credentials', 'w') as f:
        f.write(creds)

    with open('/root/.aws/config', 'w') as w:
        w.write(config)

    ec2 = boto3.resource('ec2')
    filters = [{'Name':'tag:Name', 'Values':[node_name]}]
    instances = ec2.instances.filter(Filters=filters)

    for instance in instances:
        ec2.instances.filter(InstanceIds=[instance.id]).stop()
        ec2.instances.filter(InstanceIds=[instance.id]).terminate()
