import importlib
import os
from helper import emailing
import time
import json
import asyncio
from datetime import datetime
import boto3
COMPANY_FOLDER = "companies"

def upload_data_for_website():
    bucket_name="allseeing-website"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file("/tmp/data_for_website.json","data_for_website.json")
    print("data_for_website has been uploaded")

async def main(test=False,user="private"):
    '''
    The first loop runs all the extractor functions asynchronously from all the companies in the company folder
    Second loop runs all the main function from the companies in the main folder. the main function includes the logic of compaisions
    '''
    any_new_job=False
    jobs = {}
    tasks=[]
    companies_with_bug=()
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py" and filename[:-3] not in companies_with_bug:
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            tasks.append(module.extractor())
    current_jobs=await asyncio.gather(*tasks)
    i=0
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py" and filename[:-3] not in companies_with_bug:
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            jobs[company_name]= module.main(current_jobs[i],test=test)
            i+=1
            if jobs[company_name]:
                any_new_job=True
    if any_new_job:
        emailing.send_email(jobs,user)
    if user=="public":
        data_for_website={}
        data_for_website["date"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_for_website["jobs"]=jobs
        with open("/tmp/data_for_website.json", "w") as f:
            json.dump(data_for_website, f, indent=4)
        upload_data_for_website()

if __name__ == "__main__":
    asyncio.run(main())


