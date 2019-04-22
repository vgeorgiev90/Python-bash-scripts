## This function depends on python pillow package
#mkdir package
#pip install paramiko --target .
#zip -r9 ../function.zip .
#cd ..
#zip -g function.zip script.py
#aws lambda update-function-code --function-name Deploy-skillapp --zip-file fileb://function.zip

##Function can be triggered on s3 upload

import os
import tempfile

import boto3
from PIL import image

s3 = boto3.client('s3')
DEST_BUCKET = os.environ['DEST_BUCKET']
SIZE = 128, 128


def lambda_handler(event, context):

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        thumb = 'thumb-' + key

        with tempfile.TemporaryDirectory() as tmpdir:
            download_path = os.path.join(tmpdir, key)
            upload_path = os.path.join(tmpdir, thumb)
            s3.download_file(source_bucket, key, download_path)
            generate_thumbnail(download_path, upload_path)
            s3.upload_file(upload_path, DEST_BUCKET, thumb)

        print("Thumbnail image saved at {}/{}".format(DEST_BUCKET, thumb))

def generate_thumbnail(source_path, dest_path):
    print("Generating thumbnail from: %s" % source_path)

    with Image.open(source_path) as img:
        img.thumbnail(SIZE)
        img.save(dest_path)
