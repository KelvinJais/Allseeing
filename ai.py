import requests
def get_career_url(company):
    API_KEY = "AIzaSyDltkatU5575gTr175cYAYKduiaUvGGOuo"
    CX = "a2779d9bf5e19454a"
    query = f"{company} search jobs careers"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": 1,   # number of results (max 10 per request)
    }

    resp = requests.get(url, params=params)
    data = resp.json()


    items=data.get("items", [])
    if items:
        return (items[0]["link"])
    else:
        print("No results")
    #todo add branching to workday


import time
import json
import re

def network_details(url):
    """
    Opens the given URL in a headless browser and captures all network requests.
    Prints out URLs of any requests with a JSON response.
    """
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)
    driver.scopes = ['.*']  # capture everything

    try:
        driver.get(url)
        time.sleep(3)  # allow requests to be performed

        seen = set()
        print(f"Network requests returning JSON for {url}:\n")
    # For each network request with response as JSON, send URL/summary to LLM to classify if it's a job search API endpoint.
        import requests as pyrequests

        def is_likely_job_api(url ):
            """
            Use Ollama LLM to classify if this endpoint is likely a job search API.
            """
            ollama_url = "http://localhost:11434/api/generate"
            prompt = (
                "You are an expert software engineer. Given the following information, "
                "determine if the URL is an API endpoint serving job search results OR job listings. "
                "Return only 'yes' or 'no'.\n\n"
                f"URL: {url}\n"
            )
            data = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            try:
                res = pyrequests.post(ollama_url, json=data, timeout=15)
                if res.ok:
                    answer = res.json()["response"].strip().lower()
                    return answer.startswith("yes")
            except Exception as e:
                print(f"Ollama error: {e}")
            return False
        json_request=[]

        for request in driver.requests:
            # Check if request body is JSON
            is_json_body = False
            if request.response and request.response.headers:
                content_type = request.response.headers.get('Content-Type', '')
            else:
                continue
            if 'application/json' in content_type.lower():
                is_json_body = True
            if is_json_body:
                json_request.append(request)
                print(request.url)
                is_job_api=is_likely_job_api(request.url)
                print("yes" if is_job_api else "no")

    finally:
        driver.quit()

from seleniumwire import webdriver
import time
import json
import pandas as pd
from datetime import datetime
import gzip

def get_job_api(url):
    """
    Given a job board website url, return the api endpoint that serves job listings.
    if no api endpoint is found, return False
    Also saves the URL and JSON response to an Excel file.
    """
    # Set selenium-wire options if needed
    options = {
        'request_storage': 'memory',
        'request_storage_max_size': 1000
    }

    driver = webdriver.Chrome()
    driver.get(url)
    # Allow some time for the page to load and requests to fire
    time.sleep(7)

    json_endpoints = []
    json_data = []  # Store URL and JSON response pairs

    for request in driver.requests:
        try:
            if request.response:
                content_type = request.response.headers.get('Content-Type', '')
                if 'application/json' in content_type.lower():
                    print(f"JSON endpoint: {request.url}")
                    json_endpoints.append(request.url)
                    
                    # Get the JSON response body
                    try:
                        response_body = request.response.body
                        if response_body:
                            # Check if response is compressed
                            content_encoding = request.response.headers.get('Content-Encoding', '').lower()
                            
                            if isinstance(response_body, bytes):
                                # Handle gzip compression
                                if 'gzip' in content_encoding or (len(response_body) > 2 and response_body[:2] == b'\x1f\x8b'):
                                    try:
                                        response_body = gzip.decompress(response_body)
                                    except Exception as e:
                                        print(f"Warning: Failed to decompress gzip for {request.url}: {e}")
                                
                                # Decode the response body
                                try:
                                    response_text = response_body.decode('utf-8')
                                except UnicodeDecodeError:
                                    # Try other encodings if UTF-8 fails
                                    try:
                                        response_text = response_body.decode('latin-1')
                                    except Exception as e:
                                        print(f"Warning: Failed to decode response for {request.url}: {e}")
                                        response_text = str(response_body)
                            else:
                                response_text = str(response_body)
                            
                            # Try to parse as JSON
                            try:
                                json_response = json.loads(response_text)
                                json_str = json.dumps(json_response, indent=2)
                            except json.JSONDecodeError:
                                json_str = response_text
                            
                            json_data.append({
                                'URL': request.url,
                                'JSON Response': json_str
                            })
                    except Exception as e:
                        print(f"Error reading response body for {request.url}: {e}")
                        json_data.append({
                            'URL': request.url,
                            'JSON Response': f'Error: {str(e)}'
                        })
        except Exception as e:
            print(f"Error processing request: {e}")

    driver.quit()
    
    # Save to Excel file if we have data
    if json_data:
        df = pd.DataFrame(json_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_api_responses_{timestamp}.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Saved {len(json_data)} JSON responses to {filename}")
    
    if json_endpoints:
        return json_endpoints
    return False

if __name__=="__main__":
    company="blackrock"
    #career_url=get_career_url(company)
    #career_url="https://careers.blackrock.com/search-jobs"
    #amazon="https://www.amazon.jobs/en/search"
    #network_details(amazon)
    career_url="https://hex.tech/careers/"
    job_api=get_job_api(career_url)
    
    