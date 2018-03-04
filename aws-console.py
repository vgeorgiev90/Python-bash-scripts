#!/bin/python

import boto3
import argparse
from botocore.exceptions import ClientError


########## Functions #############
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ec2',nargs='*',metavar='cmd',help='EC2 interaction')
    parser.add_argument('--s3',nargs='*',metavar='cmd',help='S3 interaction --s3 help  for comands list')

    return parser

class amazon_ec2():
    def __init__(self):
        self.ec2 = boto3.client('ec2')
    def list(self):
        response = self.ec2.describe_instances()
        data = response['Reservations']
        for server in data:
            for detail in server['Instances']:
                state = detail['State']['Name']
                if state == 'running':
                    print "PublicDNS: %s" % detail['PublicDnsName']
                    print "PrivateDNS: %s" % detail['PrivateDnsName']
                    print "PublicIp: %s" % detail['PublicIpAddress']
                    print "PrivateIP: %s" % detail['PrivateIpAddress']
                    print "VPCID: %s" % detail['VpcId']
                    print "InstaceID: %s" % detail['InstanceId']
                    print "InstanceType: %s" % detail['InstanceType']
                    print "Security-Groups: %s" % [i['GroupName'] for i in detail['SecurityGroups']]
                    print "State: %s" % state
                    print ""
                elif state == 'stopped':
                    print "InstaceID: %s" % detail['InstanceId']
                    print "InstanceType: %s" % detail['InstanceType']
                    print "State: %s" % state
                    print ""
                else:
                    print "Not enough information"
    def stop(self,id):
        response = self.ec2.stop_instances(InstanceIds=[id])
        print "InstanceID: %s" % response['StoppingInstances'][0]['InstanceId']
        print "Current State: %s" % response['StoppingInstances'][0]['CurrentState']['Name']
    def start(self,id):
        response = self.ec2.start_instances(InstanceIds=[id])
        print "InstanceID: %s" % response['StartingInstances'][0]['InstanceId']
        print "Current State: %s" % response['StartingInstances'][0]['CurrentState']['Name']

class amazon_s3():
    def __init__(self):
        self.s3 = boto3.resource('s3')
    def list_buckets(self):
        buckets = self.s3.buckets.all()
        for buck in buckets:
            print "Bucket: %s" % str(buck).split("'")[1]
    def list_buck_cont(self,buck):
        client = boto3.client('s3')
        paginator = client.get_paginator('list_objects')
        page_iterator = paginator.paginate(Bucket=buck)
        for page in page_iterator:
            items = page['Contents']
            for i in range(0,len(items)):
                print page['Contents'][i]['Key']
    def buck_upload(self,buck,file):
        bucket = self.s3.Bucket(buck)
        with open(file,'rb') as f:
            bucket.upload_fileobj(f,file)
    def buck_download(self,buck,file):
        bucket = self.s3.Bucket(buck)
        file_name = file.split('/')[-1]
        with open(file_name,'wb') as f:
            bucket.download_fileobj(file,f)

############## Script ###########

parser = Parser()
args = parser.parse_args()

try:
    if args.ec2:
        cmd = args.ec2[0]
        ec2 = amazon_ec2()
        if cmd == 'list':
            ec2.list()
        elif cmd == 'stop':
            id = args.ec2[1]
            ec2.stop(id)
        elif cmd == 'start':
            id = args.ec2[1]
            ec2.start(id)
        else:
            print "Only list is available as command for now"
    elif args.s3:
        cmd = args.s3[0]
        s3 = amazon_s3()
        try:
            if cmd == 'list':
                s3.list_buckets()
            elif cmd == 'list-bucket':
                bucket = args.s3[1]
                s3.list_buck_cont(bucket)
            elif cmd == 'upload':
                bucket = args.s3[1]
                file = args.s3[2]
                s3.buck_upload(bucket,file)
            elif cmd == 'download':
                bucket = args.s3[1]
                file = args.s3[2]
                s3.buck_download(bucket,file)
            elif cmd == 'help':
                print "Commands for S3:"
                print "list                 -  list all buckets"
                print "list-bucket BUCKET   -  list bucket contents"
                print "upload BUCKET FILE   -  upload file to bucket"
                print "download BUCKET FILE -  download file from bucket"
            else:
                print "No such command type --s3 help for info"
        except ClientError:
            print "Check the bucket or file name provided...."
    else:
        parser.print_help()
except IndexError:
    print "Incomplete command...."

                                    
