import requests
import httpx
from selectolax.parser import HTMLParser
import helper
def extractor():
    url="https://careers.nutanix.com/en/jobs/?search=Software+Engineer&country=United+States&pagesize=20#results"
    headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"}
    resp=httpx.get(url,headers=headers)
    html=HTMLParser(resp.text)
    search_results=html.css("div.card-body")
    items={}
    for search_result in search_results:
        item={"title":search_result.css_first("h3").text(),
              "link":"https://careers.nutanix.com/"+search_result.css_first("a").attributes["href"],
            "id":search_result.css("li.list-inline-item")[2].text().strip().replace(" ", "")
              }
        items[item["id"]]=item
    return items
        #print(search_result.css("li.list-inline-item")[2].text())


def get_new(test=False):
    new_job_data=extractor()
    old_job_data=helper.load_json("Nutanix_jobs_list")
    brand_new_jobs=[]

    for job in new_job_data.keys():
        if job not in old_job_data:
            brand_new_jobs.append(job)
    if not test:
        helper.download_json(new_job_data,"nutanix_jobs_list")
    print("total", len(brand_new_jobs),"new jobs")
    #if brand_new_jobs:
        #send_email()

if __name__=="__main__":
    get_new(True)
