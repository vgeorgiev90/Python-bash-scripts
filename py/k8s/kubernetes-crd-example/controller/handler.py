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



@kopf.on.create('kubernetes.io', 'v1', 's3buckets')
def create_bucket(body, spec, **kwargs):
    aws_key = body['spec']['awsKey']
    aws_secret = body['spec']['awsSecret']
    bucket_name = body['spec']['bucketName']
    aws_region = body['spec']['awsRegion']

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

    bucket_config = { "LocationConstraint": aws_region }

    try:
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=bucket_config)
    except ClientError as e:
        print(e)




@kopf.on.delete('kubernetes.io', 'v1', 's3buckets')
def delete_bucket(body, spec, **kwargs):
    aws_key = body['spec']['awsKey']
    aws_secret = body['spec']['awsSecret']
    bucket_name = body['spec']['bucketName']

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

    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)

        for key in bucket.objects.all():
            key.delete()
        bucket.delete()
    except ClientError as e:
        print(e)
