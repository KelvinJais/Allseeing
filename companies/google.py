import httpx
from datetime import datetime,timezone
from selectolax.parser import HTMLParser
from helper import load_download
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://www.google.com/about/careers/applications/jobs/results/?q=%22Software%20Engineer%22&location=United%20States&target_level=MID&target_level=EARLY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            html = HTMLParser(data)
            search_results = html.css("li.lLd3Je")  # each job posting
            
            items = {}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                title_tag = search_result.css_first("h3.QJPWVe")
                link_tag = search_result.css_first("a[aria-label^='Learn more about']")
                job_id = search_result.attributes.get("jsdata", "")
                
                if title_tag and link_tag:
                    item = {
                        "title": title_tag.text(),
                        "url": "https://www.google.com" + link_tag.attributes["href"],
                        "jobId":"https://www.google.com" + link_tag.attributes["href"],
                        "detected": detected_time
                    }
                    items[item["jobId"]] = item
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
