def check():
    import requests
    from bs4 import BeautifulSoup
    def here():
        print("-- The odyssey is here--")
        send_email_movie()

    #url = "https://www.amctheatres.com/movie-theatres/new-york-city/amc-lincoln-square-13/showtimes?date=2026-08-11" # with odyssey
    url ="https://www.amctheatres.com/movie-theatres/new-york-city/amc-lincoln-square-13/showtimes?premium-offering=imax70mm&date=2026-08-22"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract movie titles
    movie_titles = []
    for a in soup.select("section > header h1 > a"):
        movie_titles.append(a.get_text(strip=True))

    print("Movies")
    print(movie_titles)
    print()

    for title in movie_titles:
        if title == "The Odyssey":
            here()


import os
import json
import smtplib
from email.mime.text import MIMEText

def send_email_movie():
    print("Sending Email....")
    recipient = "kelvin4jaison@gmail.com"

    # Load credentials
    if os.environ.get("sender"):
        sender = os.environ["sender"]
        password = os.environ["password"]
    else:
        with open("secrets.json") as f:
            data = json.load(f)
        sender = data["sender"]
        password = data["password"]

    # Email
    subject = "Odysseus is here"
    body = "Odysseus is here."

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    # Send
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())

    print("Email sent!")
