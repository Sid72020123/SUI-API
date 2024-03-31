import json
import time
import pymysql.cursors

from Config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


class DataBase:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect_server(self):
        try:
            config = {
                "host": DB_HOST,
                "port": int(DB_PORT),
                "user": DB_USERNAME,
                "password": DB_PASSWORD,
                "database": DB_NAME,
                "charset": "utf8mb4",
                "cursorclass": pymysql.cursors.DictCursor
            }
            self.connection = pymysql.connect(**config)
        except Exception as E:
            return [False, E]
        self.cursor = self.connection.cursor()
        return [True]

    def update_documents_count(self):
        q = "SELECT COUNT(*) AS count FROM data;"
        self.cursor.execute(q)
        length = self.cursor.fetchone()["count"]
        with open('count.json', 'w') as file:
            file.write(json.dumps(
                {'Count': length, 'UpdateTimestamp': time.time()}))

    def _process_data(self, data):
        processed = []
        for user_id in data:
            processed.append([int(user_id), data[user_id]])
        return processed

    def upsert_data(self, data):
        """
        Why did I use "cursor.execute()" instead of "cursor.executemany()"?
        The main reason is this:
            1. https://github.com/PyMySQL/PyMySQL/issues/506
            2. https://github.com/PyMySQL/PyMySQL/issues/898
        And pymysql library is faster than some major MySQL in Python connection libraries...
        """
        requests = self._process_data(data)
        result = []
        if not len(requests) == 0:
            for each_one in requests:
                query = f"INSERT INTO `data` (id, username) VALUES ('{each_one[0]}', '{each_one[1]}') ON DUPLICATE KEY UPDATE `username`='{each_one[1]}';"
                result.append(self.cursor.execute(query))
                self.connection.commit()
            return result
        else:
            return []

    def get_id(self, username):
        query = f"SELECT * FROM `data` WHERE `username` LIKE '{username.strip()}';"
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_username(self, id):
        query = f"SELECT * FROM `data` WHERE `id` = '{int(id)}';"
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_random(self):
        query = "SELECT * FROM `data` ORDER BY RAND() LIMIT 1;"
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_data(self, limit=1000, offset=0):
        query = f"SELECT * FROM `data` LIMIT {int(limit)} OFFSET {int(offset)};"
        self.cursor.execute(query)
        return self.cursor.fetchall()

