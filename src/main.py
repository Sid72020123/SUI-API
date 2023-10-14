"""
Made by @Sid72020123 on Scratch
"""

from threading import Thread

from Indexers import start_all_indexing_threads
from StatusUpdater import set_status_thread, updates_thread

start_all_indexing_threads()
Thread(target=set_status_thread).start()
Thread(target=updates_thread).start()
