# Panopticron

stalk users on github to learn stuff. Mentorship from afar.

**Panopticron** is a simple Python script designed to monitor GitHub activity for a specific user, ensuring you stay informed about their latest contributions, commits, and events.
I use it for learning purposes, when I see someone i would like to learn from, or actively working on a project I am interested in.

I run the script with a cron job at regular intervals to keep track of their activities and events.

## Features

- **Daily Activity Monitoring**: Tracks GitHub activity for a specified target user through the Github API.
- **Email Notifications**: Sends email notifications summarizing the latest events, with links to repos.
- **Logging**: Records the script's activity in log files for debugging, monitoring and saving latest result to a file (limit email spam to once every 12 hours, might move to once a day).
- **Internet Connection Detection**: Ensures the script only runs when an active internet connection is available. else retries after a delay.

## Installation and Usage

1. **Clone/Fork the Repository**:
   ```bash
   git clone https://github.com/adnene-guessoum/panopticron.git
	 cd Panopticron
   ```

2. **Install Dependencies**:

	 for ease of use, i dockerized the project and provided an example run script. see usage below.

   If you want to not use docker/script, I use Poetry to manage dependencies. you can install with the official installer here : https://python-poetry.org/docs/#installing-with-the-official-installer .

3. **Add your environment variables**:
   Create a `.env` file in the project root directory. an example is provided in the `.env.example` file, with the necessary environment variables and some explanations.
	 Most importantly, you will need:
   - A GitHub personal access token. (cf. .env.example)
   - The GitHub username you want to monitor.
   - Your email credentials for sending notifications.

	 adhere to the ".env.example" file format and fill in the necessary information, as it is used to load the environment variables in the docker container.

4. **Run using the script/docker**:

	 1) Setup the correct paths in the script example.run.sh file to match your setup,
	 2) don't forget to modify the environment variables in the `.env.example` file to match your infos and rename it to `.env` (as explained in step 3),
	 3) then run:
	 ```bash
	 mv example.run.sh run.sh
	 chmod +x run.sh
	 ./run.sh
	 ```
	 you should be good to go for a manual run (docker image build and run).


6. **Set Up Daily Execution**:
   I use a cron job to run the script once every 12 hours.

	to setup a cron job:
	 ```bash
	 crontab -e
	 ```
	 then add the cron job line at the end of the file:
	 ```bash
	 */12 * * *  /path/to/repo/Panopticron/run.sh >> /path/to/repo/Panopticron/logs/cron_logs.log 2>&1
	 ```

	 This will run the script (docker build then docker run) every 12 hours and log the output of the cron job to the specified file.
	 Modify the path to the repo to match your setup and the frequency of the cron job to your needs.

Feel free to adjust based on your needs, or to offer contributions to make this more user-friendly.
You can open an issue if need help setting it up.

## Example Email Notification

```
Subject: Last 24H GitHub Activity from adnene-guessoum

 =====================
New activity by adnene-guessoum:

Event Type: PushEvent
Repository: adnene-guessoum/Panopticron
Time: 2024-12-22T12:34:42Z
Repo_URL: https://github.com/adnene-guessoum/Panopticron
author_URL: https://github.com/adnene-guessoum
 =====================

etc...
```

## Contributions

Contributions are obviously welcome. Probably i won't work too much on it as it meets my need as is.
If you have ideas for additional features or improvements, feel free to submit a pull request or open an issue of course.

## Acknowledgments

- The GitHub API, for providing the necessary data.
- The devs that don't know they are mentoring me.
