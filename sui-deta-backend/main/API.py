import json
from requests import Session

URL = f"http://63073.site.bot-hosting.net"

class API:
    def __init__(self, p) -> None:
        self.p = p
        self.session = Session()

    def get_random_data(self) -> dict:
        response = self.session.get(f"{URL}/random?password={self.p}")
        return response.json()["Data"]

    def find_id(self, username: str) -> dict:
        response = self.session.get(f"{URL}/get_id?username={username}&password={self.p}")
        return response.json()["Data"]

    def find_username(self, id: int) -> dict:
        response = self.session.get(f"{URL}/get_user?id={id}&password={self.p}")
        return response.json()["Data"]

    def get_data(self, limit: int, offset: int) -> list:
        response = self.session.get(f"{URL}/data?limit={limit}&offset={offset}&password={self.p}")
        return response.json()["Data"]
