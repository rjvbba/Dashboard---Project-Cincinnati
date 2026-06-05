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
# EXECUTAR SIMULAÇÃO
# =====================================================

if st.button("▶️ Executar Simulação"):

    simulation_row = selected_processed.copy()

    simulation_row["JOB_TYPE_REPAIR"] = (
        1 if job_type == "REPAIR" else 0
    )

    simulation_row["WORK_ORDER_YR"] = work_year

    simulation_row["CREATE_MONTH"] = create_month

    simulation_row["PRI_PRIORITY_CODE"] = priority

    # ==========================================
    # INPUTS DOS MODELOS
    # ==========================================

    downtime_input = pd.DataFrame(
        [simulation_row[downtime_features]]
    )

    cost_input = pd.DataFrame(
        [simulation_row[cost_features]]
    )

    # ==========================================
    # PREVISÕES
    # ==========================================

    predicted_downtime = (
        downtime_model.predict(
            downtime_input
        )[0]
    )

    predicted_cost = (
        cost_model.predict(
            cost_input
        )[0]
    )

    # ==========================================
    # MAPEAR CLASSE DE DOWNTIME
    # ==========================================

    downtime_str = str(predicted_downtime).upper()

    if downtime_str in ["0", "NORMAL"]:

        downtime_class = "NORMAL"
        downtime_icon = "✅"

        downtime_description = (
            "Downtime esperado inferior a 168 horas."
        )

    elif downtime_str in ["1", "MODERATE"]:

        downtime_class = "MODERADO"
        downtime_icon = "⚠️"

        downtime_description = (
            "Downtime esperado entre 168 e 720 horas."
        )

    else:

        downtime_class = "CRÍTICO"
        downtime_icon = "🚨"

        downtime_description = (
            "Downtime esperado superior a 720 horas."
        )

    # ==========================================
    # PROBABILIDADES
    # ==========================================

    st.header("🔮 Resultados da Simulação")

    try:

        probabilities = (
            downtime_model
            .predict_proba(downtime_input)[0]
        )

        prob_df = pd.DataFrame({

            "Classe": [
                "NORMAL",
                "MODERADO",
                "CRÍTICO"
            ],

            "Probabilidade": [
                round(prob * 100, 2)
                for prob in probabilities
            ]
        })

    except:

        prob_df = None

    # ==========================================
    # RESULTADOS PRINCIPAIS
    # ==========================================

    col1, col2 = st.columns(2)

    col1.metric(
        "Classe de Downtime Prevista",
        f"{downtime_icon} {downtime_class}"
    )

    col2.metric(
        "Custo Previsto",
        f"${predicted_cost:,.2f}"
    )

    st.info(
        downtime_description
    )

    # ==========================================
    # PROBABILIDADES POR CLASSE
    # ==========================================

    if prob_df is not None:

        st.subheader(
            "🎯 Probabilidade por Classe"
        )

        st.dataframe(
            prob_df,
            use_container_width=True,
            hide_index=True
        )

    # ==========================================
    # COMPARAÇÃO
    # ==========================================

    st.subheader(
        "📊 Comparação com Situação Atual"
    )

    comparison = pd.DataFrame({

        "Indicador": [

            "Intervenções",

            "Custo Médio Atual",

            "Custo Previsto",

            "Classe Prevista"
        ],

        "Valor": [

            int(
                selected_master[
                    "TOTAL_INTERVENTIONS"
                ]
            ),

            f"${selected_master['AVG_COST_EQUIP']:,.2f}",

            f"${predicted_cost:,.2f}",

            downtime_class
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================
    # INTERPRETAÇÃO AUTOMÁTICA
    # ==========================================

    st.subheader(
        "🧠 Interpretação Automática"
    )

    current_cost = (
        selected_master[
            "AVG_COST_EQUIP"
        ]
    )

    delta_cost = (
        predicted_cost
        - current_cost
    )

    if delta_cost > 0:

        st.warning(
            f"Prevê-se um aumento de ${delta_cost:,.2f} relativamente ao histórico."
        )

    else:

        st.success(
            f"Prevê-se uma redução de ${abs(delta_cost):,.2f} relativamente ao histórico."
        )

    if downtime_class == "CRÍTICO":

        st.error(
            "Risco elevado de indisponibilidade prolongada."
        )

    elif downtime_class == "MODERADO":

        st.warning(
            "Risco moderado de downtime."
        )

    else:

        st.success(
            "Baixo risco operacional."
        )

    # ==========================================
    # EXPORTAR
    # ==========================================

    export_df = pd.DataFrame({

        "Equipamento": [
            equipment
        ],

        "Departamento": [
            selected_master[
                "DEPT_EQUIP_DEPT_NAME"
            ]
        ],

        "Tipo_Trabalho": [
            job_type
        ],

        "Ano": [
            work_year
        ],

        "Mes": [
            create_month
        ],

        "Prioridade": [
            priority
        ],

        "Classe_Downtime": [
            downtime_class
        ],

        "Custo_Previsto": [
            round(predicted_cost, 2)
        ]
    })

    st.download_button(
        "📥 Exportar Simulação",
        export_df.to_csv(
            index=False
        ),
        file_name=f"simulacao_{equipment}.csv",
        mime="text/csv"
    )