#!/bin/python
# Script to create backup on ec2 via snapshots

import boto3
import argparse
import datetime
from botocore.exceptions import ClientError

######## Functions ###########

def parser():
    parser = argparse.ArgumentParser(description='Script to automate snapshots of EC2 ebs volumes')
    parser.add_argument('--list','-l', action='store_true', help='List all volumes found')
    parser.add_argument('--snapshot','-s', nargs=1, metavar='Volume-ID', help='Take snapshot of the provided volume id')
    return parser

def list_volumes():
    ec2 = boto3.resource('ec2')
    volumes = ec2.volumes.all()
    for vol in volumes:
        print str(vol) + " --- " + vol.state
        print "Tags: %s" % vol.tags
        print ""

def snapshot(id):
    ec2 = boto3.resource('ec2')
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    description = 'backup-%s-%s' % (id,time)
    try:
        ec2.create_snapshot(VolumeId=id, Description=description)
        print "Snapshot is being created with description: %s" % description
    except ClientError:
        print "Please check if the id provided is not wrong"

#### Script #####

par = parser()
args = par.parse_args()

if args.list:
    list_volumes()
elif args.snapshot:
    id = args.snapshot[0]
    snapshot(id)
                       
