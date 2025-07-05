from helper import load_download
import requests
import json
import os

def extractor():
    url = "https://www.metacareers.com/graphql"

    payload = 'av=0&__user=0&__a=1&__req=2&__hs=20273.BP%3ADEFAULT.2.0...0&dpr=2&__ccg=EXCELLENT&__rev=1024461766&__s=nv5zyy%3Ah1us9v%3A1jakyd&__hsi=7523374642259300045&__dyn=7xeUmwkHg7ebwKBAg5S1Dxu13wqovzEdEc8uxa1twKzobo1nEhwem0nCq1ewcG0RU2Cwooa81VohwnU14E9k2C0sy0H82NxCawcK1iwmE2ewnE2Lw6OyES4E3PwbS1Lwqo3cwbq0x84C0hi1TwmUpwto5a&__hsdp=gTEbMEOUWjUm58_xkwx193SO1m3G3PK48CF8S5VEa81cpUR02yE11o0wR3Q5XxZ0_o3Oo8o3Yc1fxSz3k2i1Hw1eK&__hblp=0Vwau14whE1RU7u0gO0wU3Dw10u2u0my0PE1wU4-1Ow3rE08280c883Ww3yFpUKqE8UhK4ETjG06_88E2zwrVo0Eq&lsd=AVpxMo8xXtY&jazoest=21040&__spin_r=1024461766&__spin_b=trunk&__spin_t=1751672160&__jssesw=1&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=CareersJobSearchResultsDataQuery&variables=%7B%22search_input%22%3A%7B%22q%22%3A%22software%20engineer%22%2C%22divisions%22%3A%5B%5D%2C%22offices%22%3A%5B%22Menlo%20Park%2C%20CA%22%2C%22Seattle%2C%20WA%22%2C%22New%20York%2C%20NY%22%2C%22Ashburn%2C%20VA%22%2C%22Austin%2C%20TX%22%2C%22Bellevue%2C%20WA%22%2C%22Boston%2C%20MA%22%2C%22Cambridge%2C%20MA%22%2C%22Chicago%2C%20IL%22%2C%22Denver%2C%20CO%22%2C%22Detroit%2C%20MI%22%2C%22Forest%20City%2C%20NC%22%2C%22Fort%20Worth%2C%20TX%22%2C%22Foster%20City%2C%20CA%22%2C%22Fremont%2C%20CA%22%2C%22Henrico%2C%20VA%22%2C%22Eagle%20Mountain%2C%20UT%22%2C%22Houston%2C%20TX%22%2C%22Irvine%2C%20CA%22%2C%22Kansas%20City%2C%20MO%22%2C%22Los%20Angeles%2C%20CA%22%2C%22Mountain%20View%2C%20CA%22%2C%22New%20Albany%2C%20OH%22%2C%22Newark%2C%20CA%22%2C%22Pittsburgh%2C%20PA%22%2C%22Redmond%2C%20WA%22%2C%22Remote%2C%20US%22%2C%22Rosemount%2C%20MN%22%2C%22Salt%20Lake%2C%20UT%22%2C%22San%20Diego%2C%20CA%22%2C%22San%20Francisco%2C%20CA%22%2C%22San%20Mateo%2C%20CA%22%2C%22Sandston%2C%20VA%22%2C%22Santa%20Clara%2C%20CA%22%2C%22Sarpy%20County%2C%20NE%22%2C%22Sunnyvale%2C%20CA%22%5D%2C%22roles%22%3A%5B%5D%2C%22leadership_levels%22%3A%5B%5D%2C%22saved_jobs%22%3A%5B%5D%2C%22saved_searches%22%3A%5B%5D%2C%22sub_teams%22%3A%5B%5D%2C%22teams%22%3A%5B%5D%2C%22is_leadership%22%3Afalse%2C%22is_remote_only%22%3Afalse%2C%22sort_by_new%22%3Atrue%2C%22results_per_page%22%3Anull%7D%7D&server_timestamps=true&doc_id=29615178951461218'
    headers = {
      'accept': '*/*',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'cache-control': 'no-cache',
      'content-type': 'application/x-www-form-urlencoded',
      'origin': 'https://www.metacareers.com',
      'pragma': 'no-cache',
      'priority': 'u=1, i',
      'referer': 'https://www.metacareers.com/jobs?q=software%20engineer&sort_by_new=true&offices[0]=Menlo%20Park%2C%20CA&offices[1]=Seattle%2C%20WA&offices[2]=New%20York%2C%20NY&offices[3]=Ashburn%2C%20VA&offices[4]=Austin%2C%20TX&offices[5]=Bellevue%2C%20WA&offices[6]=Boston%2C%20MA&offices[7]=Cambridge%2C%20MA&offices[8]=Chicago%2C%20IL&offices[9]=Denver%2C%20CO&offices[10]=Detroit%2C%20MI&offices[11]=Forest%20City%2C%20NC&offices[12]=Fort%20Worth%2C%20TX&offices[13]=Foster%20City%2C%20CA&offices[14]=Fremont%2C%20CA&offices[15]=Henrico%2C%20VA&offices[16]=Eagle%20Mountain%2C%20UT&offices[17]=Houston%2C%20TX&offices[18]=Irvine%2C%20CA&offices[19]=Kansas%20City%2C%20MO&offices[20]=Los%20Angeles%2C%20CA&offices[21]=Mountain%20View%2C%20CA&offices[22]=New%20Albany%2C%20OH&offices[23]=Newark%2C%20CA&offices[24]=Pittsburgh%2C%20PA&offices[25]=Redmond%2C%20WA&offices[26]=Remote%2C%20US&offices[27]=Rosemount%2C%20MN&offices[28]=Salt%20Lake%2C%20UT&offices[29]=San%20Diego%2C%20CA&offices[30]=San%20Francisco%2C%20CA&offices[31]=San%20Mateo%2C%20CA&offices[32]=Sandston%2C%20VA&offices[33]=Santa%20Clara%2C%20CA&offices[34]=Sarpy%20County%2C%20NE&offices[35]=Sunnyvale%2C%20CA',
      'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
      'x-asbd-id': '359341',
      'x-fb-friendly-name': 'CareersJobSearchResultsDataQuery',
      'x-fb-lsd': 'AVpxMo8xXtY'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jobs=response.json().get('data').get('job_search_with_featured_jobs').get('all_jobs')
    items={}
    for job in jobs[:25]:  #only taking the first 20
        item={"jobId":job.get('id'),
              "title":job.get('title'),
              #"url":job.get("applyUrl")  meta has no url to it unfortunately
                                }
        items[job.get("id")]=item
    return items


def main(test=False):
    company_name=os.path.basename(__file__)[:-3]
    file_path=os.path.join("/tmp","data",f"{company_name}_jobs_list.json")
    if not os.path.exists(file_path):
        job_data=extractor()
        load_download.download_json(job_data,f"{company_name}_jobs_list")
        load_download.download_json(job_data,f"{company_name}_jobs_list_t_new_jobs")
    else:
        if test:
            new_job_data=load_download.load_json(f"{company_name}_jobs_list_t_new_jobs")
        else:
            new_job_data=extractor()
        old_job_data=load_download.load_json(f"{company_name}_jobs_list")
        brand_new_jobs=[]

        for job in new_job_data.keys():
            if job not in old_job_data:
                brand_new_jobs.append(new_job_data[job])
        if not test:
            load_download.download_json(new_job_data,f"{company_name}_jobs_list")
        print(len(brand_new_jobs),"new jobs at",company_name)
        return brand_new_jobs


if __name__ =="__main__":
    main()
