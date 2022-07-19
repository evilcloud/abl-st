from functools import total_ordering
import os
import sys
import datetime
import humanize
from numpy import block
import pymongo
import json


def connect_mongodb():
    mongo_uri = os.environ.get("MONGO", None)
    if not mongo_uri:
        print("Missing MONGO environment variable")
        sys.exit(1)
    print("Connecting to mongodb...", end="")
    client = pymongo.MongoClient(mongo_uri)
    print("done")
    return client


def get_mongo_data():
    client = connect_mongodb()
    db = client.Abel
    data = db.mining.find()
    return data


def load_lost_machines():
    lost_machines = []
    lost_machines_file = "lost_machines.txt"
    if os.path.exists(lost_machines_file):
        with open(lost_machines_file, "r") as f:
            lost_machines = list(f.readlines())
    lost_machines = [x.strip() for x in lost_machines]
    return lost_machines


def process_df(data):
    wallets = []
    workers = []
    found_machines = []
    lost_machines = load_lost_machines()
    for item in data:
        current_time = datetime.datetime.utcnow()
        last_update = item.get("update_time", None)
        # block_height = str(item.get("block_height", " "))
        version = item.get("version", " ")
        timedelta = (
            humanize.naturaldelta(current_time - last_update) if last_update else ""
        )
        is_worker = item.get("cluster", None)
        if is_worker or is_worker == None:
            workers.append(
                {
                    "Machine": item["_id"],
                    "Since last update": str(timedelta),
                    "Version": version,
                }
            )
        else:
            wallets.append(
                {
                    "Machine": item["_id"],
                    "Balance": item["total_balance"],
                    "Programmatic": item["programmatic"],
                    "Since last update": str(timedelta),
                    "Version": version,
                }
            )
        if item["_id"] in lost_machines and item["programmatic"]:
            found_machines.append(item["_id"])

    return wallets, workers, found_machines


def data_wallets_workers():
    data = get_mongo_data()
    wallets, workers, found_machines = process_df(data)
    return wallets, workers, found_machines


if __name__ == "__main__":
    data_wallets_workers()
