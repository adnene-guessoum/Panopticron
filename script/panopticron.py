""" Script to check on specific gh user's contributions, and send an email. """
import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin

import requests
from dateutil import parser
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
PERSONAL_GITHUB_TOKEN = os.getenv("PERSONAL_GITHUB_TOKEN")
TARGET_GITHUB_USERNAME = os.getenv("TARGET_GITHUB_USERNAME")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")


def get_user_activity(username):
    """request target user's activity from GitHub API based on username."""

    url = f"https://api.github.com/users/{username}/events"
    headers = {
        "Authorization": f"token {os.getenv('PERSONAL_GITHUB_TOKEN')}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.Timeout as err:
        retry = 0
        while retry < 3:
            logger.warning("Timeout on %s, retrying... %s/3", url, retry)
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                break
            retry += 1
        raise SystemExit(err) from err
    except requests.exceptions.RequestException as err:
        raise SystemExit(err) from err

    return check_sanity_github_api_response(response, username)


def check_sanity_github_api_response(response, username):
    """handle empty response from GitHub API."""

    if not bool(response.json()):  # empty response
        logger.error("No data found for %s", username)
        logger.warning(
            "No email will be sent. Exiting script..."
            "Check if the username is correct. %s"
            "Otherwise, check the GitHub API documentation for more information : "
            "https://docs.github.com/rest",
            username,
        )
        return None

    return response.json()


def filter_last_24_hours_activity(user_activity):
    """extract relevant info from response"""

    if not user_activity:
        return None

    today = datetime.datetime.now(datetime.timezone.utc)
    user_activity_last_24_hours = []
    for event in user_activity:
        if not today - parser.parse(event["created_at"]) < datetime.timedelta(days=1):
            continue
        event_type = event["type"]
        repo_name = event["repo"]["name"]
        created_at = event["created_at"]
        body = (
            f"\n ===================== \n"
            f"New activity by {TARGET_GITHUB_USERNAME}:\n\n"
            f"Url: {event.get('url', '')}"
            f"Event Type: {event_type}\n"
            f"Repository: {repo_name}\n"
            f"Time: {created_at}\n"
            f"Repo_URL: {urljoin('https://github.com/', repo_name)}\n"
            f"author_URL: {urljoin('https://github.com/', TARGET_GITHUB_USERNAME)}"
            f"\n ===================== \n"
        )
        user_activity_last_24_hours.append(body)

    return user_activity_last_24_hours


def send_email(user_activity_last_24_hours):
    """send email with the extracted info"""

    if not user_activity_last_24_hours:
        return

    content = "".join(user_activity_last_24_hours)

    email = MIMEMultipart()
    email["From"] = EMAIL_SENDER
    email["To"] = EMAIL_RECIPIENT
    email["Subject"] = f"Last 24H GitHub Activity from {TARGET_GITHUB_USERNAME}"
    email.attach(MIMEText(content, "plain"))

    with smtplib.SMTP_SSL(host=SMTP_SERVER, port=SMTP_PORT) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(email)
        logger.info("Email sent successfully: %s", email["Subject"])

    return


def main(username):
    """main function when running the script"""
    user_activity = get_user_activity(username)
    user_activity_last_24_hours = filter_last_24_hours_activity(user_activity)
    send_email(user_activity_last_24_hours)


if __name__ == "__main__":
    main(TARGET_GITHUB_USERNAME)
