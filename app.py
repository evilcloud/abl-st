import streamlit as st
import pandas as pd
import mongo_data
import time

# from st_aggrid import AgGrid

wallets, workers = mongo_data.data_wallets_workers()

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

st.title(f"Total:")
st.markdown(f'<p class="big-font">{total:,}</p>', unsafe_allow_html=True)
st.write(f"###### Total machines: {total_machines}")

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Wallets {df_wallets_count}")
    # AgGrid(df_wallets)
    st.dataframe(df_wallets)
    # df_wallets_form = df_wallets
    # df_prim_thousand['Balance'] = df_primary['Balance'].apply('{:,}'.format)
    # df_prim_formated['Machine'] = df_prim_formated['Machine'].split(".")[0]
    # st.dataframe(df_wallets_form)

with col2:
    st.subheader(f"Workers {df_workers_count}")
    st.dataframe(df_workers)
