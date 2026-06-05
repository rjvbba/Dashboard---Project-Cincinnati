import streamlit as st
import pandas as pd

from utils.loaders import load_data

master_df, df_processed = load_data()

st.title("Fleet Overview")

st.markdown("""
Esta página apresenta uma visão global da frota municipal de Cincinnati,
incluindo indicadores operacionais, custos, downtime e equipamentos com
maior risco de intervenção.
""")

st.write("Fleet KPIs and risk overview")


# =====================================================
# KPIs GERAIS DA FROTA
# =====================================================

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
    "Custo Total da Frota",
    f"${master_df['TOTAL_COST'].sum():,.2f}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Custo Médio por Intervenção",
    f"${master_df['TOTAL_COST'].mean():,.2f}"
)

col5.metric(
    "Downtime Médio",
    f"{master_df['DOWNTIME_HRS_USER'].mean():,.2f} h"
)

col6.metric(
    "Reparações Últimos 12 Meses",
    f"{master_df['REPAIRS_LAST_12M'].sum():,.0f}"
)

# =====================================================
# ÚLTIMO REGISTO DE CADA EQUIPAMENTO
# =====================================================

latest_equipment = (
    master_df
    .drop_duplicates(
        subset="EQ_EQUIP_NO",
        keep="first"
    )
)

# =====================================================
# TOP 10 MAIS INTERVENÇÕES
# =====================================================

top_repairs = (
    latest_equipment
    .sort_values(
        "TOTAL_INTERVENTIONS",
        ascending=False
    )
    .head(10)
    .reset_index(drop=True)
)

display_repairs = top_repairs[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "TOTAL_INTERVENTIONS",
        "TOTAL_COST_EQUIP",
        "AVG_DOWNTIME_EQUIP"
    ]
].rename(
    columns={
        "EQ_EQUIP_NO": "Equipamento",
        "DEPT_EQUIP_DEPT_NAME": "Departamento",
        "TOTAL_INTERVENTIONS": "Intervenções",
        "TOTAL_COST_EQUIP": "Custo Total",
        "AVG_DOWNTIME_EQUIP": "Downtime Médio"
    }
)

display_repairs["Custo Total"] = (
    display_repairs["Custo Total"]
    .apply(lambda x: f"${x:,.2f}")
)

display_repairs["Downtime Médio"] = (
    display_repairs["Downtime Médio"]
    .apply(lambda x: f"{x:,.2f} h")
)

st.subheader(
    "🔧 Top 10 Equipamentos com Mais Intervenções"
)

st.dataframe(
    display_repairs,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EQUIPAMENTOS POR DEPARTAMENTO
# =====================================================

dept_summary = (
    latest_equipment
    .groupby("DEPT_EQUIP_DEPT_NAME")
    .size()
    .reset_index(name="Equipamentos")
    .sort_values(
        "Equipamentos",
        ascending=False
    )
)

st.subheader(
    "🏢 Equipamentos por Departamento"
)

st.bar_chart(
    dept_summary.set_index(
        "DEPT_EQUIP_DEPT_NAME"
    )
)

# =====================================================
# TOP 10 MAIOR CUSTO HISTÓRICO
# =====================================================

top_cost = (
    latest_equipment
    .sort_values(
        "TOTAL_COST_EQUIP",
        ascending=False
    )
    .head(10)
    .reset_index(drop=True)
)

display_cost = top_cost[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "TOTAL_COST_EQUIP"
    ]
].rename(
    columns={
        "EQ_EQUIP_NO": "Equipamento",
        "DEPT_EQUIP_DEPT_NAME": "Departamento",
        "TOTAL_COST_EQUIP": "Custo Total"
    }
)

display_cost["Custo Total"] = (
    display_cost["Custo Total"]
    .apply(lambda x: f"${x:,.2f}")
)

st.subheader(
    "💰 Top 10 Equipamentos com Maior Custo Histórico"
)

