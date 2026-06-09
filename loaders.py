import streamlit as st
import pandas as pd
import joblib


# =====================================================
# DATASETS
# =====================================================

@st.cache_data
def load_master_data():
    return pd.read_parquet("master_df.parquet")


@st.cache_data
def load_processed_data():
    return pd.read_parquet("df_processed.parquet")


# =====================================================
# MODELS
# =====================================================

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