import httpx
from selectolax.parser import HTMLParser
from helper import load_download
import os

def extractor():
    url="https://careers.walmart.com/results?q=Software%20Engineer&page=1&sort=date&expand=department,brand,type,rate&jobCareerArea=all"
    headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"}
    resp=httpx.get(url,headers=headers)
    html=HTMLParser(resp.text)
    search_results=html.css("div.job-listing__headline")
    print(search_results)
    items={}
    """
    for search_result in search_results:
        item={"title":search_result.css_first("h3").text(),
              "url":"https://careers.nutanix.com/"+search_result.css_first("a").attributes["href"],
            "jobId":search_result.css("li.list-inline-item")[2].text().strip().replace(" ", "")
              }
        items[item["jobId"]]=item
    return items
        #print(search_result.css("li.list-inline-item")[2].text())
        """
    return


if __name__=="__main__":
    extractor()



