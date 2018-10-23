#!/bin/python

import boto3
import argparse

def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--old','-o',nargs=1, type=str, required=True, metavar="OLD-SG",help='Old security group')
    parser.add_argument('--new','-n',nargs=1, type=str, required=True, metavar="NEW-SG", help='New security group')
    return parser

class ec2():
    def __init__(self):
        self.ec2 = boto3.client('ec2')

    def list(self):
        self.response = self.ec2.describe_instances()
        self.data = self.response['Reservations']
        self.instance_ids = []
        for inst in self.data:
            self.instance_ids.append(inst['Instances'][0]['InstanceId'])
        return self.instance_ids

class security_group():

    def __init__(self,old_sg,new_sg):
        self.ec2 = boto3.resource('ec2')
        self.old_sg = old_sg
        self.new_sg = new_sg

    def modify(self):
        instances = self.ec2.instances.filter()
        for instance in instances:
            all_sg_ids = [sg['GroupId'] for sg in instance.security_groups]
            if self.old_sg in all_sg_ids:
                all_sg_ids.remove(self.old_sg)
                all_sg_ids.append(self.new_sg)
            instance.modify_attribute(Groups=all_sg_ids)
            print "Security group changed sucessfully"




parser = Parser()
args = parser.parse_args()

if args.old and args.new:
    old_group = args.old[0]
    new_group = args.new[0]
    group = security_group(old_group,new_group)
    group.modify()
