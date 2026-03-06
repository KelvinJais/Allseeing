from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://api.greenhouse.io/v1/boards/discord/jobs?content=true"

    payload = {}
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Referer': 'https://discord.com/',
      'Origin': 'https://discord.com',
      'Sec-GPC': '1',
      'Connection': 'keep-alive',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'cross-site',
      'Priority': 'u=4',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache',
      'TE': 'trailers'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data = await response.json()
            jobs=data.get('jobs')
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                if job.get('departments')[0].get('name') in ("Product Engineering","Developers","Data Platform","Core Tech Engineering", "Data Science & Engineering"):
                    item = ensure_job(_COMPANY, {
                        "jobId": str(job.get("id")),
                        "title": job.get("title"),
                        "url": job.get("absolute_url"),
                        "updated_time": job.get("updated_at"),
                        "detected": detected_time
                    })
                    items[item.get("jobId")] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)

