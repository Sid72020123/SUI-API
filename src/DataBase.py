import json
import time
import pymongo

from pymongo import UpdateOne

from Config import PASSWORD

class DataBase:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect_server(self):
        try:
            # f"mongodb://localhost:27017/"
            self.client = pymongo.MongoClient(
                f"mongodb+srv://SUI:{PASSWORD}@sui.3k3k5.mongodb.net/?retryWrites=true&w=majority")
        except pymongo.errors.ConfigurationError as E:
            return [False, E]
        self.db = self.client['SUI']
        self.collection = self.db['data']
        return [True]

    def update_documents_count(self):
        length = self.collection.count_documents({})
        with open('count.json', 'w') as file:
            file.write(json.dumps({'Count': length, 'UpdateTimestamp': time.time()}))

    def _process_data(self, data):
        processed = []
        for user_id in data:
            processed.append(
                UpdateOne({"_id": user_id}, {"$set": {"_id": user_id, "Username": data[user_id]}}, upsert=True))
        return processed

    def upsert_data(self, data):
        requests = self._process_data(data)
        if not len(requests) == 0:
            result = self.collection.bulk_write(requests, ordered=False)
            return result.bulk_api_result
        else:
            return {}
