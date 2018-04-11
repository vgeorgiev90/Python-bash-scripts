#!/bin/python

import boto3
import argparse
import os


def parser():
    parser = argparse.ArgumentParser('Script to automate IP cidr block change for security group rule')
    parser.add_argument('--group','-s',metavar='GROUP IP-old IP-new', nargs=3, help='Provide security group name and CIDR IP')
    parser.add_argument('--check','-c',action='store_true',help='Check your current IP')
    parser.add_argument('--list','-l',metavar='ID',nargs=1,help='Check the rules in the provided group')
    return parser

class security():
    def __init__(self,id):
        self.id = id
        self.ec2 = boto3.resource('ec2')
        self.security_group = self.ec2.SecurityGroup(self.id)

    def revoke(self,ip_old):
        self.ip_old = ip_old
        self.security_group.revoke_ingress(IpProtocol="tcp", CidrIp=self.ip_old, FromPort=6543, ToPort=6543)

    def auth(self,ip_new):
        self.ip_new = ip_new
        self.security_group.authorize_ingress(IpProtocol="tcp",CidrIp=self.ip_new,FromPort=6543,ToPort=6543)

def check():
    ip = os.system('curl ipinfo.io')

def list(id):
    ec2 = boto3.client('ec2')
    group = ec2.describe_security_groups(GroupIds=[id])
    ingress = group['SecurityGroups'][0]['IpPermissions'] ### Checking only the first rule which is for SSH access
    print "Port: %s" % ingress[0]['FromPort']
    print "IP: %s" % ingress[0]['IpRanges'][0]['CidrIp']


#### Script #####

parser = parser()
args = parser.parse_args()

if args.group:
    id = args.group[0]
    ip_old = args.group[1]
    ip_new = args.group[2]
    sec = security(id)
    sec.revoke(ip_old)
    sec.auth(ip_new)
elif args.check:
    check()
elif args.list:
    id = args.list[0]
    list(id)

