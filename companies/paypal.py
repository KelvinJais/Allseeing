import requests
import os
from helper import load_download
import json
import time
import asyncio
import aiohttp


async def get_page(session, url, headers, payload):
    async with session.get(url, headers=headers, data=payload) as response:
        return await response.json()

async def get_all_pages(session,url,pages,headers,payload):
    tasks=[]
    for page in pages:
        task=asyncio.create_task(get_page(session,url.format(page*10),headers,payload))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def extractor():
    url ="https://paypal.eightfold.ai/api/pcsx/search?domain=paypal.com&query=software%20engineer%201&location=united%20states&start={}&sort_by=solr&"
    payload = {}
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'cache-control': 'no-cache',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://paypal.eightfold.ai/careers?query=software+engineer+1&start=0&location=united+states&pid=274907848527&sort_by=solr&filter_include_remote=1',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
      'x-csrf-token': 'ImMyMjBiMDVhMWQ5YWYzNmI3ZTdmM2E3YzVmMDVmMTEzM2NiMmMwYzEi.G0rv-w.NnOrOOCDOSHZQ70lR0TR57-bPS4',
      'Cookie': '_vs=4749559566357125838:1751735557.7193546:246203503074128067; _vscid=0'
    }

    async with aiohttp.ClientSession() as session:
        pages=range(6)
        responses=await get_all_pages(session,url,pages,headers,payload)
    jobs=[]
    for response in responses:
        jobs.extend(response.get('data').get('positions'))
    #response= requests.request("GET", url.format(0), headers=headers, data=payload)
    #jobs=response.json().get('data').get('positions')
    '''
    jobs=[]
    tasks=[]
    for i in range(6):#getting first 6 pages
        url =f"https://paypal.eightfold.ai/api/pcsx/search?domain=paypal.com&query=software%20engineer%201&location=united%20states&start={i*10}&sort_by=solr&"
        tasks.append(requests.request("GET", url, headers=headers, data=payload))
        #response= requests.request("GET", url, headers=headers, data=payload)
        #jobs.extend(response.json().get('data').get('positions'))
    responses=await asyncio.gather(*tasks)
    for response in responses:
        jobs.extend(response.json().get('data').get('positions'))
    '''
    items={}
    for job in jobs:
        item={"jobId":str(job.get("id")),
              "displayId":str(job.get("displayJobId")),
              "title":job.get("name"),
              "url":"https://paypal.eightfold.ai"+job.get("positionUrl")
                                }
        items[str(job.get("id"))]=item
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
                #old_job_data.append(new_job_data[job]) For Aggregating
        if not test:
            load_download.download_json(new_job_data,f"{company_name}_jobs_list")
            #load_download.download_json(old_job_data,f"{company_name}_jobs_list")
        print(len(brand_new_jobs),"new jobs at",company_name)
        return brand_new_jobs


if __name__=="__main__":
    current_jobs=asyncio.run(extractor())
    main(current_jobs)


