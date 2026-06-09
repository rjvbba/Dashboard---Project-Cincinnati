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

MASTER_FILE_ID = "1Xvl1QRJ5qznJQiRYaWkFTI-kDqBd1n0f"

DF_PROCESSED_FILE_ID = "1twRI0-1IowIcGpvlMPjaIz-3uDQ5nNPa"

# =====================================================
# DOWNLOAD DATASETS (APENAS UMA VEZ)
# =====================================================

if not os.path.exists("master_df.parquet"):
    gdown.download(
        f"https://drive.google.com/uc?id={MASTER_FILE_ID}",
        "master_df.parquet",
        quiet=False
    )

if not os.path.exists("df_processed.parquet"):
    gdown.download(
        f"https://drive.google.com/uc?id={DF_PROCESSED_FILE_ID}",
        "df_processed.parquet",
        quiet=False
    )

# =====================================================
# DATASETS
# =====================================================

master_df = pd.read_parquet("master_df.parquet")
df_processed = pd.read_parquet("df_processed.parquet")

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
# CACHE DATASETS
# =====================================================

@st.cache_data
def load_data():

    master_df = pd.read_parquet(
        "master_df.parquet"
    )

    df_processed = pd.read_parquet(
        "df_processed.parquet"
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
# LOADING
# =====================================================

master_df, df_processed = load_data()

(
    downtime_model,
    cost_model,
    downtime_features,
    cost_features
) = load_models()

#Páginas


st.title("🚛 Dashboard de Manutenção Preditiva da Frota de Cincinnati")

st.markdown("""
Bem-vindo à plataforma de análise e manutenção preditiva da frota municipal de Cincinnati.

Este dashboard utiliza modelos de Machine Learning para apoiar a tomada de decisão na gestão de equipamentos, permitindo identificar riscos de avaria, estimar custos de reparação e prever tempos de indisponibilidade.

---

## 📊 Fleet Overview

Visão global da frota.

Nesta página poderá consultar:

- Indicadores-chave da frota
- Equipamentos com maior risco de intervenção
- Estatísticas de custo e downtime
- Resumo operacional da frota

---

## 🔧 Manutenção Preditiva

Análise individual de equipamentos.

Nesta página poderá:

- Pesquisar equipamentos específicos
- Consultar histórico resumido
- Visualizar probabilidade de reparação nos próximos 30 dias
- Analisar métricas operacionais relevantes

---

## 📈 Simulador de Impacto

Ferramenta de apoio à decisão.

Nesta página poderá:

- Simular novas intervenções
- Introduzir parâmetros operacionais
- Estimar downtime esperado
- Estimar custo previsto de reparação""")
