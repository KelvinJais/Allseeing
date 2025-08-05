from re import search
from datetime import datetime,timezone
import httpx
from selectolax.parser import HTMLParser
from helper import load_download
import os
import asyncio
import aiohttp

async def extractor():
    import requests
    url = "https://careers.walmart.com/api/search?q=Software%20Engineer&page=1&sort=date&expand=department,brand,type,rate&jobCareerArea=all&type=jobs"

    payload = {}
    headers = {
      'Cookie': 'walcar.ab=fab065a8-cfbf-4b40-92ca-57ab710b3a8e'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data=await response.text()
            html=HTMLParser(data)
            search_results=html.css("ul#search-results li")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                title=search_result.css_first("div h4").text()
                url=search_result.css_first("div h4 a").attrs["href"]
                jobId=url #using url as jobid
                posted_date=search_result.css("div")[1].css("span")[1].text()
                item={"title":title,
                      "url":url,
                    "jobId":jobId,
                    "posted_date":posted_date,
                    "detected":detected_time
                      }
                items[item["jobId"]]=item
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
