import humanize
import streamlit as st
from st_aggrid import AgGrid
import requests
import pandas as pd
from st_aggrid import AgGrid
import os
import sys
from datetime import datetime, timedelta


def connect_to_api(url):
    response = requests.get(url)
    if response.status_code != 200:
        return True, response.status_code
    return False, response.json()


DETA_URL = os.environ.get("DETA_URL")
if not DETA_URL:
    print("no env var found. Exiting...")
    sys.exit(1)
err, mining = connect_to_api(DETA_URL + "mining")
if err:
    st.title("Failed to connect to API")
    st.subheader(f"Error code: {mining}")
else:
    st.title(f"Total: {mining['Total balance']:,}")
    if mining["Unknown machine names"]:
        st.warning(f"Found wallets that are not present in safe list.")
        with st.expander("See the list of unknown wallets"):
            st.table(mining["Unknown machine names"])
    if mining["Double entries"]:
        st.warning(f"Found double entries.")
        with st.expander("See double entries"):
            st.table(mining["Double entries"])
    if mining["Safe machines not found"]:
        st.warning(
            f'Found {len(mining["Safe machines not found"])} machines from in safe list not present in the current setup.'
        )
        with st.expander("See the list of missing wallets"):
            st.table(mining["Safe machines not found"])

    st.subheader(
        f"Total safe wallets in the database: {len(mining['Safe machines'])} of {len(mining['Safe machines list'])}"
    )
    online_wallets = len(
        [
            wallet
            for wallet in mining["Safe machines"]
            if wallet.get("programmatic", None)
        ]
    )
    st.subheader(f"of which programmatic (online) are: {online_wallets}")
    for entry in mining["Safe machines"]:
        if entry["updatetime"]:
            timetime = datetime.strptime(entry["updatetime"], "%Y-%m-%dT%H:%M:%S")
            since_last_upd = str(humanize.naturaldelta(datetime.utcnow() - timetime))
        else:
            since_last_upd = ""
        entry["since last update"] = since_last_upd
        del entry["updatetime"]
        # del entry["update block difference"]

    df = pd.DataFrame(mining["Safe machines"])
    st.dataframe(df)


err, ping = connect_to_api(DETA_URL + "ping")
if err:
    st.title("Failed to connect to API")
    st.subheader(f"Error code: {ping}")
else:
    over_one_hour = []
    over_12_hours = []
    over_one_day = []
    over_one_week = []
    utcnow = datetime.utcnow()
    st.header(f"Pinging live wallets")
    st.subheader(f"Total live machines: {len(ping['raw data'])}")
    for entry in ping["raw data"]:
        if entry["time"]:
            timetime = datetime.strptime(entry["time"], "%Y-%m-%dT%H:%M:%S")
            entry["since last ping"] = humanize.naturaldelta(utcnow - timetime)
            if (utcnow - timetime) > timedelta(hours=1):
                over_one_hour.append(entry)
            if (utcnow - timetime) > timedelta(hours=12):
                over_12_hours.append(entry)
            if (utcnow - timetime) > timedelta(hours=24):
                over_one_day.append(entry)
            if (utcnow - timetime) > timedelta(days=7):
                over_one_week.append(entry)
    df = pd.DataFrame(ping["raw data"])
    st.dataframe(df)
    lag_range = st.select_slider(
        "Select data lag range", options=["1h", "12h", "1d", "1w"]
    )

    if lag_range == "1h":
        if over_one_hour:
            st.warning(
                f"Found {len(over_one_hour)} wallets that have not pinged in more than 1 hour."
            )
            with st.expander("See serevers lagging one hour or over"):
                st.dataframe(over_one_hour)
        else:
            st.write("No wallets lagging one hour or over.")
    if lag_range == "12h":
        if over_12_hours:
            st.warning(
                f"Found {len(over_12_hours)} wallets that have not pinged in more than 12 hours."
            )
            with st.expander("See serevers lagging 12 hours or over"):
                st.dataframe(over_12_hours)
        else:
            st.write("No wallets lagging 12 hours or over.")
    if lag_range == "1d":
        if over_one_day:
            st.warning(
                f"Found {len(over_one_day)} wallets that have not pinged in more than 1 day."
            )
            with st.expander("See serevers lagging one day or over"):
                st.dataframe(over_one_day)
        else:
            st.write("No wallets lagging one day or over.")
    if lag_range == "1w":
        if over_one_week:
            st.warning(
                f"Found {len(over_one_week)} wallets that have not pinged in more than 1 week."
            )
            with st.expander("See serevers lagging 1 weeek or over"):
                st.dataframe(over_one_week)
        else:
            st.write("No wallets lagging 1 week or over.")
