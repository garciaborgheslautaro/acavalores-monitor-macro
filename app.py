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
.kpi-value { font-size: 24px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
.kpi-delta-pos { font-size: 12px; color: #48BB78; }
.kpi-delta-neg { font-size: 12px; color: #FC8181; }
.kpi-delta-neu { font-size: 12px; color: #A0AEC0; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
col_logo, col_titulo, col_fecha = st.columns([1, 4, 2])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=160)
with col_titulo:
    st.markdown("## Monitor Macroeconómico Argentina")
with col_fecha:
    st.markdown(
        f"<div style='text-align:right; color:#A0AEC0; padding-top:20px'>"
        f"Actualización: {datetime.today().strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True
    )

st.divider()

# ── Carga de datos ───────────────────────────────────────────────────────────
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

# ── Selector de rango ────────────────────────────────────────────────────────
fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()

c1, c2 = st.columns(2)
with c1:
    desde = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
with c2:
    hasta = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

df_f = df[(df["fecha"].dt.date >= desde) & (df["fecha"].dt.date <= hasta)].copy()

# ── KPI Cards ────────────────────────────────────────────────────────────────
def get_kpi(df, col):
    if col not in df.columns:
        return None, None
    serie = df[["fecha", col]].dropna()
    if len(serie) < 2:
        return None, None
    valor = serie.iloc[-1][col]
    anterior = serie.iloc[-2][col]
    pct = ((valor - anterior) / anterior * 100) if anterior != 0 else 0
    return valor, pct

def kpi_card(label, valor, pct, prefijo="", sufijo="", decimales=0):
    if valor is None:
        st.markdown(
            f"<div class='kpi-card'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value'>—</div>"
            f"<div class='kpi-delta-neu'>Sin datos</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        fmt = f"{prefijo}{valor:,.{decimales}f}{sufijo}"
        signo = "▲" if pct >= 0 else "▼"
        clase = "kpi-delta-pos" if pct >= 0 else "kpi-delta-neg"
        st.markdown(
            f"<div class='kpi-card'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value'>{fmt}</div>"
            f"<div class='{clase}'>{signo} {abs(pct):.2f}% vs dia anterior</div>"
            f"</div>",
            unsafe_allow_html=True
        )

st.markdown("### Indicadores del dia")
k1, k2, k3, k4 = st.columns(4)
with k1:
    v, p = get_kpi(df, "reservas")
    kpi_card("Reservas Internacionales", v, p, prefijo="USD ", sufijo=" MM", decimales=0)
with k2:
    v, p = get_kpi(df, "base_monetaria")
    kpi_card("Base Monetaria", v, p, prefijo="$ ", sufijo=" MM", decimales=0)
with k3:
    v, p = get_kpi(df, "tc_oficial")
    kpi_card("TC Oficial Mayorista", v, p, prefijo="$ ", decimales=2)
with k4:
    v, p = get_kpi(df, "m2_privado")
    kpi_card("M2 Privado ($ MM)", v, p, prefijo="$ ", decimales=0)

st.divider()

# ── Funcion grafico ──────────────────────────────────────────────────────────
COLORES = {
    "reservas":       "#00BFFF",
    "base_monetaria": "#48BB78",
    "tc_oficial":     "#F6AD55",
    "tc_minorista":   "#FBD38D",
    "depositos":      "#A78BFA",
    "creditos":       "#FC8181",
    "m2_privado":     "#00BFFF",
    "depositos_usd":  "#68D391",
    "prestamos_priv": "#F687B3",
}

def grafico(df, col, titulo, sufijo="", color=None):
    if col not in df.columns:
        st.caption(f"Variable '{col}' no disponible aun.")
        return
    color = color or COLORES.get(col, "#00BFFF")
    df_plot = df[["fecha", col]].copy()
    df_plot[col] = df_plot[col].interpolate(method="linear")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["fecha"],
        y=df_plot[col],
        mode="lines",
        line=dict(color=color, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br>" + titulo + ": %{y:,.2f}" + sufijo + "<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="#0D1B2A",
        plot_bgcolor="#0D1B2A",
        font=dict(family="Montserrat", color="white", size=11),
        xaxis=dict(showgrid=False, color="#A0AEC0", tickformat="%b %Y"),
        yaxis=dict(showgrid=True, gridcolor="#1E2D3D", color="#A0AEC0"),
        margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=titulo, font=dict(size=13, color="white")),
        hovermode="x unified",
        height=320
    )
    st.plotly_chart(fig, use_container_width=True)

def par(df, col1, tit1, col2, tit2, suf1="", suf2=""):
    c1, c2 = st.columns(2)
    with c1:
        grafico(df, col1, tit1, sufijo=suf1)
    with c2:
        grafico(df, col2, tit2, sufijo=suf2)

# ── Pestanas ─────────────────────────────────────────────────────────────────
tabs = st.tabs(["Sector Externo", "Politica Monetaria", "Sistema Financiero", "Tabla de datos"])

with tabs[0]:
    par(df_f, "reservas", "Reservas Internacionales (USD MM)",
        "tc_oficial", "TC Oficial Mayorista ($)", suf2=" $")
    par(df_f, "tc_minorista", "TC Oficial Minorista ($)",
        "depositos_usd", "Depositos en Dolares (USD MM)", suf1=" $")

with tabs[1]:
    par(df_f, "base_monetaria", "Base Monetaria ($ MM)",
        "m2_privado", "M2 Privado ($ MM)")

with tabs[2]:
    par(df_f, "depositos", "Depositos Totales ($ MM)",
        "creditos", "Creditos Totales ($ MM)")
    par(df_f, "prestamos_priv", "Prestamos Sector Privado ($ MM)",
        "depositos_usd", "Depositos en Dolares (USD MM)")

with tabs[3]:
    cols_ok = [c for c in ["fecha", "reservas", "base_monetaria", "tc_oficial",
                            "tc_minorista", "depositos", "creditos",
                            "m2_privado", "depositos_usd", "prestamos_priv"]
               if c in df_f.columns]
    st.dataframe(
        df_f[cols_ok].sort_values("fecha", ascending=False).head(60),
        use_container_width=True,
        hide_index=True
    )

st.caption("ACA Valores · Monitor Macroeconomico · Fuente: BCRA · Actualizacion diaria automatica")
