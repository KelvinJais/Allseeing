'''
This is the file that is to be run on aws lambda
'''
import json
import os
import boto3
from main import main, update_website_remove_old_jobs
import asyncio
from main import clear_website_data

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
    if event["remove_old_jobs"]=="True":
        update_website_remove_old_jobs()
    elif event["user"]=="private":
        print("Private Run")
        download_s3_folder("allseeings3data")
        if event["test"]=="True":
            asyncio.run(main(test=True,send_email=(event["send_email"]=="True")))
        else:
            asyncio.run(main(send_email=(event["send_email"]=="True")))
        upload_s3_folder("allseeings3data")
        return {
            'statusCode': 200,
            'body': json.dumps('Private Program completed')
        }
    else:
        print("Public Run")
        download_s3_folder("allseeings3-public-data")
        if event["test"]=="True":
            asyncio.run(main(user="public",test=True,send_email=(event["send_email"]=="True")))
        else:
            asyncio.run(main(user="public",send_email=(event["send_email"]=="True")))
        upload_s3_folder("allseeings3-public-data")
        return {
            'statusCode': 200,
            'body': json.dumps('Public Program completed')
        }


if __name__=="__main__":
    # Default Send Email private no test
    private_event={
        "send_email":"True",
        "remove_old_jobs":"False",
        "user":"private",
        "test":"False"
            }

    remove_old_jobs={
        "remove_old_jobs":"True",
                     }
    #lambda_handler(event,"")
    lambda_handler(private_event,"")
