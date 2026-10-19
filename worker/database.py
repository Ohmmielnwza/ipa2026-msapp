"""Part 12: save one timestamped snapshot for each successful router job."""

import os
from datetime import datetime, timezone
from pymongo import MongoClient


def connect_database():
    client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000)
    return client, client[os.getenv("DB_NAME", "ipa2026_db")]


def save_interface_status(db, router, interfaces):
    return db.interface_status.insert_one(
        {
            "router_id": router["_id"],
            "router_ip": router.get("ip", router.get("ip_address")),
            "timestamp": datetime.now(timezone.utc),
            "interfaces": interfaces,
            "source": os.getenv("ROUTER_MODE", "ssh"),
        }
    )
