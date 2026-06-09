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
# CENÁRIOS GUARDADOS
# =====================================================

if "simulations" not in st.session_state:
    st.session_state.simulations = []

if "last_simulation" not in st.session_state:
    st.session_state.last_simulation = None

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

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Intervenções",
    int(selected_master["TOTAL_INTERVENTIONS"])
)

col2.metric(
    "Custo Médio",
    f"${selected_master['AVG_COST_EQUIP']:,.0f}"
)

col3.metric(
    "Downtime Médio (horas)",
    f"{selected_master['AVG_DOWNTIME_EQUIP']:,.0f} h"
)

col4.metric(
    "Downtime Médio (dias)",
    f"{selected_master['AVG_DOWNTIME_EQUIP'] / 24:,.0f} dias"
)

col5.metric(
    "Risco Atual Reparação 30 Dias",
    f"{selected_master['PRED_REPAIR_30D_PCT']:.0f}%"
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
        4,
        int(selected_processed["PRI_PRIORITY_CODE"])
    )

    st.caption(
        "1 = Urgente | 2 = Prioritário | 3 = Baixa Prioridade | 4 = Não Prioritário"
    )

# =====================================================
# EXECUTAR SIMULAÇÃO
# =====================================================

run_simulation = st.button(
    "▶️ Executar Simulação"
)

if run_simulation:

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
            "Downtime esperado inferior a 168 horas (até 7 dias)."
        )

    elif downtime_str in ["1", "MODERATE"]:

        downtime_class = "MODERADO"
        downtime_icon = "⚠️"

        downtime_description = (
            "Downtime esperado entre 168 e 720 horas (7 a 30 dias)."
        )

    else:

        downtime_class = "CRÍTICO"
        downtime_icon = "🚨"

        downtime_description = (
            "Downtime esperado superior a 720 horas (mais de 30 dias)."
        )

    # ==========================================
    # RESULTADOS
    # ==========================================

    st.header("🔮 Resultados da Simulação")

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

            f"${selected_master['AVG_COST_EQUIP']:,.0f}",

            f"${predicted_cost:,.0f}",

            downtime_class
        ]
    })

    st.dataframe(
        comparison,
        width="stretch",
        hide_index=True
    )

    # ==========================================
    # GUARDAR SIMULAÇÃO
    # ==========================================

    st.session_state.last_simulation = {

        "Equipamento": equipment,

        "Departamento":
        selected_master[
            "DEPT_EQUIP_DEPT_NAME"
        ],

        "Tipo Trabalho":
        job_type,

        "Ano":
        work_year,

        "Mês":
        create_month,

        "Prioridade":
        priority,

        "Intervenções":
        int(
            selected_master[
                "TOTAL_INTERVENTIONS"
            ]
        ),

        "Risco 30 Dias":
        round(
            selected_master[
                "PRED_REPAIR_30D_PCT"
            ],
            2
        ),

        "Classe Downtime":
        downtime_class,

        "Custo Previsto":
        round(
            predicted_cost,
            2
        )
    }

# =====================================================
# ÚLTIMA SIMULAÇÃO
# =====================================================

if st.session_state.last_simulation is not None:

    st.markdown("---")

    st.subheader(
        "📌 Última Simulação"
    )

    last_df = pd.DataFrame(
        [st.session_state.last_simulation]
    )

    st.dataframe(
        last_df,
        width="stretch",
        hide_index=True
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "➕ Adicionar Cenário",
            key="save_last_simulation"
        ):

            st.session_state.simulations.append(
                st.session_state.last_simulation.copy()
            )

            st.success(
                "Cenário adicionado com sucesso."
            )

    with col2:

        st.download_button(
            "📥 Exportar Última Simulação",
            last_df.to_csv(index=False),
            file_name="ultima_simulacao.csv",
            mime="text/csv"
        )

# ==========================================
# CENÁRIOS GUARDADOS
# ==========================================

if len(st.session_state.simulations) > 0:

    st.markdown("---")

    st.header(
        "📚 Cenários Guardados"
    )

    scenarios_df = pd.DataFrame(
        st.session_state.simulations
    )

    st.dataframe(
        scenarios_df,
        width="stretch",
        hide_index=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📥 Exportar Todos os Cenários",
            scenarios_df.to_csv(index=False),
            file_name="cenarios_simulados.csv",
            mime="text/csv"
        )

    with col2:

        if st.button(
            "🗑️ Limpar Cenários"
        ):

            st.session_state.simulations = []

            st.rerun()