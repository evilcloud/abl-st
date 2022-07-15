import os
import redis
import time
import streamlit as st


def connect_redis():
    redis_connect = None
    redis_pass = os.environ.get("REDIS", None)
    redis_host = os.environ.get("REDIS_HOST", None)
    redis_port = os.environ.get("REDIS_PORT", None)
    if redis_pass and redis_host and redis_port:
        print("Redis validators positive. Connecting to Redis")
        for attempt in range(3):
            print(f"Connecting to Redis. Attempt {attempt +1}")
            try:
                redis_connect = redis.Redis(host=redis_host,
                                            port=redis_port, password=redis_pass)
                print("Redis connected successfully")
                break
            except Exception:
                time.sleep(2)
                print("Redis connect failed")
    return redis_connect


r = connect_redis()
machines = r.keys()
total = 0
current = {}
for machine in sorted(machines):
    value = int(r.get(machine))
    current[machine.decode("utf-8")] = value
    print(f"{machine.decode('utf-8').strip('.local')}: {value:,}")
    total += value
print(f"{total:,}")
print(current)
