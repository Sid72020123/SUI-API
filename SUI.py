"""
Made by @Sid72020123
"""

# ----- Importing libraries and setup -----
import os
import time
import json
import requests

import pymongo
from pyEventLogger import pyLogger

WAIT_TIME = 1

# ----- Make the logger object and format the log -----
logger = pyLogger(colored_output=True,
                  make_file=True,
                  file_name='info',
                  rewrite_file=False)

# Info Log:
format_string = "[indexer_type] [time] [log_type] [message]"
logger.format_log(log_type=["INFO", "SUCCESS", "ERROR"],
                  format_string=format_string)

info_format_color = "[bold cyan black][bold yellow black][bold magenta black][normal #FFFFFF black]"
logger.format_log_color(log_type="INFO", format_string=info_format_color)

# Success Log:
success_format_color = "[bold cyan black][bold yellow black][bold green black][bold #FFFFFF black]"
logger.format_log_color(log_type="SUCCESS", format_string=success_format_color)

# Error Log:
error_format_color = "[bold cyan black][bold #FF0000 black][bold red black][bold #FF0000 black]"
logger.format_log_color(log_type="ERROR", format_string=error_format_color)

# ----- Headers and URLs -----
headers = {'user-agent': 'SUI API v2.0'}
ScracthDB = "https://scratchdb.lefty.one/v3/user/rank/global/followers"
ScratchAPI = "https://api.scratch.mit.edu/"

password = os.environ["password"]


