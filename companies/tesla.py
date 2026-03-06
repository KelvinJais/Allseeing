from re import search
import httpx
from datetime import datetime,timezone
from selectolax.parser import HTMLParser
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://www.tesla.com/careers/search/?region=5&site=US&query=Software%20Engineer&type=fulltime"  # <-- Replace with the page URL you are scraping
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print("Status code:", response.status)
            data = await response.text()
            html = HTMLParser(data)
            search_results = html.css("li.style_SearchListItem__WS-y8")
            items = {}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for search_result in search_results:
                # Job Title
                a_tag = search_result.css_first("a.style_TitleLink__PepSM")
                title = a_tag.text(strip=True)
                job_url = "https://www.tesla.com" + a_tag.attributes["href"]
                # Location
                location_tag = search_result.css_first("li.style_ListResultItemSublistLocation__dLo4G strong")
                location = location_tag.text(strip=True) if location_tag else ""

                # Department & Type (First <li> under sublist)
                sublist_lis = search_result.css("ul.style_ListResultItemSublist__LGJOs li")
                if sublist_lis:
                    details = sublist_lis[0].text(strip=True).split("・")
                    department = details[0].strip() if len(details) > 0 else ""
                    job_type = details[1].strip() if len(details) > 1 else ""
                else:
                    department, job_type = "", ""

                # Attempt to grab job ID from URL or fallback
                job_id = a_tag.attributes["href"].split('-')[-1] if "href" in a_tag.attributes else str(hash(title + location))
                item = ensure_job(_COMPANY, {
                    "title": title,
                    "url": job_url,
                    "location": location,
                    "jobId": job_id,
                    "detected": detected_time
                })
                items[item["jobId"]] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
