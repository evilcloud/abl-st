import os
import sys
import datetime
import humanize
from numpy import block
import deta_data


def load_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
    return [x.strip() for x in lines]


def load_lost_machines():
    lost_machines = []
    lost_machines_file = "lost_machines.txt"
    lost_machines = load_file(lost_machines_file)
    return lost_machines


def load_safe_machines():
    safe_machines = []
    safe_machines_file = "safe_machines.txt"
    safe_machines = load_file(safe_machines_file)
    return safe_machines


def get_wallets():
    wallets = deta_data.Detadb("ABEL_MINING")
    # lost_machines = load_lost_machines()
    # lost = []
    # for item in wallets:
    #     if item("key") in lost_machines:
    #         lost.append(item)
    #         wallets.remove(item)
    return wallets


def get_ping():
    ping = deta_data.Detadb("ABEL_PING")
    return ping


def add_time_diff(data):
    for item in data:
        current_time = datetime.datetime.utcnow()
        last_update = item.get("updatetime", None)
        timedelta = (
            humanize.naturaldelta(current_time - last_update) if last_update else ""
        )
        item["since last update"] = timedelta
    return data


def process_df(data):
    wallets = []
    workers = []
    found_machines = []
    unsafe_machines = []
    lost_machines = load_lost_machines()
    safe_machines = load_safe_machines()
    for item in data:
        machine = item["_id"]
        current_time = datetime.datetime.utcnow()
        last_update = item.get("update_time", None)
        timedelta = (
            humanize.naturaldelta(current_time - last_update) if last_update else ""
        )
        # block_height = str(item.get("block_height", " "))
        version = item.get("version", " ")
        is_worker = item.get("cluster", None)
        entry = {
            "Machine": machine,
            "Balance": item.get("total_balance", " "),
            "Programmatic": item.get("programmatic"),
            "Last block": item.get("block_height", " "),
            "Since last update": str(timedelta),
            "Version": version,
        }
        if is_worker or is_worker == None:
            workers.append(entry)
        else:
            if machine in safe_machines:
                wallets.append(entry)
            else:
                unsafe_machines.append(entry)
        if machine in lost_machines and item["programmatic"]:
            found_machines.append(machine)

    return wallets, workers, found_machines, unsafe_machines


def data_wallets_workers():
    data = get_mongo_data()
    wallets, workers, found_machines, unsafe_machines = process_df(data)
    return wallets, workers, found_machines, unsafe_machines


if __name__ == "__main__":
    data_wallets_workers()
