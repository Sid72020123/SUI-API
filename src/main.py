"""
Made by @Sid72020123 on Scratch
"""

from threading import Thread
from fastapi import FastAPI
import uvicorn

from Indexers import start_all_indexing_threads
from StatusUpdater import set_status_thread, updates_thread
from DataBase import DataBase

app = FastAPI()
db = DataBase()
db.connect_server()
  
@app.get("/")
def root():
  return {"Info": "DataBase Backend for SUI API"}


@app.get("/get_user")
def get_user(id: int):
  d = db.get_username(id)
  return {"Data": d}


@app.get("/get_id")
def get_id(username: str):
  d = db.get_id(username)
  return {"Data": d}


@app.get("/random")
def get_random_data():
  d = db.get_random()
  return {"Data": d}


@app.get("/data")
def get_data(limit: int, offset: int):
  d = db.get_data(limit, offset)
  return {"Data": d}


if __name__ == "__main__":
  start_all_indexing_threads()
  Thread(target=set_status_thread).start()
  Thread(target=updates_thread).start()
  uvicorn.run("main:app", host="0.0.0.0", port=20615)
  
