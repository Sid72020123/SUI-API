"""
Made by @Sid72020123
"""

import os
import time
import json
import requests
import pymongo
from pyEventLogger import pyLogger

logger = pyLogger(colored_output=True,
                  make_file=True,
                  file_name='errors',
                  rewrite_file=False,
                  file_logs=['ERROR', 'CRITICAL'])


headers = {'user-agent': 'SUI API'}
ScracthDB = "https://scratchdb.lefty.one/v3/user/rank/global/followers"
ScratchAPI = "https://api.scratch.mit.edu/"

password = os.environ['password']


class SUI:
    def __init__(self):
        self.run = True
        self.client = pymongo.MongoClient(
            f"mongodb+srv://SUI:{password}@sui.3k3k5.mongodb.net/SUI?retryWrites=true&w=majority"
        )
        self.db = self.client['SUI']
        self.collection = self.db['data']
        #data = list(self.collection.find())
        #length = len(data)
        length = self.collection.count_documents({})
        open('count.json', 'w').write(json.dumps({'Count': length}))
        #open('all_data.json', 'w').write(json.dumps(data, indent=4))
        logger.success(message="Connected External Server!")

    def get_famous_scratchers(self):
        data = requests.get(url=ScracthDB, headers=headers).json()
        usernames = []
        for i in data:
            usernames.append(i['username'])
        return usernames

    def get_main_user_id(self, username):
        data = requests.get(url=f"{ScratchAPI}users/{username}/",
                            headers=headers).json()
        return {str(data['id']): data['username']}

    def get_user_followers(self, username, limit=40, offset=0):
        data = requests.get(
            url=f"{ScratchAPI}users/{username}/followers/?limit={limit}&offset={offset}",
            headers=headers).json()
        followers = {}
        for i in data:
            followers[str(i['id'])] = i['username']
        return followers

    def get_user_following(self, username, limit=40, offset=0):
        data = requests.get(
            url=f"{ScratchAPI}users/{username}/following/?limit={limit}&offset={offset}",
            headers=headers).json()
        followers = {}
        for i in data:
            followers[str(i['id'])] = i['username']
        return followers

    def collect_user_data(self, username, offset):
        offset = offset
        while True:  # Another loop to get all followers of a famous user
            data = self.get_user_followers(username=username,
                                           offset=offset)  # Data
            if len(
                    data
            ) == 0:  # * Break the loop if the length of followers data is 0
                break
            self.add_data(data)  # Add the followers data
            logger.info(message=f"Finished Offset: {offset}")
            offset += 40  # Increase offset
            self.update_status(username=username,
                               offset=offset)  # Update the status
            for i in data:  # Another loop to get the follower's followers and following
                followers_d = self.get_user_followers(username=data[i])
                following_d = self.get_user_following(username=data[i])
                self.add_data(followers_d)
                self.add_data(following_d)
                time.sleep(0.5)  # Sleep to reduce the load on Servers
            time.sleep(0.5)  # Sleep to reduce the load on Servers
        logger.success(message=f"Finished Indexing User: {username}")

    def _start_loop(self):
        try:
            while self.run:
                famous_users = self.get_famous_scratchers(
                )  # Get famous Scratchers
                file = open('status.json')
                done = json.load(file)
                if done['Continue']:  # If the script breaks in between and has to continue
                    offset = done['Offset']  # Offset
                    index = famous_users.index(done['Username'])
                else:
                    offset = 0  # Offset
                    index = 0  # Index
                while index < len(
                        famous_users
                ):  # Loop to get the follower data of a famous users
                    user = famous_users[index]
                    self.add_data(self.get_main_user_id(
                        username=user))  # Add the famous user data
                    self.collect_user_data(username=user, offset=offset)
                    index += 1  # Increase Index by 1
                    offset = 0  # Set the offset to 0
                self.update_status(username="", offset=0,
                                   c=False)  # Update the status
                time.sleep(60)  # Sleep to reduce the load on Servers
        except:
            logger.error(message="An Error Occurred!",
                         include_error_message=True)

    def start_loop(self):
        self._start_loop()
        self.run=False

    def add_data(self, d):
        for i in d:
            print(i, d[i])
            try:
                self.collection.insert_one({"_id": i, "Username": d[i]})
                length = json.loads(open('count.json', 'r').read())["Count"]
                file = open("count.json", "w")
                file.write(json.dumps({"Count": length + 1}))
                file.close()
            except pymongo.errors.DuplicateKeyError:
                new_data = {"$set": {"_id": i, "Username": d[i]}}
                self.collection.update_one({
                    "_id": i,
                    "Username": d[i]
                }, new_data)

    def update_status(self, username, offset, c=True):
        file = open('status.json', 'w')
        data = {"Continue": c, "Username": username, "Offset": offset}
        file.write(json.dumps(data))
        file.close()
