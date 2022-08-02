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
    st.error("No environment variable found. Terminating...")
    st.stop()
    sys.exit(1)

err, mining = connect_to_api(DETA_URL + "mining")
if err:
    st.title("Failed to connect to API")
    st.subheader(f"Error code: {mining}")
else:
    st.title(f"Total: {mining['Total balance']:,}")

    # just a little fun
    # _, col1, _ = st.columns(3)
    # with col1:
    #     snow = st.button("Press here to begin")
    # if snow:
    #     st.snow()

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
    # Prep for the slider at the bottom of the page
    time_lag_options = {
        "10 seconds": timedelta(seconds=10),
        "1 minute": timedelta(minutes=1),
        "10 minutes": timedelta(minutes=10),
        "1 hour": timedelta(hours=1),
        "6 hours": timedelta(hours=6),
        "12 hours": timedelta(hours=12),
        "1 day": timedelta(days=1),
        "2 days": timedelta(days=2),
        "1 week": timedelta(weeks=1),
    }
    time_lag_data = {}
    for key in time_lag_options:
        time_lag_data[key] = []

    utcnow = datetime.utcnow()
    st.header(f"Pinging live wallets")
    st.subheader(f"Total live machines: {len(ping['raw data'])}")
    for entry in ping["raw data"]:
        entry["CPU"] = int(entry["CPU"]) if entry["CPU"] else ""
        if entry["time"]:
            timetime = datetime.strptime(entry["time"], "%Y-%m-%dT%H:%M:%S")
            entry["since last ping"] = humanize.naturaldelta(utcnow - timetime)
            for lag, delta in time_lag_options.items():
                if utcnow - timetime > delta:
                    time_lag_data[lag] += [entry]

    df = pd.DataFrame(ping["raw data"])
    st.dataframe(df)

    lag_choice = st.select_slider(
        "Select data lag range",
        options=[x for x in time_lag_options.keys() if time_lag_data[x]],
    )

    if time_lag_data[lag_choice]:
        st.warning(
            f"Found {len(time_lag_data[lag_choice])} machines that have been offline for {lag_choice} or over"
        )
        with st.expander(f"See the list of lagging machines"):
            st.dataframe(time_lag_data[lag_choice])
    else:
        st.success(f"No machines found that have been offline")

    _, col2, _ = st.columns(3)
    with col2:
        baloons = st.button("The end")
    if baloons:
        st.balloons()
