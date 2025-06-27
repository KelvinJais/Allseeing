import helper

import requests
import re
import json
from datetime import datetime
import smtplib
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
class Job:
    def __init__(self,id, job_path, title, updated_time, posted_date):
        self.id = id
        self.job_path =job_path
        self.title = title
        self.updated_time = updated_time
        self.posted_date = posted_date

    def __repr__(self):
        return (f"Job(title={self.title!r},id={self.id!r}, job_path={self.job_path!r}, "
                f"updated_time={self.updated_time!r}, posted_date={self.posted_date!r})")


def extract(url):
    resp=requests.get(url)
    jobs=resp.json()
    return jobs

def transform(jobs):
    job_list = []
    for job in jobs:
        job_info = {
            'id': job.get('id'),
            'job_path': "https://amazon.jobs"+job.get('job_path'),
            'title': job.get('title'),
            'updated_time': job.get('updated_time'),
            'posted_date': job.get('posted_date')
        }
        job_list.append(job_info)
    return job_list

def hashmap(jobs_data):
    jobs_hashmap = {}
    for job in jobs_data:
        job_obj = Job(
            id=job.get('id'),
            job_path=job.get('job_path'),
            title=job.get('title'),
            updated_time=job.get('updated_time'),
            posted_date=job.get('posted_date')
        )
        jobs_hashmap[job_obj.id] = job_obj
    return jobs_hashmap

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

def get_new_test(url):
    new_jobs_data=helper.load_json("Amazon_job_list_test")#testing
    old_jobs_data=helper.load_json("Amazon_job_list")#testing

    old_jobs_hashmap=hashmap(old_jobs_data)
    brand_new_jobs=[]
    for new_job in new_jobs_data:
        id=new_job.get('id')
        if id not in old_jobs_hashmap:
            brand_new_jobs.append(new_job)
        else:
            old_updated_time=updated_time_converter(old_jobs_hashmap[id].updated_time)
            new_updated_time=updated_time_converter(new_job.get('updated_time'))
            if new_updated_time[0]=="hour" and (old_updated_time[0]=="day" or old_updated_time[0]=="month"):
                brand_new_jobs.append(new_job)
            elif new_updated_time[0]=="day" and old_updated_time[0]=="month":
                brand_new_jobs.append(new_job)
            elif new_updated_time[0]==old_updated_time[0] and new_updated_time[1]<old_updated_time[1]:
                brand_new_jobs.append(new_job)
    #download_json(new_job_data) #new jobs
    print(len(brand_new_jobs))
    print(brand_new_jobs)
    if len(brand_new_jobs)>0:
        send_email(brand_new_jobs)

def get_new(url):
    jobs=extract(url)
    new_job_data=transform(jobs['jobs'])
    old_jobs_data=helper.load_json("Amazon_job_list")#testing

    old_jobs_hashmap=hashmap(old_jobs_data)
    brand_new_jobs=[]
    for new_job in new_job_data:
        id=new_job.get('id')
        if id not in old_jobs_hashmap:
            brand_new_jobs.append(new_job)
        else:
            old_updated_time=updated_time_converter(old_jobs_hashmap[id].updated_time)
            new_updated_time=updated_time_converter(new_job.get('updated_time'))
            if new_updated_time[0]=="hour" and (old_updated_time[0]=="day" or old_updated_time[0]=="month"):
                brand_new_jobs.append(new_job)
            elif new_updated_time[0]=="day" and old_updated_time[0]=="month":
                brand_new_jobs.append(new_job)
            elif new_updated_time[0]==old_updated_time[0] and new_updated_time[1]<old_updated_time[1]:
                brand_new_jobs.append(new_job)
    helper.download_json(new_job_data,"Amazon_job_list") #new jobs
    print("total", len(brand_new_jobs), "new jobs")
    if len(brand_new_jobs)>0:
        send_email(brand_new_jobs)

import creds

def format_job_listings_html(data):
    html = '''<html><body><h2>Amazon Job Listings</h2><hr>'''
    for job in data:
        html += f"""
        <div style='margin-bottom:20px;'>
            <h3 style='color:#2a7ae2;'>{job['title']}</h3>
            <p><strong>Posted Date:</strong> {job['posted_date']}</p>
            <p><strong>Last Updated:</strong> {job['updated_time']} ago</p>
            <p><a href='{job['job_path']}' style='color:#1a0dab;'>Apply Here</a></p>
            <hr>
        </div>
        """
    html += '</body></html>'
    return html

def send_email(jobs):
    html_content = format_job_listings_html(jobs)
    message = MIMEMultipart()
    message['Subject'] = "Amazon new Jobs"
    message['From'] ="kelvin4jaison@gmail.com"
    message['To'] ="kelvin4jaison@gmail.com"
    message.attach(MIMEText(html_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(creds.sender, creds.password)
        server.sendmail(creds.sender, creds.recipient, message.as_string())

def download_new(url):
    jobs=extract(url)
    job_list=transform(jobs['jobs'])
    helper.download_json(job_list,"Amazon_job_list")

if __name__=="__main__":
    url="https://amazon.jobs/en/search.json?normalized_country_code%5B%5D=USA&radius=24km&industry_experience[]=less_than_1_year&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=40&sort=recent&latitude=&longitude=&loc_group_id=&loc_query=&base_query=software%20engineer&city=&country=&region=&county=&query_options=&"
    #download_new(url)
    get_new(url)





