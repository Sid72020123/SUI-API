"""
SUI API - Indexers
--------------------

This file contains the code of various indexing methods used by the API
Currently, there are 8 indexing methods:
1. Username Indexer
2. Studio Indexer
3. Project Indexer
4. Short Usernames Indexer
5. Forums Indexer
6. Cloud Game Indexer
7. User Comments Indexer
8. Front Page Indexer

--------------------
Author: @Sid72020123 on Github
"""

# ----- Imports -----
import json
import time
import datetime
from requests import Session
from requests import get
from bs4 import BeautifulSoup
from pyEventLogger import pyLogger
from threading import Thread

from DataBase import DataBase
from ForumsDB import ForumDB
from Config import HEADERS, ScratchDB, PROXIES, WAIT_TIME, SCRATCH_PROJECTS, SCRATCH_STUDIOS, ALL_FORUM_DATA, \
    CLOUD_PROJECTS_STUDIO

# ----- Log Formatting -----
format_string = "[log_type] [time] [indexer_type] [message]"
info_format_color = "[bold magenta #000000][bold yellow #000000][bold cyan #000000][normal #FFFFFF #000000]"
success_format_color = "[bold green #000000][bold yellow #000000][bold cyan #000000][bold #FFFFFF #000000]"
error_format_color = "[bold red #000000][bold #FF0000 #000000][bold cyan #000000][bold #FF0000 #000000]"

# ----- Global Variables -----
FORUMS_MONTHS = {
    "Jan.": 1,
    "Feb.": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "Aug.": 8,
    "Sept.": 9,
    "Oct.": 10,
    "Nov.": 11,
    "Dec.": 12
}  # Required by the Forum Indexing thread

# ----- Main Code -----


class Indexer:
    def __init__(self, indexer_type):
        """
        THe base class with the methods common to all the indexers
        """
        self.run = False
        self.indexer_type = str(indexer_type).upper()

        self.logger = pyLogger(colored_output=True,
                               make_file=True,
                               file_name=f"logs/{self.indexer_type}",
                               rewrite_file=False, file_logs=["SUCCESS", "ERROR"])
        self.logger.format_log(
            log_type=["INFO", "SUCCESS", "ERROR"], format_string=format_string)
        self.logger.format_log_color(
            log_type="INFO", format_string=info_format_color)
        self.logger.format_log_color(
            log_type="SUCCESS", format_string=success_format_color)
        self.logger.format_log_color(
            log_type="ERROR", format_string=error_format_color)

        self.db_object = DataBase()
        is_connected = self.db_object.connect_server()
        if not is_connected[0]:
            self.log_error(
                f"Couldn't connect the external server: {is_connected[1]}")
            exit()
        self.log_success("Successfully connected the external server!")
        self.db = self.db_object

        self.URL = PROXIES[0]
        self.use_proxy = 0
        self.ScratchAPI = PROXIES[self.use_proxy]

        self.session = Session()
        self.session.headers = HEADERS

        # Create New status files if they don't exist...
        try:
            open(f"status/{self.indexer_type}.json", "r+")
        except FileNotFoundError:
            open(f"status/{self.indexer_type}.json",
                 "w").write(json.dumps({"Data": {"Continue": False}}))

        try:
            open(
                f"upserts_count/{self.indexer_type.lower()}_upserts.txt", "r+")
        except FileNotFoundError:
            open(f"upserts_count/{self.indexer_type.lower()}_upserts.txt",
                 "w").write("0")

    def log_message(self, message):
        self.logger.info(message=message, indexer_type=self.indexer_type)

    def log_success(self, message):
        self.logger.success(message=message, indexer_type=self.indexer_type)

    def log_error(self, message):
        self.logger.error(
            message=message, indexer_type=self.indexer_type, include_error_message=True)

    def _update_upserts_count(self, c):
        old = None
        tries = 0
        while tries < 2:
            with open(f"upserts_count/{self.indexer_type.lower()}_upserts.txt", "r") as file:
                try:
                    old = int(file.read())
                except Exception as E:
                    print("Upserts Error:", E)
                    old = 0
                tries += 1
            with open(f"upserts_count/{self.indexer_type.lower()}_upserts.txt", "w+") as file:
                new = old + c
                file.write(str(new))
            break

    def add_data(self, d):
        # ----- Add the data to the DB -----
        try:
            response = self.db.upsert_data(d)
            self._update_upserts_count(len(d))
        except Exception as E:
            self.log_error(f"Error occurred during upsert: {E}")

    def update_status(self, i, c=True, o=0):
        try:
            with open(f"status/{self.indexer_type}.json", "r+") as file:
                try:
                    data = json.load(file)["Data"]
                except Exception as E:
                    self.log_error(f"Error occurred while reading status: {E}")
                    data = {}
        except FileNotFoundError:
            open(f"status/{self.indexer_type}.json", "w").write("")
            data = {}
        with open(f"status/{self.indexer_type}.json", "w+") as file:
            indexer_name = self.indexer_type.lower()
            if indexer_name == "username":
                data["Continue"] = c
                data["Username"] = i
                data["Offset"] = o
            elif indexer_name == "project":
                data["Continue"] = c
                data["ID"] = i
            elif indexer_name == "studio":
                data["Continue"] = c
                data["ID"] = i
            elif indexer_name == "short_username":
                data["Continue"] = c
                data["Index"] = i
            elif indexer_name == "forum":
                data["Continue"] = c
                data["CategoryIndex"] = i[0]
                data["CategoryPage"] = i[1]
                data["Page"] = i[2]
            elif indexer_name == "cloud_game":
                data["Continue"] = None
                data["ID"] = i
            elif indexer_name == "user_comments":
                data["Continue"] = None
                data["Username"] = i
            elif indexer_name == "front_page":
                data["Continue"] = None
            else:
                raise TypeError("Invalid Indexer Type!")
            file.write(json.dumps({"Data": data}))

    def get_main_user_id(self, username):
        data = self.session.get(f"{self.ScratchAPI}users/{username}/").json()
        return {str(data['id']): data['username']}

    def get_user_followers(self, username, limit=40, offset=0):
        data = self.session.get(
            f"{self.ScratchAPI}users/{username}/followers/?limit={limit}&offset={offset}").json()
        followers = {}
        try:
            for i in data:
                followers[str(i['id'])] = i['username']
        except TypeError:
            return []
        return followers

    def get_user_following(self, username, limit="40", offset=0):
        data = self.session.get(
            f"{self.ScratchAPI}users/{username}/following/?limit={limit}&offset={offset}").json()
        following = {}
        for i in data:
            try:
                following[str(i['id'])] = i['username']
            except TypeError:
                return []
        return following


class UsernameIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the first 40 followers and following of all the followers of the first 100 most popular users on Scratch
        """
        Indexer.__init__(self, indexer_type="username")

    def get_famous_scratchers(self):
        try:
            data = self.session.get(ScratchDB).json()
            usernames = []
            for i in data:
                usernames.append(i['username'])
            with open("scratch_db_cache.json", "w") as file:
                file.write(json.dumps(usernames))  # Store the cache
            return usernames
        except:  # Execute the code when Scratch DB gives an error
            self.log_error(
                message="Failed to get famous Scratchers from the ScratchDB!")
            with open("scratch_db_cache.json", "r") as file:
                data = json.loads(file.read())  # Read the cache
            self.log_message(
                message="Continuing with cached API response as there was an error...")
            return data

    def collect_user_data(self, username, offset):
        i = offset
        while True:  # Another loop to get all followers of a famous user
            data = self.get_user_followers(username, offset=i)  # Data
            if len(data) == 0:  # * Break the loop if the length of followers data is 0
                break
            self.add_data(data)  # Add the followers data
            for d in data:  # Another loop to get the follower's followers and following
                followers_d = self.get_user_followers(username=data[d])
                following_d = self.get_user_following(username=data[d])
                self.add_data(followers_d)
                self.add_data(following_d)
                time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
            self.log_message(f"Finished Offset: {i}")
            i += 40  # Increase offset
            self.update_status(i=username, o=i)  # Update the status
            time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
        self.log_success(f"Finished Indexing User: {username}")

    def start_main_loop(self):
        try:
            while self.run:
                famous_users = self.get_famous_scratchers()  # Get famous Scratchers
                with open(f'status/{self.indexer_type}.json') as file:
                    done = json.load(file)["Data"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    offset = int(done['Offset'])  # Offset
                    # Continue from the index
                    index = famous_users.index(done['Username'])
                    self.log_message(
                        f"Continuing from index: {index} and offset: {offset}")
                else:
                    offset = 0  # Offset
                    index = 0  # Index
                    self.log_message(
                        f"Starting from index: {index} and offset: {offset}")
                # Loop to get the follower data of a famous users
                while index < len(famous_users):
                    user = famous_users[index]
                    try:
                        # ----- Main script to collect the user's data -----
                        # Add the famous user data
                        self.add_data(self.get_main_user_id(user))
                        self.collect_user_data(username=user, offset=offset)
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(PROXIES) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = PROXIES[self.use_proxy]
                        self.log_message(
                            f"Current proxy failed! Using proxy index: {self.use_proxy}")
                        continue
                    index += 1  # Increase Index by 1
                    offset = 0  # Set the offset to 0
                self.update_status(i="", o=0, c=False)  # Update the status
                time.sleep(60)  # Sleep to reduce the load on Servers
                self.run = True
        except Exception as E:
            self.log_error(f"An Error Occurred: {E}")


class StudioIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the host, members and curators (and their first 40 following and followers) of the studios on Scratch
        """
        Indexer.__init__(self, indexer_type="studio")

    def start_main_loop(self):
        try:
            while self.run:
                fails = 0  # Count the number of unshared studios
                with open(f'status/{self.indexer_type}.json') as file:
                    done = json.load(file)["Data"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    studio_id = done['ID']  # Studio ID
                    self.log_message(f"Continuing from studio id: {studio_id}")
                else:
                    studio_id = 1  # Studio ID
                    self.log_message(
                        message=f"Starting from studio id: {studio_id}")
                # ----- Main script to collect the user's data by checking every studio -----
                while True:
                    try:
                        data = self.session.get(
                            f"{self.ScratchAPI}studios/{studio_id}/managers").json()
                        if type(data) != dict:
                            try:
                                studio_managers = {}
                                for d in data:
                                    studio_managers[str(
                                        d["id"])] = d["username"]
                                    followers_d = self.get_user_followers(
                                        username=d["username"])
                                    following_d = self.get_user_following(
                                        username=d["username"])
                                    self.add_data(followers_d)
                                    self.add_data(following_d)
                                self.add_data(studio_managers)
                                studio_curators = {}
                                try:
                                    data = self.session.get(
                                        f"{self.ScratchAPI}/studios/{studio_id}/curators").json()
                                    for d in data:
                                        studio_curators[str(
                                            d["id"])] = d["username"]
                                        followers_d = self.get_user_followers(
                                            username=d["username"])
                                        following_d = self.get_user_following(
                                            username=d["username"])
                                        self.add_data(followers_d)
                                        self.add_data(following_d)
                                    self.add_data(studio_curators)
                                except (KeyError, TypeError):
                                    pass
                                fails = 0
                            except KeyError:
                                fails += 1
                        if fails >= 1000 and studio_id > SCRATCH_STUDIOS:
                            studio_id -= 1000
                            fails = 0
                            self.log_message(
                                f"Starting from studio id: {studio_id} as there were 1000 fails (because those studios doesn't exist)")
                        self.log_message(f"Studio ID: {studio_id} done")
                        studio_id += 1  # Increase Index by 1
                        # Update the status
                        self.update_status(i=studio_id, c=True)
                        self.run = True
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(PROXIES) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = PROXIES[self.use_proxy]
                        self.log_message(
                            f"Current proxy failed! Using proxy index: {self.use_proxy}")
                        continue
                    # Sleep to reduce the load on Servers
                    time.sleep(WAIT_TIME)
        except Exception as E:
            self.log_error(f"An Error Occurred: {E}")


class ProjectIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the creators (and their first 40 following and followers) of projects on Scratch starting from project ID 104
        """
        Indexer.__init__(self, indexer_type="project")

    def start_main_loop(self):
        try:
            while self.run:
                fails = 0  # Count the number of unshared projects
                with open(f'status/{self.indexer_type}.json') as file:
                    done = json.load(file)["Data"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    project_id = done['ID']  # Project ID
                    self.log_message(
                        f"Continuing from project id: {project_id}")
                else:
                    project_id = 104  # Project ID
                    self.log_message(f"Starting from project id: {project_id}")
                # ----- Main script to collect the user's data by checking every project -----
                while True:
                    try:
                        data = self.session.get(
                            f"{self.ScratchAPI}projects/{project_id}").json()
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
                            fails = 0
                        except KeyError:
                            fails += 1
                        if fails >= 1000 and project_id > int(SCRATCH_PROJECTS):
                            project_id -= 1000
                            fails = 0
                            self.log_message(
                                message=f"Starting from project id: {project_id} as there were 1000 fails (because those projects were unshared)")
                        self.log_message(f"Project ID: {project_id} done")
                        project_id += 1  # Increase Index by 1
                        # Update the status
                        self.update_status(i=project_id, c=True)
                        self.run = True
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(PROXIES) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = PROXIES[self.use_proxy]
                        self.log_message(
                            message=f"Current proxy failed! Using proxy index: {self.use_proxy}")
                        continue
                    # Sleep to reduce the load on Servers
                    time.sleep(WAIT_TIME)
        except Exception as E:
            self.log_error(f"An Error Occurred: {E}")


class ShortUsernamesIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the pre-generated 3-letter short usernames (and their first 40 followers and following) on Scratch
        """
        Indexer.__init__(self, indexer_type="short_username")

    def start_main_loop(self):
        """
        import json
        import string
        all_chars = string.ascii_lowercase + string.digits + "_-"
        with open("three_letter_usernames.json", "w") as file:
            d = []
            for i in all_chars:
                for j in all_chars:
                    for k in all_chars:
                        d.append(i + j + k)
            file.write(json.dumps(d, indent=4))
        """
        while self.run:
            try:
                with open("three_letter_usernames.json", "r") as file:
                    all_short_usernames = json.loads(file.read())
                with open(f'status/{self.indexer_type}.json') as file:
                    done = json.load(file)["Data"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    index = int(done['Index'])  # Offset
                    self.log_message(f"Continuing from index: {index}")
                else:
                    index = 0  # Index
                    self.log_message(f"Starting from index: {index}")
                while index < len(all_short_usernames):
                    try:
                        username = all_short_usernames[index]
                        self.add_data(self.get_main_user_id(username))
                        self.add_data(self.get_user_followers(username))
                        self.add_data(self.get_user_following(username))
                    except:
                        pass
                    self.log_message(
                        f"Indexed short username no. {index} out of {len(all_short_usernames)}")
                    index += 1
                    self.update_status(index)
                    time.sleep(WAIT_TIME + 9)
                self.update_status(i=0, c=False)
                self.log_success("Finished indexing all Short Usernames!")
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


class ForumIndexer(Indexer):
    # TODO: Add a way to detect the errors on the Scratch Froum pages and skip that topic...
    def __init__(self):
        """
        This Indexer indexes the usernames from forum posts in the Scratch Forums.
        -> Because ScratchDB went down recently, this also stores the forum post data in an external database
        """
        Indexer.__init__(self, indexer_type="forum")
        self.forum_db = ForumDB()
        try:
            open(
                f"upserts_count/forum_db_upserts.txt", "r+")
        except FileNotFoundError:
            open(f"upserts_count/forum_db_upserts.txt",
                 "w").write("0")

    def add_forum_data(self, data):
        try:
            self.forum_db.add_post_data(data)
        except Exception as E:
            print(f"ForumDB Upsert Add Data: {E}")
        try:
            previous = int(
                open("upserts_count/forum_db_upserts.txt", "r+").read())
        except Exception as E:
            print(f"ForumDB Upsert Update: {E}")
            previous = 0
        new = len(data)
        open("upserts_count/forum_db_upserts.txt",
             "w").write(str(previous + new))

    def _crawl_category(self, category_idx, category_page=0, page=1):
        self.forum_db.connect()
        self.category_idx = category_idx
        self.category = list(ALL_FORUM_DATA.keys())[self.category_idx]
        CATEGORY_PAGES = ALL_FORUM_DATA[self.category]
        cp = category_page
        while cp < len(CATEGORY_PAGES):
            # for CATEGORY_PAGE in CATEGORY_PAGES:  # Loop through all the category pages
            CATEGORY_PAGE = CATEGORY_PAGES[cp]
            page = page  # The category page number index
            while True:  # Loop through a single category page to get the links of forum topics
                content = get(
                    f"https://scratch.mit.edu/discuss/{CATEGORY_PAGE}/?page={page}").content
                soup = BeautifulSoup(content, "html.parser")
                LINKS = []
                t = soup.find_all(attrs={"class": "tclcon"})
                if len(t) == 0:
                    break
                for main_element in t:
                    LINK = main_element.find("a")["href"]
                    LINKS.append(LINK)

                # Loop through the links (topic pages) parsed
                for link in LINKS:
                    TOPIC_ID = int(link.split("/")[-2])
                    t_page = 1
                    while True:  # Loop through a single topic page to get the posts
                        try:
                            page_content = get(
                                f"https://scratch.mit.edu{link}?page={t_page}", headers=HEADERS).content
                            s = BeautifulSoup(page_content, "html.parser")
                            CATEGORY = s.find("div", attrs={"class": "linkst"}).find_all("li")[
                                1].find("a").text
                            d = s.find_all(
                                attrs={"class": "blockpost roweven firstpost"})
                            if len(d) == 0:
                                break
                            u = {}
                            POST_DATA = []
                            for el in d:  # Loop through all the post elements to get the username
                                POST_ID = el["id"][1:]
                                username = el.find(
                                    "a", {"class": "black username"}).text
                                POST_CONTENT = str(el.find(
                                    "div", {"class": "post_body_html"}).text)[0:50000]
                                post_time = el.find(
                                    "div", {"class": "box-head"}).find("a").text
                                split1 = post_time.split(",")
                                sub_split1 = split1[0].split(" ")
                                sub_split2 = str(split1[1].strip()).split(" ")
                                month = sub_split1[0]
                                day = sub_split1[1]
                                year = sub_split2[0]
                                hour, min, sec = sub_split2[1].split(":")
                                POST_CREATED = datetime.datetime(
                                    int(year), FORUMS_MONTHS[month], int(day), int(hour), int(min), int(sec))
                                a = self.get_main_user_id(username)
                                id = list(a.keys())[0]
                                user = list(a.values())[0]
                                u[id] = user
                                POST_DATA.append({"topic_id": TOPIC_ID, "category": CATEGORY, "post_id": int(
                                    POST_ID), "post_user": user, "post_content": POST_CONTENT, "post_created": POST_CREATED})
                            self.add_forum_data(POST_DATA)
                            self.add_data(u)
                            self.update_status(
                                c=True, i=[category_idx, cp, page])
                            self.log_message(
                                f"Finished the topic page: {t_page} of the topic index: {LINKS.index(link)} of the category index: {category_idx}")
                            # Sleep to reduce the load on Scratch Servers
                            time.sleep(WAIT_TIME + 2)
                            t_page += 1  # Increase the topic page index by 1
                        except Exception as E:
                            print("FORUM INDEXER:", E)
                            break
                page += 1  # Increase the category page index by 1
            cp += 1

    def start_main_loop(self):
        while self.run:
            try:
                with open(f'status/{self.indexer_type}.json') as file:
                    done = json.load(file)["Data"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    category_index = int(done['CategoryIndex'])
                    category_page = int(done['CategoryPage'])
                    page = int(done['Page'])
                    self.log_message(
                        f"Continuing from Category Index: {category_index}, Category Page: {category_page} and page {page}")
                else:
                    category_index = 0
                    category_page = 0
                    page = 1
                    self.log_message(
                        f"Starting from Category Index: {category_index}, Category Page: {category_page} and page {page}")
                forum_category = category_index
                while forum_category < len(ALL_FORUM_DATA):
                    self._crawl_category(
                        category_idx=forum_category, category_page=category_page, page=page)
                    self.log_success(
                        f"Finished Indexing the category at index: {forum_category}")
                    forum_category += 1
                    category_page = 0
                    page = 1
                    self.update_status(
                        i=[forum_category, category_index, category_page], c=True)
            except Exception as E:
                self.log_message(f"An Error Occurred: {E}")


class CloudGameIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the usernames from the cloud data of some selected (popular cloud projects) projects pre-added to the Scratch studio: 34001844
        """
        Indexer.__init__(self, indexer_type="cloud_game")

    def _get_all_projects(self, studio_id):
        try:
            projects = []
            offset = 0
            while True:
                request = self.session.get(
                    f"{self.ScratchAPI}studios/{studio_id}/projects?limit=40&offset={offset}").json()
                if len(request) == 0:
                    break
                for d in request:
                    projects.append(d["id"])
                offset += 40
            return projects
        except Exception as E:
            self.log_error(
                f"An error occurred while fetching the projects from the studio: {E}")
            return []

    def _process_logs(self, d):
        result = {}
        for i in d:
            ud = self.get_main_user_id(i["user"])
            result[list(ud.keys())[0]] = list(ud.values())[0]
        return result

    def start_main_loop(self):
        while self.run:
            try:
                ALL_PROJECT_IDS = self._get_all_projects(
                    studio_id=CLOUD_PROJECTS_STUDIO)
                self.log_message(
                    f"Starting to index the cloud data of {len(ALL_PROJECT_IDS)} projects")
                for project in ALL_PROJECT_IDS:
                    data = self.session.get(
                        f"https://clouddata.scratch.mit.edu/logs?projectid={project}&limit=100&offset=0").json()
                    processed_data = self._process_logs(data)
                    self.add_data(processed_data)
                    self.update_status(i=project)
                    self.log_message(
                        f"Project no. {ALL_PROJECT_IDS.index(project) + 1} done")
                    time.sleep(WAIT_TIME + 2)
                self.log_success("All the projects' cloud data indexing done!")
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


class UserCommentsIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the users from top 5 comments on top 5 popular Scratch users' profiles
        """
        Indexer.__init__(self, indexer_type="user_comments")

    def start_main_loop(self):
        while self.run:
            try:
                try:
                    with open("scratch_db_cache.json", "r") as file:
                        famous_scratchers = json.loads(file.read())[0:5]
                except Exception as E:
                    self.log_error(
                        f"An error occurred while reading ScratchDB cache file: {E}")
                    # Some famous Scratchers in case there is an error...
                    famous_scratchers = [
                        "griffpatch", "ScratchCat", "Will_Wam", "griffpatch_tutor", "ceebee"]
                self.log_message("Starting the iteration...")
                for scratcher in famous_scratchers:
                    try:
                        comments = self.session.get(
                            f"https://apis.scratchconnect.eu.org/comments/user/?username={scratcher}").json()
                        if "Error" in comments:
                            self.log_message(
                                f"Ignoring the user at index '{famous_scratchers.index(scratcher)}' due to comments API error...")
                            continue
                        for comment in comments:
                            self.add_data(
                                self.get_main_user_id(comment["User"]))
                            for reply in comment["Replies"][0:3]:
                                self.add_data(
                                    self.get_main_user_id(reply["User"]))
                                time.sleep(1)
                        self.log_message(
                            f"Completed the user at index '{famous_scratchers.index(scratcher)}'...")
                        self.update_status(scratcher)
                        time.sleep(60)  # Wait for 1 minute
                    except Exception as E:
                        self.log_error(f"Error fetching comments: {E}")
                self.log_success("Completed the iteration...")
                time.sleep(180)  # Wait for 3 minutes
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


class FrontPageIndexer(Indexer):
    def __init__(self):
        """
        This Indexer indexes the creators of the front-paged projects on Scratch's front page
        """
        Indexer.__init__(self, indexer_type="front_page")

    def start_main_loop(self):
        while self.run:
            try:
                try:
                    self.log_message("Starting the iteration...")
                    data = self.session.get(
                        f"{self.ScratchAPI}proxy/featured").json()
                    try:
                        for content in data:
                            for i in data[content]:
                                self.add_data(
                                    self.get_main_user_id(i["creator"]))
                                time.sleep(1)
                    except KeyError:
                        pass
                    self.update_status(None)
                    self.log_success("Completed the iteration...")
                except json.decoder.JSONDecodeError:
                    self.log_error("API response not of expected format...")
                time.sleep(3600)  # Wait for 1 hour
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


def start_all_indexing_threads():
    """
    The function to start all the indexing threads from the 'threads' list
    """
    # threads = [UsernameIndexer(), StudioIndexer(), ProjectIndexer(), ShortUsernamesIndexer(), ForumIndexer(),
    #            CloudGameIndexer(), UserCommentsIndexer(), FrontPageIndexer()]

    # Temporarily removed the Forum Indexer to reduce the requests to the Scratch Forum pages...
    threads = [UsernameIndexer(), StudioIndexer(), ProjectIndexer(), ShortUsernamesIndexer(),
               CloudGameIndexer(), UserCommentsIndexer(), FrontPageIndexer()]

    # Add/remove the objects from the 'threads' list above to enable/disable the indexers...
    for thread in threads:
        thread.run = True
        fun = thread.start_main_loop
        Thread(target=fun).start()
