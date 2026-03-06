from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url="https://amazon.jobs/en/search.json?normalized_country_code%5B%5D=USA&radius=24km&industry_experience[]=less_than_1_year&facets%5B%5D=normalized_country_code&facets%5B%5D=normalized_state_name&facets%5B%5D=normalized_city_name&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&facets%5B%5D=is_manager&facets%5B%5D=is_intern&offset=0&result_limit=40&sort=recent&latitude=&longitude=&loc_group_id=&loc_query=&base_query=software%20engineer&city=&country=&region=&county=&query_options=&"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            jobs=await response.json()
            all_jobs={}
            detected_time = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
            for job in jobs['jobs']:
                item = ensure_job(_COMPANY, {
                    'jobId': job.get('id'),
                    'url': "https://amazon.jobs"+job.get('job_path'),
                    'title': job.get('title'),
                    'updated_time': job.get('updated_time'),
                    'posted_date': job.get('posted_date'),
                    "detected": detected_time
                })
                all_jobs[item['jobId']] = item
            return all_jobs


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
