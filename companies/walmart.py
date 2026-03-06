from re import search
from datetime import datetime,timezone
import httpx
from selectolax.parser import HTMLParser
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://careers.walmart.com/api/search?q=Software%20Engineer&page=1&sort=date&expand=department,brand,type,rate&jobCareerArea=all&type=jobs"

    payload = {}
    headers = {
      'Cookie': 'walcar.ab=fab065a8-cfbf-4b40-92ca-57ab710b3a8e'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, data=payload) as response:
            data=await response.text()
            html=HTMLParser(data)
            search_results=html.css("ul#search-results li")
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                title = search_result.css_first("div h4").text()
                url = search_result.css_first("div h4 a").attrs["href"]
                jobId = url
                posted_date = search_result.css("div")[1].css("span")[1].text()
                item = ensure_job(_COMPANY, {
                    "title": title,
                    "url": url,
                    "jobId": jobId,
                    "posted_date": posted_date,
                    "detected": detected_time
                })
                items[item["jobId"]] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
