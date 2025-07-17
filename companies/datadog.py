from helper import load_download
import requests
import json
import os
import asyncio
import aiohttp

async def extractor():
    url = "https://gk6e3zbyuntvc5dap.a1.typesense.net/multi_search?x-typesense-api-key=1Hwq7hntXp211hKvRS3CSI2QSU7w2gFm"

    payload = "{\"searches\":[{\"preset\":\"careers_list_view\",\"collection\":\"careers_alias\",\"q\":\"software engineer\",\"facet_by\":\"child_department_Engineering,child_department_GeneralAdministrative,child_department_Marketing,child_department_Sales,child_department_TechnicalSolutions,location_APAC,location_Americas,location_EMEA,parent_department_Engineering,parent_department_GeneralAdministrative,parent_department_Marketing,parent_department_ProductDesign,parent_department_ProductManagement,parent_department_Sales,parent_department_TechnicalSolutions,region_APAC,region_Americas,region_EMEA,remote,time_type\",\"filter_by\":\"language: en && location_Americas:=[`Boston`,`California`,`Colorado`,`Massachusetts`,`New York`,`San Francisco`,`Washington`] && region_Americas:=[`Americas`] && time_type:=[`Experienced Hire`]\",\"max_facet_values\":50,\"page\":1,\"per_page\":10},{\"preset\":\"careers_list_view\",\"collection\":\"careers_alias\",\"q\":\"software engineer\",\"facet_by\":\"location_Americas\",\"filter_by\":\"language: en && region_Americas:=[`Americas`] && time_type:=[`Experienced Hire`]\",\"max_facet_values\":50,\"page\":1},{\"preset\":\"careers_list_view\",\"collection\":\"careers_alias\",\"q\":\"software engineer\",\"facet_by\":\"region_Americas\",\"filter_by\":\"language: en && location_Americas:=[`Boston`,`California`,`Colorado`,`Massachusetts`,`New York`,`San Francisco`,`Washington`] && time_type:=[`Experienced Hire`]\",\"max_facet_values\":50,\"page\":1},{\"preset\":\"careers_list_view\",\"collection\":\"careers_alias\",\"q\":\"software engineer\",\"facet_by\":\"time_type\",\"filter_by\":\"language: en && location_Americas:=[`Boston`,`California`,`Colorado`,`Massachusetts`,`New York`,`San Francisco`,`Washington`] && region_Americas:=[`Americas`]\",\"max_facet_values\":50,\"page\":1}]}"
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'cache-control': 'no-cache',
      'content-type': 'text/plain',
      'origin': 'https://careers.datadoghq.com',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://careers.datadoghq.com/',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'cross-site',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get('results')[1].get('hits')
            items={}
            for job in jobs:
                a_job=job.get('document')
                item={"jobId":a_job.get("id"), #data dog has id, job_id and internal_job_id 
                      "title":a_job.get("title"),
                      "url":a_job.get("absolute_url")
                                        }
                items[item.get("jobId")]=item

            return items

def main(current_jobs,test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
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


if __name__=="__main__":
    main()
