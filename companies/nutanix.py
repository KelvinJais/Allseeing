import httpx
from selectolax.parser import HTMLParser
from helper import load_download
import os
import asyncio
import aiohttp

async def extractor():
    url="https://careers.nutanix.com/en/jobs/?search=Software+Engineer&country=United+States&pagesize=20#results"
    headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as response:
            data=await response.text()
            html=HTMLParser(data)
            search_results=html.css("div.card-body")
            items={}
            for search_result in search_results:
                item={"title":search_result.css_first("h3").text(),
                      "url":"https://careers.nutanix.com/"+search_result.css_first("a").attributes["href"],
                    "jobId":search_result.css("li.list-inline-item")[2].text().strip().replace(" ", "")
                      }
                items[item["jobId"]]=item
            return items
        #print(search_result.css("li.list-inline-item")[2].text())
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
