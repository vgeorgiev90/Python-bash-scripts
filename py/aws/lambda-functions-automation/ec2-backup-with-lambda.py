###IAM role
#{
#  "Version": "2012-10-17",
#  "Statement": [{
#      "Effect": "Allow",
#      "Action": [
#        "logs:CreateLogGroup",
#        "logs:CreateLogStream",
#        "logs:PutLogEvents"
#      ],
#      "Resource": "arn:aws:logs:*:*:*"
#    },
#    {
#      "Effect": "Allow",
#      "Action": [
#        "ec2:CreateSnapshot",
#        "ec2:CreateTags",
#        "ec2:DeleteSnapshot",
#        "ec2:Describe*",
#        "ec2:ModifySnapshotAttribute",
#        "ec2:ResetSnapshotAttribute"
#      ],
#      "Resource": "*"
#    }
#  ]
#}




from datetime import datetime

import boto3


def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    ## Get all regions
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    #### Snapshot will be performed on instances with tag backup=true
    for region in regions:
        print('Instances in EC2 Region {0}:'.format(region))
        ec2 = boto3.resource('ec2', region_name=region)
        instances = ec2.instances.filter(
            Filters=[
                {'Name': 'tag:backup', 'Values': ['true']}
            ]
        )
        # ISO 8601 timestamp, i.e. 2019-01-31T14:01:58
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat()

        for i in instances.all():
            for v in i.volumes.all():
                desc = 'Backup of {0}, volume {1}, created {2}'.format(
                    i.id, v.id, timestamp)
                print(desc)
                snapshot = v.create_snapshot(Description=desc)
                print("Created snapshot:", snapshot.id)

