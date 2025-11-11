import requests
from datetime import datetime, timezone
from helper import load_download
import re
import os
import asyncio
import aiohttp

async def extractor():
    url="https://amazon.jobs/en/search.json?normalized_country_code%5B%5D=USA&radius=24km&industry_experience[]=less_than_1_year&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=40&sort=recent&latitude=&longitude=&loc_group_id=&loc_query=&base_query=software%20engineer&city=&country=&region=&county=&query_options=&"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            jobs=await response.json()
            all_jobs={}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
            for job in jobs['jobs']:
                all_jobs[job.get('id')]={ 
                    'jobId': job.get('id'),
                    'url': "https://amazon.jobs"+job.get('job_path'),
                    'title': job.get('title'),
                    'updated_time': job.get('updated_time'),
                    'posted_date': job.get('posted_date'),
                    "detected":detected_time
                }
            return all_jobs


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
                old_job_data[job]=new_job_data[job]
        if not test:
            #load_download.download_json(new_job_data,f"{company_name}_jobs_list")
            load_download.download_json(old_job_data,f"{company_name}_jobs_list")
        print(len(brand_new_jobs),"new jobs at",company_name)
        return brand_new_jobs


if __name__=="__main__":
    current_jobs=asyncio.run(extractor())
    main(current_jobs)
