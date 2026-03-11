import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# ── Configuración de página ─────────────────────────────────
st.set_page_config(
    page_title="Monitor Macro — ACA Valores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Estilos ACA Valores ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #0a0f1e;
    color: #e0e6f0;
}
.metric-card {
    background: linear-gradient(135deg, #0d1b3e, #1a2f6b);
    border: 1px solid #1e3a8a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-label {
    color: #7eb3e0;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.metric-value {
    color: #ffffff;
    font-size: 26px;
    font-weight: 700;
    margin: 8px 0 4px 0;
}
.metric-delta-pos { color: #22c55e; font-size: 12px; }
.metric-delta-neg { color: #ef4444; font-size: 12px; }
h1, h2, h3 { font-family: 'Montserrat', sans-serif; color: #ffffff; }
.stTabs [data-baseweb="tab"] { color: #7eb3e0; font-family: 'Montserrat', sans-serif; }
.stTabs [aria-selected="true"] { color: #38bdf8; border-bottom: 2px solid #38bdf8; }
</style>
""", unsafe_allow_html=True)

# ── Colores para gráficos ───────────────────────────────────
AZUL       = "#1e3a8a"
CELESTE    = "#38bdf8"
CELESTE2   = "#7eb3e0"
VERDE      = "#22c55e"
ROJO       = "#ef4444"
BG         = "#0a0f1e"
GRID       = "#1e2d4a"

def estilo_fig(fig, titulo=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(family="Montserrat", size=16, color="#ffffff")),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Montserrat", color="#7eb3e0"),
        xaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7eb3e0")),
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    return fig

# ── Carga de datos ──────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos():
    path = "data/bcra_data.csv"
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["fecha"])
    df.sort_values("fecha", inplace=True)
    return df

df = cargar_datos()

# ── Header ──────────────────────────────────────────────────
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=140)
with col_titulo:
    st.markdown("## 📊 Monitor Macroeconómico Argentina")
    st.markdown(f"<small style='color:#7eb3e0'>Actualización: {datetime.today().strftime('%d/%m/%Y')}</small>", unsafe_allow_html=True)

st.divider()

if df is None:
    st.warning("⚠️ Los datos aún no fueron generados. Ejecutá `data/fetch_data.py` primero.")
    st.stop()

ult = df.dropna(how="all").iloc[-1]
ant = df.dropna(how="all").iloc[-2]

def delta(col):
    try:
        v, a = ult[col], ant[col]
        pct = (v - a) / a * 100
        signo = "▲" if pct >= 0 else "▼"
        color = "metric-delta-pos" if pct >= 0 else "metric-delta-neg"
        return f'<span class="{color}">{signo} {abs(pct):.1f}% vs día anterior</span>'
    except:
        return ""

def fmt(col, decimales=1, divisor=1, prefijo="", sufijo=""):
    try:
        return f"{prefijo}{ult[col]/divisor:,.{decimales}f}{sufijo}"
    except:
        return "—"

# ── KPI Cards ───────────────────────────────────────────────
st.markdown("### Indicadores del día")
cols = st.columns(4)
kpis = [
    ("Reservas Internacionales", fmt("reservas", 1, 1000, "USD ", " MM"), delta("reservas")),
    ("Base Monetaria",           fmt("base_monetaria", 1, 1, "$", " MM"),  delta("base_monetaria")),
    ("Tipo de Cambio Oficial",   fmt("tc_oficial", 2, 1, "$"),             delta("tc_oficial")),
    ("Tasa Política Monetaria",  fmt("tasa_politica", 2, 1, "", "%"),      delta("tasa_politica")),
]
for i, (label, valor, d) in enumerate(kpis):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{valor}</div>
            {d}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏦 Sector Externo",
    "💵 Política Monetaria",
    "🏛️ Sistema Financiero",
    "📋 Tabla de datos"
])

# Selector de rango compartido
rango = st.sidebar.selectbox("Rango histórico", ["1 año", "2 años", "5 años"], index=0)
dias = {"1 año": 365, "2 años": 730, "5 años": 1825}[rango]
desde = pd.Timestamp.today() - pd.Timedelta(days=dias)
dff = df[df["fecha"] >= desde]

def linea(df, cols, nombres, titulo, formato_y=""):
    fig = go.Figure()
    colores = [CELESTE, CELESTE2, VERDE, ROJO]
    for i, (col, nom) in enumerate(zip(cols, nombres)):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["fecha"], y=df[col],
                name=nom, line=dict(color=colores[i % len(colores)], width=2),
                hovertemplate=f"{nom}: %{{y:{formato_y}}}<extra></extra>"
            ))
    return estilo_fig(fig, titulo)

with tab1:
    st.plotly_chart(linea(dff, ["reservas"], ["Reservas brutas"], "Reservas Internacionales (millones USD)", ",.0f"), use_container_width=True)
    st.plotly_chart(linea(dff, ["tc_oficial"], ["TC Oficial mayorista"], "Tipo de Cambio Oficial", ",.2f"), use_container_width=True)

with tab2:
    st.plotly_chart(linea(dff, ["base_monetaria", "m2_privado"], ["Base Monetaria", "M2 Privado"], "Base Monetaria y M2 (millones $)", ",.0f"), use_container_width=True)
    st.plotly_chart(linea(dff, ["tasa_politica"], ["Tasa de política monetaria"], "Tasa de Política Monetaria (%)", ".2f"), use_container_width=True)

with tab3:
    st.plotly_chart(linea(dff, ["depositos", "creditos"], ["Depósitos totales", "Créditos totales"], "Depósitos y Créditos del Sistema Financiero (millones $)", ",.0f"), use_container_width=True)

with tab4:
    st.dataframe(
        df.tail(30).sort_values("fecha", ascending=False).style.format({
            "reservas": "{:,.0f}", "base_monetaria": "{:,.0f}",
            "tc_oficial": "{:,.2f}", "tasa_politica": "{:,.2f}",
            "depositos": "{:,.0f}", "creditos": "{:,.0f}", "m2_privado": "{:,.0f}"
        }),
        use_container_width=True, height=500
    )
