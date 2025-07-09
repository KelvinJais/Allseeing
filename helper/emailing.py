from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import json

def format_job_listings_html(data):
    html = '''<html><body><h2>New Job Listings</h2><hr>'''
    for job in data:
        html += f"""
        <div style='margin-bottom:20px;'>
            <h3 style='color:#2a7ae2;'>{job['title']}</h3>
            <p><strong>Posted Date:</strong> {job['posted_date']}</p>
            <p><strong>Last Updated:</strong> {job['updated_time']} ago</p>
            <p><a href='{job['job_path']}' style='color:#1a0dab;'>Apply Here</a></p>
            <hr>
        </div>
        """
    html += '</body></html>'
    return html
def generate_job_board_email_content(job_data):
    # Filter out companies with no jobs
    filtered_job_data = {company: jobs for company, jobs in job_data.items() if jobs}

    # Start HTML content
    email_content = '''<html>
  <body>
    <h2>New Job Listings</h2>
'''

    # Add each company and its jobs
    for company, jobs in filtered_job_data.items():
        email_content += f'<h3 style="color:#2E86C1;">{company.capitalize()}</h3>\n'
        email_content += '<ul>\n'
        for job in jobs:
            title = job.get('title', 'No Title')
            url = job.get('url', '#')
            posted_date = job.get('posted_date', 'N/A')
            email_content += f'<li>\n  <a href="{url}" style="text-decoration:none;color:#2874A6; font-weight:bold;">{title}</a><br>\n  <small>Posted: {posted_date}</small>\n</li>\n'
        email_content += '</ul>\n'

    email_content += '  </body>\n</html>'
    return email_content

def send_email(all_jobs):
    # not able to run this locally,
    #if os.environ.get('sender')
    #with open('env.json') as f:
    #data = json.load(f)
    if os.environ.get('sender'):
        sender = os.environ.get('sender')
        recipient = os.environ.get('recipient') #you can make it for multiple ppl
        password = os.environ.get('password')
    else:
        with open('secrets.json') as f:
            data = json.load(f)
        sender = data['sender']
        recipient = "kelvin.konnoth@stonybrook.edu"
        password = data['password']
    print(all_jobs)
    html_content = generate_job_board_email_content(all_jobs)
    message = MIMEMultipart()
    message['Subject'] = "Project Allseeing"
    message['From'] ="kelvin4jaison@gmail.com"
    message['To'] ="kelvin4jaison@gmail.com"
    message.attach(MIMEText(html_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())

