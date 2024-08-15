"""
SUI API - Main
--------------------

This file contains a function to start all the threads required by the API.
To start the API, just run this file...

--------------------
Author: @Sid72020123 on Github
"""

# ----- Imports -----
from threading import Thread
import uvicorn

from app import setup_databases, start_threads
from Indexers import start_all_indexing_threads
from StatusUpdater import set_status_thread, updates_thread


def main():
    """
    The main function to start all the main threads
    """
    setup_databases()
    start_threads()
    start_all_indexing_threads()
    Thread(target=set_status_thread).start()
    Thread(target=updates_thread).start()
    # This configuration is required by the hosting server to serve the app properly:
    uvicorn.run("app:app", host="0.0.0.0", port=20615)


if __name__ == "__main__":
    main()
