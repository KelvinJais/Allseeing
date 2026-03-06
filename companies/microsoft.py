from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=software%20engineer&location=United%20States&start=0&filter_seniority=Entry&sort_by=timestamp"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data= await response.json()
            jobs=data.get("data").get("positions")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            print(len(jobs),"jobs found")
            for job in jobs:
                item = ensure_job(_COMPANY, {
                    "jobId": str(job.get("id")),
                    "title": job.get("name"),
                    "url": "https://apply.careers.microsoft.com"+str(job.get("positionUrl")),
                    "detected": detected_time
                })
                items[item.get("jobId")] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)