import os
import json
from requests import Session

API_KEY = os.environ["API_KEY"] # The API Key of MongoDB
APP_ID = os.environ["APP_ID"] # The APP ID of MongoDB
URL = f"https://data.mongodb-api.com/app/{APP_ID}/endpoint/data/v1/action/"


class API:
    def __init__(self) -> None:
        self.session = Session()
        self.session.headers = {
            "Content-Type": "application/json",
            "Access-Control-Request-Headers": "*",
            "api-key": API_KEY,
            "User-Agent": "API :P"
        }

    def count_all_documents(self) -> int:
        payload = json.dumps(
            {
                "collection": "data",
                "database": "SUI",
                "dataSource": "SUI",
                "pipeline": [{"$count": "total_count"}],
            }
        )
        response = self.session.post(f"{URL}aggregate", data=payload)
        return response.json()["documents"][0]["total_count"]

    def get_random_data(self) -> dict:
        payload = json.dumps(
            {
                "collection": "data",
                "database": "SUI",
                "dataSource": "SUI",
                "pipeline": [{"$sample": {"size": 1}}],
            }
        )
        response = self.session.post(f"{URL}aggregate", data=payload)
        return response.json()["documents"][0]

    def find_id(self, username: str) -> dict:
        payload = json.dumps(
            {
                "collection": "data",
                "database": "SUI",
                "dataSource": "SUI",
                "projection": {"_id": 1, "Username": 1},
                "filter": {"Username": {"$regex": f"^{username}$", "$options": "i"}},
            }
        )
        response = self.session.post(f"{URL}findOne", data=payload)
        return response.json()["document"]

    def find_username(self, id: int) -> dict:
        payload = json.dumps(
            {
                "collection": "data",
                "database": "SUI",
                "dataSource": "SUI",
                "projection": {"_id": 1, "Username": 1},
                "filter": {"_id": id},
            }
        )
        response = self.session.post(f"{URL}findOne", data=payload)
        return response.json()["document"]

    def get_data(self, limit: int, offset: int) -> list:
        payload = json.dumps(
            {
                "collection": "data",
                "database": "SUI",
                "dataSource": "SUI",
                "pipeline": [
                    {"$project": {"_id": 1, "Username": 1}},
                    {"$skip": offset},
                    {"$limit": limit},
                ],
            }
        )
        response = self.session.post(f"{URL}aggregate", data=payload)
        return response.json()["documents"]
