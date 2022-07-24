from calendar import c
import streamlit as st
import pandas as pd
import time
from st_aggrid import AgGrid
import processor
import deta_data
import os


wallet_db_name = os.environ.get("WALLET_DB_NAME", None)
ping_db_name = os.environ.get("PING_DB_NAME", None)

# wallets, workers, found_machines, unsafe_machines = mongo_data.data_wallets_workers()
wallets = pd.DataFrame(processor.get_wallets())
ping = pd.DataFrame(processor.get_ping())
found_machines = 0
unsafe_machines = 0

# df_wallets_count = wallets["Machine"].count()
# df_workers_count = ping["Machine"].count()
# total = wallets["Balance"].sum()
# total_machines = ping["Machine"].count()

st.markdown(
    """
<style>
.big-font {
    font-size:10vw !important;
    font-weight:bold !important;
}
</style>
""",
    unsafe_allow_html=True,
)


st.title("ABEL")

st.write(f"last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")

total = 0
total_machines = 0
df_wallets_count = 0
df_workers_count = 0

refresh = st.button("Refresh now")

st.title(f"Total:")
st.markdown(f'<p class="big-font">{total:,}</p>', unsafe_allow_html=True)
st.write(f"###### Total machines: {total_machines}")

if found_machines:
    st.warning(f"Found {len(found_machines)} lost machines. Total may be inaccurate!")
    st.table(found_machines)

if unsafe_machines:
    st.warning(f"Found {len(unsafe_machines)} unsafe machines. Not included in Total!")
    st.table(unsafe_machines)

# col1, col2 = st.columns(2)
# with col1:
st.subheader(f"Wallets {df_wallets_count}")


# st.dataframe(df_wallets)
AgGrid(wallets)

# with col2:
st.subheader(f"Workers {df_workers_count}")
# st.dataframe(df_workers)
AgGrid(ping)
