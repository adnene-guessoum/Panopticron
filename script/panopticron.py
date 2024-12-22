""" Script to check on specific gh user's contributions, and send an email. """
import logging
import os

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
PERSONAL_GITHUB_USERNAME = os.getenv("PERSONAL_GITHUB_USERNAME")
PERSONAL_GITHUB_TOKEN = os.getenv("PERSONAL_GITHUB_TOKEN")


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
        logger.info(
            "Check if the username is correct. %s"
            "Otherwise, check the GitHub API documentation for more information : "
            "https://docs.github.com/rest",
            username,
        )
        return None

    return response.json()


def main():
    """TODO"""
    print("TODO")
    return 0


if __name__ == "__main__":
    main()
