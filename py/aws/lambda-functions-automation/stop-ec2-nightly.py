### Create cloudwatch rule  and add the lambda function as target

import boto3

def lambda_handler(event, context):
    #Get a list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in e2_client.describe_regions()['Regions']]

    # Iterate over each regions
    for reg in regions:
        ec2 = boto3.resource('ec2', region_name=reg)

        print "Region: " + reg


        # Get only running instances
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        # Stop the instances
        for inst in instances:
            inst.stop()
            print "Stopped instance: " + inst.id
