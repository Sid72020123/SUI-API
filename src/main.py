"""
Made by @Sid72020123 on Scratch
"""

import time
import arrow
import json
from threading import Thread
from requests import get
from fastapi import FastAPI, Request
import uvicorn

from Indexers import start_all_indexing_threads
from StatusUpdater import set_status_thread, updates_thread, get_status
from DataBase import DataBase
from Config import STATS_RESET_TIME, TIMEZONE

db = DataBase()
db.connect_server()

# --- FastAPI Docs ---
accepted_endpoints = [
    "",
    "docs",
    "status",
    "get_id",
    "get_user",
    "random",
    "get_data",
    "stats",
]

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
    "**Note: You may not be able to find all the usernames from their IDs because this API hasn't indexed much users on Scratch! But it has indexed over 6M+ users!**",
    version="4.0",
    openapi_tags=tags_metadata,
)


# --- ScratchAPI methods used by the functions of FastAPI ---
def get_main_user_id(username):
    data = get(f"https://api.scratch.mit.edu/users/{username}/").json()
    return {str(data["id"]): data["username"]}


# -- Routes --
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
        "DataCredits": "Scratch API and Scratch DB",
        "Error": False,
    }


@app.get("/status/", tags=["Status"])
async def status() -> dict:
    """
    The Status Page
    """
    data = get_status()
    return data


@app.get("/stats/", tags=["Status"])
async def stats() -> dict:
    """
    The Stats of Endpoints
    """
    try:
        with open("stats.json", "r") as f:
            s = json.loads(f.read())
            s["/"] = s[""]
            del s[""]
        data = {"Error": False, "Endpoints": s}
    except Exception as e:
        data = {
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data


@app.get("/get_user/{id}", tags=["Main"])
async def user(id: str) -> dict:
    """
    Get the username from its ID
    """
    try:
        user = db.get_username(id)["username"]
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
        search = db.get_id(user)
        id = search["id"]
        u = search["username"]
        data = {"Error": False, "ID": id, "Username": u}
    except TypeError:
        data = {
            "Error": True,
            "Info": f"User '{user}' not found",
        }
        try:
            data["TemporaryIndexing"] = "Started"
            temp = get_main_user_id(user)
            db.upsert_data(temp)
            data["TemporaryIndexing"] = "Success"
        except Exception as E:
            print(f"Temporary Index Error: {E}")
            data["TemporaryIndexing"] = "Failed"
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
        random_data = {"Data": db.get_random()}
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
        d = list(db.get_data(limit=limit, offset=offset))
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


def increase_stats_count(endpoint):
    try:
        file = open("stats.json", "r")
        stats = json.loads(file.read())
    except Exception as E:
        print(f"Error in Stats Count: {E}")
        stats = {}
        for i in accepted_endpoints:
            stats[i] = 0
    if endpoint in accepted_endpoints:
        stats[endpoint] += 1
    with open("stats.json", "w+") as file:
        file.write(json.dumps(stats))


@app.middleware("http")
async def store_stats(request: Request, call_next):
    increase_stats_count(str(request.url.path).split("/")[1])
    return await call_next(request)


def stats_reset_thread():
    while True:
        current_time = arrow.now(TIMEZONE)
        current_hour = current_time.strftime("%H")
        current_minute = current_time.strftime("%M")
        current_second = current_time.strftime("%S")
        if (
            f"{current_hour}:{current_minute}:{current_second}"
            == STATS_RESET_TIME + ":00"
        ):
            s = {}
            for i in accepted_endpoints:
                s[i] = 0
            with open("stats.json", "w+") as file:
                file.write(json.dumps(s))
        if f"{current_second}" == "00":
            # Ping DB connection and reconnect
            db.connection.ping(reconnect=True)
        time.sleep(1)


def main():
    """
    The main function to start main threads
    """
    #start_all_indexing_threads()
    #Thread(target=set_status_thread).start()
    #Thread(target=updates_thread).start()
    #Thread(target=stats_reset_thread).start()
    uvicorn.run("main:app", host="0.0.0.0", port=20615)


if __name__ == "__main__":
    main()
