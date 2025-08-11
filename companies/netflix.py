from helper import load_download
from datetime import datetime,timezone
import requests
import json
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://explore.jobs.netflix.net/api/apply/v2/jobs?domain=netflix.com&microsite=netflix.com&start=0&num=10&exclude_pid=790304048633&query=Software%20Engineer&location=United%20States&pid=790304269505&domain=netflix.com&sort_by=new&microsite=netflix.com&triggerGoButton=false"

    payload = {}
    headers = {
      'Cookie': '_vs=7355042181395060895:1753813449.6980038:1413341020276280066; _vscid=2'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get("positions")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                item={"jobId":str(job.get("id")),
                      "title":job.get("name"),
                      "url":"https://explore.jobs.netflix.net/careers/search?pid="+str(job.get("id")),
                    "detected":detected_time
                        }
                items[item.get("jobId")]=item
            return items

#aggregating
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

