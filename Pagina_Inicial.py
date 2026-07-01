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

DF_PROCESSED_FILE_ID = "175BdY7k_UpuMEGPE8m9Uh2WpiJUjomnp"

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

Esta aplicação utiliza modelos de Machine Learning para apoiar a gestão da manutenção dos equipamentos da frota, permitindo identificar ativos de maior risco, analisar indicadores operacionais e simular cenários de intervenção.

---

## 📊 Fleet Overview

Apresenta uma visão global da frota através de indicadores de desempenho, custos, downtime e distribuição dos equipamentos.

Nesta página poderá consultar:

- Indicadores gerais da frota
- Distribuição dos equipamentos por departamento
- Equipamentos com mais intervenções
- Equipamentos com maior custo de manutenção
- Equipamentos com maior downtime médio
- Histórico operacional de cada equipamento

---

## 🔧 Manutenção Preditiva

Permite identificar equipamentos com maior probabilidade de necessitarem de reparação nos próximos 30 dias, explorar cada ativo e consultar os principais indicadores de risco.

Nesta página poderá:

- Consultar a probabilidade de reparação nos próximos 30 dias
- Identificar equipamentos de alto risco e críticos
- Filtrar os resultados por departamento
- Explorar indicadores individuais de cada equipamento
- Exportar a lista de equipamentos prioritários para manutenção

---

## 🕹️ Simulador de Impacto

Permite simular diferentes cenários de manutenção e estimar o custo esperado e a classe de downtime prevista para uma nova intervenção.

Nesta página poderá:

- Configurar diferentes cenários de intervenção
- Alterar os parâmetros da próxima ordem de trabalho
- Estimar o custo previsto da intervenção
- Prever a classe de downtime esperada
- Comparar os resultados da simulação com a situação atual
- Guardar e exportar os cenários simulados""")


