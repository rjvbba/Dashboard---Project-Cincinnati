import streamlit as st
import pandas as pd

from utils.loaders import load_data

master_df, df_processed = load_data()

st.title("Fleet Overview")

st.write("Fleet KPIs and risk overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Equipments",
    master_df["EQ_EQUIP_NO"].nunique()
)

col2.metric(
    "Work Orders",
    len(master_df)
)

col3.metric(
    "Average Cost",
    round(master_df["AVG_COST_EQUIP"].mean(), 2)
)

col4.metric(
    "Average Downtime",
    round(master_df["AVG_DOWNTIME_EQUIP"].mean(), 2)
)