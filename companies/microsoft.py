from helper import load_download
from datetime import datetime,timezone
import requests
import json
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=software%20engineer&location=United%20States&start=0&filter_seniority=Entry&sort_by=timestamp"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data= await response.json()
            jobs=data.get("data").get("positions")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            print(len(jobs),"jobs found")
            for job in jobs:
                item={"jobId":str(job.get("id")),
                "title":job.get("name"),
                "url":"https://apply.careers.microsoft.com"+str(job.get("positionUrl")),
                "detected":detected_time
                }
                items[item.get("jobId")]=item
            return items

# Trying out aggregating. It gets the new jobs and adds it to the old jobs and saves it all.
# Pros: Some company like paypal has an issue where they constantly remove and add the same jobs. triggering a new job alert every time
# Cons: We will miss any updated jobs. ie, jobs that came out before and is not reposted.
def main(current_jobs,test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data= current_jobs
        load_download.download_json(job_data,f"{company_name}_jobs_list")
        load_download.download_json(job_data,f"{company_name}_jobs_list_t_new_jobs")
    else:
        if test:
            new_job_data=load_download.load_json(f"{company_name}_jobs_list_t_new_jobs")
        else:
            new_job_data= current_jobs
        old_job_data=load_download.load_json(f"{company_name}_jobs_list")
        brand_new_jobs=[]
        for job in new_job_data.keys():
            if job not in old_job_data:
                brand_new_jobs.append(new_job_data[job])
                old_job_data[job]=new_job_data[job]
        if not test:
            #load_download.download_json(new_job_data,f"{company_name}_jobs_list")
            load_download.download_json(old_job_data,f"{company_name}_jobs_list")
        print(len(brand_new_jobs),"new jobs at",company_name)
        return brand_new_jobs


if __name__ =="__main__":
    current_jobs=asyncio.run(extractor())
    main(current_jobs)