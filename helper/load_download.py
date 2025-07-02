import json
import os

def download_json(job_list,filename):
    # Save the job list to the JSON file with the timestamped name
    os.makedirs('/tmp/data', exist_ok=True)
    filename=os.path.join("/tmp","data",filename)
    absolute_path = os.path.abspath(filename)
    with open(f"{absolute_path}.json", 'w', encoding='utf-8') as f:   # Save the extracted data to a JSON file
        json.dump(job_list, f, ensure_ascii=False, indent=2)

def load_json(filename):
    os.makedirs('/tmp/data', exist_ok=True)
    filename=os.path.join("/tmp","data",filename)
    absolute_path = os.path.abspath(filename)
    with open(f"{absolute_path}.json", 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    return jobs_data




