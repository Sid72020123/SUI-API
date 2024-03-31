from pytz import timezone
from os import getenv
from dotenv import load_dotenv
from json import load

load_dotenv()

WAIT_TIME = 3
PASSWORD = getenv("PASSWORD", "")
DB_USERNAME = getenv("DATABASE_USERNAME", "")
DB_PASSWORD = getenv("DATABASE_PASSWORD", "")
DB_HOST = getenv("DATABASE_HOST", "")
DB_PORT = getenv("DATABASE_PORT", "")
DB_NAME = getenv("DATABASE_NAME", "")
SCRATCH_PROJECTS = getenv("SCRATCH_PROJECTS", "")
SCRATCH_STUDIOS = getenv("SCRATCH_STUDIOS", "")
HEADERS = {'User-Agent': 'SUI API v4.0'}
ScratchDB = "https://scratchdb.lefty.one/v3/user/rank/global/followers"
ScratchAPI = "https://api.scratch.mit.edu/"
BackendAPI = "https://sui.scratchconnect.eu.org/"
PROXIES = [ScratchAPI, f"https://api.allorigins.win/raw?url={ScratchAPI}"]
ALL_FORUM_DATA = load(open("scratch_forums.json"))
CLOUD_PROJECTS_STUDIO = getenv("CLOUD_PROJECTS_STUDIO", "")
TIMEZONE = timezone("Asia/Kolkata")
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
STATUS_UPDATE_TIME = int(getenv("STATUS_UPDATE_TIME", 500))
TelegramAPI = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID", "")
STATUS_RESET_TIME = getenv("STATUS_RESET_TIME", "06:45")
