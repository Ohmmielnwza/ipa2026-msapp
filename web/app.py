import os
from datetime import datetime, timezone
from ipaddress import ip_address

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
client = MongoClient(
    os.getenv("MONGO_URI", "mongodb://mongo:27017/"),
    serverSelectionTimeoutMS=5000,
)
db = client[os.getenv("DB_NAME", "ipa2026_db")]
routers = db["routers"]
interface_status = db["interface_status"]


def show_page(error=None, status=200):
    try:
        # Do not send stored passwords to the browser.
        data = list(routers.find({}, {"password": 0}).sort("created_at", -1))
    except PyMongoError:
        data = []
        error = (
            "Cannot connect to MongoDB. Check the mongo container and app-net network."
        )
        status = 503
    return render_template("index.html", routers=data, error=error), status


@app.get("/")
def index():
    return show_page()


@app.get("/router/<id>")
def router_detail(id):
    try:
        router_id = ObjectId(id)
    except (InvalidId, TypeError):
        return show_page("Invalid router ID.", 400)
    try:
        router = routers.find_one({"_id": router_id}, {"password": 0})
        if router is None:
            return show_page("Router not found.", 404)
        snapshots = list(
            interface_status.find(
                {
                    "router_id": router_id,
                    "source": "demo" if os.getenv("ROUTER_MODE") == "demo" else "ssh",
                }
            )
            .sort([("timestamp", -1), ("_id", -1)])
            .limit(3)
        )
    except PyMongoError:
        return show_page("Cannot read interface status from MongoDB.", 503)
    return render_template("router_detail.html", router=router, snapshots=snapshots)


@app.post("/add")
def add_router():
    router_ip = request.form.get("ip", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not router_ip or not username or not password:
        return show_page("Please enter IP address, username and password.", 400)
    try:
        router_ip = str(ip_address(router_ip))
    except ValueError:
        return show_page("Please enter a valid IPv4 or IPv6 address.", 400)
    try:
        routers.insert_one(
            {
                "ip": router_ip,
                "username": username,
                "password": password,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except PyMongoError:
        return show_page("Cannot save the router to MongoDB.", 503)
    return redirect(url_for("index"))


@app.post("/delete/<id>")
def delete_router(id):
    try:
        router_id = ObjectId(id)
    except (InvalidId, TypeError):
        return show_page("Invalid router ID.", 400)
    try:
        routers.delete_one({"_id": router_id})
    except PyMongoError:
        return show_page("Cannot delete the router from MongoDB.", 503)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
