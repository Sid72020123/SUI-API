"""
Made by @Sid72020123 on Scratch
"""
# ----- Imports -----
from fastapi import FastAPI
from API import API

# ----- Main Indexing Threads -----
api = API()

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
    description="**The indexing program is stopped! The data provided by this API may not be up-to-date!**\n\nScratch Username Index API which indexes the users (only the username and the id) on the Scratch website and stores them in a database! "
    "You can find the username from their id using this API!\n\n This API was made because the Scratch API didn't had any endpoint to get username from their id.\n\n\n"
    "**Note: You may not be able to find all the usernames from their IDs because this API hasn't indexed much users on Scratch! But it has indexed over 3M+ users!**",
    version="2.6",
    openapi_tags=tags_metadata,
)


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    The Root Page
    """
    return {
        "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
        "Name": "SUI",
        "Version": "2.6",
        "Description": "Scratch Username Index API",
        "Documentation": "https://github.com/Sid72020123/SUI-API#readme or /docs",
        "Credits": "Made by @Sid72020123 on Scratch",
        "DataCredits": "Scratch API and Scratch DB"
    }


async def get_status():
    try:
        total_data = 3618782  # Hard-coded because the indexing is stopped :(
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": False,
            "ServerStatus": "Indexing stopped!",
            "TotalUsers": total_data,
        }
    except Exception as e:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
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
        user = api.find_username(id)["Username"]
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": False,
            "ID": id,
            "Username": user,
        }
    except TypeError:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Info": f"User with ID '{id}' not found",
        }
    except Exception as e:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Info": f"An error occurred{e}",
        }
    return data


@app.get("/get_id/{user}", tags=["Main"])
async def id(user: str) -> dict:
    """
    Get ID from the username
    """
    try:
        search = api.find_id(user)
        id = search["_id"]
        u = search["Username"]
        data = {"Error": False, "ID": id, "Username": u}
    except TypeError:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Info": f"User '{user}' not found",
        }
    except Exception as e:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
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
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": False,
            "RandomData": random_data,
        }
    except Exception as e:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
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
            "ImportantMessage": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Message": "Limit can't be greater than 10K!",
        }
    try:
        d = list(api.get_data(limit=limit, offset=offset))
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": False,
            "Data": d,
        }
    except Exception as e:
        data = {
            "Message": "The indexing program is stopped! The data provided by this API may not be up-to-date!",
            "Error": True,
            "Info": f"An error occurred: {e}",
        }
    return data
