import streamlit as st
import pandas as pd

from loaders import load_data

master_df, df_processed = load_data()

st.set_page_config(
    layout="wide"
)
# =====================================================
# PREPARAÇÃO
# =====================================================

latest_equipment = (
    master_df
    .sort_values("CREATE_DATE", ascending=False)
    .drop_duplicates(
        subset="EQ_EQUIP_NO",
        keep="first"
    )
)

# =====================================================
# TÍTULO
# =====================================================

st.title("🔮 Manutenção Preditiva")

st.markdown("""
Esta página apresenta os resultados do modelo preditivo de manutenção.

Os equipamentos são classificados de acordo com a probabilidade
de necessitarem de reparação nos próximos 30 dias.
""")

# =====================================================
# KPIs GERAIS
# =====================================================

st.header("📌 Indicadores de Risco")

moderate = latest_equipment[
    latest_equipment["PRED_REPAIR_30D_PCT"] >= 50
]

high_risk = latest_equipment[
    latest_equipment["PRED_REPAIR_30D_PCT"] >= 70
]

critical_risk = latest_equipment[
    latest_equipment["PRED_REPAIR_30D_PCT"] >= 90
]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Risco Moderado (>50%)",
    f"{len(moderate):,}"
)

col2.metric(
    "Alto Risco (>70%)",
    f"{len(high_risk):,}"
)

col3.metric(
    "Críticos (>90%)",
    f"{len(critical_risk):,}"
)


# =====================================================
# FILTRO DEPARTAMENTO
# =====================================================

st.header("🏢 Filtrar por Departamento")

departments = sorted(
    latest_equipment[
        "DEPT_EQUIP_DEPT_NAME"
    ]
    .dropna()
    .unique()
)

selected_department = st.selectbox(
    "Departamento",
    ["Todos"] + departments
)

if selected_department == "Todos":

    filtered_df = latest_equipment.copy()

else:

    filtered_df = latest_equipment[
        latest_equipment[
            "DEPT_EQUIP_DEPT_NAME"
        ] == selected_department
    ]

# =====================================================
# TOP 20 RISCO
# =====================================================

st.header("🚨 Top 20 Equipamentos com Maior Risco")

top_risk = (
    filtered_df
    .sort_values(
        "PRED_REPAIR_30D_PCT",
        ascending=False
    )
    .head(20)
)

display_risk = top_risk[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "PRED_REPAIR_30D_PCT",
        "TOTAL_INTERVENTIONS",
        "AVG_COST_EQUIP",
        "AVG_DOWNTIME_EQUIP"
    ]
].copy()

display_risk.columns = [
    "Equipamento",
    "Departamento",
    "Risco (%)",
    "Intervenções",
    "Custo Médio",
    "Downtime Médio"
]

display_risk["Custo Médio"] = (
    display_risk["Custo Médio"]
    .apply(lambda x: f"${x:,.2f}")
)

display_risk["Downtime Médio"] = (
    display_risk["Downtime Médio"]
    .apply(lambda x: f"{x:,.2f} h")
)

st.dataframe(
    display_risk,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EXPLORADOR
# =====================================================

st.header("🔎 Explorar Equipamento")

equipment_options = sorted(
    filtered_df["EQ_EQUIP_NO"]
    .astype(str)
    .unique()
)

selected_equipment = st.selectbox(
    "Selecionar Equipamento",
    equipment_options
)

equipment_data = filtered_df[
    filtered_df["EQ_EQUIP_NO"]
    .astype(str)
    == selected_equipment
]

record = equipment_data.iloc[0]

# =====================================================
# SCORECARD
# =====================================================

st.subheader(
    f"Equipamento {selected_equipment}"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Probabilidade Reparação",
    f"{record['PRED_REPAIR_30D_PCT']:.2f}%"
)

col2.metric(
    "Failure Frequency",
    f"{record['FAILURE_FREQUENCY']:.2f}"
)

col3.metric(
    "Intervenções Totais",
    f"{int(record['TOTAL_INTERVENTIONS']):,}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Reparações Últimos 12M",
    f"{int(record['REPAIRS_LAST_12M'])}"
)

col5.metric(
    "PM Últimos 12M",
    f"{int(record['PM_LAST_12M'])}"
)

col6.metric(
    "Downtime Médio",
    f"{record['AVG_DOWNTIME_EQUIP']:.2f} h"
)

# =====================================================
# ALERTA DE RISCO
# =====================================================

risk = record["PRED_REPAIR_30D_PCT"]

if risk >= 90:

    st.error(
        f"🚨 Equipamento Crítico ({risk:.2f}%)"
    )

elif risk >= 80:

    st.warning(
        f"⚠️ Equipamento de Alto Risco ({risk:.2f}%)"
    )

elif risk >= 50:

    st.info(
        f"🔍 Equipamento a Monitorizar ({risk:.2f}%)"
    )

else:

    st.success(
        f"✅ Risco Reduzido ({risk:.2f}%)"
    )

# =====================================================
# EQUIPAMENTOS CRÍTICOS
# =====================================================

st.header("🚨 Lista de Equipamentos Alto Risco e Críticos")

critical_equipment = (
    latest_equipment[
        latest_equipment[
            "PRED_REPAIR_30D_PCT"
        ] >= 70
    ]
    .sort_values(
        "PRED_REPAIR_30D_PCT",
        ascending=False
    )
)

critical_display = critical_equipment[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "PRED_REPAIR_30D_PCT",
        "TOTAL_COST_EQUIP",
        "AVG_DOWNTIME_EQUIP"
    ]
].copy()

critical_display.columns = [
    "Equipamento",
    "Departamento",
    "Risco (%)",
    "Custo Histórico",
    "Downtime Médio"
]

critical_display["Custo Histórico"] = (
    critical_display["Custo Histórico"]
    .apply(lambda x: f"${x:,.2f}")
)

critical_display["Downtime Médio"] = (
    critical_display["Downtime Médio"]
    .apply(lambda x: f"{x:,.2f} h")
)

st.dataframe(
    critical_display,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EXPORTAÇÃO
# =====================================================

st.download_button(
    "📥 Exportar Equipamentos Alto Risco e Críticos",
    critical_equipment.to_csv(index=False),
    file_name="equipamentos_alto_risco_criticos.csv",
    mime="text/csv"
)