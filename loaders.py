import streamlit as st
import pandas as pd
import joblib

@st.cache_data
def load_data():

    master_df = pd.read_pickle(
        "master_df.pkl"
    )

    df_processed = pd.read_pickle(
        "df_processed.pkl"
    )

    return master_df, df_processed


@st.cache_resource
def load_models():

    downtime_model = joblib.load(
        "downtime_model.pkl"
    )

    cost_model = joblib.load(
        "cost_model.pkl"
    )

    downtime_features = joblib.load(
        "downtime_features.pkl"
    )

    cost_features = joblib.load(
        "cost_features.pkl"
    )

    return (
        downtime_model,
        cost_model,
        downtime_features,
        cost_features
    )