class SUI:
    def __init__(self, type):
        self.type = type
        self.proxies = [
            f"https://proxy-k90c.onrender.com/api/{ScratchAPI}",
            f"https://api.allorigins.win/raw?url={ScratchAPI}"
        ]  # List of all the proxies which the API can use
        self.ScratchAPI = self.proxies[
            0]  # Get the current URL along with the proxy URL
        self.use_proxy = 0  # Current proxy index
        self.run = {"Username": True, "Project": True}
        try:
            self.client = pymongo.MongoClient(
                f"mongodb+srv://SUI:{password}@sui.3k3k5.mongodb.net/?retryWrites=true&w=majority"
            )
        except pymongo.errors.ConfigurationError as E:
            logger.error(message="pymongo server configuration error",
                         indexer_type=self.type.upper(),
                         include_error_message=True)
            os.system("python main.py")
        self.db = self.client['SUI']
        self.collection = self.db['data']
        length = self.collection.count_documents({})
        with open('count.json', 'w') as file:
            file.write(json.dumps({'Count': length}))
        logger.success(message="Connected External Server!",
                       indexer_type=self.type.upper())

    def get_famous_scratchers(self):
        try:
            data = requests.get(url=ScracthDB, headers=headers).json()
            usernames = []
            for i in data:
                usernames.append(i['username'])
            return usernames
        except:  # Execute the code when Scratch DB gives an error
            logger.error(
                message="Failed to get famous Scratchers from the ScratchDB!",
                indexer_type=self.type.upper())
            data = ["griffpatch", "Will_Wam", "griffpatch_tutor"]
            logger.info(
                message=
                "Continuing with some famous users as there was an error...",
                indexer_type=self.type.upper())
            return data

    def get_main_user_id(self, username):
        data = requests.get(url=f"{self.ScratchAPI}users/{username}/",
                            headers=headers).json()
        return {str(data['id']): data['username']}

    def get_user_followers(self, username, limit="40", offset=0):
        data = requests.get(
            url=
            f"{self.ScratchAPI}users/{username}/followers/?limit={limit}&offset={offset}",
            headers=headers).json()
        followers = {}
        try:
            for i in data:
                followers[str(i['id'])] = i['username']
        except TypeError:
            return []
        return followers

    def get_user_following(self, username, limit="40", offset=0):
        data = requests.get(
            url=
            f"{self.ScratchAPI}users/{username}/following/?limit={limit}&offset={offset}",
            headers=headers).json()
        following = {}
        for i in data:
            try:
                following[str(i['id'])] = i['username']
            except TypeError:
                return []
        return following

    def collect_user_data(self, username, offset):
        i = offset
        while True:  # Another loop to get all followers of a famous user
            data = self.get_user_followers(username=username, offset=i)  # Data
            if len(
                    data
            ) == 0:  # * Break the loop if the length of followers data is 0
                break
            self.add_data(data)  # Add the followers data
            logger.info(message=f"Finished Offset: {i}",
                        indexer_type=self.type.upper())
            i += 40  # Increase offset
            self.update_status(i=username, offset=i)  # Update the status
            for d in data:  # Another loop to get the follower's followers and following
                followers_d = self.get_user_followers(username=data[d])
                following_d = self.get_user_following(username=data[d])
                self.add_data(followers_d)
                self.add_data(following_d)
                time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
            time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
        logger.success(message=f"Finished Indexing User: {username}",
                       indexer_type=self.type.upper())

    def _start_loop_username(self):
        run = self.run["Username"]
        try:
            while run:
                famous_users = self.get_famous_scratchers(
                )  # Get famous Scratchers
                with open('status.json') as file:
                    done = json.load(file)["Username"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    offset = int(done['Offset'])  # Offset
                    index = famous_users.index(
                        done['Username'])  # Continue from the index
                    logger.info(
                        message=
                        f"Continuing from index: {index} and offset: {offset}",
                        indexer_type=self.type.upper())
                else:
                    offset = 0  # Offset
                    index = 0  # Index
                    logger.info(
                        message=
                        f"Starting from index: {index} and offset: {offset}",
                        indexer_type=self.type.upper())
                while index < len(
                        famous_users
                ):  # Loop to get the follower data of a famous users
                    user = famous_users[index]
                    try:
                        # ----- Main script to collect the user's data -----
                        self.add_data(self.get_main_user_id(
                            username=user))  # Add the famous user data
                        self.collect_user_data(username=user, offset=offset)
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(self.proxies) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = self.proxies[self.use_proxy]
                        logger.info(
                            message=
                            f"Current proxy failed! Using proxy index: {self.use_proxy}",
                            indexer_type=self.type.upper(),
                            include_error_message=True)
                        continue
                    index += 1  # Increase Index by 1
                    offset = 0  # Set the offset to 0
                self.update_status(i="", offset=0,
                                   c=False)  # Update the status
                time.sleep(60)  # Sleep to reduce the load on Servers
        except:
            logger.error(message="An Error Occurred!",
                         include_error_message=True,
                         indexer_type=self.type.upper())

    def _start_loop_project(self):
        run = self.run["Project"]
        try:
            while run:
                fails = 0  # Count the number of unshared projects
                with open('status.json') as file:
                    done = json.load(file)["Project"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    project_id = done['ID']  # Project ID
                    logger.info(
                        message=f"Continuing from project id: {project_id}",
                        indexer_type=self.type.upper())
                else:
                    project_id = 104  # Project ID
                    logger.info(
                        message=f"Starting from project id: {project_id}",
                        indexer_type=self.type.upper())
                # ----- Main script to collect the user's data by checking every project -----
                while True:
                    try:
                        data = requests.get(
                            f"{self.ScratchAPI}/projects/{project_id}").json()
                        try:
                            project_author = data["author"]["username"]
                            self.add_data(
                                {str(data["author"]['id']): project_author})
                            followers_d = self.get_user_followers(
                                username=project_author)
                            following_d = self.get_user_following(
                                username=project_author)
                            self.add_data(followers_d)
                            self.add_data(following_d)
                        except KeyError:
                            fails += 1
                        if fails >= 500:
                            project_id -= 500
                            logger.info(
                                message=
                                f"Starting from project id: {project_id} as there were 500 fails (because those projects were unshared)",
                                indexer_type=self.type.upper())
                        logger.info(message=f"Project ID: {project_id} done",
                                    indexer_type=self.type.upper())
                        project_id += 1  # Increase Index by 1
                        self.update_status(i=project_id,
                                           c=True)  # Update the status
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(self.proxies) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = self.proxies[self.use_proxy]
                        logger.info(
                            message=
                            f"Current proxy failed! Using proxy index: {self.use_proxy}",
                            indexer_type=self.type.upper())
                        continue
                    time.sleep(
                        WAIT_TIME)  # Sleep to reduce the load on Servers
        except:
            logger.error(message="An Error Occurred!",
                         include_error_message=True,
                         indexer_type=self.type.upper())

    def start_loop(self):
        if self.type == "Username":
            self._start_loop_username()
            self.run["Username"] = True
        else:
            self._start_loop_project()
            self.run["Project"] = True

    def add_data(self, d):
        # ----- Add the data to the DB -----
        for i in d:
            # print(self.type.upper(), i, d[i])
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

    def update_status(self, i, offset=0, c=True):
        # ----- Update the status -----
        with open("status.json", "r") as file:
            data = json.load(file)
        with open("status.json", "w") as file:
            if self.type == "Username":
                data["Username"]["Continue"] = c
                data["Username"]["Username"] = i
                data["Username"]["Offset"] = offset
            else:
                data["Project"]["Continue"] = c
                data["Project"]["ID"] = i
            file.write(json.dumps(data))
