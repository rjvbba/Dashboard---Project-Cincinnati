import streamlit as st
import pandas as pd

from loaders import load_data

master_df, df_processed = load_data()

# =====================================================
# TÍTULO
# =====================================================

st.set_page_config(
    layout="wide"
)

st.title("📊 Fleet Overview")

st.markdown("""
Esta página apresenta uma visão global da frota municipal de Cincinnati.

Aqui poderá analisar:

- Indicadores gerais da frota
- Custos operacionais
- Downtime dos equipamentos
- Equipamentos com maior risco
- Histórico individual de cada ativo
""")

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
# KPIS
# =====================================================

st.header("📌 Indicadores Gerais")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Equipamentos",
    f"{master_df['EQ_EQUIP_NO'].nunique():,}"
)

col2.metric(
    "Intervenções",
    f"{master_df['UNIQUE_WORK_ORDER_NO'].nunique():,}"
)

col3.metric(
    "Custo Total",
    f"${master_df['TOTAL_COST'].sum():,.0f}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Custo Médio",
    f"${master_df['TOTAL_COST'].mean():,.0f}"
)

col5.metric(
    "Downtime Médio",
    f"{master_df['DOWNTIME_HRS_USER'].mean()/24:,.0f} Dias"
)

col6.metric(
    "Risco Médio Reparação a 30D",
    f"{latest_equipment['PRED_REPAIR_30D_PCT'].mean():,.0f}%"
)

# =====================================================
# TOP INTERVENÇÕES
# =====================================================

st.header("🔧 Top 10 Equipamentos com Mais Intervenções")

top_repairs = (
    latest_equipment
    .sort_values(
        "TOTAL_INTERVENTIONS",
        ascending=False
    )
    .head(10)
)

display_repairs = top_repairs[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "TOTAL_INTERVENTIONS",
        "TOTAL_COST_EQUIP",
        "AVG_DOWNTIME_EQUIP"
    ]
].copy()

display_repairs.columns = [
    "Equipamento",
    "Departamento",
    "Intervenções",
    "Custo Total",
    "Downtime Médio"
]

display_repairs["Custo Total"] = (
    display_repairs["Custo Total"]
    .apply(lambda x: f"${x:,.0f}")
)

display_repairs["Downtime Médio"] = (
    display_repairs["Downtime Médio"]
    .apply(lambda x: f"{x/24:,.0f} DIas")
)

st.dataframe(
    display_repairs,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# TOP CUSTOS
# =====================================================

st.header("💰 Top 10 Equipamentos com Maior Custo")

top_cost = (
    latest_equipment
    .sort_values(
        "TOTAL_COST_EQUIP",
        ascending=False
    )
    .head(10)
)

display_cost = top_cost[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "TOTAL_COST_EQUIP"
    ]
].copy()

display_cost.columns = [
    "Equipamento",
    "Departamento",
    "Custo Total"
]

display_cost["Custo Total"] = (
    display_cost["Custo Total"]
    .apply(lambda x: f"${x:,.0f}")
)

st.dataframe(
    display_cost,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# TOP DOWNTIME
# =====================================================

st.header("⏱️ Top 10 Equipamentos com Maior Downtime")

top_downtime = (
    latest_equipment
    .sort_values(
        "AVG_DOWNTIME_EQUIP",
        ascending=False
    )
    .head(10)
)

display_downtime = top_downtime[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "AVG_DOWNTIME_EQUIP"
    ]
].copy()

display_downtime.columns = [
    "Equipamento",
    "Departamento",
    "Downtime Médio"
]

display_downtime["Downtime Médio"] = (
    display_downtime["Downtime Médio"]
    .apply(lambda x: f"{x/24:,.2f} Dias")
)

