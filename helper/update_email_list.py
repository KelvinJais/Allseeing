import boto3

def upload():
    bucket_name="allseeings3-public-data"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file("email-list.txt","email-list.txt")
    print("email-list has been uploaded")

def download():
    bucket_name="allseeings3-public-data"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.download_file("email-list.txt","/tmp/email-list.txt")
    print("email-list has been downloaded")


if __name__=="__main__":
    upload()
