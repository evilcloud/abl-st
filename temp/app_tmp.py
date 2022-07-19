import os
import time
import datetime
import humanize
import streamlit as st
import plotly.express as px
import pandas as pd
from pymongo import MongoClient


def connect_mongo():
    mongo_client = None
    mongo_line = os.environ.get("MONGO", None)
    if mongo_line:
        print("Mongo validators positive. Connecting to MongoDB")
        for attempt in range(3):
            print(f"Connecting to MongoDB. Attempt {attempt +1}")
            try:
                mongo_client = MongoClient(mongo_line)
                print("MongoDB connected successfully")
                break
            except Exception:
                time.sleep(2)
                print("MongoDB connect failed")
    return mongo_client


def show_all_wallets_donut(current):
    fig = px.pie(
        hole=0.3,
        names=current.keys(),
        values=current.values(),
    )
    st.plotly_chart(fig)


def show_all_table(current):
    df = pd.DataFrame(current.items(), columns=["Wallet", "Balance"])
    st.table(df)


def machines_info(mdata):
    machines_cluster = []
    machines_primary = []
    current_time = datetime.datetime.utcnow()
    for machine in mdata:
        cluster = machine.get("cluster", None)
        try:
            timedelta = humanize.naturaldelta(current_time - machine["update_time"])
        except Exception:
            timedelta = "N/A"
        if cluster or cluster == None:
            print(machine)
            machines_cluster.append(
                {
                    "Machine": machine["_id"],
                    "State": machine["programmatic"],
                    "Since last update": str(timedelta),
                }
            )
            print("Cluster: ", machine["_id"])
        else:
            machines_primary.append(
                {
                    "Machine": machine["_id"],
                    "State": machine["programmatic"],
                    "Balance": machine["total_balance"],
                    "Since last update": str(timedelta),
                }
            )
            print("Primary: ", machine["_id"])
    print(machines_cluster)
    df_cluster = pd.DataFrame(machines_cluster)
    df_primary = pd.DataFrame(machines_primary)
    return (df_primary, df_cluster)


mongo_connection = connect_mongo()
mdb = mongo_connection.Abel
mdata = mdb.mining.find()
df_primary, df_cluster = machines_info(mdata)


total = 0
st.title(f"ABEL")

st.write(f"last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")

total = df_primary["Balance"].sum()
st.title(f"Total: {total:,}")
st.write(
    f"###### Total machines: {df_primary['Machine'].count() + df_cluster['Machine'].count()}"
)

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Wallets {df_primary['Machine'].count()}")
    df_prim_formated = df_primary
    # df_prim_thousand['Balance'] = df_primary['Balance'].apply('{:,}'.format)
    # df_prim_formated['Machine'] = df_prim_formated['Machine'].split(".")[0]
    st.dataframe(df_prim_formated)

with col2:
    st.subheader(f"Workers {df_cluster['Machine'].count()}")
    st.dataframe(df_cluster)

# show_all_wallets_donut(current)

# st.write(current)

# time.sleep(10)
