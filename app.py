import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, base64
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Monitor Macroeconómico | ACA Valores",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: #F7F9FC; color: #1A202C; }
.stApp { background-color: #F7F9FC; }
.row-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.var-label {
    font-size: 11px;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}
.var-value {
    font-size: 24px;
    font-weight: 700;
    color: #1B2A6B;
    margin-bottom: 2px;
}
.var-fecha {
    font-size: 10px;
    color: #A0AEC0;
    margin-bottom: 10px;
}
.var-delta-row {
    display: flex;
    flex-direction: column;
    gap: 3px;
    margin-top: 6px;
}
.delta-item {
    font-size: 13px;
    display: flex;
    justify-content: space-between;
}
.delta-label { color: #718096; font-size: 13px; }
.pos { color: #276749; font-weight: 600; }
.neg { color: #C53030; font-weight: 600; }
.neu { color: #718096; font-weight: 600; }
.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #1B2A6B;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 18px 0 10px 0;
    border-left: 4px solid #1B2A6B;
    padding-left: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_titulo, col_fecha = st.columns([1, 4, 2])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=160)
with col_titulo:
    st.markdown("## Monitor Macroeconómico Argentina")
with col_fecha:
    st.markdown(
        "<div style='text-align:right; color:#A0AEC0; padding-top:20px'>Actualización: "
        + datetime.today().strftime("%d/%m/%Y") + "</div>",
        unsafe_allow_html=True
    )

st.divider()

# ── Carga de datos ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def cargar_datos():
    path = "data/bcra_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_mercados():
    path = "data/mercados_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_dolar():
    path = "data/dolar_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_itcrm():
    path = "data/itcrm_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"], encoding="utf-8", encoding_errors="replace").sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_riesgo_pais():
    path = "data/riesgo_pais_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"], encoding="utf-8", encoding_errors="replace").sort_values("fecha").reset_index(drop=True)

df  = cargar_datos()
if df is None:
    st.warning("Los datos aún no fueron generados.")
    st.stop()

dfm = cargar_mercados()
dfd = cargar_dolar()
dfi = cargar_itcrm()
dfr = cargar_riesgo_pais()

# ── Selector de fechas ─────────────────────────────────────────────────────────
fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()
c1, c2 = st.columns(2)
with c1:
    desde = st.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
with c2:
    hasta = st.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

df_f  = df[(df["fecha"].dt.date >= desde) & (df["fecha"].dt.date <= hasta)].copy()

# ── Colores ────────────────────────────────────────────────────────────────────
COLORES = {
    "reservas":             "#00BFFF",
    "base_monetaria":       "#48BB78",
    "tc_mayorista":         "#F6AD55",
    "tc_minorista":         "#FBD38D",
    "depositos":            "#A78BFA",
    "prestamos_priv":       "#F687B3",
    "prestamos_usd":        "#68D391",
    "m2_privado":           "#00BFFF",
    "m2_transaccional":     "#63B3ED",
    "depositos_usd":        "#68D391",
    "compras_usd_bcra":     "#48BB78",
    "badlar":               "#F687B3",
    "tamar":                "#B794F4",
    "inflacion_mensual":    "#FC8181",
    "inflacion_interanual": "#F6AD55",
    "rem_inflacion":        "#48BB78",
    "cer":                  "#F6AD55",
    "itcrm":                "#4299E1",
    "riesgo_pais":          "#E53E3E",
    "mep":                  "#E53E3E",
    "ccl":                  "#805AD5",
    "blue":                 "#2B6CB0",
    "sp500":                "#1B2A6B",
    "nasdaq":               "#2B4FBF",
    "brent":                "#C05621",
    "wti":                  "#DD6B20",
    "oro":                  "#D4A017",
    "dxy":                  "#2D3748",
    "us10y":                "#C53030",
    "eem":                  "#276749",
    "emb":                  "#285E61",
    "soja":                 "#68D391",
    "maiz":                 "#F6AD55",
    "trigo":                "#FBD38D",
    "merval":               "#00BFFF",
    "merval_ccl":           "#1B2A6B",
}

