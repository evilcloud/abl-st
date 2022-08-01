import os
import sys
import datetime
import humanize
from numpy import block
import deta_data
from dataclasses import dataclass


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


def call_db_list(db_name):
    db = deta_data.Detadb(db_name)
    ret = db.entries_obj.items
    return ret


def get_wallets(wallet_db_name):
    """
    Get all wallets from Deta, match against 'lost wallets' list and return the wallets present,
    wallets that deemed to have been lost, but now found,
    and wallets that are deemed to be safe but missing in the current query
    """
    # wallets = deta_data.Detadb(wallet_db_name)
    # unidentified_wallets = wallets.entries.items
    unidentified_wallets = call_db_list(wallet_db_name)
    lost_wallets = load_lost_machines()
    safe_wallets = load_safe_machines()
    recovered_wallets = []
    current_safe_wallets = []
    for item in unidentified_wallets:
        print(item["key"], "... ", end="")
        if item["key"] in lost_wallets:
            print("lost wallet")
            recovered_wallets.append(item)
            unidentified_wallets.remove(item)
        elif item["key"] in safe_wallets:
            print("safe wallet")
            current_safe_wallets.append(item)
            unidentified_wallets.remove(item)
        else:
            print("unknown")
    return current_safe_wallets, recovered_wallets, unidentified_wallets


def get_ping_machines(ping_db_name):
    ping = call_db_list(ping_db_name)
    return ping


def replace_updatetime_updatediff(data):
    for item in data:
        current_time = datetime.datetime.utcnow()
        last_update = item.get("updatetime", None)
        if last_update:
            last_update = datetime.datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S")
            timedelta = humanize.naturaldelta(current_time - last_update)
        else:
            timedelta = None
        item["since last update"] = timedelta
        del item["updatetime"]
    return data


def clean_wrong_update_amount(data):
    for item in data:
        update_amount = item['update amount']
        if item["balance"] == update_amount:
            update_amount = " "
    return data


def annull_if_equal(data, base, match):
    for item in data:
        if item[base] == item[match]:
            item[match] = " "
    return data


def clean_wallets(data):
    a = annull_if_equal(data, "balance", "update amount")
    b = annull_if_equal(a, "block", "update block difference")
    return annull_if_equal(b, "block", "update block difference")


def clean_ping(data):
    return annull_if_equal(data, "block", "blocks since last")


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



if __name__ == "__main__":
    data_wallets_workers()
