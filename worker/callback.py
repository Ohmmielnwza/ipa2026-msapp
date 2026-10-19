"""Parts 10-12: decode a job, collect interfaces, save, then acknowledge."""

import json
import time
from datetime import datetime, timezone
from bson import json_util
from pymongo.errors import PyMongoError
from router_client import get_interfaces
from database import save_interface_status


def callback(channel, method, properties, body, db):
    router_ip = "unknown"
    try:
        job = json_util.loads(body.decode("utf-8"))
        if not isinstance(job, dict) or "_id" not in job:
            raise ValueError("Invalid router job")
        router = db.routers.find_one({"_id": job["_id"]})
        if router is None:
            print("Skipped job for removed router", flush=True)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return
        router_ip = router.get("ip", router.get("ip_address"))
        print(f"Received job for router {router_ip}", flush=True)
        interfaces = get_interfaces(
            router_ip,
            router["username"],
            router["password"],
            router.get("ssh_port", 22),
            router.get("device_type", "cisco_ios"),
        )
        save_interface_status(db, router, interfaces)
        print(json.dumps(interfaces, indent=2), flush=True)
        print(f"Stored interface status for {router_ip}", flush=True)
    except PyMongoError:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        print("MongoDB unavailable; job requeued", flush=True)
        time.sleep(3)
        return
    except Exception as error:
        try:
            db.job_errors.insert_one(
                {
                    "router_ip": router_ip,
                    "timestamp": datetime.now(timezone.utc),
                    "error_type": type(error).__name__,
                }
            )
        except PyMongoError:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(3)
            return
        print(f"Job failed for {router_ip}: {type(error).__name__}", flush=True)
    # Failed SSH jobs are recorded; the next scheduler round retries them.
    channel.basic_ack(delivery_tag=method.delivery_tag)
