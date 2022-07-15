import os
import redis
import time
import streamlit as st
import plotly.express as px
import pandas as pd

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

def show_all_wallets_donut(current):
    fig = px.pie(
    hole = 0.3,
    names = current.keys(),
    values = current.values(),
)
    st.plotly_chart(fig)

def show_total_numbers(total, current):
    st.title(f"Total: {total:,}")
    st.subheader(f"Wallets: {len(current)}")


r = connect_redis()
machines = r.keys()
total = 0
current = {}
st.title("ABL")

data_load_state = st.text("Loading data")
bar = st.progress(0)
for i, machine in enumerate(sorted(machines)):
    bar.progress((i+1)/len(machines))
    curr_key = machine.decode("utf-8").split(".")[0]
    curr_value = int(r.get(machine))
    current[curr_key] = curr_value
    print(f"{curr_key}: {curr_value:,}")
    total += curr_value
st.spinner(" ")

print(f"{total:,}")
print(current)

show_total_numbers(total, current)
# show_all_wallets_donut(current)
st.write(current)

time.sleep(10)
