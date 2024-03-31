# ----- Imports -----
import json
import time
from requests import Session
from requests import get
from bs4 import BeautifulSoup
from pyEventLogger import pyLogger
from threading import Thread

from DataBase import DataBase
from Config import HEADERS, ScratchDB, PROXIES, WAIT_TIME, SCRATCH_PROJECTS, SCRATCH_STUDIOS, ALL_FORUM_DATA, \
    CLOUD_PROJECTS_STUDIO

# ----- Log Formatting -----
format_string = "[indexer_type] [time] [log_type] [message]"
info_format_color = "[bold cyan black][bold yellow black][bold magenta black][normal #FFFFFF black]"
success_format_color = "[bold cyan black][bold yellow black][bold green black][bold #FFFFFF black]"
error_format_color = "[bold cyan black][bold #FF0000 black][bold red black][bold #FF0000 black]"


class Indexer:
    def __init__(self, indexer_type):
        self.run = False
        self.indexer_type = str(indexer_type).upper()

        self.logger = pyLogger(colored_output=True,
                               make_file=True,
                               file_name=f"logs/{self.indexer_type}",
                               rewrite_file=False, file_logs=["SUCCESS", "ERROR"])
        self.logger.format_log(log_type=["INFO", "SUCCESS", "ERROR"], format_string=format_string)
        self.logger.format_log_color(log_type="INFO", format_string=info_format_color)
        self.logger.format_log_color(log_type="SUCCESS", format_string=success_format_color)
        self.logger.format_log_color(log_type="ERROR", format_string=error_format_color)

        self.db_object = DataBase()
        is_connected = self.db_object.connect_server()
        if not is_connected[0]:
            self.log_error(f"Couldn't connect the external server: {is_connected[1]}")
            exit()
        self.log_success("Successfully connected the external server!")
        self.db = self.db_object

        self.URL = PROXIES[0]
        self.use_proxy = 0
        self.ScratchAPI = PROXIES[self.use_proxy]

        self.session = Session()
        self.session.headers = HEADERS

    def log_message(self, message):
        self.logger.info(message=message, indexer_type=self.indexer_type)

    def log_success(self, message):
        self.logger.success(message=message, indexer_type=self.indexer_type)

    def log_error(self, message):
        self.logger.error(message=message, indexer_type=self.indexer_type, include_error_message=True)

    def _update_upserts_count(self, c):
        old = None
        tries = 0
        while tries < 2:
            with open(f"upserts_count/{self.indexer_type.lower()}_upserts.txt", "r") as file:
                try:
                    old = int(file.read())
                except Exception as E:
                    print(E)
                    old = 0
                    tries += 1
                    continue
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
        with open("status.json", "r") as file:
            data = json.load(file)
        with open("status.json", "w") as file:
            if self.indexer_type.lower() == "username":
                data["Username"]["Continue"] = c
                data["Username"]["Username"] = i
                data["Username"]["Offset"] = o
            elif self.indexer_type.lower() == "project":
                data["Project"]["Continue"] = c
                data["Project"]["ID"] = i
            elif self.indexer_type.lower() == "studio":
                data["Studio"]["Continue"] = c
                data["Studio"]["ID"] = i
            elif self.indexer_type.lower() == "short_username":
                data["ShortUsername"]["Continue"] = c
                data["ShortUsername"]["Index"] = i
            elif self.indexer_type.lower() == "forum":
                data["Forum"]["Continue"] = c
                data["Forum"]["CategoryIndex"] = i[0]
                data["Forum"]["CategoryPage"] = i[1]
                data["Forum"]["Page"] = i[2]
            elif self.indexer_type.lower() == "cloud_game":
                data["CloudGame"]["ID"] = i
            else:
                raise TypeError("Invalid Indexer Type!")
            file.write(json.dumps(data))

    def get_main_user_id(self, username):
        data = self.session.get(f"{self.ScratchAPI}users/{username}/").json()
        return {str(data['id']): data['username']}

    def get_user_followers(self, username, limit=40, offset=0):
        data = self.session.get(f"{self.ScratchAPI}users/{username}/followers/?limit={limit}&offset={offset}").json()
        followers = {}
        try:
            for i in data:
                followers[str(i['id'])] = i['username']
        except TypeError:
            return []
        return followers

    def get_user_following(self, username, limit="40", offset=0):
        data = self.session.get(f"{self.ScratchAPI}users/{username}/following/?limit={limit}&offset={offset}").json()
        following = {}
        for i in data:
            try:
                following[str(i['id'])] = i['username']
            except TypeError:
                return []
        return following


