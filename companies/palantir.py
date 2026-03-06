from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://www.palantir.com/api/lever/v1/postings?state=published"
    payload = {}
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'cache-control': 'no-cache',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://www.palantir.com/careers/',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data=await response.json()
    jobs=data.get('data')
    items={}
    detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
    for job in jobs:
        tags = job.get('tags')
        for tag in tags:
            if tag == "Category:New Graduates":
                item = ensure_job(_COMPANY, {
                    "jobId": job.get("id"),
                    "title": job.get("text"),
                    "url": job.get("urls").get("apply"),
                    "detected": detected_time
                })
                items[item.get("jobId")] = item
                break
    return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
