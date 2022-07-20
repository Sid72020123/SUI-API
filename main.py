"""
Made by @Sid72020123
"""
#exit() # Stopped due to Scratch API Spam
import os
import json
from threading import Thread

try:
    import pymongo
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import pyEventLogger
except ModuleNotFoundError:
    os.system('pip install fastapi')
    os.system('pip install uvicorn')
    #os.system("pip install pymongo")
    os.system("pip install pymongo[srv]")
    os.system("pip install pyEventLogger")
    import pymongo
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import pyEventLogger
from SUI import SUI
# CORS

origins = ["*"]

sui = SUI()
main = Thread(target=sui.start_loop, args=())
main.start()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "Name": "SUI",
        "Version": "1.3",
        "Description": "Scratch Username Index API",
        "Documentation": "https://github.com/Sid72020123/SUI-API#readme",
        "Credits": "Made by @Sid72020123 on Scratch",
        "DataCredits": "Scratch API and Scratch DB"
    }


@app.get("/status/")
async def status():
    try:
        total_data = json.loads(open('count.json', 'r').read())['Count']
        working_at = json.loads(open('status.json', 'r').read())
        data = {
            "ServerStatus": "Online",
            "TotalUsers": total_data,
            "ProgramRunning": sui.run,
            "Working": {
                "Username": working_at["Username"],
                "Offset": working_at["Offset"]
            }
        }
    except:
        data = {"Error": True, "Info": "An error occurred"}
    return data


@app.get("/get_user/{id}")
async def user(id):
    try:
        user = sui.collection.find_one({"_id": id})["Username"]
        data = {"Error": False, "ID": id, "Username": user}
    except TypeError:
        data = {"Error": True, "Info": f"User with ID '{id}' not found"}
    except:
        data = {"Error": True, "Info": "An error occurred"}

    return data


@app.get("/get_id/{user}")
async def id(user):
    try:
        id = sui.collection.find_one({"Username": user})["_id"]
        data = {"Error": False, "ID": id, "Username": user}
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


@app.get("/random/")
async def random():
    try:
        random_data = list(sui.collection.aggregate([{"$sample": {"size": 1}}]))
        data = {"Error": False, "RandomData": random_data}
    except:
        data = {"Error": True, "Info": "An error occurred"}
    return data


uvicorn.run(app, host='0.0.0.0', port=8080)
