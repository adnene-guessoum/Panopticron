""" Script to check on specific gh user's contributions, and send an email. """
import datetime
import logging
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin

import requests
from dateutil import parser
from dotenv import load_dotenv

logging.basicConfig(
    level=[logging.INFO, logging.WARNING, logging.ERROR][0],
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="./logs/panopticron_general_logs.log",
    filemode="w",
)

logger = logging.getLogger(__name__)

SUCCESS_LOG_FILE = "./logs/successful_run_logs.txt"
LAST_RESULT_LOG_FILE = "./logs/last_24h_activity_content.txt"

load_dotenv()
PERSONAL_GITHUB_TOKEN = os.getenv("PERSONAL_GITHUB_TOKEN")
TARGET_GITHUB_USERNAME = os.getenv("TARGET_GITHUB_USERNAME")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

required_env_vars = [
    "PERSONAL_GITHUB_TOKEN",
    "TARGET_GITHUB_USERNAME",
    "SMTP_SERVER",
    "SMTP_PORT",
    "EMAIL_SENDER",
    "EMAIL_PASSWORD",
    "EMAIL_RECIPIENT",
]


def check_env_vars(env_vars):
    """check if all required environment variables are set"""

    for env_var in env_vars:
        if not os.getenv(env_var):
            logger.error("Missing environment variables: %s", env_var)
            return


def has_internet_connection():
    """check if the script has internet connection"""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as err:
        logger.info("No internet connection: %s", err)
        return False


def has_run_less_than_12_hours():
    """check if the script has run less than 12 hours ago"""
    if not os.path.exists(SUCCESS_LOG_FILE) or os.path.getsize(SUCCESS_LOG_FILE) == 0:
        return False

    with open(SUCCESS_LOG_FILE, "r", encoding="utf-8") as log_file:
        last_run = parser.parse(log_file.read())
        return datetime.datetime.now() - last_run < datetime.timedelta(hours=12)


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
        logger.warning("No activity found in the last 24 hours. Exiting script...")
        return False

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

    return True


def log_successful_run():
    """log successful runs to ensure no runs less than 12 hours apart"""
    with open(SUCCESS_LOG_FILE, "w", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def log_last_run_results(user_activity_last_24_hours):
    """log the last run results to keep a file if needed"""
    with open(LAST_RESULT_LOG_FILE, "w", encoding="utf-8") as log_file:
        log_file.write("".join(user_activity_last_24_hours))


def main(username):
    """main function when running the script"""
    check_env_vars(required_env_vars)

    retries = 0
    while not has_internet_connection() and retries < 6:
        retries += 1
        logger.warning(
            "No internet connection. Retrying in 10 minutes... %s/6", retries
        )
        time.sleep(600)

    if has_run_less_than_12_hours():
        logger.warning("Last run was less than 12 hours ago. Exiting script...")
        return

    user_activity = get_user_activity(username)
    user_activity_last_24_hours = filter_last_24_hours_activity(user_activity)
    log_last_run_results(user_activity_last_24_hours)
    email_status = send_email(user_activity_last_24_hours)
    if email_status:
        log_successful_run()


if __name__ == "__main__":
    # TODO: argparse or typer for command line args. but already overkill for me and for now.
    main(TARGET_GITHUB_USERNAME)