# ── Watermark ─────────────────────────────────────────────────────────────────
def _wm_image():
    for path in ["assets/watermark.jpg", "watermark.jpg", "/mount/src/acavalores-monitor-macro/assets/watermark.jpg"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return [dict(source=f"data:image/jpeg;base64,{b64}",
                xref="paper", yref="paper", x=0.5, y=0.5,
                sizex=0.85, sizey=0.85, xanchor="center", yanchor="middle",
                opacity=0.15, layer="below")]
    return []

LAYOUT_BASE = dict(
    paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
    font=dict(family="Montserrat", size=11, color="#2D3748"),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified", height=160,
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#EDF2F7", zeroline=False, tickfont=dict(size=9)),
    images=_wm_image(),
    showlegend=False,
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_variaciones(serie_df, col):
    """Retorna (valor, fecha, var_ult, var_30d, var_365d) todos como floats o None"""
    if col not in serie_df.columns:
        return None, None, None, None, None
    s = serie_df[["fecha", col]].dropna(subset=[col]).sort_values("fecha")
    if len(s) < 2:
        return None, None, None, None, None
    val = float(s.iloc[-1][col])
    fecha = s.iloc[-1]["fecha"]
    fecha_str = fecha.strftime("%d/%m/%y") if hasattr(fecha, "strftime") else str(fecha)[:10]
    ant = float(s.iloc[-2][col])
    var_ult = ((val - ant) / ant * 100) if ant != 0 else 0

    fecha_30 = fecha - timedelta(days=30)
    s30 = s[s["fecha"] <= fecha_30]
    var_30 = ((val - float(s30.iloc[-1][col])) / float(s30.iloc[-1][col]) * 100) if len(s30) > 0 and float(s30.iloc[-1][col]) != 0 else None

    fecha_365 = fecha - timedelta(days=365)
    s365 = s[s["fecha"] <= fecha_365]
    var_365 = ((val - float(s365.iloc[-1][col])) / float(s365.iloc[-1][col]) * 100) if len(s365) > 0 and float(s365.iloc[-1][col]) != 0 else None

    return val, fecha_str, var_ult, var_30, var_365

def fmt_delta(val, sufijo="%"):
    if val is None:
        return '<span class="neu">-</span>'
    clase = "pos" if val >= 0 else "neg"
    flecha = "▲" if val >= 0 else "▼"
    return f'<span class="{clase}">{flecha} {abs(val):.2f}{sufijo}</span>'

def mini_chart(df_plot, col, color, key):
    if col not in df_plot.columns or df_plot[col].dropna().empty:
        return
    dp = df_plot[["fecha", col]].dropna(subset=[col])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dp["fecha"], y=dp[col], mode="lines",
        line=dict(color=color, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.2f}<extra></extra>"
    ))
    layout = dict(LAYOUT_BASE)
    fig.update_layout(**layout)
    _, c_chart, _ = st.columns([1, 8, 1])
    with c_chart:
        st.plotly_chart(fig, use_container_width=True, key=key)

def mini_chart_barras(df_plot, col, key):
    if col not in df_plot.columns or df_plot[col].dropna().empty:
        return
    dp = df_plot[["fecha", col]].dropna(subset=[col])
    colores = ["#48BB78" if v >= 0 else "#FC8181" for v in dp[col]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dp["fecha"], y=dp[col],
        marker_color=colores, opacity=0.85,
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.2f}<extra></extra>"
    ))
    layout = dict(LAYOUT_BASE)
    fig.update_layout(**layout)
    _, c_chart, _ = st.columns([1, 8, 1])
    with c_chart:
        st.plotly_chart(fig, use_container_width=True, key=key)

