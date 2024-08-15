"""
SUI API - Config
--------------------

This file contains all the global variables and constants used by various functions of the API

--------------------
Author: @Sid72020123 on Github
"""

from pytz import timezone
from os import getenv
from dotenv import load_dotenv
from json import load

load_dotenv()

WAIT_TIME = 1 # The variable to control the number of requests made to the Scratch API
PASSWORD = getenv("PASSWORD", "")
DB_USERNAME = getenv("DATABASE_USERNAME", "")
DB_PASSWORD = getenv("DATABASE_PASSWORD", "")
DB_HOST = getenv("DATABASE_HOST", "")
DB_PORT = getenv("DATABASE_PORT", "")
DB_NAME = getenv("DATABASE_NAME", "")
SCRATCH_PROJECTS = getenv("SCRATCH_PROJECTS", "")
SCRATCH_STUDIOS = getenv("SCRATCH_STUDIOS", "")
HEADERS = {"User-Agent": "SUI API v5.0"}
ScratchDB = "https://scratchdb.lefty.one/v3/user/rank/global/followers"
ScratchAPI = "https://api.scratch.mit.edu/"
BackendAPI = "https://sui-backend.scratchconnect.eu.org/"
PROXIES = [ScratchAPI, f"https://api.allorigins.win/raw?url={ScratchAPI}"] # I may add more if I find some...
ALL_FORUM_DATA = load(open("scratch_forums.json"))
CLOUD_PROJECTS_STUDIO = getenv("CLOUD_PROJECTS_STUDIO", "")
TIMEZONE = timezone("Asia/Kolkata") # Required to perform certain actions at a specific time in the given time zone
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "") # Required to send hourly API updates and statuses to the maintainer
STATUS_UPDATE_TIME = int(getenv("STATUS_UPDATE_TIME", 500)) # The time interval (in seconds) to update the current status of the indexing threads to an external API 
TelegramAPI = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID", "")
STATUS_RESET_TIME = getenv("STATUS_RESET_TIME", "06:45") # The time (according to the above time zone) when the API will update the count of users in the main DB
STATS_RESET_TIME = getenv("STATS_RESET_TIME", "06:45") # The time (according to the above time zone) when the API will reset the stats data of endpoints
COCKROACH_DB_LINK = getenv("COCKROACH_DB_LINK", "") # This is required by the Forum Indexer to store post data to external DB
