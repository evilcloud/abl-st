from calendar import c
import streamlit as st
import pandas as pd
import mongo_data
import time
from st_aggrid import AgGrid


wallets, workers, found_machines, unsafe_machines = mongo_data.data_wallets_workers()

df_wallets = pd.DataFrame(wallets)
df_workers = pd.DataFrame(workers)

df_wallets_count = df_wallets["Machine"].count()
df_workers_count = df_workers["Machine"].count()
total = df_wallets["Balance"].sum()
total_machines = df_wallets["Machine"].count() + df_workers["Machine"].count()

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
AgGrid(df_wallets)

# with col2:
st.subheader(f"Workers {df_workers_count}")
# st.dataframe(df_workers)
AgGrid(df_workers)
