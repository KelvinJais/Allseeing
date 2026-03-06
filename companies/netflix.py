from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://explore.jobs.netflix.net/api/apply/v2/jobs?domain=netflix.com&microsite=netflix.com&start=0&num=10&exclude_pid=790304048633&query=Software%20Engineer&location=United%20States&pid=790304269505&domain=netflix.com&sort_by=new&microsite=netflix.com&triggerGoButton=false"

    payload = {}
    headers = {
      'Cookie': '_vs=7355042181395060895:1753813449.6980038:1413341020276280066; _vscid=2'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data=await response.json()
            jobs=data.get("positions")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                item = ensure_job(_COMPANY, {
                    "jobId": str(job.get("id")),
                    "title": job.get("name"),
                    "url": "https://explore.jobs.netflix.net/careers/search?pid="+str(job.get("id")),
                    "detected": detected_time
                })
                items[item.get("jobId")] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)

