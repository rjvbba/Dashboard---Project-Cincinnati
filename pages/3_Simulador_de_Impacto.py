import streamlit as st
import pandas as pd

from loaders import load_data, load_models


st.set_page_config(
    layout="wide"
)
# =====================================================
# LOAD
# =====================================================

master_df, df_processed = load_data()

(
    downtime_model,
    cost_model,
    downtime_features,
    cost_features
) = load_models()

# =====================================================
# PREPARAÇÃO
# =====================================================

latest_master = (
    master_df
    .sort_values(
        "CREATE_DATE",
        ascending=False
    )
    .drop_duplicates(
        subset="EQ_EQUIP_NO",
        keep="first"
    )
)

latest_processed = (
    df_processed
    .drop_duplicates(
        subset="EQ_EQUIP_NO",
        keep="first"
    )
)

# =====================================================
# TÍTULO
# =====================================================

st.title("🧮 Simulador de Impacto")

st.markdown("""
Esta ferramenta permite simular o impacto esperado de uma intervenção.

O utilizador pode alterar algumas características da próxima ordem de trabalho
e observar o impacto esperado em:

- Downtime
- Custo
""")

# =====================================================
# EQUIPAMENTO
# =====================================================

equipment_options = (
    latest_master
    .sort_values("EQ_EQUIP_NO")
    .apply(
        lambda row:
        f"{row['EQ_EQUIP_NO']} | {row['DEPT_EQUIP_DEPT_NAME']}",
        axis=1
    )
)

selected = st.selectbox(
    "Selecione um equipamento",
    equipment_options
)

equipment = selected.split(" | ")[0]

selected_master = (
    latest_master[
        latest_master["EQ_EQUIP_NO"].astype(str)
        == equipment
    ]
    .iloc[0]
)

selected_processed = (
    latest_processed[
        latest_processed["EQ_EQUIP_NO"].astype(str)
        == equipment
    ]
    .iloc[0]
    .copy()
)

# =====================================================
# SITUAÇÃO ATUAL
# =====================================================

st.header("📋 Situação Atual")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Intervenções",
    int(selected_master["TOTAL_INTERVENTIONS"])
)

col2.metric(
    "Custo Médio",
    f"${selected_master['AVG_COST_EQUIP']:,.2f}"
)

col3.metric(
    "Downtime Médio",
    f"{selected_master['AVG_DOWNTIME_EQUIP']:,.2f} h"
)

# =====================================================
# CENÁRIO
# =====================================================

st.header("⚙️ Configuração da Simulação")

col1, col2 = st.columns(2)

with col1:

    job_type = st.selectbox(
        "Tipo de Trabalho",
        ["REPAIR", "PM"]
    )

    work_year = st.number_input(
        "Ano da Ordem",
        min_value=2007,
        max_value=2026,
        value=int(
            selected_processed["WORK_ORDER_YR"]
        )
    )

with col2:

    create_month = st.slider(
        "Mês",
        1,
        12,
        int(
            selected_processed["CREATE_MONTH"]
        )
    )

    priority = st.slider(
        "Prioridade",
        1,
        5,
        int(
            selected_processed["PRI_PRIORITY_CODE"]
        )
    )

# =====================================================
# EXECUTAR
# =====================================================

if st.button("▶️ Executar Simulação"):

    simulation_row = selected_processed.copy()

    simulation_row["JOB_TYPE_REPAIR"] = (
        1 if job_type == "REPAIR" else 0
    )

    simulation_row["WORK_ORDER_YR"] = work_year

    simulation_row["CREATE_MONTH"] = create_month

    simulation_row["PRI_PRIORITY_CODE"] = priority

    # =================================================
    # DOWNTIME
    # =================================================

    downtime_input = pd.DataFrame(
        [simulation_row[downtime_features]]
    )

    predicted_downtime = (
        downtime_model
        .predict(downtime_input)[0]
    )

    # =================================================
    # COST
    # =================================================

    cost_input = pd.DataFrame(
        [simulation_row[cost_features]]
    )

    predicted_cost = (
        cost_model
        .predict(cost_input)[0]
    )

    
    # =================================================
    # RESULTADOS
    # =================================================

    st.header("🔮 Resultados da Simulação")

    col1, col2 = st.columns(2)

    col1.metric(
        "Downtime Previsto",
        f"{predicted_downtime:,.2f} h"
    )

    col2.metric(
        "Custo Previsto",
        f"${predicted_cost:,.2f}"
    )

  

    # =================================================
    # EXPORTAÇÃO
    # =================================================

    simulation_export = pd.DataFrame({

        "Equipamento": [equipment],

        "Tipo_Trabalho": [job_type],

        "Ano": [work_year],

        "Mes": [create_month],

        "Prioridade": [priority],

        "Downtime_Previsto": [predicted_downtime],

        "Custo_Previsto": [predicted_cost]
    })

    st.download_button(
        "📥 Exportar Simulação",
        simulation_export.to_csv(index=False),
        file_name=f"simulacao_{equipment}.csv",
        mime="text/csv"
    )


