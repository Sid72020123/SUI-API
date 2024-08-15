"""
SUI API - Forums DataBase
--------------------

This file contains the code for database connection and other functions used by the forum indexer thread

--------------------
Author: @Sid72020123 on Github
"""

from Config import COCKROACH_DB_LINK
import psycopg

UPSERT_QUERY = """INSERT INTO posts (topic_id, category, post_id, post_user, post_content, post_created) VALUES (%(topic_id)s, %(category)s, %(post_id)s, %(post_user)s, %(post_content)s, %(post_created)s) ON CONFLICT (post_id) DO UPDATE SET topic_id = %(topic_id)s, category = %(category)s, post_id = %(post_id)s, post_user = %(post_user)s, post_content = %(post_content)s, post_created = %(post_created)s, last_updated = NOW();"""

"""
Query to Create Table:

CREATE TABLE posts (
  topic_id INT NOT NULL, 
  category VARCHAR(50) NOT NULL,
  post_id INT PRIMARY KEY NOT NULL UNIQUE,
  post_user VARCHAR(30) NOT NULL,
  post_content VARCHAR(50000),
  post_created TIMESTAMP NOT NULL,
  last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class ForumDB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg.connect(COCKROACH_DB_LINK)
        self.cursor = self.connection.cursor()

    def add_post_data(self, data: list):
        try:
            for d in data:
                self.cursor.execute(UPSERT_QUERY, d)
            self.connection.commit()
            return True
        except Exception as E:
            print(f"ForumsDB Add Data: {E}")
            return False

    def find_posts(self, q, l=10, o=0):
        try:
            FIND_QUERY = f"""SELECT * FROM posts WHERE post_content LIKE '%{q}%' LIMIT {l} OFFSET {o};"""
            self.cursor.execute(FIND_QUERY)
            raw = self.cursor.fetchall()
            result = []
            for r in raw:
                topic_id, category, post_id, post_user, post_content, post_created, last_updated = r
                result.append({"post_id": post_id, "category": category, "topic_id": topic_id, "post_user": post_user,
                               "post_content_text": post_content, "post_created": post_created.timestamp(), "last_updated": last_updated.timestamp()})
            return [True, result]
        except Exception as E:
            return [False, E]
