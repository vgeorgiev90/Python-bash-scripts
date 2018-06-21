#!/bin/python

import boto3
import argparse


################### Functions ###################


#Declare parser to collect cli arguments
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--appservers','-a',action='store_true',help='Deploy app servers')
    parser.add_argument('--options','-o',metavar='SUBNET KEY',nargs='*',help='Options for app servers or db instances')
    parser.add_argument('--dbservers','-d',action='store_true',help='Deploy db servers')
    parser.add_argument('--example','-e',action='store_true', help='example usage')
    return parser


# Class for EC2 app server deployment
class ec2():

    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def create(self,subnet,key):
        instances = self.ec2.create_instances(ImageId='ami-14c5486b',
                InstanceType='t2.micro',
                MinCount = 1,
                MaxCount = 1,
                SecurityGroupIds = ['sg-b4e562ff'],  ### Can be changed
                SubnetId = subnet,
                BlockDeviceMappings = [{'DeviceName': '/dev/xvda','Ebs': { 'VolumeSize': 10 }}],
                KeyName = key,
                UserData = 'eXVtIGluc3RhbGwgaHR0cGQgLXkgJiYgc2VydmljZSBodHRwZCBzdGFydCAmJiBjaGtjb25maWcgaHR0cGQgb24K',
                TagSpecifications = [{ 'ResourceType': 'instance' , 'Tags': [{ 'Key': 'Name', 'Value': 'app-server'}] }],

        )


## RDS deployment
class rds():

    def __init__(self):
        self.rds = boto3.client('rds')

    def create(self,subnet_group,instance_name):
        response = self.rds.create_db_instance(
                DBName = 'wordpress',   ### name of the database
                AllocatedStorage = 20,
                DBInstanceClass = 'db.t2.micro',
                Engine = 'mysql',
                DBInstanceIdentifier = instance_name, ## name - can be changed
                MasterUsername = 'root',
                MasterUserPassword = 'yazdan-hasainar',  ## root password - Can be changed
                VpcSecurityGroupIds = [ 'sg-48c54303' ], ### sec groups - Can be changed
                Tags = [{'Key': 'Name', 'Value': 'db-server'}],
                DBSubnetGroupName = subnet_group,
        )



################# Script ##############

parser = Parser()
args = parser.parse_args()

if args.appservers and args.options:
    subnet = args.options[0]
    key = args.options[1]

    launch = ec2()
    instance = launch.create(subnet,key)


elif args.dbservers and args.options:
    subnet_group = args.options[0]

    launch = rds()

    for i in range(1,3):
        name = "db-server-%s" % i
        instance = launch.create(subnet_group,name)

elif args.example:
    print "==========================================================="
    print "example for app-server creation"
    print "./aws-app-db-deploy.py -a -o subnet-6bf56d41 viktor-testing"
    print "This will create instance in subnet: subnet-6bf56d41 with ssh key pair called: viktor-testing"
    print ""
    print "db server example"
    print "./aws-app-db-deploy.py -d -o db-subnet-group"
    print "for the moment only one argument is provided subnet group for the database\nTwo db servers are created"
    print ""
    print "==========================================================="

else:
    parser.print_help()
