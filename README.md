# All Seeing
This project is to help in job hunting. I was adviced to try to be the first few people to apply to a new postion. So I made this Python script. This script gets data from company job boards and check if there is a new job post, if there is then send an email about the new job. To make the most of this project I recommend you to deploy this to aws lambda and have AWS EventBridge run this script every hour or less.

## How to run this project
- Create a python virtual env. The package requirements are given in the requirements.txt
- A dockerfile is also included if you would like to use docker.
  
### Setting up email
- Since we are using email to let you know about job postings, please set up your email. The emailing function is located at helper/emailing.py. I use smtp.gmail.com to send my email. To set this up for yourself: Create a new google app password and save it to a secrets.json file with this format:

{
  "sender": your email,
  "password": your app password
}

-Additionally, change the recipient email of your choosing in the helper/emailing.py file
## Running
- Once you have completed setting up email functionality you can run the code by typing this in your terminal python -m main

## How to contribute
- To add a new company go to the folder companies and create a file in the format company_name.py
- The company_name.py file will have two function extractor() and main() add a if __name__=="__main__" for debugging too.
### Extractor
- Most of the time the company job boards use api to get the search results for their jobs. Use web developer tool and go to the network section, and look for api calls that give a JSON response with all the job postings. Once you find that out, you can right click and copy as curl. You can go to this link https://curlconverter.com/ to convert the curl command to a python script. Use this to create your extractor tool.
- The extractor function should return a dictionary in this format:
  {
  "<jobid>":{"jobId":<jobid>,
            "url":<url>,
            "title:<title>}
  ....
  }
### Main
- If you have created the extractor function properly then you can just copy the main function code from the other company files (use adobe.py).