class UsernameIndexer(Indexer):
    def __init__(self):
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
                with open('status.json') as file:
                    done = json.load(file)["Username"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    offset = int(done['Offset'])  # Offset
                    index = famous_users.index(done['Username'])  # Continue from the index
                    self.log_message(f"Continuing from index: {index} and offset: {offset}")
                else:
                    offset = 0  # Offset
                    index = 0  # Index
                    self.log_message(f"Starting from index: {index} and offset: {offset}")
                while index < len(famous_users):  # Loop to get the follower data of a famous users
                    user = famous_users[index]
                    try:
                        # ----- Main script to collect the user's data -----
                        self.add_data(self.get_main_user_id(user))  # Add the famous user data
                        self.collect_user_data(username=user, offset=offset)
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(PROXIES) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = PROXIES[self.use_proxy]
                        self.log_message(f"Current proxy failed! Using proxy index: {self.use_proxy}")
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
        Indexer.__init__(self, indexer_type="studio")

    def start_main_loop(self):
        try:
            while self.run:
                fails = 0  # Count the number of unshared studios
                with open('status.json') as file:
                    done = json.load(file)["Studio"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    studio_id = done['ID']  # Studio ID
                    self.log_message(f"Continuing from studio id: {studio_id}")
                else:
                    studio_id = 1  # Studio ID
                    self.log_message(message=f"Starting from studio id: {studio_id}")
                # ----- Main script to collect the user's data by checking every studio -----
                while True:
                    try:
                        data = self.session.get(f"{self.ScratchAPI}studios/{studio_id}/managers").json()
                        if type(data) != dict:
                            try:
                                studio_managers = {}
                                for d in data:
                                    studio_managers[str(d["id"])] = d["username"]
                                    followers_d = self.get_user_followers(username=d["username"])
                                    following_d = self.get_user_following(username=d["username"])
                                    self.add_data(followers_d)
                                    self.add_data(following_d)
                                self.add_data(studio_managers)
                                studio_curators = {}
                                try:
                                    data = self.session.get(f"{self.ScratchAPI}/studios/{studio_id}/curators").json()
                                    for d in data:
                                        studio_curators[str(d["id"])] = d["username"]
                                        followers_d = self.get_user_followers(username=d["username"])
                                        following_d = self.get_user_following(username=d["username"])
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
                        self.update_status(i=studio_id, c=True)  # Update the status
                        self.run = True
                    # ----- Change the Proxy if one of those gives an error -----
                    except ValueError:
                        p = self.use_proxy + 1
                        if p > len(PROXIES) - 1:
                            p = 0
                        self.use_proxy = p
                        self.ScratchAPI = PROXIES[self.use_proxy]
                        self.log_message(f"Current proxy failed! Using proxy index: {self.use_proxy}")
                        continue
                    time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
        except Exception as E:
            self.log_error(f"An Error Occurred: {E}")


class ProjectIndexer(Indexer):
    def __init__(self):
        Indexer.__init__(self, indexer_type="project")

    def start_main_loop(self):
        try:
            while self.run:
                fails = 0  # Count the number of unshared projects
                with open('status.json') as file:
                    done = json.load(file)["Project"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    project_id = done['ID']  # Project ID
                    self.log_message(f"Continuing from project id: {project_id}")
                else:
                    project_id = 104  # Project ID
                    self.log_message(f"Starting from project id: {project_id}")
                # ----- Main script to collect the user's data by checking every project -----
                while True:
                    try:
                        data = self.session.get(f"{self.ScratchAPI}projects/{project_id}").json()
                        try:
                            project_author = data["author"]["username"]
                            self.add_data({str(data["author"]['id']): project_author})
                            followers_d = self.get_user_followers(username=project_author)
                            following_d = self.get_user_following(username=project_author)
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
                        self.update_status(i=project_id, c=True)  # Update the status
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
                    time.sleep(WAIT_TIME)  # Sleep to reduce the load on Servers
        except Exception as E:
            self.log_error(f"An Error Occurred: {E}")


class ShortUsernamesIndexer(Indexer):
    def __init__(self):
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
                with open('status.json') as file:
                    done = json.load(file)["ShortUsername"]
                if done['Continue']:  # If the script breaks in between and has to continue
                    index = int(done['Index'])  # Offset
                    self.log_message(f"Continuing from index: {index}")
                else:
                    index = 0  # Index
                    self.log_message(f"Starting from index: {index}")
                while index < len(all_short_usernames):
                    try:
                        self.add_data(self.get_main_user_id(all_short_usernames[index]))
                    except:
                        pass
                    self.log_message(f"Indexed short username no. {index} out of {len(all_short_usernames)}")
                    index += 1
                    self.update_status(index)
                    time.sleep(WAIT_TIME + 9)
                self.update_status(i=0, c=False)
                self.log_success("Finished indexing all Short Usernames!")
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


class ForumIndexer(Indexer):
    def __init__(self):
        Indexer.__init__(self, indexer_type="forum")

    def _crawl_category(self, category_idx, category_page=0, page=1):
        self.category_idx = category_idx
        self.category = list(ALL_FORUM_DATA.keys())[self.category_idx]
        CATEGORY_PAGES = ALL_FORUM_DATA[self.category]
        cp = category_page
        while cp < len(CATEGORY_PAGES):
            # for CATEGORY_PAGE in CATEGORY_PAGES:  # Loop through all the category pages
            CATEGORY_PAGE = CATEGORY_PAGES[cp]
            page = page  # The category page number index
            while True:  # Loop through a single category page to get the links of forum topics
                content = get(f"https://scratch.mit.edu/discuss/{CATEGORY_PAGE}/?page={page}").content
                soup = BeautifulSoup(content, "html.parser")
                LINKS = []
                t = soup.find_all(attrs={"class": "tclcon"})
                if len(t) == 0:
                    break
                for main_element in t:
                    LINK = main_element.find("a")["href"]
                    LINKS.append(LINK)

                for link in LINKS:  # Loop through the links (topic pages) parsed
                    t_page = 1
                    while True:  # Loop through a single topic page to get the posts
                        try:
                            page_content = get(f"https://scratch.mit.edu{link}?page={t_page}", headers=HEADERS).content
                            s = BeautifulSoup(page_content, "html.parser")
                            d = s.find_all(attrs={"class": "blockpost roweven firstpost"})
                            if len(d) == 0:
                                break
                            u = {}
                            for el in d:  # Loop through all the post elements to get the username
                                username = el.find("a", {"class": "black username"}).text
                                a = self.get_main_user_id(username)
                                id = list(a.keys())[0]
                                user = list(a.values())[0]
                                u[id] = user
                            self.add_data(u)
                            self.update_status(c=True, i=[category_idx, cp, page])
                            self.log_message(
                                f"Finished the topic page: {t_page} of the topic index: {LINKS.index(link)} of the category index: {category_idx}")
                            time.sleep(WAIT_TIME + 2)  # Sleep to reduce the load on Scratch Servers
                            t_page += 1  # Increase the topic page index by 1
                        except Exception as E:
                            print("FORUM INDEXER:", E)
                            break
                page += 1  # Increase the category page index by 1
            cp += 1

    def start_main_loop(self):
        while self.run:
            try:
                with open('status.json') as file:
                    done = json.load(file)["Forum"]
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
                    self._crawl_category(category_idx=forum_category, category_page=category_page, page=page)
                    self.log_success(f"Finished Indexing the category at index: {forum_category}")
                    forum_category += 1
                    category_page = 0
                    page = 1
                    self.update_status(i=[forum_category, category_index, category_page], c=True)
            except Exception as E:
                self.log_message(f"An Error Occurred: {E}")


class CloudGameIndexer(Indexer):
    def __init__(self):
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
            self.log_error(f"An error occurred while fetching the projects from the studio: {E}")
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
                ALL_PROJECT_IDS = self._get_all_projects(studio_id=CLOUD_PROJECTS_STUDIO)
                self.log_message(f"Starting to index the cloud data of {len(ALL_PROJECT_IDS)} projects")
                for project in ALL_PROJECT_IDS:
                    data = self.session.get(
                        f"https://clouddata.scratch.mit.edu/logs?projectid={project}&limit=100&offset=0").json()
                    processed_data = self._process_logs(data)
                    self.add_data(processed_data)
                    self.update_status(i=project)
                    self.log_message(f"Project no. {ALL_PROJECT_IDS.index(project) + 1} done")
                    time.sleep(WAIT_TIME + 2)
                self.log_success("All the projects' cloud data indexing done!")
            except Exception as E:
                self.log_error(f"An Error Occurred: {E}")


def start_all_indexing_threads():
    threads = [UsernameIndexer(), StudioIndexer(), ProjectIndexer(), ShortUsernamesIndexer(), ForumIndexer(),
               CloudGameIndexer()]
    for thread in threads:
        thread.run = True
        fun = thread.start_main_loop
        Thread(target=fun).start()
