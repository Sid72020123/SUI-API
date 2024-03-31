"""
Made by @Sid72020123 on Scratch
"""

# ----- Imports -----
import os
from json import loads, dumps
from requests import get, post
from fastapi import FastAPI
from pytz import timezone
import arrow
from API import API
from deta import Deta
from quickchart import QuickChart

deta = Deta()
api = API()

status_db = deta.Base("status")
history_db = deta.Base("history")
PASSWORD = os.environ["PASSWORD"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
TIMEZONE = timezone("Asia/Kolkata")

# ----- The API -----
tags_metadata = [
    {
        "name": "Root",
        "description": "The main/root page of the API",
    },
    {
        "name": "Status",
        "description": "Get the status of the API",
    },
    {
        "name": "Main",
        "description": "The main API endpoints",
    },
]

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    title="SUI - Scratch Username Index API",
    description="Scratch Username Index API which indexes the users (only the username and the id) on the Scratch website and stores them in a database! "
    "You can find the username from their id using this API!\n\n This API was made because the Scratch API didn't had any endpoint to get username from their id.\n\n\n"
    "**Note: You may not be able to find all the usernames from their IDs because this API hasn't indexed much users on Scratch! But it has indexed over 3M+ users!**",
    version="4.0",
    openapi_tags=tags_metadata,
)

def send_message(content):
    return get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": content,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )

def send_telegram_photo(b):
    return post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        params={"chat_id": TELEGRAM_CHAT_ID},
        files={"photo": b}
    )

