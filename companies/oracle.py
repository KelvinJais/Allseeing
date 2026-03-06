from datetime import datetime, timezone
import os
import asyncio
import aiohttp
from schemas import ensure_job

_COMPANY = os.path.basename(__file__)[:-3]

async def extractor():
    url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=14,keyword=%22software%20engineer%22,lastSelectedFacet=AttributeChar6,selectedCategoriesFacet=300000001917356%3B300000001917350,selectedFlexFieldsFacets=%22AttributeChar6%7C0%20to%202%2B%20years%22,selectedLocationsFacet=300000000149325,selectedPostingDatesFacet=7,sortBy=RELEVANCY"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data=await response.json()
            jobs=data.get('items')[0].get('requisitionList')
            items={}
            detected_time=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            for job in jobs:
                item = ensure_job(_COMPANY, {
                    "jobId": str(job.get("Id")),
                    "title": job.get("Title"),
                    "url": "https://careers.oracle.com/en/sites/jobsearch/job/"+str(job.get("Id")),
                    "detected": detected_time
                })
                items[item.get("jobId")] = item
            return items


if __name__ == "__main__":
    from helper import job_state
    current_jobs = asyncio.run(extractor())
    job_state.diff_and_persist(_COMPANY, current_jobs)
