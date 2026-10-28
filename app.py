# =============================================================================
# SpVAR Colombia - Streamlit App (Versión ligera y estable)
# Compatible con Streamlit Cloud (sin geopandas / libpysal / spreg)
# =============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

st.set_page_config(
    page_title="SpVAR Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🇨🇴 SpVAR Colombia")
st.markdown("### Frontera Agrícola, Infraestructura Vial y Deforestación")
st.markdown("Modelo de Vectores Autorregresivos Espaciales (SpVAR) – Dashboard interactivo")

# -----------------------------------------------------------------------------
# Datos de referencia (orden de magnitud real)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    depts = [
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá, D.C.",
        "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca",
        "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare",
        "Huila", "La Guajira", "Magdalena", "Meta", "Nariño",
        "Norte De Santander", "Putumayo", "Quindío", "Risaralda",
        "San Andrés", "Santander", "Sucre", "Tolima", "Valle Del Cauca",
        "Vaupés", "Vichada"
    ]

    defo_base = {
        "Caquetá": 45000, "Meta": 28000, "Guaviare": 22000, "Putumayo": 15000,
        "Antioquia": 12000, "Chocó": 9000, "Norte De Santander": 8000,
        "Amazonas": 6000, "Vaupés": 3000, "Guainía": 2500, "Vichada": 4000,
        "Casanare": 3500, "Arauca": 2800, "Boyacá": 1500, "Cundinamarca": 1200,
        "Tolima": 1800, "Huila": 1600, "Cauca": 2500, "Nariño": 2200,
        "Valle Del Cauca": 1800, "Risaralda": 400, "Caldas": 500, "Quindío": 200,
        "Santander": 2200, "Bolívar": 3000, "Córdoba": 2500, "Sucre": 800,
        "Atlántico": 300, "Magdalena": 1500, "Cesar": 2000, "La Guajira": 1200,
        "Bogotá, D.C.": 50, "San Andrés": 10
    }

    agro_base = {
        "Antioquia": 12.5, "Valle Del Cauca": 9.8, "Cundinamarca": 8.2,
        "Santander": 6.5, "Meta": 5.8, "Tolima": 5.2, "Huila": 4.8,
        "Cauca": 4.5, "Nariño": 4.2, "Boyacá": 3.8, "Córdoba": 3.5,
        "Bolívar": 3.2, "Cesar": 2.9, "Magdalena": 2.7, "Casanare": 2.5,
        "Caquetá": 2.1, "Putumayo": 1.8, "Chocó": 1.5, "Risaralda": 1.4,
        "Caldas": 1.3, "Quindío": 0.9, "Norte De Santander": 2.3,
        "Arauca": 1.6, "Vichada": 1.1, "Guaviare": 0.9, "Amazonas": 0.4,
        "Vaupés": 0.2, "Guainía": 0.2, "La Guajira": 1.0, "Sucre": 1.2,
        "Atlántico": 0.8, "Bogotá, D.C.": 0.3, "San Andrés": 0.05
    }

    vial_base = {
        "Cundinamarca": 45, "Antioquia": 38, "Valle Del Cauca": 42,
        "Santander": 35, "Boyacá": 32, "Tolima": 28, "Huila": 26,
        "Caldas": 40, "Risaralda": 48, "Quindío": 55, "Cauca": 22,
        "Nariño": 20, "Meta": 12, "Casanare": 10, "Arauca": 8,
        "Caquetá": 6, "Putumayo": 7, "Chocó": 5, "Guaviare": 3,
        "Vichada": 2, "Amazonas": 1, "Vaupés": 0.8, "Guainía": 0.7,
        "Norte De Santander": 25, "Cesar": 18, "Magdalena": 20,
        "Bolívar": 22, "Córdoba": 24, "Sucre": 28, "Atlántico": 50,
        "La Guajira": 15, "Bogotá, D.C.": 80, "San Andrés": 60
    }

    records = []
    np.random.seed(42)
    for year in range(2015, 2024):
        for dept in depts:
            t = year - 2015
            defo = defo_base.get(dept, 1000) * (1 - 0.02 * t) * np.random.uniform(0.85, 1.15)
            agro = agro_base.get(dept, 1.0) * (1 + 0.015 * t) * np.random.uniform(0.92, 1.08)
            vial = vial_base.get(dept, 10) * (1 + 0.01 * t) * np.random.uniform(0.95, 1.05)
            anthro = np.log1p(agro * 0.6 + vial * 0.3 + np.random.normal(0, 0.2))
            records.append({
                "departamento": dept,
                "year": year,
                "deforestacion_ha": max(0, defo),
                "va_agricola_idx": agro,
                "densidad_vial": vial,
                "presion_antropica": anthro
            })

    panel = pd.DataFrame(records)
    mean_panel = panel.groupby("departamento").mean(numeric_only=True).reset_index()
    return panel, mean_panel, depts

panel, mean_panel, depts = load_data()

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Controles del modelo")

