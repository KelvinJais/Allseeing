import httpx
from datetime import datetime,timezone
from selectolax.parser import HTMLParser
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url="https://careers.nutanix.com/en/jobs/?search=Software+Engineer&country=United+States&pagesize=20#results"
    headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data=await response.text()
            html=HTMLParser(data)
            search_results=html.css("div.card-body")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                item = ensure_job(_COMPANY, {
                    "title": search_result.css_first("h3").text(),
                    "url": "https://careers.nutanix.com/"+search_result.css_first("a").attributes["href"],
                    "jobId": search_result.css("li.list-inline-item")[2].text().strip().replace(" ", ""),
                    "detected": detected_time
                })
                items[item["jobId"]] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