@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    The Root Page
    """
    return {
        "Name": "SUI",
        "Version": "4.0",
        "Description": "Scratch Username Index API",
        "Documentation": "https://github.com/Sid72020123/SUI-API#readme or /docs",
        "Credits": "Made by @Sid72020123 on Scratch",
        "DataCredits": "Scratch API and Scratch DB"
    }


async def get_status():
    try:
        data = status_db.get("data")["status"]
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data

@app.get("/set_status/")
async def set_status(password: str, data: str):
    if password == PASSWORD: 
        status_db.put({"status": loads(data)}, "data")
        return "Done!"
    else:
        return "Access Denied!"

@app.get("/set_history/")
async def set_history(password: str, data: str, date: str):
    if password == PASSWORD:
        history_db.put({"status": loads(data)}, date)
        return "Done!"
    else:
        return "Access Denied!"


@app.get("/get_history/")
async def get_history(password: str, date: str):
    if password == PASSWORD:
        return history_db.get(date)["status"]
    else:
        return "Access Denied!"

@app.get("/status/", tags=["Status"])
async def status() -> dict:
    """
    The Status Page
    """
    data = await get_status()
    return data


@app.get("/get_user/{id}", tags=["Main"])
async def user(id: str) -> dict:
    """
    Get the username from its ID
    """
    try:
        user = api.find_username(id)["username"]
        data = {
            "Error": False,
            "ID": id,
            "Username": user,
        }
    except TypeError:
        data = {
            "Error": True,
            "Info": f"User with ID '{id}' not found",
        }
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data


@app.get("/get_id/{user}", tags=["Main"])
async def id(user: str) -> dict:
    """
    Get ID from the username
    """
    try:
        search = api.find_id(user)
        id = search["id"]
        u = search["username"]
        data = {"Error": False, "ID": id, "Username": u}
    except TypeError:
        data = {
            "Error": True,
            "Info": f"User '{user}' not found",
        }
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data


@app.get("/random/", tags=["Main"])
async def random() -> dict:
    """
    Get Random Data
    """
    try:
        random_data = api.get_random_data()
        data = {
            "Error": False,
            "RandomData": random_data,
        }
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data


@app.get("/get_data/", tags=["Main"])
async def gd(limit: int = 1000, offset: int = 0) -> dict:
    """
    Get Data with the stated limit and skip from the given offset
    """
    if limit > 10000:
        return {
            "Error": True,
            "Message": "Limit can't be greater than 10K!",
        }
    try:
        d = list(api.get_data(limit=limit, offset=offset))
        data = {
            "Error": False,
            "Data": d,
        }
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data

INDEXER_NAMES = ["Username", "Studio", "Project", "Short Username", "Forum", "Cloud Game"]
REAL_NAMES = ["UsernameIndexer", "StudioIndexer", "ProjectIndexer", "ShortUsernameIndexer", "ForumIndexer", "CloudGameIndexer"]
COLORS = ["#ff6b6b", "#f06595", "#cc5de8", "#845ef7", "#20c997", "#94d82d"]

def create_weekly_chart(iutc, lc, dates):
    qc = QuickChart()
    qc.version = '4.4.0'
    qc.width = 700
    qc.height = 500
    qc.background_color = "rgb(0, 0, 0)"
    
    # Indexer Upserts Total Count
    keys = INDEXER_NAMES
    iutc_values = list(iutc.values())
     
    # Make Bar Chart
    try:
        qc.config = {
            "type": "bar",
            "data": {
                "labels": keys,
                "datasets": [{
                    "label": "Upserts Count",
                    "data": iutc_values,
                    "backgroundColor": "#ff6b6b",
                }]
            },
            "options": {
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"SUI API ({dates[-1]} - {dates[0]}) - Upserts Count of the Indexers over the week",
                        "color": "#FFFFFF",
                        "font": {"weight": "bold"},
                    },
                    "legend": {
                        "display": True,
                        "labels": {
                            "color": "#FFFFFF"
                        }
                    },
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Indexer Type", "color": "#ffd43b"},
                        "ticks": {"color": "#FFFFFF"}
                    },
                    "y": {
                        "title": {"display": True, "text": "No. of upserts", "color": "#ffd43b"},
                        "ticks": {"color": "#FFFFFF"}
                    }
                },
            },
        }
        bb = qc.get_bytes()
        bar_success = True
    except Exception as E:
        print("BAR:", E)
        bar_success = False

    # Make Line Chart
    try:
        new_dates = list(dates)
        new_dates.reverse()
        qc.config = {
            "type": "line",
            "data": {
                "labels": new_dates,
                "datasets": [{
                    "label": INDEXER_NAMES[i],
                    "data": lc[i],
                    "borderColor": COLORS[i],
                    "tension": 0.5,
                } for i in range(0, len(INDEXER_NAMES))]
            },
            "options": {
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"SUI API ({dates[-1]} - {dates[0]}) - Upserts Count of the Indexers over the week",
                        "color": "#FFFFFF",
                        "font": {"weight": "bold"},
                    },
                    "legend": {
                        "display": True,
                        "labels": {
                            "color": "#FFFFFF"
                        }
                    },
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Date", "color": "#ffd43b"},
                        "ticks": {"color": "#FFFFFF"}
                    },
                    "y": {
                        "title": {"display": True, "text": "No. of upserts", "color": "#ffd43b"},
                        "ticks": {"color": "#FFFFFF"}
                    }
                },
            },
        }
        lb = qc.get_bytes()
        line_success = True
    except Exception as E:
        print("LINE:", E)
        line_success = False
    return [bar_success, line_success, bb, lb]
    

@app.post("/__space/v0/actions")
def actions(event: dict):
    if event["event"]["id"] == "Send_Message":
        try:
            current_time = arrow.now(TIMEZONE)
            dates = []
            historical_data = []
            for i in range(1, 9):
                temp_date = current_time.shift(days=-i).strftime('%d/%m/%Y')
                d = history_db.get(temp_date)
                if d is not None:
                    dates.append(temp_date)
                    historical_data.append(d["status"])
                    
            total_upserts_count = 0
            for i in historical_data:
                l = list(i["UpsertsToday"].values())
                total_upserts_count += sum(l)
            
            indexer_upserts_total_count = {}
            line_chart_data = []
            for i in REAL_NAMES:
                c = 0
                ld = []
                for j in historical_data:
                    c += j["UpsertsToday"][i]
                    ld.append(j["UpsertsToday"][i])
                ld.reverse()
                line_chart_data.append(ld)
                indexer_upserts_total_count[INDEXER_NAMES[REAL_NAMES.index(i)]] = c
            
            net_users_increase = historical_data[0]["TotalUsersData"]["Count"] - historical_data[-1]["TotalUsersData"]["Count"]
            
            message = f"""Weekly ({dates[-1]} - {dates[0]}) status update for <b>SUI API:</b>\n\n<b>Total Upserts Count:</b> {total_upserts_count:,}\n\n<b>Net New Users Indexed:</b> {net_users_increase:,}"""
            send_message(message)
            cc = create_weekly_chart(indexer_upserts_total_count, line_chart_data, dates)
            if cc[0]:
                send_telegram_photo(cc[2])
            if cc[1]:
                send_telegram_photo(cc[3])
        except Exception as E:
            send_message(f"""<b>An error occurred while sending weekly update:</b> <pre>{E}</pre>""")
