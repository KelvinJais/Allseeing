"""
Shared job state diffing and persistence.
Uses the aggregating pattern: merge new jobs into old state, persist the merged state.
"""

import os

from helper import load_download


def diff_and_persist(company_name: str, current_jobs: dict, test: bool = False) -> list:
    """
    Compare current_jobs to previous state, persist using aggregating pattern, return new jobs.

    - current_jobs: dict[jobId, job] from extractor()
    - test: if True, use _jobs_list_t_new_jobs as "current" instead of current_jobs; do not persist
    - Returns: list of job dicts that are new (not seen before)
    """
    file_path = os.path.join("/tmp", "data", f"{company_name}_jobs_list.json")

    if not os.path.exists(file_path):
        load_download.download_json(current_jobs, f"{company_name}_jobs_list")
        load_download.download_json(current_jobs, f"{company_name}_jobs_list_t_new_jobs")
        return []

    if test:
        new_job_data = load_download.load_json(f"{company_name}_jobs_list_t_new_jobs")
    else:
        new_job_data = current_jobs

    old_job_data = load_download.load_json(f"{company_name}_jobs_list")
    brand_new_jobs = []

    for job_id in new_job_data:
        if job_id not in old_job_data:
            brand_new_jobs.append(new_job_data[job_id])
            old_job_data[job_id] = new_job_data[job_id]

    if not test:
        load_download.download_json(old_job_data, f"{company_name}_jobs_list")

    print(len(brand_new_jobs), "new jobs at", company_name)
    return brand_new_jobs
