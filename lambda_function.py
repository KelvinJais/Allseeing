import json
import os
import boto3
from main import main

def download_s3_folder(bucket_name):
    prefix = 'data/'  # For example: 'data/images/'
    os.makedirs('/tmp/data', exist_ok=True)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix):
        if obj.key.endswith('/'):
            continue
        target="/tmp/"+obj.key
        bucket.download_file(obj.key, target)

def upload_s3_folder(bucket_name):
    prefix = 'data/'  # For example: 'data/images/'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for root, dirs, files in os.walk('/tmp/data'):
        for file in files:
            file_path = os.path.join(root, file)
            s3_path = os.path.join(prefix, os.path.relpath(file_path, '/tmp/data'))
            bucket.upload_file(file_path, s3_path)

def lambda_handler(event, context):
    download_s3_folder("allseeings3data")
    main()
    upload_s3_folder("allseeings3data")
    return {
        'statusCode': 200,
        'body': json.dumps('Program completed')
    }

def lambda_handler_public(event,context):
    download_s3_folder("allseeings3_public_data")
    main()
    upload_s3_folder("allseeings3_public_data")
    return {
        'statusCode': 200,
        'body': json.dumps('Public Program completed')
    }

if __name__=="__main__":
    lambda_handler("","")

