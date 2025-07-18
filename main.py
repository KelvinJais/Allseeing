import importlib
import os
from helper import emailing
import time
import asyncio

COMPANY_FOLDER = "companies"

def get_all_new_jobs(test):
    any_new_job=False
    jobs = {}
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            jobs[company_name]= module.main(test)
            if jobs[company_name]:
                any_new_job=True
    return jobs,any_new_job

def old_main(test=False,user="private"):
    all_jobs,any_new_job =  get_all_new_jobs(test)
    if any_new_job:
        emailing.send_email(all_jobs,user)

async def main(test=False,user="private"):
    any_new_job=False
    jobs = {}
    tasks=[]
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py" :
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            tasks.append(module.extractor())
    current_jobs=await asyncio.gather(*tasks)
    i=0
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py" :
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            jobs[company_name]= module.main(current_jobs[i])
            i+=1
            if jobs[company_name]:
                any_new_job=True
    if any_new_job:
        emailing.send_email(jobs,user)

if __name__ == "__main__":
    #without async 8.8 seconds
    #with async 1.2 seconds bruh!!!!
    #total time saved with async is from 20 seconds to 7 seconds!!!!
    asyncio.run(main())