def row_card_barras(df_plot, col, label, prefijo="", sufijo="", decimales=2, key=None, invertir_colores=False):
    """Card a la izquierda + mini gráfico de barras a la derecha"""
    val, fecha_str, var_ult, var_30, var_365 = get_variaciones(df_plot, col)
    col_card, col_chart = st.columns([3, 7])
    with col_card:
        if val is None:
            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">-</div>
                <div class="var-fecha">Sin datos</div>
            </div>""", unsafe_allow_html=True)
        else:
            fmt_val = prefijo + "{:,.{dec}f}".format(val, dec=decimales) + sufijo
            def _d(v):
                if v is None: return '<span class="neu">-</span>'
                clase = ("neg" if v >= 0 else "pos") if invertir_colores else ("pos" if v >= 0 else "neg")
                flecha = "▲" if v >= 0 else "▼"
                return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'
            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">{fmt_val}</div>
                <div class="var-fecha">últ. dato: {fecha_str}</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d(var_30)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d(var_365)}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    with col_chart:
        mini_chart_barras(df_plot, col, key=key or col)

def row_card(df_plot, col, label, prefijo="", sufijo="", decimales=2, color=None, key=None, invertir_colores=False):
    """Card a la izquierda + mini gráfico a la derecha en una fila"""
    color = color or COLORES.get(col, "#1B2A6B")
    val, fecha_str, var_ult, var_30, var_365 = get_variaciones(df_plot, col)

    col_card, col_chart = st.columns([3, 7])
    with col_card:
        if val is None:
            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">-</div>
                <div class="var-fecha">Sin datos</div>
            </div>""", unsafe_allow_html=True)
        else:
            fmt_val = prefijo + "{:,.{dec}f}".format(val, dec=decimales) + sufijo

            def _d(v):
                if v is None: return '<span class="neu">-</span>'
                if invertir_colores:
                    clase = "neg" if v >= 0 else "pos"
                else:
                    clase = "pos" if v >= 0 else "neg"
                flecha = "▲" if v >= 0 else "▼"
                return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">{fmt_val}</div>
                <div class="var-fecha">últ. dato: {fecha_str}</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d(var_30)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d(var_365)}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    with col_chart:
        mini_chart(df_plot, col, color, key=key or col)

def row_card_ext(df_plot, col, label, prefijo="", sufijo="", decimales=2, color=None, key=None, invertir_colores=False):
    """Igual que row_card pero acepta df ya calculado con columna col"""
    row_card(df_plot, col, label, prefijo, sufijo, decimales, color, key, invertir_colores)

