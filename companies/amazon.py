import requests
from helper import load_download
import re
import os

def extractor():
    url="https://amazon.jobs/en/search.json?normalized_country_code%5B%5D=USA&radius=24km&industry_experience[]=less_than_1_year&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=40&sort=recent&latitude=&longitude=&loc_group_id=&loc_query=&base_query=software%20engineer&city=&country=&region=&county=&query_options=&"
    resp=requests.get(url)
    jobs=resp.json()
    all_jobs={}
    for job in jobs['jobs']:
        all_jobs[job.get('id')]={ 
            'jobId': job.get('id'),
            'url': "https://amazon.jobs"+job.get('job_path'),
            'title': job.get('title'),
            'updated_time': job.get('updated_time'),
            'posted_date': job.get('posted_date')
        }
    return all_jobs


def updated_time_converter(updated_time):
    match = re.search(r"(\d+\smonth)", updated_time)
    extracted_months = match.group(1) if match else None
    #days
    match = re.search(r"(\d+\sday)", updated_time)
    extracted_days= match.group(1) if match else None
    #hours
    match = re.search(r'(\d+\s*hour)', updated_time)
    extracted_hours = match.group(1) if match else None
    if extracted_months:
        match = re.search(r'\d+', extracted_months)
        number = int(match.group()) if match else None
        return ["month",number]
    if extracted_days:
        match = re.search(r'\d+', extracted_days)
        number = int(match.group()) if match else None
        return ["day",number]
    if extracted_hours:
        match = re.search(r'\d+', extracted_hours)
        number = int(match.group()) if match else None
        return ["hour",number]

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
            if job not in old_job_data.keys():
                brand_new_jobs.append(new_job_data[job])
            else:
                old_updated_time=updated_time_converter(old_job_data[job]['updated_time'])
                new_updated_time=updated_time_converter(new_job_data[job]['updated_time'])
                if new_updated_time[0]=="hour" and (old_updated_time[0]=="day" or old_updated_time[0]=="month"):
                    brand_new_jobs.append(new_job_data[job])
                elif new_updated_time[0]=="day" and old_updated_time[0]=="month":
                    brand_new_jobs.append(new_job_data[job])
                elif new_updated_time[0]==old_updated_time[0] and new_updated_time[1]<old_updated_time[1]:
                    brand_new_jobs.append(new_job_data[job])
        if not test:
            load_download.download_json(new_job_data,"amazon_jobs_list")
        print(len(brand_new_jobs),"new jobs at amazon")
        if test:
            for job in brand_new_jobs:
                print(job)
        return brand_new_jobs

if __name__=="__main__":
    main()
