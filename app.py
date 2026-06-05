#Bibliotecas

import streamlit as st
import joblib
import pandas as pd
import gdown
import os

# =====================================================
# CONFIGURAÇÃO STREAMLIT
# =====================================================

st.set_page_config(
    page_title="Cincinnati Fleet Dashboard",
    page_icon="🚚",
    layout="wide"
)

#Importação de datasets e pkl

# =====================================================
# GOOGLE DRIVE FILE IDS
# =====================================================

MASTER_FILE_ID = "1_6rqblhCDduCD7zeRPV4_wS7ggl6MaUa"

DF_PROCESSED_FILE_ID = "1EgYt6ZGIDtPwAi1w5-9UsKQh2vMFIpeA"

# =====================================================
# DOWNLOAD DATASETS (APENAS UMA VEZ)
# =====================================================

if not os.path.exists("master_df.pkl"):

    gdown.download(
        f"https://drive.google.com/uc?id={MASTER_FILE_ID}",
        "master_df.pkl",
        quiet=False
    )

if not os.path.exists("df_processed.pkl"):

    gdown.download(
        f"https://drive.google.com/uc?id={DF_PROCESSED_FILE_ID}",
        "df_processed.pkl",
        quiet=False
    )

# =====================================================
# DATASETS
# =====================================================

master_df = pd.read_pickle(
    "master_df.pkl"
)

df_processed = pd.read_pickle(
    "df_processed.pkl"
)

# =====================================================
# MODELOS
# =====================================================

downtime_model = joblib.load(
    "downtime_model.pkl"
)

cost_model = joblib.load(
    "cost_model.pkl"
)

# =====================================================
# FEATURES
# =====================================================

downtime_features = joblib.load(
    "downtime_features.pkl"
)

cost_features = joblib.load(
    "cost_features.pkl"
)

# =====================================================
# TESTE
# =====================================================

st.success("Todos os ficheiros carregados com sucesso")

st.write("Master DF:", master_df.shape)

st.write("Processed DF:", df_processed.shape)

st.write("Downtime Features:", len(downtime_features))

st.write("Cost Features:", len(cost_features))

# =====================================================
# CACHE DATASETS
# =====================================================
@st.cache_data
def load_data():

    master_df = pd.read_pickle(
        "master_df.pkl"
    )

    df_processed = pd.read_pickle(
        "df_processed.pkl"
    )

    return master_df, df_processed

# =====================================================
# CACHE MODELOS
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

# =====================================================
# lOADING
# =====================================================

master_df, df_processed = load_data()

(
    downtime_model,
    cost_model,
    downtime_features,
    cost_features
) = load_models()

#Páginas


st.title(
    "🚚 Cincinnati Fleet Dashboard"
)

st.markdown("""
Welcome to the Cincinnati Fleet Predictive Maintenance Platform.

Use the menu on the left to navigate through the dashboard.
""")