st.dataframe(
    display_downtime,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# DEPARTAMENTOS
# =====================================================

st.header("🏢 Equipamentos por Departamento")

dept_summary = (
    latest_equipment
    .groupby("DEPT_EQUIP_DEPT_NAME")
    .size()
    .sort_values(ascending=False)
)

st.bar_chart(dept_summary)

# =====================================================
# EXPLORADOR
# =====================================================

st.header("🔎 Explorador de Equipamentos")

equipment_list = sorted(
    latest_equipment["EQ_EQUIP_NO"]
    .astype(str)
    .unique()
)

equipment = st.selectbox(
    "Selecionar Equipamento",
    equipment_list
)

equipment_df = master_df[
    master_df["EQ_EQUIP_NO"]
    .astype(str) == equipment
]

latest_record = equipment_df.iloc[0]

# =====================================================
# RESUMO
# =====================================================

st.subheader(f"Equipamento {equipment}")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Departamento",
    latest_record["DEPT_EQUIP_DEPT_NAME"]
)

col2.metric(
    "Intervenções",
    int(latest_record["TOTAL_INTERVENTIONS"])
)

col3.metric(
    "Risco 30 Dias",
    f"{latest_record['PRED_REPAIR_30D_PCT']:.0f}%"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Custo Total",
    f"${latest_record['TOTAL_COST_EQUIP']:,.0f}"
)

col5.metric(
    "Custo Médio",
    f"${latest_record['AVG_COST_EQUIP']:,.0f}"
)

col6.metric(
    "Downtime Médio",
    f"{latest_record['AVG_DOWNTIME_EQUIP']/24:,.0f} Dias"
)

# =====================================================
# FILTRO ANO
# =====================================================

st.subheader("📅 Filtro Temporal")

anos_disponiveis = sorted(
    equipment_df["WORK_ORDER_YR"]
    .dropna()
    .unique()
)

ano_selecionado = st.selectbox(
    "Selecionar Ano",
    ["Todos"] + list(anos_disponiveis)
)

if ano_selecionado != "Todos":

    equipment_df_filtered = equipment_df[
        equipment_df["WORK_ORDER_YR"] == ano_selecionado
    ]

else:

    equipment_df_filtered = equipment_df.copy()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Intervenções no Período",
    len(equipment_df_filtered)
)

col2.metric(
    "Custo no Período",
    f"${equipment_df_filtered['TOTAL_COST'].sum():,.0f}"
)

col3.metric(
    "Downtime no Período",
    f"{equipment_df_filtered['DOWNTIME_HRS_USER'].sum()/24:,.0f} Dias"
)
# =====================================================
# HISTÓRICO
# =====================================================

st.subheader("🛠️ Histórico de Intervenções")

history = (
    equipment_df_filtered
    .sort_values(
        "CREATE_DATE",
        ascending=False
    )
    [
        [
            "CREATE_DATE",
            "WORK_ORDER_YR",
            "JOB_TYPE",
            "WORK_ORDER_STATUS",
            "PRI_PRIORITY_CODE",
            "TOTAL_COST",
            "DOWNTIME_HRS_USER"
        ]
    ]
    .head(50)
)

history = history.rename(
    columns={
        "CREATE_DATE": "Data",
        "WORK_ORDER_YR": "Ano",
        "JOB_TYPE": "Tipo",
        "WORK_ORDER_STATUS": "Estado",
        "PRI_PRIORITY_CODE": "Prioridade",
        "TOTAL_COST": "Custo",
        "DOWNTIME_HRS_USER": "Downtime"
    }
)

history["Data"] = pd.to_datetime(
    history["Data"]
).dt.strftime("%d/%m/%Y")

history["Custo"] = history["Custo"].apply(
    lambda x: f"${x:,.0f}"
)

history["Downtime"] = history["Downtime"].apply(
    lambda x: f"{x/24:,.0f} Dias"
)

st.dataframe(
    history,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EXPORTAR HISTÓRICO
# =====================================================

export_history = history.copy()

st.download_button(
    "📥 Exportar Histórico do Equipamento",
    export_history.to_csv(index=False),
    file_name=(
        f"historico_{equipment}_"
        f"{ano_selecionado}.csv"
    ),
    mime="text/csv"
)