# ── Pestañas ──────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Sector Externo",
    "Política Monetaria",
    "Sistema Financiero",
    "Inflación",
    "Mercados",
    "Tabla de datos"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 0 — SECTOR EXTERNO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-title">Reservas & Divisas</div>', unsafe_allow_html=True)
    row_card(df_f, "reservas", "Reservas Internacionales (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t0_reservas")
    row_card_barras(df_f, "compras_usd_bcra", "Compras Netas de Divisas BCRA (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t0_compras")
    row_card(df_f, "depositos_usd", "Depósitos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t0_depusd")

    st.markdown('<div class="section-title">Tipo de Cambio</div>', unsafe_allow_html=True)

    # TC: gráfico especial con 4 series
    val_min, fecha_str_min, var_ult_min, var_30_min, var_365_min = get_variaciones(df_f, "tc_mayorista")
    val_may, fecha_str_may, var_ult_may, var_30_may, var_365_may = get_variaciones(df_f, "tc_minorista")

    def _d_tc(v, inv=False):
        if v is None: return '<span class="neu">-</span>'
        clase = ("neg" if v >= 0 else "pos") if inv else ("pos" if v >= 0 else "neg")
        flecha = "▲" if v >= 0 else "▼"
        return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

    fmt_val_min = f"{val_min:,.2f}" if val_min is not None else "-"
    fmt_val_may = f"{val_may:,.2f}" if val_may is not None else "-"
    col_card_tc, col_chart_tc = st.columns([3, 7])
    with col_card_tc:
        st.markdown(f"""
        <div class="row-card">
            <div class="var-label">Tipo de Cambio ($)</div>
            <div style="margin-bottom:8px">
                <div style="font-size:13px;font-weight:700;color:#1B2A6B">Minorista: $ {fmt_val_min}</div>
                <div style="font-size:10px;color:#A0AEC0;margin-bottom:4px">últ. dato: {fecha_str_min or '-'}</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_tc(var_ult_min)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_tc(var_30_min)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_tc(var_365_min)}</div>
                </div>
            </div>
            <div style="margin-bottom:8px">
                <div style="font-size:13px;font-weight:700;color:#1B2A6B">Mayorista: $ {fmt_val_may}</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_tc(var_ult_may)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_tc(var_30_may)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_tc(var_365_may)}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_chart_tc:
        fig_tc = go.Figure()
        for col_tc, lab_tc, color_tc in [
            ("tc_mayorista", "Minorista", COLORES["tc_mayorista"]),
            ("tc_minorista", "Mayorista A3500", COLORES["tc_minorista"]),
        ]:
            if col_tc in df_f.columns:
                dp = df_f[["fecha", col_tc]].dropna()
                fig_tc.add_trace(go.Scatter(x=dp["fecha"], y=dp[col_tc], mode="lines",
                    name=lab_tc, line=dict(color=color_tc, width=2),
                    hovertemplate="%{x|%d/%m/%Y}<br>" + lab_tc + ": $%{y:,.2f}<extra></extra>"))
        if dfd is not None:
            dfd_f = dfd[(dfd["fecha"].dt.date >= desde) & (dfd["fecha"].dt.date <= hasta)]
            for col_tc, lab_tc, color_tc in [
                ("mep", "MEP", COLORES["mep"]),
                ("ccl", "CCL", COLORES["ccl"]),
            ]:
                if col_tc in dfd_f.columns:
                    dp = dfd_f[["fecha", col_tc]].dropna(subset=[col_tc])
                    fig_tc.add_trace(go.Scatter(x=dp["fecha"], y=dp[col_tc], mode="lines",
                        name=lab_tc, line=dict(color=color_tc, width=2),
                        hovertemplate="%{x|%d/%m/%Y}<br>" + lab_tc + ": $%{y:,.2f}<extra></extra>"))
        layout_tc = dict(LAYOUT_BASE)
        layout_tc["height"] = 200
        layout_tc["showlegend"] = True
        layout_tc["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
        fig_tc.update_layout(**layout_tc)
        st.plotly_chart(fig_tc, use_container_width=True, key="t0_tc")

    # MEP y CCL cards individuales
    if dfd is not None:
        dfd_f2 = dfd[(dfd["fecha"].dt.date >= desde) & (dfd["fecha"].dt.date <= hasta)]
        row_card(dfd_f2, "mep", "Dólar MEP ($)", prefijo="$ ", decimales=2, color=COLORES["mep"], key="t0_mep")
        row_card(dfd_f2, "ccl", "Dólar CCL ($)", prefijo="$ ", decimales=2, color=COLORES["ccl"], key="t0_ccl")

    st.markdown('<div class="section-title">Competitividad & Riesgo</div>', unsafe_allow_html=True)
    if dfi is not None:
        dfi_f = dfi[(dfi["fecha"].dt.date >= desde) & (dfi["fecha"].dt.date <= hasta)]
        row_card(dfi_f, "itcrm", "ITCRM (base 17-12-15=100)", decimales=2, color=COLORES["itcrm"], key="t0_itcrm")
    if dfr is not None:
        dfr_f = dfr[(dfr["fecha"].dt.date >= desde) & (dfr["fecha"].dt.date <= hasta)]
        row_card(dfr_f, "riesgo_pais", "Riesgo País EMBI (puntos básicos)", sufijo=" pb", decimales=0, color=COLORES["riesgo_pais"], key="t0_riesgo", invertir_colores=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — POLÍTICA MONETARIA
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-title">Agregados Monetarios</div>', unsafe_allow_html=True)
    row_card(df_f, "base_monetaria", "Base Monetaria ($ MM)", prefijo="$ ", sufijo=" MM", decimales=0, key="t1_bm")
    row_card(df_f, "m2_transaccional", "M2 Transaccional Sector Privado ($ MM)", prefijo="$ ", sufijo=" MM", decimales=0, key="t1_m2trans")
    row_card(df_f, "m2_privado", "M2 Privado - Var. interanual (%)", sufijo="%", decimales=2, color=COLORES["m2_privado"], key="t1_m2")

    st.markdown('<div class="section-title">Tasas de Interés</div>', unsafe_allow_html=True)
    row_card(df_f, "tamar", "TAMAR Bancos Privados (% TNA)", sufijo="%", decimales=2, color=COLORES["tamar"], key="t1_tamar")
    row_card(df_f, "badlar", "BADLAR Bancos Privados (% TNA)", sufijo="%", decimales=2, color=COLORES["badlar"], key="t1_badlar")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — SISTEMA FINANCIERO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-title">Crédito & Depósitos</div>', unsafe_allow_html=True)
    row_card(df_f, "depositos_usd", "Depósitos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t2_depusd")
    row_card(df_f, "prestamos_usd", "Préstamos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t2_prestusd")

    if "prestamos_priv" in df_f.columns and "cer" in df_f.columns:
        df_prest = df_f[["fecha", "prestamos_priv", "cer"]].dropna().copy()
        cer_hoy = df_prest["cer"].iloc[-1]
        df_prest["prestamos_constantes"] = df_prest["prestamos_priv"] * cer_hoy / df_prest["cer"]
        row_card(df_prest, "prestamos_constantes", "Préstamos al Sector Privado ($ MM constantes de hoy)",
                 prefijo="$ ", sufijo=" MM", decimales=0, key="t2_prest_const")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — INFLACIÓN
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-title">IPC & Expectativas</div>', unsafe_allow_html=True)
    row_card_barras(df_f, "inflacion_mensual", "Inflación Mensual IPC (%)", sufijo="%", decimales=1,
             key="t3_inf_men", invertir_colores=True)
    row_card(df_f, "inflacion_interanual", "Inflación Interanual IPC (%)", sufijo="%", decimales=1,
             color=COLORES["inflacion_interanual"], key="t3_inf_ia", invertir_colores=True)
    row_card(df_f, "rem_inflacion", "Inflación Esperada REM - Próximos 12 meses - Mediana (% i.a.)",
             sufijo="%", decimales=1, color=COLORES["rem_inflacion"], key="t3_rem", invertir_colores=True)

    st.markdown('<div class="section-title">Indexación</div>', unsafe_allow_html=True)
    row_card(df_f, "cer", "CER - Coeficiente de Estabilización de Referencia (base 2-feb-02=1)",
             decimales=2, color=COLORES["cer"], key="t3_cer")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — MERCADOS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    if dfm is None:
        st.warning("Datos de mercados no disponibles aún.")
    else:
        dfm_f = dfm[(dfm["fecha"].dt.date >= desde) & (dfm["fecha"].dt.date <= hasta)].copy()

        st.markdown('<div class="section-title">Índices & Renta Variable</div>', unsafe_allow_html=True)
        row_card(dfm_f, "sp500", "S&P 500", decimales=2, color=COLORES["sp500"], key="t4_sp500")
        row_card(dfm_f, "nasdaq", "Nasdaq Composite", decimales=2, color=COLORES["nasdaq"], key="t4_nasdaq")

        # Merval CCL
        if dfd is not None:
            dfd_m = dfd[(dfd["fecha"].dt.date >= desde) & (dfd["fecha"].dt.date <= hasta)]
            df_mccl = pd.merge(dfm_f[["fecha","merval"]], dfd_m[["fecha","ccl"]], on="fecha", how="inner").dropna()
            if len(df_mccl) > 0:
                df_mccl["merval_ccl"] = df_mccl["merval"] / df_mccl["ccl"]
                row_card(df_mccl, "merval_ccl", "Merval en USD (CCL)", prefijo="USD ", decimales=2,
                         color=COLORES["merval_ccl"], key="t4_merval_ccl")

        row_card(dfm_f, "eem", "EEM - iShares MSCI Emerging Markets ETF", prefijo="USD ", decimales=2,
                 color=COLORES["eem"], key="t4_eem")

        st.markdown('<div class="section-title">Renta Fija & Moneda</div>', unsafe_allow_html=True)
        row_card(dfm_f, "us10y", "US Treasury 10Y (% yield)", sufijo="%", decimales=2,
                 color=COLORES["us10y"], key="t4_us10y", invertir_colores=True)
        row_card(dfm_f, "emb", "EMB - iShares JP Morgan EM Bond ETF", prefijo="USD ", decimales=2,
                 color=COLORES["emb"], key="t4_emb")
        row_card(dfm_f, "dxy", "DXY - Índice Dólar", decimales=2, color=COLORES["dxy"], key="t4_dxy")

        st.markdown('<div class="section-title">Commodities</div>', unsafe_allow_html=True)
        row_card(dfm_f, "oro", "Oro (USD/oz)", prefijo="USD ", decimales=2, color=COLORES["oro"], key="t4_oro")

        # Petróleo — gráfico especial con Brent y WTI
        val_brent, fecha_brent, var_ult_brent, var_30_brent, var_365_brent = get_variaciones(dfm_f, "brent")
        val_wti, _, var_ult_wti, var_30_wti, var_365_wti = get_variaciones(dfm_f, "wti")

        def _d_pet(v):
            if v is None: return '<span class="neu">-</span>'
            clase = "pos" if v >= 0 else "neg"
            flecha = "▲" if v >= 0 else "▼"
            return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

        fmt_val_brent = f"{val_brent:,.2f}" if val_brent is not None else "-"
        fmt_val_wti = f"{val_wti:,.2f}" if val_wti is not None else "-"
        col_card_pet, col_chart_pet = st.columns([3, 7])
        with col_card_pet:
            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">Petróleo (USD/bbl)</div>
                <div style="margin-bottom:8px">
                    <div style="font-size:13px;font-weight:700;color:#1B2A6B">Brent: USD {fmt_val_brent}</div>
                    <div class="var-delta-row">
                        <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_pet(var_ult_brent)}</div>
                        <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_pet(var_30_brent)}</div>
                        <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_pet(var_365_brent)}</div>
                    </div>
                </div>
                <div>
                    <div style="font-size:13px;font-weight:700;color:#1B2A6B">WTI: USD {fmt_val_wti}</div>
                    <div class="var-delta-row">
                        <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_pet(var_ult_wti)}</div>
                        <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_pet(var_30_wti)}</div>
                        <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_pet(var_365_wti)}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_chart_pet:
            fig_pet = go.Figure()
            for col_p, lab_p, color_p in [("brent", "Brent", COLORES["brent"]), ("wti", "WTI", COLORES["wti"])]:
                if col_p in dfm_f.columns:
                    dp = dfm_f[["fecha", col_p]].dropna()
                    fig_pet.add_trace(go.Scatter(x=dp["fecha"], y=dp[col_p], mode="lines",
                        name=lab_p, line=dict(color=color_p, width=2),
                        hovertemplate="%{x|%d/%m/%Y}<br>" + lab_p + ": USD %{y:,.2f}<extra></extra>"))
            layout_pet = dict(LAYOUT_BASE)
            layout_pet["height"] = 200
            layout_pet["showlegend"] = True
            layout_pet["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
            fig_pet.update_layout(**layout_pet)
            st.plotly_chart(fig_pet, use_container_width=True, key="t4_petroleo")

        # Granos en USD/ton
        dfm_granos = dfm_f.copy()
        if "soja" in dfm_granos.columns:
            dfm_granos["soja_ton"] = (dfm_granos["soja"] / 100) * 36.744
        if "maiz" in dfm_granos.columns:
            dfm_granos["maiz_ton"] = (dfm_granos["maiz"] / 100) * 39.368
        if "trigo" in dfm_granos.columns:
            dfm_granos["trigo_ton"] = (dfm_granos["trigo"] / 100) * 36.744

        row_card(dfm_granos, "soja_ton", "Soja CBOT (USD/ton)", prefijo="USD ", decimales=2,
                 color=COLORES["soja"], key="t4_soja")
        row_card(dfm_granos, "maiz_ton", "Maíz CBOT (USD/ton)", prefijo="USD ", decimales=2,
                 color=COLORES["maiz"], key="t4_maiz")
        row_card(dfm_granos, "trigo_ton", "Trigo CBOT (USD/ton)", prefijo="USD ", decimales=2,
                 color=COLORES["trigo"], key="t4_trigo")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — TABLA DE DATOS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    cols_orden = [
        "fecha", "reservas", "compras_usd_bcra",
        "base_monetaria", "m2_transaccional",
        "tc_minorista", "tc_mayorista",
        "depositos_usd", "prestamos_usd", "prestamos_priv",
        "m2_privado", "tamar", "badlar",
        "inflacion_mensual", "inflacion_interanual", "rem_inflacion", "cer"
    ]
    cols_ok = [c for c in cols_orden if c in df_f.columns]
    st.dataframe(
        df_f[cols_ok].sort_values("fecha", ascending=False).head(90),
        use_container_width=True, hide_index=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#A0AEC0; font-size:11px'>"
    "Fuentes: BCRA (API v4.0 & Excel ITCRM) · Ámbito Financiero (Riesgo País, MEP, CCL) · "
    "Bluelytics (Dólar Blue) · Yahoo Finance (Mercados Internacionales) · INDEC"
    "</div>",
    unsafe_allow_html=True
)