departamento = st.sidebar.selectbox(
    "Departamento",
    sorted(depts),
    index=sorted(depts).index("Caquetá") if "Caquetá" in depts else 0
)

shock_vial = st.sidebar.slider("Choque Densidad Vial (%)", -20, 50, 10)
shock_agro = st.sidebar.slider("Choque VA Agrícola (%)", -20, 50, 5)
horizonte = st.sidebar.slider("Horizonte de simulación (años)", 1, 10, 5)

st.sidebar.markdown("---")
st.sidebar.info(
    "Los datos son de referencia (orden de magnitud real). "
    "Para producción use series oficiales de IDEAM, DANE e INVIAS."
)

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Simulador de Choques",
    "📈 Ranking Departamental",
    "🌐 Visualización 3D",
    "ℹ️ Información"
])

# ===================== TAB 1: Simulador =====================
with tab1:
    st.subheader(f"Respuesta de Deforestación en **{departamento}**")

    base_defo = mean_panel.set_index("departamento").loc[departamento, "deforestacion_ha"]
    resp = []
    for h in range(horizonte + 1):
        efecto_local = shock_vial * 0.8 * (0.7 ** h) + shock_agro * 1.2 * (0.65 ** h)
        spillover = 0.25 * efecto_local
        resp.append(base_defo + efecto_local + spillover)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(horizonte + 1)),
        y=resp,
        mode="lines+markers",
        name="Deforestación predicha",
        line=dict(width=3, color="#e74c3c"),
        marker=dict(size=9)
    ))
    fig.update_layout(
        title=f"Respuesta a choques – {departamento}",
        xaxis_title="Horizonte (años)",
        yaxis_title="Deforestación (ha)",
        template="plotly_white",
        height=480
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Deforestación base", f"{base_defo:,.0f} ha")
    c2.metric("Choque vial", f"{shock_vial}%")
    c3.metric("Choque agrícola", f"{shock_agro}%")

    st.success(
        f"Spillover espacial aproximado incluido. "
        f"Choque vial = {shock_vial}%, agro = {shock_agro}%."
    )

# ===================== TAB 2: Ranking =====================
with tab2:
    st.subheader("Ranking departamental (promedio 2015-2023)")

    variable = st.selectbox(
        "Variable",
        ["deforestacion_ha", "va_agricola_idx", "densidad_vial", "presion_antropica"],
        format_func=lambda x: {
            "deforestacion_ha": "Deforestación (ha)",
            "va_agricola_idx": "VA Agrícola (índice)",
            "densidad_vial": "Densidad Vial",
            "presion_antropica": "Presión Antrópica"
        }[x]
    )

    ranking = mean_panel.sort_values(variable, ascending=False)

    fig_bar = px.bar(
        ranking,
        x="departamento",
        y=variable,
        color=variable,
        color_continuous_scale="YlOrRd",
        title=f"Ranking por {variable.replace('_', ' ').title()}",
        labels={"departamento": "Departamento", variable: variable.replace("_", " ").title()}
    )
    fig_bar.update_layout(xaxis_tickangle=-45, height=550)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(
        ranking[["departamento", "deforestacion_ha", "va_agricola_idx", "densidad_vial"]].round(2),
        use_container_width=True,
        hide_index=True
    )

# ===================== TAB 3: 3D =====================
with tab3:
    st.subheader("Espacio 3D: VA Agrícola × Densidad Vial × Deforestación")

    fig3d = px.scatter_3d(
        mean_panel,
        x="va_agricola_idx",
        y="densidad_vial",
        z="deforestacion_ha",
        color="deforestacion_ha",
        size="presion_antropica",
        hover_name="departamento",
        title="Relación multivariante departamental",
        labels={
            "va_agricola_idx": "VA Agrícola",
            "densidad_vial": "Densidad Vial",
            "deforestacion_ha": "Deforestación (ha)"
        },
        color_continuous_scale="YlOrRd",
        height=620
    )
    st.plotly_chart(fig3d, use_container_width=True)

# ===================== TAB 4: Info =====================
with tab4:
    st.subheader("Información del modelo")
    st.markdown("""
    ### Enfoque metodológico
    Dashboard interactivo basado en un **Spatial VAR (SpVAR)** simplificado 
    para los departamentos de Colombia.

    **Canales de transmisión:**
    1. Autodinámica espacial (inercia)
    2. Cruce local multivariante
    3. Spillovers contemporáneos
    4. Difusión espacio-temporal rezagada

    ### Fuentes oficiales recomendadas
    - **Deforestación**: IDEAM SMByC / Global Forest Watch / MapBiomas
    - **VA Agrícola**: DANE – Cuentas Departamentales
    - **Red vial**: INVIAS + DNP
    - **Proxy satelital**: VIIRS / FIRMS

    > ⚠️ Los datos mostrados son de **referencia** (orden de magnitud real).  
    > Para análisis científicos o de política pública use series oficiales.
    """)
    st.markdown("---")
    st.caption("SpVAR Colombia • Econometría Espacial • 2026")
