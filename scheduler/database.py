"""Read router documents from the same database as the web application."""

import os

from bson import json_util
from pymongo import MongoClient


def get_router_info():
    with MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000) as client:
        return list(client[os.getenv("DB_NAME", "ipa2026_db")]["routers"].find())


if __name__ == "__main__":
    # Avoid printing router passwords to the terminal.
    documents = get_router_info()
    for document in documents:
        document.pop("password", None)
    print(json_util.dumps(documents, indent=2))
