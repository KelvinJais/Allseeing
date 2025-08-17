from helper import load_download
from datetime import datetime,timezone
import requests
import json
import os
import asyncio
import aiohttp
import re

async def get_page(session, url, headers, payload):
    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()
        
async def get_all_pages(session,url,pages,headers,payload):
    tasks=[]
    for page in pages:
      page_payload = json.loads(payload)
      page_payload['page'] = page
      task = asyncio.create_task(get_page(session,url,headers,json.dumps(page_payload)))
      tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results
    
async def  multi_extractor():
    url = "https://jobs.apple.com/api/v1/search"
    payload = json.dumps({
      "query": "Software Engineer",
      "filters": {
        "locations": [
          "postLocation-USA"
        ]
      },
      "page": 1,
      "locale": "en-us",
      "sort": "newest",
      "format": {
        "longDate": "MMMM D, YYYY",
        "mediumDate": "MMM D, YYYY"
      }
    })
    headers = {
      'Content-Type': 'application/json',
      'Cookie': 'jobs=ee033c8a1751152e4f575a3dc86470ca; AWSALBAPP-0=AAAAAAAAAAB6GF24SlLuoDJvfkWbHe3RCZvP61I+/OrTmyhDYMaXp2ONWwdwHM/qE8rn52txEPRztzmREBWFMx6b1mqYWSYHzEdYlC94UQ/G3yKwUL+qVqw6igmCzlHbnX+SQmicjzzpYVY=; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; jssid=s%3AgD_pygnTOWq1Fe1t0wzgiuyX6MZCQT7E.AYXd5tEKYRrGgFgxrsyGqPl8JqaOV%2B0of1o2LVGUhnA'
    }
    async with aiohttp.ClientSession() as session:
            pages=range(3)
            responses=await get_all_pages(session,url,pages,headers,payload)
    jobs=[]
    for response in responses:
      jobs.extend(response.get('res').get('searchResults'))
    items={}
    detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    for job in jobs:
        match = re.search(r'-(.*)', str(job.get("id")))
        id_without_code=match.group(1)  # Output: 200609565
        item={"jobId":str(job.get("id")),
              "title":job.get("postingTitle"),
              "url":"https://jobs.apple.com/en-us/details/"+str(job.get("id")),
              "detected":detected_time
              }
        items[item.get("jobId")]=item
        print(item)
    return items


async def extractor():
    url = "https://jobs.apple.com/api/v1/search"
    payload = json.dumps({
      "query": "Software Engineer",
      "filters": {
        "locations": [
          "postLocation-USA"
        ]
      },
      "page": 1,
      "locale": "en-us",
      "sort": "newest",
      "format": {
        "longDate": "MMMM D, YYYY",
        "mediumDate": "MMM D, YYYY"
      }
    })
    headers = {
      'Content-Type': 'application/json',
      'Cookie': 'jobs=ee033c8a1751152e4f575a3dc86470ca; AWSALBAPP-0=AAAAAAAAAAB6GF24SlLuoDJvfkWbHe3RCZvP61I+/OrTmyhDYMaXp2ONWwdwHM/qE8rn52txEPRztzmREBWFMx6b1mqYWSYHzEdYlC94UQ/G3yKwUL+qVqw6igmCzlHbnX+SQmicjzzpYVY=; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; jssid=s%3AgD_pygnTOWq1Fe1t0wzgiuyX6MZCQT7E.AYXd5tEKYRrGgFgxrsyGqPl8JqaOV%2B0of1o2LVGUhnA'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get("res").get("searchResults")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                match = re.search(r'-(.*)', str(job.get("id")))
                id_without_code=match.group(1)  # Output: 200609565
                item={"jobId":str(job.get("id")),
                      "title":job.get("postingTitle"),
                      "url":"https://jobs.apple.com/en-us/details/"+str(job.get("id")),
                      "detected":detected_time
                      }
                items[item.get("jobId")]=item
            return items

#Aggregate
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
    #main(current_jobs)
