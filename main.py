import importlib
from datetime import datetime,timezone
import os
from helper import emailing
import time
import json
import asyncio
import boto3
from schemas import ensure_job

COMPANY_FOLDER = "companies"
# Possible error if the data_for_website is never initialised then we will get an error
def get_json_from_s3(bucket_name="allseeing-website", key="data_for_website.json"):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    content = response['Body'].read()
    return json.loads(content)

def upload_data_for_website():
    bucket_name="allseeing-website"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.upload_file("/tmp/data_for_website.json","data_for_website.json")
    print("data_for_website has been uploaded")

def update_website(jobs):
    """
    jobs: dict[company_name, list[job_dict]] where each job_dict has the canonical schema
    (jobId, title, url, detected, source; optional: location, posted_date, updated_time).
    """
    data=get_json_from_s3()
    data["date"]=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    for key, new_jobs in jobs.items():
        # Skip if there are no new jobs for this company
        if not new_jobs:
            continue
        # Initialize missing company list
        data["jobs"].setdefault(key, [])
        # Prepend new jobs to the beginning
        data["jobs"][key][:0] = new_jobs
    with open("/tmp/data_for_website.json", "w") as f:
        json.dump(data, f, indent=4)
    upload_data_for_website()

def update_website_remove_old_jobs():
    """Remove jobs older than 3 days from website data. Expects data['jobs'] to be dict of list[job_dict] with canonical schema (detected field)."""
    data=get_json_from_s3()
    # Remove jobs that are 3 days older
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - 3 * 24 * 60 * 60  # 3 days in seconds

    for company, jobs_list in data.get("jobs", {}).items():
        filtered_jobs = []
        for job in jobs_list:
            detected_str = job.get("detected")
            if detected_str:
                try:
                    detected_dt = datetime.strptime(detected_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    # If detected is not in expected format, skip this job
                    continue
                if detected_dt.timestamp() >= cutoff:
                    filtered_jobs.append(job)
        data["jobs"][company] = filtered_jobs

    with open("/tmp/data_for_website.json", "w") as f:
    #with open("updated.json", "w") as f:
        json.dump(data, f, indent=4)
    upload_data_for_website()

def clear_website_data():
    data = {}
    data["date"]=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    data["jobs"]={}
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py" and filename[:-3]:
            company_name = filename[:-3]  # Remove '.py'
            data["jobs"][company_name]= []
    with open("/tmp/data_for_website.json", "w") as f:
        json.dump(data, f, indent=4)
    print("website data cleared")
    upload_data_for_website()

async def main(test=False,user="private",send_email=True):
    '''
    Runs all company extractors, diffs for new jobs, optionally emails and updates website.
    Returns jobs: dict[company_name, list[job_dict]] where each job_dict has the canonical
    schema (jobId, title, url, detected, source; optional: location, posted_date, updated_time).
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
            raw_list = module.main(current_jobs[i],test=test)
            jobs[company_name] = [ensure_job(company_name, j) for j in (raw_list or [])]
            i+=1
            if jobs[company_name]:
                any_new_job=True
    if not send_email:
        print("Email not being sent")
    if any_new_job and send_email:
        emailing.send_email(jobs,user)
        print("Email Sent")
    if user=="private" and not test:
        update_website(jobs)
    return jobs

if __name__ == "__main__":
    #asyncio.run(main())
    #clear_website_data()
    update_website_remove_old_jobs()

