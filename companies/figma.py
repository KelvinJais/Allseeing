from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data=await response.json()
            jobs=data.get("jobs")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                if job.get('departments')[0].get('name') in ('Engineering'):
                    item = ensure_job(_COMPANY, {
                        "jobId": str(job.get("id")),
                        "title": job.get("title"),
                        "url": job.get("absolute_url"),
                        "detected": detected_time
                    })
                    items[item.get("jobId")] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
