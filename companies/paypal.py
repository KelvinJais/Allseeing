import requests
from datetime import datetime,timezone
import os
import json
import time
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]


async def get_page(session, url, headers, payload):
    async with session.get(url, headers=headers, data=payload) as response:
        return await response.json()

async def get_all_pages(session,url,pages,headers,payload):
    tasks=[]
    for page in pages:
        task=asyncio.create_task(get_page(session,url.format(page*10),headers,payload))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def extractor():
    url ="https://paypal.eightfold.ai/api/pcsx/search?domain=paypal.com&query=software%20engineer%201&location=united%20states&start={}&sort_by=solr&"
    payload = {}
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'cache-control': 'no-cache',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://paypal.eightfold.ai/careers?query=software+engineer+1&start=0&location=united+states&pid=274907848527&sort_by=solr&filter_include_remote=1',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
      'x-csrf-token': 'ImMyMjBiMDVhMWQ5YWYzNmI3ZTdmM2E3YzVmMDVmMTEzM2NiMmMwYzEi.G0rv-w.NnOrOOCDOSHZQ70lR0TR57-bPS4',
      'Cookie': '_vs=4749559566357125838:1751735557.7193546:246203503074128067; _vscid=0'
    }
    headers={}

    async with aiohttp.ClientSession() as session:
        pages=range(6)
        responses=await get_all_pages(session,url,pages,headers,payload)
    jobs=[]
    for response in responses:
        jobs.extend(response.get('data').get('positions'))
    items={}
    detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    for job in jobs:
        item = ensure_job(_COMPANY, {
            "jobId": str(job.get("id")),
            "title": job.get("name"),
            "url": "https://paypal.eightfold.ai"+job.get("positionUrl"),
            "detected": detected_time
        })
        items[item.get("jobId")] = item
    return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)


