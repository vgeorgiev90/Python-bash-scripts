#!/usr/bin/python3

import boto3
from time import sleep
import json
from os import path
from sys import exit
import subprocess
import argparse



def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['check', 'get-vpc', 'get-subnets', 'create-bastion', 'delete-bastion'], help='sub-command')
    parser.add_argument('--vpc', '-v', nargs=1, help='VPC Id for the instance')
    parser.add_argument('--subnet', '-s', nargs=1, help='Subnet for the instance')
    return parser


def create_config(vpc_id, instance_id, group_id, subnet_id):
    data = {
        'VPC': vpc_id,
        'Subnet': subnet_id,
        'instance': instance_id,
        'security_group': group_id
    }
    if not path.exists('bastion_config.json'):
        with open('bastion_config.json', 'w') as f:
            json.dump(data, f)
    else:
        print("It seems that you already have instance runnig, check bastion_config.json")
        exit(0)


def get_config():
    if path.exists('bastion_config.json'):
        with open('bastion_config.json', 'r') as f:
            config = json.load(f)
        return config
    else:
        print("Cant find bastion_config.json are you sure you have instance deployed ?")
        exit(0)



class Bastion():

    def __init__(self):
        self.client = boto3.client('ec2')

    def display_vpcs(self):
        VPCs = self.client.describe_vpcs()
        for vpc in VPCs['Vpcs']:
            vpc_id = vpc['VpcId']
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']

            print("<-------------------------------------------->")
            print("VPC_ID: %s  ->  VPC_Name: %s " % (vpc_id, vpc_name))


    def display_subnets(self, vpc_id):
        subnets = self.client.describe_subnets()
        for subnet in subnets['Subnets']:
            if subnet['VpcId'] == vpc_id:
                subnet_id = subnet['SubnetId']
                for tag in subnet['Tags']:
                    if tag['Key'] == 'Name':
                        subnet_name = tag['Value']

                print("<-------------------------------------------->")
                print("Subnet_ID: %s  ->  Subnet_Name: %s " % (subnet_id, subnet_name))


    def launch_instance(self, vpc_id, subnet_id):
        if path.exists('bastion_config.json'):
            print("You already have instance running, check your bastion_config.json")
            exit(0)

        response = self.client.create_security_group(
                    Description = "Security Group for temporary bastion host",
                    GroupName = "Bastion",
                    VpcId = vpc_id,
                )
        group_id = response['GroupId']
        self.client.authorize_security_group_ingress(
                    GroupId = group_id,
                    IpPermissions = [{
                        'FromPort': 22,
                        'IpProtocol': 'tcp',
                        'IpRanges': [{
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'SSH'
                                }],
                        'ToPort': 22
                        }]
                )
        response_instance = self.client.run_instances(
                    ImageId = 'ami-0dc8d444ee2a42d8a',
                    InstanceType = 't2.small',
                    MinCount = 1,
                    MaxCount = 1,
                    SecurityGroupIds = [ group_id ],
                    SubnetId = subnet_id,
                    KeyName = 'cobrowser.pem',
                    TagSpecifications = [{
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'temp_33fDEcvjhpp'
                        }]}]
                )
        instance_id = response_instance['Instances'][0]['InstanceId']
        create_config(vpc_id, instance_id, group_id, subnet_id)
        print("Bastion host created in vpc: %s and subnet: %s" % (vpc_id, subnet_id))


    def check_instance(self):
        config = get_config()
        response = self.client.describe_instances(
                    InstanceIds = [ config['instance'] ]
                )
        public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        print("Public_IP: %s" % public_ip)


    def terminate_instance(self):
        config = get_config()
        print("Deleting intance: %s" % config['instance'])
        self.client.terminate_instances(
                    InstanceIds = [ config['instance'] ]
                )
        sleep(180)
        print("Deleting security group: %s" % config['security_group'])
        self.client.delete_security_group(
                    GroupId = config['security_group']
                )
        subprocess.call(['rm', '-rf', 'bastion_config.json'])






parser = Parser()

args = parser.parse_args()

bastion = Bastion()

if args.cmd:
    if args.cmd == 'get-vpc':
        bastion.display_vpcs()

    elif args.cmd == 'get-subnets':
        if args.vpc:
            bastion.display_subnets(args.vpc[0])
        else:
            print("Please specify the VPC Id with --vpc")
    elif args.cmd == 'create-bastion':
        if args.vpc and args.subnet:
            vpc = args.vpc[0]
            subnet = args.subnet[0]
            bastion.launch_instance(vpc, subnet)
        else:
            print("Please specify vpc ID and subnet ID")

    elif args.cmd == 'delete-bastion':
        bastion.terminate_instance()

    elif args.cmd == 'check':
        bastion.check_instance()
