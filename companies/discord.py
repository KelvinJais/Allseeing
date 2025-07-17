from helper import load_download
import requests
import json
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://api.greenhouse.io/v1/boards/discord/jobs?content=true"

    payload = {}
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Referer': 'https://discord.com/',
      'Origin': 'https://discord.com',
      'Sec-GPC': '1',
      'Connection': 'keep-alive',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'cross-site',
      'Priority': 'u=4',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data = await response.json()
            jobs=data.get('jobs')
            items={}
            for job in jobs:
                if job.get('departments')[0].get('name') in ("Product Engineering","Developers","Data Platform","Core Tech Engineering", "Data Science & Engineering"):
                    item={"jobId":str(job.get("id")),
                          "title":job.get("title"),
                          "url":job.get("absolute_url"),
                        "updated_time":job.get("updated_at")
                                            }
                    items[item.get("jobId")]=item
            return items

def main(current_jobs,test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data=current_jobs
        load_download.download_json(job_data,f"{company_name}_jobs_list")
        load_download.download_json(job_data,f"{company_name}_jobs_list_t_new_jobs")
    else:
        if test:
            new_job_data=load_download.load_json(f"{company_name}_jobs_list_t_new_jobs")
        else:
            new_job_data=current_jobs
        old_job_data=load_download.load_json(f"{company_name}_jobs_list")
        brand_new_jobs=[]
        for job in new_job_data.keys():
            if job not in old_job_data:
                brand_new_jobs.append(new_job_data[job])
        if not test:
            load_download.download_json(new_job_data,f"{company_name}_jobs_list")
        print(len(brand_new_jobs),"new jobs at",company_name)
        return brand_new_jobs

if __name__=="__main__":
    current_jobs=asyncio.run(extractor())
    main(current_jobs)

