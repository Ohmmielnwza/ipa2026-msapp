"""Publish router jobs every 60 seconds for the Week08 lab."""

import argparse
import os
import time
from datetime import datetime

from bson import json_util

from database import get_router_info
from producer import produce


def scheduler(runs=None):
    interval = float(os.getenv("INTERVAL", "60"))
    if interval <= 0:
        raise ValueError("INTERVAL must be positive")
    next_run = time.monotonic()
    count = 0
    host = os.getenv("RABBITMQ_HOST", "localhost")
    while runs is None or count < runs:
        now = datetime.now().astimezone().isoformat(timespec="milliseconds")
        print(f"[{now}] run #{count}", flush=True)
        try:
            documents = get_router_info()
            for document in documents:
                produce(host, json_util.dumps(document).encode("utf-8"))
            print(f"Published {len(documents)} router jobs", flush=True)
        except Exception as error:
            # Error type is enough for logs; connection errors may include credentials.
            print(f"Run failed: {type(error).__name__}; retry on next run", flush=True)
            time.sleep(3)
        count += 1
        if runs is not None and count >= runs:
            break
        next_run += interval
        time.sleep(max(0.0, next_run - time.monotonic()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs", type=int, help="Stop after N rounds for lab verification"
    )
    args = parser.parse_args()
    if args.runs is not None and args.runs < 1:
        parser.error("--runs must be at least 1")
    try:
        scheduler(args.runs)
    except KeyboardInterrupt:
        print("Scheduler stopped", flush=True)
