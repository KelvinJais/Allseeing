import requests
from datetime import datetime,timezone
import json
import os
import time
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"
    payload = json.dumps({
      "appliedFacets": {
        "locationHierarchy1": [
          "2fcb99c455831013ea52fb338f2932d8"
        ],
        "workerSubType": [
          "ab40a98049581037a3ada55b087049b7"
        ]
      },
      "limit": 20,
      "offset": 0,
      "searchText": "Software+Engineer"
    })
    headers = {
      'accept': 'application/json',
      'accept-language': 'en-US',
      'cache-control': 'no-cache',
      'content-type': 'application/json',
      'origin': 'https://nvidia.wd5.myworkdayjobs.com',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/jobs?q=Software+Engineer&locationHierarchy1=2fcb99c455831013ea52fb338f2932d8&workerSubType=ab40a98049581037a3ada55b087049b7',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
      'x-calypso-csrf-token': '6cf60848-49c9-4d7b-8a45-73bced2509f2',
      'Cookie': 'PLAY_SESSION=8d5d8660808a94f58b7ffd62d7d0b90d076705f1-instance=vps-prod-max9cnjc.prod-vps.pr502.cust.pdx.wd; __cf_bm=NfIdieEtUomq5iB5tCtpucnUn6to3akTHRIVA3Sl5wE-1750796111-1.0.1.1-gjVr3Wl7GkEz6oxJmDOSOxG3LuCSMa0E9t64zBhU5ECnC_GnuXlC.xZWLwHHAVBfYdj1Bfr4uYJs8EiRWsXre8VH7XBAgKh3W37IbPgYeN8; __cflb=02DiuHJZe28xXz6hQKLf1exjNbMDM5uxf8UXrAjS7hD5n; _cfuvid=6h0HO1M407vdL1OC_59LGnHMaw53VYirohrQdfSHC3w-1750796111256-0.0.1.1-604800000; wd-browser-id=49586d05-997b-4713-a014-c15842638df2; wday_vps_cookie=3102514186.53810.0000'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs= data['jobPostings']
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                if job.get("title"):
                    item = ensure_job(_COMPANY, {
                        "jobId": job.get("bulletFields")[0],
                        "title": job.get("title"),
                        "url": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/"+job.get("externalPath"),
                        "detected": detected_time
                    })
                    items[item["jobId"]] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
