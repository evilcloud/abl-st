from functools import total_ordering
import os
import sys
import datetime
import humanize
from numpy import block
import pymongo


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


def data_to_walletworkers(data):
    wallets = []
    workers = []
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
                    # "Block Heigth": block_height,
                    "Since last update": str(timedelta),
                    "Version": version,
                }
            )
        else:
            wallets.append(
                {
                    "Machine": item["_id"],
                    "Balance": item["total_balance"],
                    # "Block Heigth": block_height,
                    "Programmatic": item["programmatic"],
                    "Since last update": str(timedelta),
                    "Version": version,
                }
            )
    return wallets, workers


def data_wallets_workers():
    data = get_mongo_data()
    wallets, workers = data_to_walletworkers(data)
    return wallets, workers


if __name__ == "__main__":
    data_wallets_workers()