st.dataframe(
    display_cost,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# TOP 10 MAIOR DOWNTIME
# =====================================================

top_downtime = (
    latest_equipment
    .sort_values(
        "AVG_DOWNTIME_EQUIP",
        ascending=False
    )
    .head(10)
    .reset_index(drop=True)
)

display_downtime = top_downtime[
    [
        "EQ_EQUIP_NO",
        "DEPT_EQUIP_DEPT_NAME",
        "AVG_DOWNTIME_EQUIP"
    ]
].rename(
    columns={
        "EQ_EQUIP_NO": "Equipamento",
        "DEPT_EQUIP_DEPT_NAME": "Departamento",
        "AVG_DOWNTIME_EQUIP": "Downtime Médio"
    }
)

display_downtime["Downtime Médio"] = (
    display_downtime["Downtime Médio"]
    .apply(lambda x: f"{x:,.2f} h")
)

st.subheader(
    "⏱️ Top 10 Equipamentos com Maior Downtime Médio"
)

st.dataframe(
    display_downtime,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EXPLORADOR DE EQUIPAMENTOS
# =====================================================

st.markdown("---")

st.header("🔎 Explorar Equipamento")

equipment_options = (
    latest_equipment
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

equipment_df = (
    master_df[
        master_df["EQ_EQUIP_NO"].astype(str) == equipment
    ]
    .copy()
)

latest_record = equipment_df.iloc[0]

# =====================================================
# RESUMO EXECUTIVO
# =====================================================

st.subheader(
    f"📋 Resumo do Equipamento {equipment}"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Departamento",
    latest_record["DEPT_EQUIP_DEPT_NAME"]
)

col2.metric(
    "Intervenções",
    f"{int(latest_record['TOTAL_INTERVENTIONS']):,}"
)

col3.metric(
    "Risco Reparação 30 Dias",
    f"{latest_record['PRED_REPAIR_30D_PCT']:.2f}%"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Custo Total Histórico",
    f"${latest_record['TOTAL_COST_EQUIP']:,.2f}"
)

col5.metric(
    "Custo Médio",
    f"${latest_record['AVG_COST_EQUIP']:,.2f}"
)

col6.metric(
    "Downtime Médio",
    f"{latest_record['AVG_DOWNTIME_EQUIP']:,.2f} h"
)

# =====================================================
# INDICADOR DE RISCO
# =====================================================

risk = latest_record["PRED_REPAIR_30D_PCT"]

if risk >= 80:

    st.error(
        f"🚨 Risco Muito Elevado de Reparação ({risk:.2f}%)"
    )

elif risk >= 50:

    st.warning(
        f"⚠️ Risco Moderado de Reparação ({risk:.2f}%)"
    )

else:

    st.success(
        f"✅ Risco Reduzido de Reparação ({risk:.2f}%)"
    )

# =====================================================
# EVOLUÇÃO ANUAL
# =====================================================

st.subheader("📈 Evolução Anual")

annual_stats = (
    equipment_df
    .groupby("WORK_ORDER_YR")
    .agg(
        Intervenções=("UNIQUE_WORK_ORDER_NO", "count"),
        Custo_Total=("TOTAL_COST", "sum"),
        Downtime_Total=("DOWNTIME_HRS_USER", "sum")
    )
    .reset_index()
)

col1, col2, col3 = st.columns(3)

with col1:

    st.write("Intervenções por Ano")

    st.bar_chart(
        annual_stats.set_index(
            "WORK_ORDER_YR"
        )["Intervenções"]
    )

with col2:

    st.write("Custos por Ano")

    st.bar_chart(
        annual_stats.set_index(
            "WORK_ORDER_YR"
        )["Custo_Total"]
    )

with col3:

    st.write("Downtime por Ano")

    st.bar_chart(
        annual_stats.set_index(
            "WORK_ORDER_YR"
        )["Downtime_Total"]
    )

# =====================================================
# DISTRIBUIÇÃO DOS CUSTOS
# =====================================================

st.subheader(
    "💰 Distribuição dos Custos"
)

cost_breakdown = pd.DataFrame({

    "Categoria": [
        "Mão de Obra",
        "Peças",
        "Comercial"
    ],

    "Valor": [

        equipment_df["LABOR_COST"].sum(),

        equipment_df["PARTS_COST"].sum(),

        equipment_df["COMML_COST"].sum()
    ]
})

st.bar_chart(
    cost_breakdown.set_index(
        "Categoria"
    )
)

# =====================================================
# HISTÓRICO RECENTE
# =====================================================

st.subheader(
    "🛠️ Histórico Recente de Intervenções"
)

history_df = (
    equipment_df[
        [
            "CREATE_DATE",
            "JOB_TYPE",
            "WORK_ORDER_STATUS",
            "PRI_PRIORITY_CODE",
            "TOTAL_COST",
            "DOWNTIME_HRS_USER"
        ]
    ]
    .head(20)
    .reset_index(drop=True)
)

history_df = history_df.rename(
    columns={
        "CREATE_DATE": "Data",
        "JOB_TYPE": "Tipo",
        "WORK_ORDER_STATUS": "Estado",
        "PRI_PRIORITY_CODE": "Prioridade",
        "TOTAL_COST": "Custo",
        "DOWNTIME_HRS_USER": "Downtime"
    }
)

history_df["Custo"] = (
    history_df["Custo"]
    .apply(lambda x: f"${x:,.2f}")
)

history_df["Downtime"] = (
    history_df["Downtime"]
    .apply(lambda x: f"{x:,.2f} h")
)

st.dataframe(
    history_df,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# EXPORTAÇÃO
# =====================================================

st.download_button(
    "📥 Exportar Histórico do Equipamento",
    equipment_df.to_csv(index=False),
    file_name=f"equipamento_{equipment}.csv",
    mime="text/csv"
)

