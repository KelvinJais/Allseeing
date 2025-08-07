from helper import load_download
from datetime import datetime, timezone
import requests
import json
import os
import asyncio
import aiohttp

async def extractor():
    #print(f"Initiate {os.path.basename(__file__)[:-3]} extraction")
    url = "https://careers.adobe.com/widgets"
    payload = json.dumps({
      "lang": "en_us",
      "deviceType": "desktop",
      "country": "us",
      "pageName": "search-results",
      "ddoKey": "refineSearch",
      "sortBy": "Most recent",
      "subsearch": "",
      "from": 0,
      "jobs": True,
      "counts": True,
      "all_fields": [
        "remote",
        "country",
        "state",
        "city",
        "experienceLevel",
        "category",
        "profession",
        "employmentType",
        "jobLevel"
      ],
      "size": 10,
      "clearAll": False,
      "jdsource": "facets",
      "isSliderEnable": False,
      "pageId": "page15-ds",
      "siteType": "external",
      "keywords": "Software%20Engineer",
      "global": True,
      "selected_fields": {
        "country": [
          "United States of America"
        ]
      },
      "sort": {
        "order": "desc",
        "field": "postedDate"
      },
      "locationData": {}
    })
    headers = {
      'Content-Type': 'application/json',
      'Cookie': 'PHPPPE_ACT=51ba89ed-092f-4591-8922-e6a997ef134e; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7IkpTRVNTSU9OSUQiOiI1MWJhODllZC0wOTJmLTQ1OTEtODkyMi1lNmE5OTdlZjEzNGUifSwibmJmIjoxNzU0NDExMDc3LCJpYXQiOjE3NTQ0MTEwNzd9.xmMG2tfFTAmTxkHVw2OsRgi91E5qKNUuGm-Ao1n5guU; jwtToken=eyJhbGciOiJIUzI1NiJ9.eyJMb2dvdXRVcmwiOiIiLCJpc3MiOiJhdXRoMCIsInNlc3Npb25JZCI6IjUxYmE4OWVkLTA5MmYtNDU5MS04OTIyLWU2YTk5N2VmMTM0ZSIsInVzZXJJZCI6Ijc5MDM1YmM2NjgzMTQwNTM4YzJjYzY2NjNkNWRjZGE0IiwidXNlclN1YlR5cGUiOiIiLCJzb2NpYWxBY2NvdW50cyI6IiIsInVzZXJQcm9maWxlVHlwZSI6IiIsInVpZCI6IiIsImlzQW5vbnltb3VzIjp0cnVlLCJTZXNzaW9uRXhwaXJlVXJsIjoiIiwiaXNTb2NpYWxMb2dpbiI6ZmFsc2UsInNvY2lhbElkIjoiIiwidXNlclR5cGUiOiJleHRlcm5hbCIsImV4cCI6MTc1NzAwMzA4OSwic29jaWFsUHJvdmlkZXIiOiIiLCJpYXQiOjE3NTQ0MTEwODksImlzU2l0ZUxvZ2luIjpmYWxzZSwic2l0ZVR5cGUiOiJleHRlcm5hbCJ9.AmPIOgjXZl9ga6hG6uV7lLdJrgUzsw6DSgpCDtbLU7Y'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get("refineSearch").get("data").get("jobs")
            items={}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
            for job in jobs:
                item={"jobId":str(job.get("jobId")),
                      "title":job.get("title"),
                      "url":"https://careers.adobe.com/us/en/search-results?keywords="+str(job.get("jobId")),
                      "detected": detected_time
                        }
                items[item.get("jobId")]=item
                print(item)
           # print(f"{os.path.basename(__file__)[:-3]} extraction complete")
            return items

#Aggregation
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
