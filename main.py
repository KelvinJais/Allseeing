import importlib
import json
import os
from datetime import datetime, timezone

import asyncio
import boto3

from schemas import ensure_job
from helper import emailing
from helper import job_state
from helper.extractor_runner import run_extractor

COMPANY_FOLDER = "companies"
CONFIG_PATH = "companies_config.json"


def _load_companies_config():
    """Load companies config and return list of enabled company names."""
    path = os.path.join(os.path.dirname(__file__), CONFIG_PATH)
    with open(path, "r") as f:
        config = json.load(f)
    return [
        name for name, opts in config.items()
        if isinstance(opts, dict) and opts.get("enabled", True)
        or not isinstance(opts, dict) and opts
    ]


def get_enabled_companies():
    """Return list of enabled company names from config."""
    return _load_companies_config()


def _log_run(company, status, jobs_found=0, new_jobs=0, duration_ms=0, error=None):
    """Structured log for CloudWatch/dashboard: {company, status, jobs_found, new_jobs, duration_ms}."""
    entry = {
        "company": company,
        "status": status,
        "jobs_found": jobs_found,
        "new_jobs": new_jobs,
        "duration_ms": round(duration_ms, 1),
    }
    if error:
        entry["error"] = str(error)
    print(json.dumps(entry))


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
    data["date"] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    data["jobs"] = {name: [] for name in get_enabled_companies()}
    with open("/tmp/data_for_website.json", "w") as f:
        json.dump(data, f, indent=4)
    print("website data cleared")
    upload_data_for_website()

async def main(test=False, user="private", send_email=True):
    '''
    Runs all company extractors, diffs for new jobs, optionally emails and updates website.
    Returns jobs: dict[company_name, list[job_dict]] where each job_dict has the canonical
    schema (jobId, title, url, detected, source; optional: location, posted_date, updated_time).
    Companies are loaded from companies_config.json; only enabled companies are run.
    Uses timeout (60s) and retries (3) per extractor; one failure does not stop the run.
    '''
    enabled = get_enabled_companies()
    any_new_job = False
    jobs = {}
    tasks = []
    for company_name in enabled:
        full_module_name = f"{COMPANY_FOLDER}.{company_name}"
        module = importlib.import_module(full_module_name)
        tasks.append(run_extractor(module.extractor))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, company_name in enumerate(enabled):
        duration_ms = 0
        if isinstance(results[i], BaseException):
            _log_run(company_name, "error", duration_ms=0, error=results[i])
            jobs[company_name] = []
            continue
        r = results[i]
        if len(r) == 3 and r[0] is None:
            _, duration_ms, err = r
            _log_run(company_name, "error", duration_ms=duration_ms, error=err)
            jobs[company_name] = []
            continue
        current_jobs, duration_ms = r[0], r[1]
        jobs_found = len(current_jobs) if isinstance(current_jobs, dict) else 0
        try:
            raw_list = job_state.diff_and_persist(company_name, current_jobs, test=test)
        except Exception as e:
            _log_run(company_name, "error", jobs_found=jobs_found, duration_ms=duration_ms, error=e)
            jobs[company_name] = []
            continue
        new_jobs_list = [ensure_job(company_name, j) for j in (raw_list or [])]
        jobs[company_name] = new_jobs_list
        _log_run(company_name, "ok", jobs_found=jobs_found, new_jobs=len(new_jobs_list), duration_ms=duration_ms)
        if new_jobs_list:
            any_new_job = True
    if not send_email:
        print("Email not being sent")
    if any_new_job and send_email:
        emailing.send_email(jobs,user)
        print("Email Sent")
    if user=="private" and not test:
        update_website(jobs)
    return jobs

if __name__ == "__main__":
    asyncio.run(main())
    #clear_website_data()
    #update_website_remove_old_jobs()

