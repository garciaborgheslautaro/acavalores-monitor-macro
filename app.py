import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

st.set_page_config(
    page_title="Monitor Macro | ACA Valores",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
.kpi-card {
    background: linear-gradient(135deg, #1B2A6B 0%, #0D1B3E 100%);
    border: 1px solid #2A3F8F;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    margin-bottom: 8px;
}
.kpi-label { font-size: 11px; color: #A0AEC0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
.kpi-delta-pos { font-size: 12px; color: #48BB78; }
.kpi-delta-neg { font-size: 12px; color: #FC8181; }
.kpi-delta-neu { font-size: 12px; color: #A0AEC0; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
col_logo, col_titulo, col_fecha = st.columns([1, 4, 2])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=160)
with col_titulo:
    st.markdown("## Monitor Macroeconómico Argentina")
with col_fecha:
    st.markdown(
        "<div style='text-align:right; color:#A0AEC0; padding-top:20px'>Actualizacion: "
        + datetime.today().strftime("%d/%m/%Y") + "</div>",
        unsafe_allow_html=True
    )

st.divider()

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos():
    path = "data/bcra_data.csv"
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["fecha"])
    return df.sort_values("fecha").reset_index(drop=True)

df = cargar_datos()
if df is None:
    st.warning("Los datos aun no fueron generados.")
    st.stop()

# ── Selector de fechas ────────────────────────────────────────────────────────
fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()
c1, c2 = st.columns(2)
with c1:
    desde = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
with c2:
    hasta = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
df_f = df[(df["fecha"].dt.date >= desde) & (df["fecha"].dt.date <= hasta)].copy()

# ── KPI helpers ───────────────────────────────────────────────────────────────
def get_kpi(df, col):
    if col not in df.columns:
        return None, None
    serie = df[["fecha", col]].dropna()
    if len(serie) < 2:
        return None, None
    valor = float(serie.iloc[-1][col])
    anterior = float(serie.iloc[-2][col])
    pct = ((valor - anterior) / anterior * 100) if anterior != 0 else 0
    return valor, pct

def kpi_card(label, valor, pct, prefijo="", sufijo="", decimales=0):
    if valor is None:
        html = "<div class='kpi-card'><div class='kpi-label'>" + label + "</div><div class='kpi-value'>-</div><div class='kpi-delta-neu'>Sin datos</div></div>"
    else:
        fmt = prefijo + "{:,.{dec}f}".format(valor, dec=decimales) + sufijo
        flecha = "▲" if pct >= 0 else "▼"
        clase = "kpi-delta-pos" if pct >= 0 else "kpi-delta-neg"
        html = "<div class='kpi-card'><div class='kpi-label'>" + label + "</div><div class='kpi-value'>" + fmt + "</div><div class='" + clase + "'>" + flecha + " " + "{:.2f}".format(abs(pct)) + "% vs dia anterior</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("### Indicadores del dia")
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    v, p = get_kpi(df, "reservas")
    kpi_card("Reservas (USD MM)", v, p, prefijo="USD ", decimales=0)
with k2:
    v, p = get_kpi(df, "base_monetaria")
    kpi_card("Base Monetaria ($ MM)", v, p, prefijo="$ ", decimales=0)
with k3:
    v, p = get_kpi(df, "tc_mayorista")
    kpi_card("TC Mayorista A3500", v, p, prefijo="$ ", decimales=2)
with k4:
    v, p = get_kpi(df, "tc_minorista")
    kpi_card("TC Minorista BNA", v, p, prefijo="$ ", decimales=2)
with k5:
    v, p = get_kpi(df, "inflacion_mensual")
    kpi_card("Inflacion Mensual", v, p, sufijo="%", decimales=1)

st.divider()

# ── Colores ───────────────────────────────────────────────────────────────────
COLORES = {
    "reservas":            "#00BFFF",
    "base_monetaria":      "#48BB78",
    "tc_mayorista":        "#F6AD55",
    "tc_minorista":        "#FBD38D",
    "depositos":           "#A78BFA",
    "creditos":            "#FC8181",
    "m2_privado":          "#00BFFF",
    "depositos_usd":       "#68D391",
    "badlar":              "#F687B3",
    "tamar":               "#B794F4",
    "inflacion_mensual":   "#FC8181",
    "inflacion_interanual":"#F6AD55",
    "rem_inflacion":       "#48BB78",
}

LAYOUT = dict(
    paper_bgcolor="#0D1B2A",
    plot_bgcolor="#0D1B2A",
    font=dict(family="Montserrat", color="white", size=11),
    xaxis=dict(showgrid=False, color="#A0AEC0", tickformat="%b %Y"),
    yaxis=dict(showgrid=True, gridcolor="#1E2D3D", color="#A0AEC0"),
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="x unified",
    height=320
)

# ── Funciones de graficos ─────────────────────────────────────────────────────
def g1(df, col, titulo, sufijo="", color=None, key=None):
    if col not in df.columns:
        st.caption("Variable '" + col + "' no disponible aun.")
        return
    color = color or COLORES.get(col, "#00BFFF")
    dp = df[["fecha", col]].copy()
    dp[col] = dp[col].interpolate(method="linear")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dp["fecha"], y=dp[col], mode="lines", name=titulo,
        line=dict(color=color, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br>" + titulo + ": %{y:,.2f}" + sufijo + "<extra></extra>"
    ))
    layout = dict(LAYOUT)
    layout["title"] = dict(text=titulo, font=dict(size=13, color="white"))
    layout["showlegend"] = False
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, key=key or col)

def g2(df, col1, lab1, col2, lab2, titulo, sufijo="", key=None):
    fig = go.Figure()
    for col, lab in [(col1, lab1), (col2, lab2)]:
        if col in df.columns:
            dp = df[["fecha", col]].copy()
            dp[col] = dp[col].interpolate(method="linear")
            fig.add_trace(go.Scatter(
                x=dp["fecha"], y=dp[col], mode="lines", name=lab,
                line=dict(color=COLORES.get(col, "#00BFFF"), width=2),
                hovertemplate="%{x|%d/%m/%Y}<br>" + lab + ": %{y:,.2f}" + sufijo + "<extra></extra>"
            ))
    layout = dict(LAYOUT)
    layout["title"] = dict(text=titulo, font=dict(size=13, color="white"))
    layout["height"] = 340
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white", size=10))
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, key=key or (col1 + "_" + col2))

def g2eje(df, col1, lab1, col2, lab2, titulo, suf1="%", suf2="%", key=None):
    fig = go.Figure()
    if col1 in df.columns:
        dp = df[["fecha", col1]].dropna(subset=[col1])
        fig.add_trace(go.Bar(
            x=dp["fecha"], y=dp[col1], name=lab1,
            marker_color=COLORES.get(col1, "#FC8181"), opacity=0.8, yaxis="y1",
            hovertemplate="%{x|%d/%m/%Y}<br>" + lab1 + ": %{y:.1f}" + suf1 + "<extra></extra>"
        ))
    if col2 in df.columns:
        dp2 = df[["fecha", col2]].dropna(subset=[col2])
        fig.add_trace(go.Scatter(
            x=dp2["fecha"], y=dp2[col2], mode="lines", name=lab2,
            line=dict(color=COLORES.get(col2, "#F6AD55"), width=2), yaxis="y2",
            hovertemplate="%{x|%d/%m/%Y}<br>" + lab2 + ": %{y:.1f}" + suf2 + "<extra></extra>"
        ))
    fig.update_layout(
        paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A",
        font=dict(family="Montserrat", color="white", size=11),
        xaxis=dict(showgrid=False, color="#A0AEC0", tickformat="%b %Y"),
        yaxis=dict(title=lab1, showgrid=True, gridcolor="#1E2D3D", color="#FC8181", titlefont=dict(color="#FC8181")),
        yaxis2=dict(title=lab2, overlaying="y", side="right", showgrid=False, color="#F6AD55", titlefont=dict(color="#F6AD55")),
        margin=dict(l=10, r=60, t=40, b=10),
        title=dict(text=titulo, font=dict(size=13, color="white")),
        hovermode="x unified", height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white", size=10))
    )
    st.plotly_chart(fig, use_container_width=True, key=key or (col1 + "_" + col2 + "_eje"))

# ── Pestanas ──────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Sector Externo",
    "Politica Monetaria",
    "Sistema Financiero",
    "Precios",
    "Tabla de datos"
])

