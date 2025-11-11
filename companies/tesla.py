from re import search
import httpx
from datetime import datetime,timezone
from selectolax.parser import HTMLParser
from helper import load_download
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://www.tesla.com/careers/search/?region=5&site=US&query=Software%20Engineer&type=fulltime"  # <-- Replace with the page URL you are scraping
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print("Status code:", response.status)
            data = await response.text()
            html = HTMLParser(data)
            search_results = html.css("li.style_SearchListItem__WS-y8")
            items = {}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                # Job Title
                a_tag = search_result.css_first("a.style_TitleLink__PepSM")
                title = a_tag.text(strip=True)
                job_url = "yourcompany" + a_tag.attributes["href"]
                # Location
                location_tag = search_result.css_first("li.style_ListResultItemSublistLocation__dLo4G strong")
                location = location_tag.text(strip=True) if location_tag else ""

                # Department & Type (First <li> under sublist)
                sublist_lis = search_result.css("ul.style_ListResultItemSublist__LGJOs li")
                if sublist_lis:
                    details = sublist_lis[0].text(strip=True).split("・")
                    department = details[0].strip() if len(details) > 0 else ""
                    job_type = details[1].strip() if len(details) > 1 else ""
                else:
                    department, job_type = "", ""

                # Attempt to grab job ID from URL or fallback
                job_id = a_tag.attributes["href"].split('-')[-1] if "href" in a_tag.attributes else str(hash(title + location))
                item = {
                    "title": title,
                    "url": job_url,
                    "location": location,
                    "department": department,
                    "type": job_type,
                    "jobId": job_id,
                    "detected": detected_time
                }
                items[item["jobId"]] = item
                print(item)
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
   # main(current_jobs)
