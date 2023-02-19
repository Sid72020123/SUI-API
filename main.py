"""
Made by @Sid72020123 on Scratch
"""


from threading import Thread
import json
import time
import os

# ----- Imports -----
try:
    import pymongo
    import uvicorn
    from fastapi import FastAPI, WebSocket
    from fastapi.middleware.cors import CORSMiddleware
    import pyEventLogger
except ModuleNotFoundError:
    os.system('pip install -r requirements.txt')
    import pymongo
    import uvicorn
    from fastapi import FastAPI, WebSocket
    from fastapi.middleware.cors import CORSMiddleware
    import pyEventLogger

from SUI import SUI

# CORS
origins = ["*"]

# ----- Main Indexing Threads -----
username_indexer = SUI("Username")
project_indexer = SUI("Project")
studio_indexer = SUI("Studio")
sui = username_indexer
thread1 = Thread(target=username_indexer.start_loop, args=())
thread2 = Thread(target=project_indexer.start_loop, args=())
thread3 = Thread(target=studio_indexer.start_loop, args=())
thread1.start()
thread2.start()
thread3.start()

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
    description=
    "Scratch Username Index API which indexes the users (only the username and the id) on the Scratch website and stores them in a database! "
    "You can find the username from their id using this API!\n\n This API was made because the Scratch API didn't had any endpoint to get username from their id.\n\n\n"
    "**Note: You may not be able to find all the usernames from their IDs because this API hasn't indexed much users on Scratch! But it has indexed over 2M+ users!**",
    version="2.6",
    openapi_tags=tags_metadata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    The Root Page
    """
    return {
        "Name": "SUI",
        "Version": "2.6",
        "Description": "Scratch Username Index API",
        "Documentation":
        "https://github.com/Sid72020123/SUI-API#readme or /docs",
        "Credits": "Made by @Sid72020123 on Scratch",
        "DataCredits": "Scratch API and Scratch DB"
    }


async def get_status():
    try:
        total_data = json.loads(open('count.json', 'r').read())['Count']
        working_at = json.loads(open('status.json', 'r').read())
        data = {
            "Error":
            False,
            "ServerStatus":
            "Online",
            "TotalUsers":
            total_data,
            "Indexers": [{
                "Username": working_at["Username"],
                "ProgramRunning": username_indexer.run["Username"],
                "ProxyIndex": username_indexer.use_proxy
            }, {
                "Project": working_at["Project"],
                "ProgramRunning": project_indexer.run["Project"],
                "ProxyIndex": project_indexer.use_proxy
            }, {
              "Studio": working_at["Studio"]
              ,
                "ProgramRunning": studio_indexer.run["Studio"],
                "ProxyIndex": studio_indexer.use_proxy
            }]
        }
    except:
        data = {"Error": True, "Info": "An error occurred"}
    return data


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
        user = sui.collection.find_one({"_id": id})["Username"]
        data = {"Error": False, "ID": id, "Username": user}
    except TypeError:
        data = {"Error": True, "Info": f"User with ID '{id}' not found"}
    except:
        data = {"Error": True, "Info": "An error occurred"}

    return data


@app.get("/get_id/{user}", tags=["Main"])
async def id(user: str) -> dict:
    """
    Get ID from the username
    """
    try:
        search = sui.collection.find_one({"Username": { "$regex": f"^{user}$", "$options" : 'i'}})
        id = search["_id"]
        u = search["Username"]
        data = {"Error": False, "ID": id, "Username": u}
    except TypeError:
        data = {
            "Error": True,
            "Info": f"User '{user}' not found",
            "Indexing": "Started"
        }
        try:
            main_d = sui.get_main_user_id(user)
            followers_d = sui.get_user_followers(user)
            following_d = sui.get_user_following(user)
            sui.add_data(main_d)
            sui.add_data(followers_d)
            sui.add_data(following_d)
        except KeyError:
            data["Indexing"] = "Failed"
    except:
        data = {"Error": True, "Info": "An error occurred"}

    return data


@app.get("/random/", tags=["Main"])
async def random() -> dict:
    """
    Get Random Data
    """
    try:
        random_data = list(sui.collection.aggregate([{
            "$sample": {
                "size": 1
            }
        }]))
        data = {"Error": False, "RandomData": random_data}
    except:
        data = {"Error": True, "Info": "An error occurred"}
    return data


@app.get("/get_data/", tags=["Main"])
async def gd(limit: int = 1000, offset: int = 0) -> dict:
    """
    Get Data with the stated limit and skip from the given offset
    """
    if limit > 10000:
        return {"Error": True, "Message": "Limit can't be greater than 10K!"}
    try:
        d = list(sui.collection.find({}).skip(offset).limit(limit))
        data = {"Error": False, "Data": d}
    except:
        data = {"Error": True, "Info": "An error occurred"}
    return data


# ----- Websocket for Live Data! -----
# (Sorry if the code is wrong/odd. I am new to asynchio)
@app.websocket("/live-data")
async def live_data(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            status_data = await get_status()
            await websocket.send_text(json.dumps(status_data))
        except (KeyError, ValueError):
            await websocket.send_text(
                json.dumps({"Error": "An error occurred!"}))
            await websocket.close()
            break
        time.sleep(0.1)


uvicorn.run(app, host='0.0.0.0', port=8080)
