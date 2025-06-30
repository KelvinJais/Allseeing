import importlib
import os
from helper import email

COMPANY_FOLDER = "companies"

def get_all_new_jobs():
    jobs = {}
    for filename in os.listdir(COMPANY_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            company_name = filename[:-3]  # Remove '.py'
            full_module_name = f"{COMPANY_FOLDER}.{company_name}"
            module = importlib.import_module(full_module_name)
            jobs[company_name]=module.main(True)
    return jobs

if __name__ == "__main__":

    all_jobs = get_all_new_jobs()
    email.send_email(all_jobs)

