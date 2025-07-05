import requests
import os
from helper import load_download
import json

def extractor():
    url = "https://paypal.eightfold.ai/api/pcsx/search?domain=paypal.com&query=software%20engineer%201&location=united%20states&start=0&sort_by=solr&"

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

    response = requests.request("GET", url, headers=headers, data=payload)
    jobs=response.json().get('data').get('positions')
    items={}
    for job in jobs:
        item={"jobId":str(job.get("id")),
              "displayId":str(job.get("displayJobId")),
              "title":job.get("name"),
              "url":"https://paypal.eightfold.ai"+job.get("positionUrl")
                                }
        items[str(job.get("id"))]=item
    return items

def main(test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data=extractor()
        load_download.download_json(job_data,f"{company_name}_jobs_list")
        load_download.download_json(job_data,f"{company_name}_jobs_list_t_new_jobs")
    else:
        if test:
            new_job_data=load_download.load_json(f"{company_name}_jobs_list_t_new_jobs")
        else:
            new_job_data=extractor()
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
    main()


