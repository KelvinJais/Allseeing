import helper
import requests
import json

def extractor():
    url = "https://careers.adobe.com/widgets"

    payload = json.dumps({
      "lang": "en_us",
      "deviceType": "desktop",
      "country": "us",
      "pageName": "search-results",
      "ddoKey": "refineSearch",
      "sortBy": "",
      "subsearch": "",
      "from": 0,
      "jobs": True,
      "counts": True,
      "all_fields": [
        "remote",
        "country",
        "state",
        "city",
        "experienceLevel",
        "category",
        "profession",
        "employmentType",
        "jobLevel"
      ],
      "size": 10,
      "clearAll": False,
      "jdsource": "facets",
      "isSliderEnable": False,
      "pageId": "page15-ds",
      "siteType": "external",
      "keywords": "Software%20Engineer",
      "global": True,
      "selected_fields": {
        "country": [
          "United States of America"
        ],
        "experienceLevel": [
          "University Graduate"
        ]
      },
      "locationData": {}
    })
    headers = {
      'content-type': 'application/json',
      'Cookie': 'PHPPPE_ACT=30428e4b-032d-4014-8da9-b494b2a3a07d; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7IkpTRVNTSU9OSUQiOiIzMDQyOGU0Yi0wMzJkLTQwMTQtOGRhOS1iNDk0YjJhM2EwN2QifSwibmJmIjoxNzUwOTA0ODU5LCJpYXQiOjE3NTA5MDQ4NTl9.nofH8dsSCaPnJBT5XtxmcbJFmtRQR5TXwVayLH71qH4'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jobs=response.json().get("refineSearch").get("data").get("jobs")# title jobId
    items={}
    for job in jobs:
        item={job.get("jobId"):{"title":job.get("id")}}


if __name__ =="__main__":
    extractor()
