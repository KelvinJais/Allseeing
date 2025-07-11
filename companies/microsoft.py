from helper import load_download
import requests
import json
import os
def extractor():
    url = "https://gcsservices.careers.microsoft.com/search/api/v1/search?q=Software%20Engineer&lc=United%20States&exp=Students%20and%20graduates&l=en_us&pg=1&pgSz=20&o=Relevance&flt=true"
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
      'x-correlationid': 'e2f840d6-7794-091d-2393-778719e7c604',
      'x-subcorrelationid': '67e29667-8af7-6873-c650-f04803b8fe0e'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    jobs=response.json().get("operationResult").get("result").get("jobs")
    items={}
    for job in jobs:
        if str(job.get("jobId")) != "1774001":
            item={"jobId":str(job.get("jobId")),
                  "title":job.get("title"),
                  "url":"https://jobs.careers.microsoft.com/global/en/apply?Job_id="+str(job.get("jobId"))                                }
            items[item.get("jobId")]=item
    return items

def main(test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data=extractor()
        print("initializing files") 
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


