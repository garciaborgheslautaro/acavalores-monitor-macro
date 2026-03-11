import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# ─── CONFIG GENERAL ───────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor Macro — ACA Valores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── ESTILOS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.kpi-card {
    background-color: #161b22;
    border: 1px solid #1B2A6B;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}

.kpi-title { font-size: 13px; color: #8b949e; font-weight: 600; }
.kpi-value { font-size: 28px; font-weight: 700; color: #ffffff; margin: 8px 0; }
.kpi-delta-pos { font-size: 13px; color: #3fb950; }
.kpi-delta-neg { font-size: 13px; color: #f85149; }

.tab-header {
    font-size: 22px;
    font-weight: 700;
    color: #4C9BE8;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ─── LOGO Y HEADER ────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://raw.githubusercontent.com/garciaborgheslautaro/acavalores-monitor-macro/main/assets/logo.png", width=120)
with col_title:
    st.markdown("<h1 style='color:#4C9BE8; font-family:Montserrat; margin-top:10px;'>Monitor Macroeconómico</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; margin-top:-15px;'>Datos actualizados al día hábil más reciente</p>", unsafe_allow_html=True)

st.markdown("---")

# ─── FUNCIONES DE DATOS ───────────────────────────────────────────
BASE_URL = "https://api.estadisticasbcra.com"

HEADERS = {"Authorization": "BEARER tu_token_aqui"}

@st.cache_data(ttl=3600)
def get_bcra(endpoint):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS)
        df = pd.DataFrame(r.json())
        df.columns = ["fecha", "valor"]
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except:
        return pd.DataFrame()

def ultima(df):
    if df.empty: return None, None, None
    ult = df.iloc[-1]["valor"]
    ant = df.iloc[-2]["valor"] if len(df) > 1 else ult
    delta = ((ult - ant) / ant) * 100
    return ult, ant, delta

def kpi_card(titulo, valor, delta=None, formato="{:,.0f}", unidad=""):
    delta_html = ""
    if delta is not None:
        clase = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        flecha = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{clase}">{flecha} {abs(delta):.2f}%</div>'
    valor_fmt = formato.format(valor) + unidad if valor is not None else "—"
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor_fmt}</div>
        {delta_html}
    </div>
    """

# ─── TABS ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Resumen", "🌐 Sector Externo", "🏦 Política Monetaria", "📈 Precios", "💳 Sistema Financiero"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — RESUMEN
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="tab-header">Resumen del día</div>', unsafe_allow_html=True)

    reservas = get_bcra("reservas")
    base     = get_bcra("base")
    tc       = get_bcra("tc")
    tasa     = get_bcra("tasa_depositos_30_dias")

    v_res, _, d_res = ultima(reservas)
    v_base, _, d_base = ultima(base)
    v_tc, _, d_tc = ultima(tc)
    v_tasa, _, d_tasa = ultima(tasa)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Reservas Brutas", v_res, d_res, "USD {:,.0f}M"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Base Monetaria", v_base, d_base, "${:,.0f}M"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Tipo de Cambio Oficial", v_tc, d_tc, "${:,.2f}"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Tasa Depósitos 30d", v_tasa, d_tasa, "{:.1f}", "%"), unsafe_allow_html=True)

    st.markdown("#### Evolución reciente")
    col1, col2 = st.columns(2)

    def line_chart(df, titulo, color="#4C9BE8", unidad=""):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["fecha"], y=df["valor"],
            mode="lines", line=dict(color=color, width=2),
            hovertemplate=f"%{{x|%d/%m/%Y}}: %{{y:,.2f}}{unidad}<extra></extra>"
        ))
        fig.update_layout(
            title=titulo, template="plotly_dark",
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font=dict(family="Montserrat"),
            margin=dict(l=20, r=20, t=40, b=20),
            height=280
        )
        return fig

    with col1:
        if not reservas.empty:
            st.plotly_chart(line_chart(reservas.tail(180), "Reservas Brutas (USD M)", "#4C9BE8", "M"), use_container_width=True)
    with col2:
        if not tc.empty:
            st.plotly_chart(line_chart(tc.tail(180), "Tipo de Cambio Oficial", "#1B2A6B"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2 — SECTOR EXTERNO
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="tab-header">Sector Externo</div>', unsafe_allow_html=True)

    if not reservas.empty:
        st.plotly_chart(line_chart(reservas, "Reservas Internacionales Brutas (USD M)", "#4C9BE8", "M"), use_container_width=True)
    if not tc.empty:
        st.plotly_chart(line_chart(tc, "Tipo de Cambio Oficial ($/USD)", "#3fb950"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 3 — POLÍTICA MONETARIA
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="tab-header">Política Monetaria</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if not base.empty:
            st.plotly_chart(line_chart(base, "Base Monetaria ($M)", "#4C9BE8", "M"), use_container_width=True)
    with col2:
        if not tasa.empty:
            st.plotly_chart(line_chart(tasa, "Tasa Depósitos 30 días (%)", "#f0883e", "%"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# TAB 4 — PRECIOS
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="tab-header">Precios</div>', unsafe_allow_html=True)
    st.info("📡 Datos de inflación (INDEC) — próximamente en la siguiente fase del proyecto.")

# ══════════════════════════════════════════════════════════════════
# TAB 5 — SISTEMA FINANCIERO
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="tab-header">Sistema Financiero</div>', unsafe_allow_html=True)
    st.info("📡 Depósitos y créditos — próximamente en la siguiente fase del proyecto.")

# ─── FOOTER ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#8b949e; font-size:12px;'>ACA Valores — Monitor Macro | Fuente: BCRA | Actualización automática diaria</p>",
    unsafe_allow_html=True
)
