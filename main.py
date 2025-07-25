import importlib
import os
from helper import emailing
import time
import asyncio

COMPANY_FOLDER = "companies"

async def main(test=False,user="private"):
    '''
    The first for loop runs all the extractor functions asynchronous from all the companies in the company folder
    Second for loop runs all the main function from the companies in the main folder. the main function includes the logic of compaisions
    '''
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
            jobs[company_name]= module.main(current_jobs[i],test=test)
            i+=1
            if jobs[company_name]:
                any_new_job=True
    if any_new_job:
        emailing.send_email(jobs,user)

if __name__ == "__main__":
    asyncio.run(main())


