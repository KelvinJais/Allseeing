import httpx
from datetime import datetime,timezone
from selectolax.parser import HTMLParser
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://www.google.com/about/careers/applications/jobs/results/?q=%22Software%20Engineer%22&location=United%20States&target_level=MID&target_level=EARLY"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            html = HTMLParser(data)
            search_results = html.css("li.lLd3Je")  # each job posting
            
            items = {}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                title_tag = search_result.css_first("h3.QJPWVe")
                link_tag = search_result.css_first("a[aria-label^='Learn more about']")
                job_id = search_result.attributes.get("jsdata", "")
                
                if title_tag and link_tag:
                    item = ensure_job(_COMPANY, {
                        "title": title_tag.text(),
                        "url": "https://www.google.com/about/careers/applications/" + link_tag.attributes["href"],
                        "jobId": "https://www.google.com/about/careers/applications/" + link_tag.attributes["href"],
                        "detected": detected_time
                    })
                    items[item["jobId"]] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