with tabs[0]:
    a, b = st.columns(2)
    with a:
        g1(df_f, "reservas", "Reservas Internacionales (USD MM)", key="t0_reservas")
    with b:
        g2(df_f, "tc_mayorista", "Mayorista A3500", "tc_minorista", "Minorista BNA",
           "Tipo de Cambio Oficial ($)", sufijo=" $", key="t0_tc")
    a, b = st.columns(2)
    with a:
        g1(df_f, "depositos_usd", "Depositos en Dolares Sector Privado (USD MM)", key="t0_depusd")
    with b:
        g1(df_f, "creditos", "Creditos Totales ($ MM)", key="t0_creditos")

with tabs[1]:
    a, b = st.columns(2)
    with a:
        g1(df_f, "base_monetaria", "Base Monetaria ($ MM)", key="t1_bm")
    with b:
        g2(df_f, "tamar", "TAMAR", "badlar", "BADLAR Priv.",
           "Tasas de Interes - TAMAR y BADLAR (% TNA)", sufijo="%", key="t1_tasas")
    a, b = st.columns(2)
    with a:
        g1(df_f, "m2_privado",
           "M2 Privado - Prom. movil 30 dias - Var. interanual (%)",
           sufijo="%", key="t1_m2")

with tabs[2]:
    a, b = st.columns(2)
    with a:
        g1(df_f, "depositos", "Depositos Totales ($ MM)", key="t2_dep")
    with b:
        g1(df_f, "creditos", "Creditos Totales ($ MM)", key="t2_cred")
    a, b = st.columns(2)
    with a:
        g1(df_f, "depositos_usd", "Depositos en Dolares Sector Privado (USD MM)", key="t2_depusd")
    with b:
        g1(df_f, "base_monetaria", "Base Monetaria ($ MM)", key="t2_bm")

with tabs[3]:
    g2eje(df_f,
          "inflacion_mensual", "Inflacion mensual (%)",
          "inflacion_interanual", "Inflacion interanual (%)",
          "Inflacion - Mensual vs Interanual (IPC INDEC)",
          key="t3_inflacion")
    a, b = st.columns(2)
    with a:
        g1(df_f, "rem_inflacion",
           "Inflacion Esperada REM - Proximos 12 meses - Mediana (% i.a.)",
           sufijo="%", color="#48BB78", key="t3_rem")

with tabs[4]:
    todas = [
        "fecha", "reservas", "base_monetaria",
        "tc_mayorista", "tc_minorista",
        "depositos", "creditos", "depositos_usd",
        "m2_privado", "tamar", "badlar",
        "inflacion_mensual", "inflacion_interanual", "rem_inflacion"
    ]
    cols_ok = [c for c in todas if c in df_f.columns]
    st.dataframe(
        df_f[cols_ok].sort_values("fecha", ascending=False).head(90),
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("ACA Valores · Monitor Macroeconomico · Fuente: BCRA API v4.0 · Actualizacion diaria automatica")















