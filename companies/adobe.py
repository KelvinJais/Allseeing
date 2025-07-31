from helper import load_download
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
      "sortBy": "",
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
        ],
        "experienceLevel": [
          "University Graduate"
        ]
      },
      "locationData": {}
    })
    headers = {
      'content-type': 'application/json',
      'Cookie': 'PHPPPE_ACT=30428e4b-032d-4014-8da9-b494b2a3a07d; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7IkpTRVNTSU9OSUQiOiIzMDQyOGU0Yi0wMzJkLTQwMTQtOGRhOS1iNDk0YjJhM2EwN2QifSwibmJmIjoxNzUwOTA0ODU5LCJpYXQiOjE3NTA5MDQ4NTl9.nofH8dsSCaPnJBT5XtxmcbJFmtRQR5TXwVayLH71qH4'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get("refineSearch").get("data").get("jobs")
            items={}
            for job in jobs:
                item={"jobId":str(job.get("jobId")),
                      "title":job.get("title"),
                      "url":job.get("applyUrl")
                        }
                items[item.get("jobId")]=item

           # print(f"{os.path.basename(__file__)[:-3]} extraction complete")
            return items

def main(current_jobs,test=False):
    # Getting Company name from the file name
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    #Initializing files
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


if __name__ =="__main__":
    current_jobs=asyncio.run(extractor())
    main(current_jobs)
