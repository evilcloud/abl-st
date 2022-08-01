import streamlit as st
import pandas as pd
import time
from st_aggrid import AgGrid
import processor
import os
import sys
import deta_data

deta_key = os.environ.get("DETA_KEY")
wallet_db_name = os.environ.get("WALLET_DB_NAME")
ping_db_name = os.environ.get("PING_DB_NAME")
if not deta_key and not wallet_db_name or not ping_db_name:
    print("Initiating data missing. Exiting...")
    sys.exit(0)

current_safe_wallets, recovered_wallets, unidentified_wallets = processor.get_wallets(
    wallet_db_name
)
ping_machines = processor.get_ping_machines(ping_db_name)

current_safe_wallets = processor.replace_updatetime_updatediff(current_safe_wallets)
current_safe_wallets = processor.clean_wallets(current_safe_wallets)
current_safe_wallets = processor.clean_wrong_update_amount(current_safe_wallets)
ping_machines = processor.clean_ping(ping_machines)

wallets = pd.DataFrame(current_safe_wallets)
pings = pd.DataFrame(ping_machines)


st.title("ABEL")

st.write(f"last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")

total = 0
total_machines = 0


refresh = st.button("Refresh now")

st.title(f"Total: ")
st.write(f"###### Total machines: {len(pings)}")

if recovered_wallets:
    st.subheader("Recovered wallets: {len(recovered_wallets)}")
    st.warning(
        f"Found wallets are in the 'safe list', but need to be removed manually from the 'lost list' to be added to the totals!"
    )
    st.table(recovered_wallets)

if unidentified_wallets:
    st.subheader("Unidentified wallets: {len(unidentified_wallets)}")
    st.warning(f"Found wallets that are not present in any list.")
    st.table(unidentified_wallets)


# st.subheader(f"Wallets {len(current_safe_wallets)}")
st.subheader(f"Wallets")
AgGrid(wallets)

st.subheader(f"Ping times")
AgGrid(pings)
