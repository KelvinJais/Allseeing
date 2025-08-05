from helper import load_download
from datetime import datetime,timezone
import requests
import json
import os
import asyncio
import aiohttp
async def extractor():
    url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=14,keyword=%22software%20engineer%22,lastSelectedFacet=AttributeChar6,selectedCategoriesFacet=300000001917356%3B300000001917350,selectedFlexFieldsFacets=%22AttributeChar6%7C0%20to%202%2B%20years%22,selectedLocationsFacet=300000000149325,selectedPostingDatesFacet=7,sortBy=RELEVANCY"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data=await response.json()
            jobs=data.get('items')[0].get('requisitionList')
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                item={"jobId":str(job.get("Id")),
                      "title":job.get("Title"),
                      "url":"https://careers.oracle.com/en/sites/jobsearch/job/"+str(job.get("Id")),
                    "detected":detected_time
                                        }
                items[str(item.get("jobId"))]=item
            return items

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
