from helper import load_download
import requests
import json
import os
def extractor():
    url = "https://gcsservices.careers.microsoft.com/search/api/v1/search?lc=United%20States&exp=Students%20and%20graduates&l=en_us&pg=1&pgSz=20&o=Relevance&flt=true"

    payload = {}
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'authorization': 'Bearer undefined',
      'cache-control': 'no-cache',
      'origin': 'https://jobs.careers.microsoft.com',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://jobs.careers.microsoft.com/',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-site',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
      'x-correlationid': 'b92982c6-6ae6-cb57-d6b4-373a45eed22c',
      'x-subcorrelationid': '9a6439bb-5982-5c14-cb55-f89042077866'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    jobs=response.json().get("operationResult").get("result").get("jobs")
    items={}
    for job in jobs:
        item={"jobId":job.get("jobId"),
              "title":job.get("title"),
              #"url":job.get("applyUrl") microsoft has no url

                                }
        items[job.get("jobId")]=item
    return items

def main(test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data=extractor()
        print("initializin files") 
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
    main(True)


