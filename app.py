import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, base64
from datetime import datetime, timedelta, date

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
    font-size: 13px;
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
    font-size: 14px;
    display: flex;
    justify-content: space-between;
}
.delta-label { color: #718096; font-size: 14px; }
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

@st.cache_data(ttl=3600)
def cargar_actividad():
    path = "data/actividad_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=1800)
def cargar_bonos():
    path = "data/bonos_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path).sort_values(["ticker", "fecha"]).reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_tasas():
    path = "data/macro_tasas.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_inflacion():
    path = "data/macro_inflacion.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_desempleo():
    path = "data/macro_desempleo.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_gdp():
    path = "data/macro_gdp.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_labor():
    path = "data/macro_labor.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_yields():
    path = "data/macro_yields.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_macro_pce():
    path = "data/macro_pce.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["fecha"]).sort_values("fecha").reset_index(drop=True)

@st.cache_data(ttl=1800)
def cargar_calendario_int():
    path = "data/calendario_internacional.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

@st.cache_data(ttl=1800)
def cargar_calendario_ar():
    path = "data/calendario_argentina.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

@st.cache_data(ttl=3600)
def cargar_earnings():
    path = "data/earnings_data.csv"
    if not os.path.exists(path): return None
    return pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

df  = cargar_datos()
if df is None:
    st.warning("Los datos aún no fueron generados.")
    st.stop()

dfm = cargar_mercados()
dfd = cargar_dolar()
dfi = cargar_itcrm()
dfr = cargar_riesgo_pais()
dfa = cargar_actividad()
dfb = cargar_bonos()

# ── Selector de fechas ─────────────────────────────────────────────────────────
fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()
fecha_default_desde = max(fecha_min, fecha_max - timedelta(days=365))
c1, c2 = st.columns(2)
with c1:
    desde = st.date_input("Desde", value=fecha_default_desde, min_value=fecha_min, max_value=fecha_max)
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
    "vix":                  "#E53E3E",
    "plata":                "#A0AEC0",
    "tasa_adelanto_cc":     "#F6AD55",
    "tasa_pases_terceros":  "#68D391",
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
    font=dict(family="Montserrat", size=13, color="#2D3748"),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified", height=340,
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor="#EDF2F7", zeroline=False, tickfont=dict(size=11)),
    images=_wm_image(),
    showlegend=False,
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_variaciones(serie_df, col, serie_full=None, pp_absoluto=False):
    if col not in serie_df.columns:
        return None, None, None, None, None
    s = serie_df[["fecha", col]].dropna(subset=[col]).copy()
    s["fecha"] = pd.to_datetime(s["fecha"])
    s = s.sort_values("fecha")
    if len(s) < 2:
        return None, None, None, None, None
    val = float(s.iloc[-1][col])
    fecha = s.iloc[-1]["fecha"]
    fecha_str = fecha.strftime("%d/%m/%y")
    ant = float(s.iloc[-2][col])

    if pp_absoluto:
        return val, fecha_str, val - ant, None, None

    var_ult = ((val - ant) / ant * 100) if ant != 0 else 0

    if serie_full is not None and col in serie_full.columns:
        s_hist = serie_full[["fecha", col]].dropna(subset=[col]).copy()
        s_hist["fecha"] = pd.to_datetime(s_hist["fecha"])
        s_hist = s_hist.sort_values("fecha")
    else:
        s_hist = s

    fecha_30 = fecha - timedelta(days=30)
    s30 = s_hist[s_hist["fecha"] <= fecha_30]
    var_30 = ((val - float(s30.iloc[-1][col])) / float(s30.iloc[-1][col]) * 100) if len(s30) > 0 and float(s30.iloc[-1][col]) != 0 else None

    fecha_365 = fecha - timedelta(days=365)
    ventana = s_hist[(s_hist["fecha"] >= fecha_365 - timedelta(days=30)) & (s_hist["fecha"] <= fecha_365 + timedelta(days=30))]
    if len(ventana) > 0:
        idx_cercano = (ventana["fecha"] - fecha_365).abs().idxmin()
        val_365 = float(ventana.loc[idx_cercano, col])
        var_365 = ((val - val_365) / val_365 * 100) if val_365 != 0 else None
    else:
        var_365 = None

    return val, fecha_str, var_ult, var_30, var_365

def get_var_pp(col, s_f, s_full):
    """Todas las variaciones como diferencia absoluta en p.p."""
    val, fecha_str, pp_ult, _, _ = get_variaciones(s_f, col, s_full, pp_absoluto=True)
    if val is None:
        return None, None, None, None, None
    src = s_full if (s_full is not None and col in s_full.columns) else s_f
    s = src[["fecha", col]].dropna(subset=[col]).copy()
    s["fecha"] = pd.to_datetime(s["fecha"])
    s = s.sort_values("fecha")
    fecha = s.iloc[-1]["fecha"]
    def _pp(dias):
        obj = fecha - timedelta(days=dias)
        v = s[(s["fecha"] >= obj - timedelta(days=30)) & (s["fecha"] <= obj + timedelta(days=30))]
        if len(v) == 0:
            return None
        return val - float(v.loc[(v["fecha"] - obj).abs().idxmin(), col])
    return val, fecha_str, pp_ult, _pp(30), _pp(365)

def fmt_delta(val, sufijo="%"):
    if val is None:
        return '<span class="neu">-</span>'
    clase = "pos" if val >= 0 else "neg"
    flecha = "▲" if val >= 0 else "▼"
    return f'<span class="{clase}">{flecha} {abs(val):.2f}{sufijo}</span>'

def mini_chart(df_plot, col, color, key, label="", fecha_str="", df_full=None):
    if col not in df_plot.columns or df_plot[col].dropna().empty:
        return
    dp = df_plot[["fecha", col]].dropna(subset=[col])
    titulo = f"<b>{label}</b>  <span style='font-size:10px;color:#718096'>últ. dato: {fecha_str}</span>" if label else ""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dp["fecha"], y=dp[col], mode="lines",
        line=dict(color=color, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.2f}<extra></extra>"
    ))
    layout = dict(LAYOUT_BASE)
    layout["title"] = dict(text=titulo, font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
    layout["margin"] = dict(l=10, r=10, t=50, b=10)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, key=key)
    # Botón descarga — usa df_full si existe, sino df_plot
    src = df_full if (df_full is not None and col in df_full.columns) else df_plot
    csv = src[["fecha", col]].dropna(subset=[col]).sort_values("fecha").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar datos",
        data=csv,
        file_name=f"{col}.csv",
        mime="text/csv",
        key=f"dl_{key}",
        use_container_width=False,
    )

def mini_chart_barras(df_plot, col, key, label="", fecha_str="", df_full=None):
    if col not in df_plot.columns or df_plot[col].dropna().empty:
        return
    dp = df_plot[["fecha", col]].dropna(subset=[col])
    colores = ["#48BB78" if v >= 0 else "#FC8181" for v in dp[col]]
    titulo = f"<b>{label}</b>  <span style='font-size:10px;color:#718096'>últ. dato: {fecha_str}</span>" if label else ""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dp["fecha"], y=dp[col],
        marker_color=colores, opacity=0.85,
        hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.2f}<extra></extra>"
    ))
    layout = dict(LAYOUT_BASE)
    layout["title"] = dict(text=titulo, font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
    layout["margin"] = dict(l=10, r=10, t=50, b=10)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, key=key)
    src = df_full if (df_full is not None and col in df_full.columns) else df_plot
    csv = src[["fecha", col]].dropna(subset=[col]).sort_values("fecha").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar datos",
        data=csv,
        file_name=f"{col}.csv",
        mime="text/csv",
        key=f"dl_{key}",
        use_container_width=False,
    )

def row_card_barras(df_plot, col, label, prefijo="", sufijo="", decimales=2, key=None, invertir_colores=False, df_full=None, es_porcentaje=False, solo_ult_dato=False):
    """Card a la izquierda + mini gráfico de barras a la derecha"""
    if solo_ult_dato:
        val, fecha_str, var_ult, _, _ = get_variaciones(df_plot, col, serie_full=df_full, pp_absoluto=True)
        var_30, var_365 = None, None
    else:
        val, fecha_str, var_ult, var_30, var_365 = get_variaciones(df_plot, col, serie_full=df_full)
    col_esp_l, col_card, col_chart, col_esp_r = st.columns([1, 2, 4, 3])
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
                unidad = " p.p." if (es_porcentaje or solo_ult_dato) else "%"
                return f'<span class="{clase}">{flecha} {abs(v):.2f}{unidad}</span>'
            if solo_ult_dato:
                delta_html = f'<div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>'
            else:
                delta_html = f"""
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d(var_30)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d(var_365)}</div>"""
            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">{fmt_val}</div>
                <div class="var-fecha">últ. dato: {fecha_str}</div>
                <div class="var-delta-row">{delta_html}
                </div>
            </div>""", unsafe_allow_html=True)
    with col_chart:
        mini_chart_barras(df_plot, col, key=key or col, label=label, fecha_str=fecha_str or "", df_full=df_full)

def row_card(df_plot, col, label, prefijo="", sufijo="", decimales=2, color=None, key=None, invertir_colores=False, df_full=None, es_porcentaje=False, solo_ult_dato=False, pp_todos=False, decimales_delta=None):
    """Card a la izquierda + mini gráfico a la derecha en una fila.
    solo_ult_dato=True: muestra solo variación vs último dato en p.p. absolutos (para inflación, tasas mensuales)"""
    color = color or COLORES.get(col, "#1B2A6B")
    if solo_ult_dato:
        val, fecha_str, var_ult, _, _ = get_variaciones(df_plot, col, serie_full=df_full, pp_absoluto=True)
        var_30, var_365 = None, None
    elif pp_todos:
        val, fecha_str, var_ult, var_30, var_365 = get_var_pp(col, df_plot, df_full)
    else:
        val, fecha_str, var_ult, var_30, var_365 = get_variaciones(df_plot, col, serie_full=df_full)

    col_esp_l, col_card, col_chart, col_esp_r = st.columns([1, 2, 4, 3])
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
                dec = decimales_delta if decimales_delta is not None else (decimales if pp_todos else 2)
                fmt = f"{abs(v):,.{dec}f}"
                if solo_ult_dato or es_porcentaje or pp_todos:
                    unidad = " pb" if (pp_todos and sufijo.strip() == "pb") else " p.p."
                    return f'<span class="{clase}">{flecha} {fmt}{unidad}</span>'
                return f'<span class="{clase}">{flecha} {fmt}%</span>'

            if solo_ult_dato:
                delta_html = f"""
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>"""
            else:
                delta_html = f"""
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d(var_ult)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d(var_30)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d(var_365)}</div>"""

            st.markdown(f"""
            <div class="row-card">
                <div class="var-label">{label}</div>
                <div class="var-value">{fmt_val}</div>
                <div class="var-fecha">últ. dato: {fecha_str}</div>
                <div class="var-delta-row">{delta_html}
                </div>
            </div>""", unsafe_allow_html=True)
    with col_chart:
        mini_chart(df_plot, col, color, key=key or col, label=label, fecha_str=fecha_str or "", df_full=df_full)

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
    "Actividad & Fiscal",
    "Macro Global",
    "Calendario",
    "Premarket",
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 0 — SECTOR EXTERNO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Reservas & Divisas</div>', unsafe_allow_html=True)
    row_card(df_f, "reservas", "Reservas Internacionales (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t0_reservas", df_full=df)
    # Compras BCRA — card sin variaciones + acumulado 2026 + barras
    _val_c, _fecha_c, _, _, _ = get_variaciones(df_f, "compras_usd_bcra", df)
    _fmt_c = f"USD {_val_c:,.0f} MM" if _val_c is not None else "-"
    # Acumulado 2026
    _acum_2026 = None
    if "compras_usd_bcra" in df.columns:
        _df_2026 = df[df["fecha"].dt.year == 2026][["fecha","compras_usd_bcra"]].dropna()
        if len(_df_2026) > 0:
            _acum_2026 = _df_2026["compras_usd_bcra"].sum()
    _fmt_acum = f"USD {_acum_2026:+,.0f} MM" if _acum_2026 is not None else "-"
    _color_acum = "#276749" if (_acum_2026 is not None and _acum_2026 >= 0) else "#C53030"
    _c_esp_l, _c_card, _c_chart, _c_esp_r = st.columns([1, 2, 4, 3])
    with _c_card:
        st.markdown(f"""<div class="row-card">
            <div class="var-label">Compras Netas de Divisas BCRA (USD MM)</div>
            <div class="var-value">{_fmt_c}</div>
            <div class="var-fecha">últ. dato: {_fecha_c or '-'}</div>
            <div style="margin-top:10px;padding-top:10px;border-top:1px solid #EDF2F7">
                <div style="font-size:12px;color:#718096;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px">Acumulado 2026</div>
                <div style="font-size:20px;font-weight:700;color:{_color_acum}">{_fmt_acum}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with _c_chart:
        mini_chart_barras(df_f, "compras_usd_bcra", key="t0_compras", label="Compras Netas de Divisas BCRA (USD MM)", fecha_str=_fecha_c or "")
    row_card(df_f, "depositos_usd", "Depósitos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t0_depusd", df_full=df)

    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Tipo de Cambio</div>', unsafe_allow_html=True)

    # TC: gráfico especial con 4 series
    val_min, fecha_str_min, var_ult_min, var_30_min, var_365_min = get_variaciones(df_f, "tc_mayorista", df)
    val_may, fecha_str_may, var_ult_may, var_30_may, var_365_may = get_variaciones(df_f, "tc_minorista", df)

    def _d_tc(v, inv=False):
        if v is None: return '<span class="neu">-</span>'
        clase = ("neg" if v >= 0 else "pos") if inv else ("pos" if v >= 0 else "neg")
        flecha = "▲" if v >= 0 else "▼"
        return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

    fmt_val_min = f"{val_min:,.2f}" if val_min is not None else "-"
    fmt_val_may = f"{val_may:,.2f}" if val_may is not None else "-"
    col_esp_l_tc, col_card_tc, col_chart_tc, col_esp_r_tc = st.columns([1, 2, 4, 3])
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
        layout_tc["height"] = 340
        layout_tc["showlegend"] = True
        layout_tc["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
        layout_tc["title"] = dict(text=f"<b>Tipo de Cambio ($)</b>  <span style='font-size:10px;color:#718096'>últ. dato: {fecha_str_min or '-'}</span>", font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
        layout_tc["margin"] = dict(l=10, r=10, t=40, b=10)
        fig_tc.update_layout(**layout_tc)
        st.plotly_chart(fig_tc, use_container_width=True, key="t0_tc")
        cols_tc = [c for c in ["tc_minorista","tc_mayorista","mep","ccl"] if c in df_f.columns or (dfd is not None and c in dfd.columns)]
        df_tc_dl = df_f[["fecha"] + [c for c in ["tc_minorista","tc_mayorista"] if c in df_f.columns]].copy()
        if dfd is not None:
            df_tc_dl = pd.merge(df_tc_dl, dfd[["fecha","mep","ccl"]].dropna(), on="fecha", how="outer")
        csv_tc = df_tc_dl.sort_values("fecha").to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Descargar datos", data=csv_tc, file_name="tipo_de_cambio.csv", mime="text/csv", key="dl_t0_tc")

    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Competitividad & Riesgo</div>', unsafe_allow_html=True)
    if dfi is not None:
        dfi_f = dfi[(dfi["fecha"].dt.date >= desde) & (dfi["fecha"].dt.date <= hasta)]
        row_card(dfi_f, "itcrm", "ITCRM (base 17-12-15=100)", decimales=2, color=COLORES["itcrm"], key="t0_itcrm", df_full=dfi)
    if dfr is not None:
        dfr_f = dfr[(dfr["fecha"].dt.date >= desde) & (dfr["fecha"].dt.date <= hasta)]
        row_card(dfr_f, "riesgo_pais", "Riesgo País EMBI", sufijo=" pb", decimales=0, color=COLORES["riesgo_pais"], key="t0_riesgo", invertir_colores=True, df_full=dfr, pp_todos=True)

    # ── Comercio Exterior ─────────────────────────────────────────────────────
    if dfa is not None:
        dfa_f0 = dfa[(dfa["fecha"].dt.date >= desde) & (dfa["fecha"].dt.date <= hasta)].copy()
        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Comercio Exterior</div>', unsafe_allow_html=True)

        _esp_l, _col_card, _col_chart, _esp_r = st.columns([1, 2, 4, 3])

        with _col_card:
            _val_bc, _fecha_bc, _var_bc, _, _ = (
                get_variaciones(dfa_f0, "balanza_comercial", dfa, pp_absoluto=True)
                if "balanza_comercial" in dfa_f0.columns else (None, None, None, None, None)
            )
            _, _, _, _, _yoy_expo = get_variaciones(dfa_f0, "exportaciones", dfa)
            _, _, _, _, _yoy_impo = get_variaciones(dfa_f0, "importaciones", dfa)
            if _val_bc is not None:
                _c_bc   = "pos" if _val_bc >= 0 else "neg"
                _s_bc   = "+" if _val_bc >= 0 else ""
                _vbc_h  = (f'<span class="{"pos" if (_var_bc or 0)>=0 else "neg"}">'
                           f'{"▲" if (_var_bc or 0)>=0 else "▼"} USD {abs(_var_bc or 0):,.0f} MM</span>')
                _ye = (f'<span class="{"pos" if (_yoy_expo or 0)>=0 else "neg"}">'
                       f'{("+" if (_yoy_expo or 0)>=0 else "")}{_yoy_expo:.1f}% a/a</span>'
                       if _yoy_expo is not None else "—")
                _yi = (f'<span class="{"neg" if (_yoy_impo or 0)>=0 else "pos"}">'
                       f'{("+" if (_yoy_impo or 0)>=0 else "")}{_yoy_impo:.1f}% a/a</span>'
                       if _yoy_impo is not None else "—")
                st.markdown(f"""
                <div class="row-card">
                    <div class="var-label">Balanza Comercial</div>
                    <div class="var-value"><span class="{_c_bc}">{_s_bc}USD {_val_bc:,.0f} MM</span></div>
                    <div class="var-fecha">últ. dato: {_fecha_bc}</div>
                    <div class="var-delta-row">
                        <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_vbc_h}</div>
                    </div>
                    <div style="margin-top:6px;font-size:11px;border-top:1px solid #E2E8F0;padding-top:5px">
                        <div style="color:#718096">Expo a/a: {_ye}</div>
                        <div style="color:#718096">Impo a/a: {_yi}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with _col_chart:
            _fig_ce = go.Figure()
            if "balanza_comercial" in dfa_f0.columns:
                _s_bal = dfa_f0[["fecha", "balanza_comercial"]].dropna(subset=["balanza_comercial"])
                _c_bal = ["#276749" if v >= 0 else "#9B2335" for v in _s_bal["balanza_comercial"]]
                _fig_ce.add_trace(go.Bar(
                    x=_s_bal["fecha"], y=_s_bal["balanza_comercial"],
                    name="Balanza", marker_color=_c_bal, yaxis="y2",
                    hovertemplate="%{x|%b/%Y}<br>Balanza: USD %{y:,.0f} MM<extra></extra>",
                ))
            for _cc, _ll, _hx in [
                ("exportaciones", "Exportaciones", "#D69E2E"),
                ("importaciones", "Importaciones", "#9B2335"),
            ]:
                if _cc in dfa_f0.columns:
                    _ss = dfa_f0[["fecha", _cc]].dropna(subset=[_cc])
                    if not _ss.empty:
                        _fig_ce.add_trace(go.Scatter(
                            x=_ss["fecha"], y=_ss[_cc], name=_ll,
                            line=dict(color=_hx, width=2),
                            hovertemplate=f"%{{x|%b/%Y}}<br>{_ll}: USD %{{y:,.0f}} MM<extra></extra>",
                        ))
            _lce = dict(LAYOUT_BASE)
            _lce.update(dict(
                height=300, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
                yaxis=dict(showgrid=True, gridcolor="#EDF2F7", zeroline=False,
                           tickfont=dict(size=10), title="USD MM"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, zeroline=True,
                            zerolinecolor="#CBD5E0", tickfont=dict(size=10), title="Balanza"),
                margin=dict(l=10, r=55, t=40, b=10),
            ))
            _fig_ce.update_layout(**_lce)
            st.plotly_chart(_fig_ce, use_container_width=True, key="t0_combo_comercio")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — POLÍTICA MONETARIA
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Agregados Monetarios</div>', unsafe_allow_html=True)
    row_card(df_f, "base_monetaria", "Base Monetaria ($ MM)", prefijo="$ ", sufijo=" MM", decimales=0, key="t1_bm", df_full=df)
    # M2 Transaccional — promedio móvil 30d
    if "m2_transaccional" in df.columns:
        df_m2t_full = df[["fecha","m2_transaccional"]].dropna().copy()
        df_m2t_full["fecha"] = pd.to_datetime(df_m2t_full["fecha"])
        df_m2t_full = df_m2t_full.sort_values("fecha")
        df_m2t_full["m2t_ma30"] = df_m2t_full["m2_transaccional"].rolling(30, min_periods=15).mean()
        df_m2t_f = df_m2t_full[(df_m2t_full["fecha"].dt.date >= desde) & (df_m2t_full["fecha"].dt.date <= hasta)]
        row_card(df_m2t_f, "m2t_ma30", "M2 Transaccional Sector Privado - Prom. 30d ($ MM)", prefijo="$ ", sufijo=" MM", decimales=0, key="t1_m2trans", df_full=df_m2t_full)
    row_card(df_f, "m2_privado", "M2 Privado - Var. interanual (%)", sufijo="%", decimales=2, color=COLORES["m2_privado"], key="t1_m2", df_full=df, es_porcentaje=True)

    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Tasas de Interés</div>', unsafe_allow_html=True)

    # Card TAMAR con gráfico TAMAR+BADLAR juntos — variaciones en p.p. absolutos
    def _get_pp(col_name, s_f, s_full):
        """Retorna (val, fecha_str, pp_ult, pp_30, pp_365) como diferencia absoluta en p.p."""
        val, fecha_str, pp_ult, _, _ = get_variaciones(s_f, col_name, s_full, pp_absoluto=True)
        if val is None:
            return val, fecha_str, None, None, None
        s = s_full[["fecha", col_name]].dropna(subset=[col_name]).copy()
        s["fecha"] = pd.to_datetime(s["fecha"])
        s = s.sort_values("fecha")
        fecha = s.iloc[-1]["fecha"]
        def _pp_vs(dias):
            objetivo = fecha - timedelta(days=dias)
            ventana = s[(s["fecha"] >= objetivo - timedelta(days=30)) & (s["fecha"] <= objetivo + timedelta(days=30))]
            if len(ventana) == 0: return None
            idx = (ventana["fecha"] - objetivo).abs().idxmin()
            return val - float(ventana.loc[idx, col_name])
        return val, fecha_str, pp_ult, _pp_vs(30), _pp_vs(365)

    val_tamar,     fecha_tamar,     var_ult_tamar,     var_30_tamar,     var_365_tamar     = _get_pp("tamar",              df_f, df)
    val_badlar,    fecha_badlar,    var_ult_badlar,    var_30_badlar,    var_365_badlar    = _get_pp("badlar",             df_f, df)
    val_adelanto,  fecha_adelanto,  var_ult_adelanto,  var_30_adelanto,  var_365_adelanto  = _get_pp("tasa_adelanto_cc",   df_f, df)
    val_pases,     fecha_pases,     var_ult_pases,     var_30_pases,     var_365_pases     = _get_pp("tasa_pases_terceros",df_f, df)

    def _d_tasa(v, pp=False):
        if v is None: return '<span class="neu">-</span>'
        clase = "pos" if v >= 0 else "neg"
        flecha = "▲" if v >= 0 else "▼"
        unidad = " p.p." if pp else "%"
        return f'<span class="{clase}">{flecha} {abs(v):.2f}{unidad}</span>'

    def _tasa_bloque(label, val, var_ult, var_30, var_365, color):
        if val is None:
            return f'<div style="margin-bottom:8px"><div style="font-size:12px;font-weight:700;color:{color}">{label}: -</div></div>'
        fmt = f"{val:,.2f}%"
        return f"""
        <div style="margin-bottom:8px">
            <div style="font-size:12px;font-weight:700;color:{color}">{label}: {fmt}</div>
            <div class="var-delta-row">
                <div class="delta-item"><span class="delta-label">vs últ.</span>{_d_tasa(var_ult, pp=True)}</div>
                <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_tasa(var_30, pp=True)}</div>
                <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_tasa(var_365, pp=True)}</div>
            </div>
        </div>"""

    col_esp_l_t, col_card_t, col_chart_t, col_esp_r_t = st.columns([1, 2, 4, 3])
    with col_card_t:
        st.markdown(f"""
        <div class="row-card">
            <div class="var-label">Tasas de Interés (% TNA)</div>
            {_tasa_bloque("TAMAR",      val_tamar,    var_ult_tamar,    var_30_tamar,    var_365_tamar,    COLORES["tamar"])}
            {_tasa_bloque("BADLAR",     val_badlar,   var_ult_badlar,   var_30_badlar,   var_365_badlar,   COLORES["badlar"])}
            {_tasa_bloque("Adelanto CC",val_adelanto, var_ult_adelanto, var_30_adelanto, var_365_adelanto, COLORES["tasa_adelanto_cc"])}
            {_tasa_bloque("Pases 3ros", val_pases,    var_ult_pases,    var_30_pases,    var_365_pases,    COLORES["tasa_pases_terceros"])}
        </div>""", unsafe_allow_html=True)
    with col_chart_t:
        fig_tasas = go.Figure()
        series_tasas = [
            ("tamar",               "TAMAR",            COLORES["tamar"]),
            ("badlar",              "BADLAR",            COLORES["badlar"]),
            ("tasa_adelanto_cc",    "Adelanto CC",       COLORES["tasa_adelanto_cc"]),
            ("tasa_pases_terceros", "Pases 3ros",        COLORES["tasa_pases_terceros"]),
        ]
        for col_t, lab_t, color_t in series_tasas:
            if col_t in df_f.columns:
                dp = df_f[["fecha", col_t]].dropna()
                if not dp.empty:
                    fig_tasas.add_trace(go.Scatter(x=dp["fecha"], y=dp[col_t], mode="lines",
                        name=lab_t, line=dict(color=color_t, width=2),
                        hovertemplate="%{x|%d/%m/%Y}<br>" + lab_t + ": %{y:,.2f}%<extra></extra>"))
        layout_t = dict(LAYOUT_BASE)
        layout_t["height"] = 340
        layout_t["showlegend"] = True
        layout_t["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
        layout_t["title"] = dict(text=f"<b>Tasas de Interés (% TNA)</b>  <span style='font-size:10px;color:#718096'>últ. dato: {fecha_tamar or '-'}</span>", font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
        layout_t["margin"] = dict(l=10, r=10, t=40, b=10)
        fig_tasas.update_layout(**layout_t)
        st.plotly_chart(fig_tasas, use_container_width=True, key="t1_tasas")
        cols_tasas = [c for c in ["tamar","badlar","tasa_adelanto_cc","tasa_pases_terceros"] if c in df.columns]
        csv_tasas = df[["fecha"] + cols_tasas].dropna(subset=cols_tasas, how="all").sort_values("fecha").to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Descargar datos", data=csv_tasas, file_name="tasas_interes.csv", mime="text/csv", key="dl_t1_tasas")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — SISTEMA FINANCIERO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Crédito & Depósitos</div>', unsafe_allow_html=True)
    row_card(df_f, "depositos_usd", "Depósitos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t2_depusd", df_full=df)
    row_card(df_f, "prestamos_usd", "Préstamos en Dólares - Sector Privado (USD MM)", prefijo="USD ", sufijo=" MM", decimales=0, key="t2_prestusd", df_full=df)

    if "prestamos_priv" in df_f.columns and "cer" in df_f.columns:
        df_prest = df_f[["fecha", "prestamos_priv", "cer"]].dropna().copy()
        # Traer a pesos constantes de hoy usando CER como deflactor
        # prestamos_priv viene en $ MM; resultado también en $ MM constantes
        cer_hoy = df_prest["cer"].iloc[-1]
        df_prest["prestamos_constantes"] = (df_prest["prestamos_priv"] * cer_hoy / df_prest["cer"]) / 1000
        row_card(df_prest, "prestamos_constantes", "Préstamos al Sector Privado ($ miles de MM constantes de hoy)",
                 prefijo="$ ", sufijo=" miles MM", decimales=0, key="t2_prest_const")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — INFLACIÓN
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">IPC & Expectativas</div>', unsafe_allow_html=True)
    row_card_barras(df_f, "inflacion_mensual", "Inflación Mensual IPC (%)", sufijo="%", decimales=1,
             key="t3_inf_men", invertir_colores=True, df_full=df, solo_ult_dato=True)
    row_card(df_f, "inflacion_interanual", "Inflación Interanual IPC (%)", sufijo="%", decimales=1,
             color=COLORES["inflacion_interanual"], key="t3_inf_ia", invertir_colores=True, df_full=df, solo_ult_dato=True)
    row_card(df_f, "rem_inflacion", "Inflación Esperada REM - Próximos 12 meses - Mediana (% i.a.)",
             sufijo="%", decimales=1, color=COLORES["rem_inflacion"], key="t3_rem", invertir_colores=True, df_full=df, solo_ult_dato=True)

    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Indexación</div>', unsafe_allow_html=True)
    row_card(df_f, "cer", "CER - Coeficiente de Estabilización de Referencia (base 2-feb-02=1)",
             decimales=2, color=COLORES["cer"], key="t3_cer", df_full=df)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — MERCADOS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    if dfm is None:
        st.warning("Datos de mercados no disponibles aún.")
    else:
        dfm_f = dfm[(dfm["fecha"].dt.date >= desde) & (dfm["fecha"].dt.date <= hasta)].copy()

        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Índices & Renta Variable</div>', unsafe_allow_html=True)
        row_card(dfm_f, "sp500", "S&P 500", decimales=2, color=COLORES["sp500"], key="t4_sp500", df_full=dfm)
        row_card(dfm_f, "nasdaq", "Nasdaq Composite", decimales=2, color=COLORES["nasdaq"], key="t4_nasdaq", df_full=dfm)

        if dfd is not None:
            dfd_m = dfd[(dfd["fecha"].dt.date >= desde) & (dfd["fecha"].dt.date <= hasta)]
            dfd_m_full = dfd.copy()
            df_mccl = pd.merge(dfm_f[["fecha","merval"]], dfd_m[["fecha","ccl"]], on="fecha", how="inner").dropna()
            if len(df_mccl) > 0:
                df_mccl["merval_ccl"] = df_mccl["merval"] / df_mccl["ccl"]
                df_mccl_full = pd.merge(dfm[["fecha","merval"]], dfd_m_full[["fecha","ccl"]], on="fecha", how="inner").dropna()
                df_mccl_full["merval_ccl"] = df_mccl_full["merval"] / df_mccl_full["ccl"]
                row_card(df_mccl, "merval_ccl", "Merval en USD (CCL)", prefijo="USD ", decimales=2,
                         color=COLORES["merval_ccl"], key="t4_merval_ccl", df_full=df_mccl_full)

        row_card(dfm_f, "eem", "EEM - iShares MSCI Emerging Markets ETF", prefijo="USD ", decimales=2,
                 color=COLORES["eem"], key="t4_eem", df_full=dfm)

        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Renta Fija & Moneda</div>', unsafe_allow_html=True)
        row_card(dfm_f, "us10y", "US Treasury 10Y (% yield)", sufijo="%", decimales=2,
                 color=COLORES["us10y"], key="t4_us10y", invertir_colores=True, pp_todos=True, df_full=dfm)
        row_card(dfm_f, "emb", "EMB - iShares JP Morgan EM Bond ETF", prefijo="USD ", decimales=2,
                 color=COLORES["emb"], key="t4_emb", df_full=dfm)
        row_card(dfm_f, "dxy", "DXY - Índice Dólar", decimales=2, color=COLORES["dxy"], key="t4_dxy", df_full=dfm)
        row_card(dfm_f, "vix", "VIX - Índice de Volatilidad (CBOE)", decimales=2, color=COLORES["vix"], key="t4_vix", invertir_colores=True, df_full=dfm)

        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Commodities</div>', unsafe_allow_html=True)
        row_card(dfm_f, "oro", "Oro (USD/oz)", prefijo="USD ", decimales=2, color=COLORES["oro"], key="t4_oro", df_full=dfm)
        row_card(dfm_f, "plata", "Plata (USD/oz)", prefijo="USD ", decimales=2, color=COLORES["plata"], key="t4_plata", df_full=dfm)

        # Petróleo — gráfico especial Brent + WTI
        val_brent, fecha_brent, var_ult_brent, var_30_brent, var_365_brent = get_variaciones(dfm_f, "brent", dfm)
        val_wti, _, var_ult_wti, var_30_wti, var_365_wti = get_variaciones(dfm_f, "wti", dfm)

        def _d_pet(v):
            if v is None: return '<span class="neu">-</span>'
            clase = "pos" if v >= 0 else "neg"
            flecha = "▲" if v >= 0 else "▼"
            return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

        fmt_val_brent = f"{val_brent:,.2f}" if val_brent is not None else "-"
        fmt_val_wti   = f"{val_wti:,.2f}"   if val_wti   is not None else "-"
        col_esp_l_pet, col_card_pet, col_chart_pet, col_esp_r_pet = st.columns([1, 2, 4, 3])
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
            layout_pet["height"] = 340
            layout_pet["showlegend"] = True
            layout_pet["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
            layout_pet["title"] = dict(text="<b>Petróleo (USD/bbl)</b>", font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
            layout_pet["margin"] = dict(l=10, r=10, t=50, b=10)
            fig_pet.update_layout(**layout_pet)
            st.plotly_chart(fig_pet, use_container_width=True, key="t4_petroleo")
            cols_pet = [c for c in ["brent","wti"] if c in dfm.columns]
            csv_pet = dfm[["fecha"] + cols_pet].dropna(subset=cols_pet, how="all").sort_values("fecha").to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Descargar datos", data=csv_pet, file_name="petroleo.csv", mime="text/csv", key="dl_t4_petroleo")

        # Granos en USD/ton
        dfm_granos_full = dfm.copy()
        for g, factor in [("soja", 36.744), ("maiz", 39.368), ("trigo", 36.744)]:
            if g in dfm_granos_full.columns:
                dfm_granos_full[f"{g}_ton"] = (dfm_granos_full[g] / 100) * factor
        dfm_granos = dfm_f.copy()
        for g, factor in [("soja", 36.744), ("maiz", 39.368), ("trigo", 36.744)]:
            if g in dfm_granos.columns:
                dfm_granos[f"{g}_ton"] = (dfm_granos[g] / 100) * factor

        row_card(dfm_granos, "soja_ton",  "Soja CBOT (USD/ton)",  prefijo="USD ", decimales=2, color=COLORES["soja"],  key="t4_soja",  df_full=dfm_granos_full)
        row_card(dfm_granos, "maiz_ton",  "Maíz CBOT (USD/ton)",  prefijo="USD ", decimales=2, color=COLORES["maiz"],  key="t4_maiz",  df_full=dfm_granos_full)
        row_card(dfm_granos, "trigo_ton", "Trigo CBOT (USD/ton)", prefijo="USD ", decimales=2, color=COLORES["trigo"], key="t4_trigo", df_full=dfm_granos_full)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — ACTIVIDAD & FISCAL
# ════════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    if dfa is None:
        st.info("Los datos de Actividad & Fiscal aún no fueron generados. Ejecutá el Action manualmente.")
    else:
        dfa_f = dfa[(dfa["fecha"].dt.date >= desde) & (dfa["fecha"].dt.date <= hasta)].copy()

        # ── Actividad Económica ───────────────────────────────────────────────
        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Actividad Económica</div>', unsafe_allow_html=True)

        row_card(dfa_f, "emae_desest", "EMAE — Serie Desestacionalizada (Base 2004)", decimales=1,
                 color="#2B4FBF", key="t5_emae_d", df_full=dfa)

        # ── Sector Fiscal ─────────────────────────────────────────────────────
        _st_l, _st_c = st.columns([1, 9])
        with _st_c:
            st.markdown('<div class="section-title">Sector Fiscal</div>', unsafe_allow_html=True)

        # Recaudación — mostrar nivel + variación interanual en el gráfico de barras
        if "recaudacion" in dfa_f.columns and len(dfa_f["recaudacion"].dropna()) > 0:
            # Calcular variación interanual nosotros
            dfa_recaud = dfa[["fecha","recaudacion"]].dropna().copy()
            dfa_recaud["fecha"] = pd.to_datetime(dfa_recaud["fecha"])
            dfa_recaud = dfa_recaud.sort_values("fecha")
            dfa_recaud["recaud_ya"] = dfa_recaud["recaudacion"] / dfa_recaud["recaudacion"].shift(12) - 1
            dfa_recaud["recaud_ya"] = dfa_recaud["recaud_ya"] * 100
            dfa_recaud_f = dfa_recaud[(dfa_recaud["fecha"].dt.date >= desde) & (dfa_recaud["fecha"].dt.date <= hasta)]

            col_esp_l, col_card, col_chart, col_esp_r = st.columns([1, 2, 4, 3])
            with col_card:
                val_r = dfa_f["recaudacion"].dropna().iloc[-1] if not dfa_f["recaudacion"].dropna().empty else None
                fecha_r = dfa_f.loc[dfa_f["recaudacion"].notna(), "fecha"].iloc[-1].strftime("%d/%m/%y") if val_r is not None else "-"
                val_ya = dfa_recaud_f["recaud_ya"].dropna().iloc[-1] if not dfa_recaud_f["recaud_ya"].dropna().empty else None
                if val_r is not None:
                    clase_ya = "pos" if (val_ya or 0) >= 0 else "neg"
                    flecha_ya = "▲" if (val_ya or 0) >= 0 else "▼"
                    ya_html = f'<span class="{clase_ya}">{flecha_ya} {abs(val_ya):.1f}%</span>' if val_ya is not None else '<span class="neu">-</span>'
                    st.markdown(f"""
                    <div class="row-card">
                        <div class="var-label">Recaudación Total AFIP/ARCA ($ miles de MM)</div>
                        <div class="var-value">$ {val_r:,.0f} miles MM</div>
                        <div class="var-fecha">últ. dato: {fecha_r}</div>
                        <div class="var-delta-row">
                            <div class="delta-item"><span class="delta-label">var. i.a.</span>{ya_html}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            with col_chart:
                if not dfa_recaud_f["recaud_ya"].dropna().empty:
                    mini_chart_barras(dfa_recaud_f, "recaud_ya", key="t5_recaud",
                                      label="Recaudación — Variación interanual (%)",
                                      fecha_str=fecha_r, df_full=dfa_recaud)

        # Resultado primario y financiero — barras
        for col_res, label_res, key_res in [
            ("resultado_primario",   "Resultado Fiscal Primario ($ miles de MM)",   "t5_rprim"),
            ("resultado_financiero", "Resultado Fiscal Financiero ($ miles de MM)", "t5_rfin"),
        ]:
            if col_res in dfa_f.columns and not dfa_f[col_res].dropna().empty:
                col_esp_l, col_card, col_chart, col_esp_r = st.columns([1, 2, 4, 3])
                with col_card:
                    val_r, fecha_r, var_r, _, _ = get_variaciones(dfa_f, col_res, pp_absoluto=True)
                    if val_r is not None:
                        color_r = "pos" if val_r >= 0 else "neg"
                        signo = "+" if val_r >= 0 else ""
                        var_html = f'<span class="{"pos" if var_r>=0 else "neg"}">{"▲" if var_r>=0 else "▼"} $ {abs(var_r):,.0f} miles MM</span>'
                        st.markdown(f"""
                        <div class="row-card">
                            <div class="var-label">{label_res}</div>
                            <div class="var-value"><span class="{color_r}">{signo}$ {val_r:,.0f} miles MM</span></div>
                            <div class="var-fecha">últ. dato: {fecha_r}</div>
                            <div class="var-delta-row">
                                <div class="delta-item"><span class="delta-label">vs últ. dato</span>{var_html}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                with col_chart:
                    mini_chart_barras(dfa_f, col_res, key=key_res, label=label_res,
                                      fecha_str=fecha_r or "", df_full=dfa)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 — MACRO GLOBAL
# ════════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    _df_tasas  = cargar_macro_tasas()
    _df_infl   = cargar_macro_inflacion()
    _df_unemp  = cargar_macro_desempleo()
    _df_gdp    = cargar_macro_gdp()
    _df_labor  = cargar_macro_labor()
    _df_yields = cargar_macro_yields()
    _df_pce    = cargar_macro_pce()

    _TASA_LABEL = {
        "us_fed":   ("Fed Funds", "EE.UU.", "#1B2A6B"),
        "ecb_rate": ("BCE", "Eurozona", "#0070C0"),
        "boj_rate": ("BoJ", "Japón", "#BC002D"),
        "selic":    ("SELIC", "Brasil", "#009C3B"),
    }
    _CPI_COLS = {
        "us_cpi_yoy": ("EE.UU.", "#1B2A6B"),
        "eu_cpi_yoy": ("Eurozona", "#0070C0"),
        "jp_cpi_yoy": ("Japón", "#BC002D"),
        "br_cpi_yoy": ("Brasil", "#009C3B"),
        "cn_cpi_yoy": ("China", "#DE2910"),
    }
    _GDP_COLS = {
        "world_gdp": ("Mundo",     "#4A5568"),
        "us_gdp":    ("EE.UU.",    "#1B2A6B"),
        "eu_gdp":    ("Eurozona",  "#0070C0"),
        "cn_gdp":    ("China",     "#DE2910"),
        "jp_gdp":    ("Japón",     "#BC002D"),
        "br_gdp":    ("Brasil",    "#009C3B"),
        "ar_gdp":    ("Argentina", "#74ACDF"),
    }

    def _ultimo(df, col):
        if df is None or col not in df.columns:
            return None, None
        s = df[["fecha", col]].dropna(subset=[col])
        if s.empty:
            return None, None
        row = s.iloc[-1]
        return float(row[col]), row["fecha"]

    def _delta(df, col):
        if df is None or col not in df.columns:
            return None
        s = df[[col]].dropna()
        if len(s) < 2:
            return None
        return float(s.iloc[-1][col]) - float(s.iloc[-2][col])

    def _stat_card(label, val, fecha, dlt, fmt="{:.2f}%", color="#1B2A6B", invert=False):
        fecha_str = pd.Timestamp(fecha).strftime("%b %Y") if fecha is not None else ""
        val_str = fmt.format(val) if val is not None else "—"
        dlt_str = f"{dlt:+.2f}" if dlt is not None else "—"
        if dlt is not None:
            dlt_class = ("neg" if invert else "pos") if dlt > 0 else (("pos" if invert else "neg") if dlt < 0 else "neu")
        else:
            dlt_class = "neu"
        return (
            f"<div style='border:1px solid #E2E8F0;border-radius:6px;padding:8px 10px;"
            f"background:#FAFAFA;text-align:center;margin:2px'>"
            f"<div style='font-size:11px;color:#718096;white-space:nowrap'>{label}</div>"
            f"<div style='font-size:18px;font-weight:700;color:{color}'>{val_str}</div>"
            f"<div style='font-size:10px;color:#A0AEC0'>{fecha_str}</div>"
            f"<div style='font-size:11px'><span class='{dlt_class}'>{dlt_str}</span></div>"
            f"</div>"
        )

    _LAYOUT_COMPACT = dict(
        height=240, margin=dict(l=5, r=5, t=25, b=5),
        legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
        yaxis=dict(title_font=dict(size=10), tickfont=dict(size=9)),
        xaxis=dict(tickfont=dict(size=9)),
        plot_bgcolor="#F7F9FC", paper_bgcolor="#F7F9FC",
    )

    # ── Fila 1: Tasas | Inflación ──────────────────────────────────────────────
    _mg_col1, _mg_col2 = st.columns(2)

    with _mg_col1:
        st.markdown('<div class="section-title">Tasas de Política Monetaria</div>', unsafe_allow_html=True)
        if _df_tasas is not None:
            _tc = st.columns(4)
            for i, (col, (label, pais, color)) in enumerate(_TASA_LABEL.items()):
                val, fecha = _ultimo(_df_tasas, col)
                dlt = _delta(_df_tasas, col)
                with _tc[i]:
                    st.markdown(_stat_card(f"{label}<br><span style='font-size:10px'>{pais}</span>",
                                           val, fecha, dlt, color=color), unsafe_allow_html=True)
            fig_t = go.Figure()
            for col, (label, pais, color) in _TASA_LABEL.items():
                if col in _df_tasas.columns:
                    _s = _df_tasas[["fecha", col]].dropna(subset=[col])
                    if not _s.empty:
                        fig_t.add_trace(go.Scatter(
                            x=_s["fecha"], y=_s[col], name=f"{label} ({pais})",
                            line=dict(color=color, width=2)
                        ))
            fig_t.update_layout(**_LAYOUT_COMPACT, yaxis_title="% anual")
            st.plotly_chart(fig_t, use_container_width=True, key="macro_tasas_chart")

    with _mg_col2:
        st.markdown('<div class="section-title">Inflación (IPC Interanual)</div>', unsafe_allow_html=True)
        if _df_infl is not None:
            _ic = st.columns(5)
            for i, (col, (pais, color)) in enumerate(_CPI_COLS.items()):
                val, fecha = _ultimo(_df_infl, col)
                dlt = _delta(_df_infl, col)
                with _ic[i]:
                    st.markdown(_stat_card(pais, val, fecha, dlt, fmt="{:.1f}%",
                                           color=color, invert=True), unsafe_allow_html=True)
            fig_i = go.Figure()
            for col, (pais, color) in _CPI_COLS.items():
                if col in _df_infl.columns:
                    _s = _df_infl[["fecha", col]].dropna(subset=[col])
                    if not _s.empty:
                        fig_i.add_trace(go.Scatter(
                            x=_s["fecha"], y=_s[col], name=pais,
                            line=dict(color=color, width=2)
                        ))
            fig_i.add_hline(y=2, line_dash="dot", line_color="#718096",
                            annotation_text="2%", annotation_position="right",
                            annotation_font_size=9)
            fig_i.update_layout(**_LAYOUT_COMPACT, yaxis_title="% interanual")
            st.plotly_chart(fig_i, use_container_width=True, key="macro_infl_chart")

    # ── Fila 2: Desempleo | PIB ────────────────────────────────────────────────
    _mg_col3, _mg_col4 = st.columns(2)

    with _mg_col3:
        st.markdown('<div class="section-title">Desempleo</div>', unsafe_allow_html=True)
        if _df_unemp is not None:
            _u_labels = {
                "us_unrate": ("EE.UU.",   "#1B2A6B"),
                "eu_unrate": ("Eurozona", "#0070C0"),
                "jp_unrate": ("Japón",    "#BC002D"),
                "uk_unrate": ("Reino Unido", "#276749"),
                "br_unrate": ("Brasil",   "#009C3B"),
            }
            _u_avail = {k: v for k, v in _u_labels.items() if k in _df_unemp.columns}
            _uc = st.columns(len(_u_avail))
            for i, (col, (pais, color)) in enumerate(_u_avail.items()):
                val, fecha = _ultimo(_df_unemp, col)
                dlt = _delta(_df_unemp, col)
                with _uc[i]:
                    st.markdown(_stat_card(pais, val, fecha, dlt, fmt="{:.1f}%",
                                           color=color, invert=True), unsafe_allow_html=True)
            fig_u = go.Figure()
            for col, (pais, color) in _u_avail.items():
                _s = _df_unemp[["fecha", col]].dropna(subset=[col])
                if not _s.empty:
                    fig_u.add_trace(go.Scatter(x=_s["fecha"], y=_s[col], name=pais,
                                               line=dict(color=color, width=2)))
            fig_u.update_layout(**_LAYOUT_COMPACT, yaxis_title="% desocupados")
            st.plotly_chart(fig_u, use_container_width=True, key="macro_unemp_chart")

    with _mg_col4:
        st.markdown('<div class="section-title">Crecimiento del PIB (%) — hist. + proy. IMF</div>', unsafe_allow_html=True)
        if _df_gdp is not None:
            _gdp_reciente = _df_gdp[_df_gdp["fecha"] >= pd.Timestamp("2018-01-01")]
            _HIST_CUTOFF = pd.Timestamp("2026-01-01")
            fig_g = go.Figure()
            for col, (pais, color) in _GDP_COLS.items():
                if col in _gdp_reciente.columns:
                    _s = _gdp_reciente[["fecha", col]].dropna(subset=[col])
                    if not _s.empty:
                        _s_hist = _s[_s["fecha"] < _HIST_CUTOFF]
                        _s_proj = _s[_s["fecha"] >= _HIST_CUTOFF]
                        if not _s_hist.empty:
                            fig_g.add_trace(go.Bar(
                                x=_s_hist["fecha"].dt.year.astype(str), y=_s_hist[col],
                                name=pais, marker_color=color, showlegend=True,
                                legendgroup=pais,
                            ))
                        if not _s_proj.empty:
                            fig_g.add_trace(go.Bar(
                                x=_s_proj["fecha"].dt.year.astype(str), y=_s_proj[col],
                                name=pais, marker_color=color,
                                showlegend=False, legendgroup=pais,
                            ))
            # Mark projection years with annotation on x-axis
            for yr in ["2026", "2027"]:
                fig_g.add_annotation(
                    x=yr, y=0, text="★", showarrow=False,
                    font=dict(size=8, color="#718096"), yshift=-14,
                )
            _layout_gdp = dict(**_LAYOUT_COMPACT)
            _layout_gdp["margin"] = dict(l=5, r=5, t=25, b=30)
            fig_g.update_layout(
                barmode="group", **_layout_gdp,
                yaxis_title="% crecimiento real",
                annotations=fig_g.layout.annotations + (go.layout.Annotation(
                    x=0.98, y=1.02, xref="paper", yref="paper",
                    text="★ proyección IMF", showarrow=False,
                    font=dict(size=9, color="#718096"), xanchor="right",
                ),),
            )
            st.plotly_chart(fig_g, use_container_width=True, key="macro_gdp_chart")

    # ── Fila 3: PCE full width ─────────────────────────────────────────────────
    _mg_col5, _mg_col6 = st.columns(2)

    with _mg_col5:
        st.markdown('<div class="section-title">PCE EE.UU. (Gasto Personal en Consumo) — medida favorita de la Fed</div>', unsafe_allow_html=True)
        if _df_pce is not None:
            _pc = st.columns(2)
            for i, (col, label, color) in enumerate([
                ("us_pce_yoy",      "PCE",      "#7B341E"),
                ("us_core_pce_yoy", "Core PCE", "#C05621"),
            ]):
                val, fecha = _ultimo(_df_pce, col)
                dlt = _delta(_df_pce, col)
                with _pc[i]:
                    st.markdown(_stat_card(label, val, fecha, dlt, fmt="{:.1f}%",
                                           color=color, invert=True), unsafe_allow_html=True)
            fig_p = go.Figure()
            for col, label, color in [
                ("us_pce_yoy", "PCE", "#7B341E"),
                ("us_core_pce_yoy", "Core PCE", "#C05621"),
            ]:
                if col in _df_pce.columns:
                    _s = _df_pce[["fecha", col]].dropna(subset=[col])
                    if not _s.empty:
                        fig_p.add_trace(go.Scatter(
                            x=_s["fecha"], y=_s[col], name=label,
                            line=dict(color=color, width=2)
                        ))
            fig_p.add_hline(y=2, line_dash="dot", line_color="#718096",
                            annotation_text="Meta 2%", annotation_position="right",
                            annotation_font_size=9)
            fig_p.update_layout(**_LAYOUT_COMPACT, yaxis_title="% interanual")
            st.plotly_chart(fig_p, use_container_width=True, key="macro_pce_chart")

    with _mg_col6:
        st.markdown('<div class="section-title">Spread Tasas EE.UU. — 10Y minus 2Y (p.b.)</div>', unsafe_allow_html=True)
        if _df_yields is not None and "us_10y" in _df_yields.columns and "us_2y" in _df_yields.columns:
            _df_spr = _df_yields[["fecha", "us_10y", "us_2y"]].dropna().copy()
            _df_spr["spread"] = (_df_spr["us_10y"] - _df_spr["us_2y"]) * 100  # convert % → bp
            _val_spr  = float(_df_spr.iloc[-1]["spread"]) if not _df_spr.empty else None
            _val_10y, _fecha_10y = _ultimo(_df_yields, "us_10y")
            _val_2y,  _fecha_2y  = _ultimo(_df_yields, "us_2y")
            _yc = st.columns(3)
            for i, (label, val, color) in enumerate([
                ("10Y", _val_10y, "#1B2A6B"),
                ("2Y",  _val_2y,  "#0070C0"),
                ("Spread", (_val_spr / 100 if _val_spr is not None else None), "#553C9A"),
            ]):
                with _yc[i]:
                    st.markdown(_stat_card(label, val, _fecha_10y, None, fmt="{:.2f}%",
                                           color=color), unsafe_allow_html=True)
            fig_y = go.Figure()
            _spr_colors = ["#276749" if v >= 0 else "#9B2335" for v in _df_spr["spread"]]
            fig_y.add_trace(go.Bar(
                x=_df_spr["fecha"], y=_df_spr["spread"],
                name="Spread 10Y-2Y", marker_color=_spr_colors,
            ))
            fig_y.add_hline(y=0, line_dash="dot", line_color="#718096")
            fig_y.update_layout(**_LAYOUT_COMPACT, yaxis_title="puntos básicos")
            st.plotly_chart(fig_y, use_container_width=True, key="macro_yields_chart")

    # ── Fila 4: Mercado Laboral EE.UU. ────────────────────────────────────────
    st.markdown('<div class="section-title">Mercado Laboral EE.UU.</div>', unsafe_allow_html=True)
    if _df_labor is not None:
        _mg_col7, _mg_col8, _mg_col9 = st.columns(3)

        with _mg_col7:
            st.markdown("<div style='font-size:12px;font-weight:600;color:#4A5568;margin-bottom:4px'>Nóminas no Agrícolas — NFP (miles)</div>", unsafe_allow_html=True)
            val_nfp, fecha_nfp = _ultimo(_df_labor, "nfp")
            dlt_nfp = _delta(_df_labor, "nfp")
            _nfp_color = "#276749" if (val_nfp or 0) > 0 else "#9B2335"
            st.markdown(_stat_card("NFP mensual", val_nfp, fecha_nfp, dlt_nfp,
                                   fmt="{:+.0f}k", color=_nfp_color), unsafe_allow_html=True)
            _s_nfp = _df_labor[["fecha", "nfp"]].dropna(subset=["nfp"]).tail(36)
            if not _s_nfp.empty:
                colors_nfp = ["#276749" if v >= 0 else "#9B2335" for v in _s_nfp["nfp"]]
                fig_nfp = go.Figure(go.Bar(
                    x=_s_nfp["fecha"], y=_s_nfp["nfp"],
                    marker_color=colors_nfp
                ))
                fig_nfp.update_layout(**_LAYOUT_COMPACT, yaxis_title="miles", showlegend=False)
                st.plotly_chart(fig_nfp, use_container_width=True, key="macro_nfp_chart")

        with _mg_col8:
            st.markdown("<div style='font-size:12px;font-weight:600;color:#4A5568;margin-bottom:4px'>Tasa de Renuncia (Quit Rate %)</div>", unsafe_allow_html=True)
            val_q, fecha_q = _ultimo(_df_labor, "quit_rate")
            dlt_q = _delta(_df_labor, "quit_rate")
            st.markdown(_stat_card("Quit Rate", val_q, fecha_q, dlt_q, fmt="{:.1f}%",
                                   color="#553C9A"), unsafe_allow_html=True)
            _s_q = _df_labor[["fecha", "quit_rate"]].dropna(subset=["quit_rate"])
            if not _s_q.empty:
                fig_q = go.Figure(go.Scatter(
                    x=_s_q["fecha"], y=_s_q["quit_rate"],
                    line=dict(color="#553C9A", width=2), fill="tozeroy",
                    fillcolor="rgba(85,60,154,0.08)"
                ))
                fig_q.update_layout(**_LAYOUT_COMPACT, yaxis_title="%", showlegend=False)
                st.plotly_chart(fig_q, use_container_width=True, key="macro_quit_chart")

        with _mg_col9:
            st.markdown("<div style='font-size:12px;font-weight:600;color:#4A5568;margin-bottom:4px'>Vacantes Laborales — JOLTS (millones)</div>", unsafe_allow_html=True)
            val_jo, fecha_jo = _ultimo(_df_labor, "job_openings")
            dlt_jo = _delta(_df_labor, "job_openings")
            st.markdown(_stat_card("Job Openings", val_jo, fecha_jo, dlt_jo, fmt="{:.1f}M",
                                   color="#276749"), unsafe_allow_html=True)
            _s_jo = _df_labor[["fecha", "job_openings"]].dropna(subset=["job_openings"])
            if not _s_jo.empty:
                fig_jo = go.Figure(go.Scatter(
                    x=_s_jo["fecha"], y=_s_jo["job_openings"],
                    line=dict(color="#276749", width=2), fill="tozeroy",
                    fillcolor="rgba(39,103,73,0.08)"
                ))
                fig_jo.update_layout(**_LAYOUT_COMPACT, yaxis_title="millones", showlegend=False)
                st.plotly_chart(fig_jo, use_container_width=True, key="macro_jo_chart")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 7 — CALENDARIO
# ════════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    _df_cal_int = cargar_calendario_int()
    _df_cal_ar  = cargar_calendario_ar()
    _df_earn    = cargar_earnings()
    _hoy        = datetime.today().date()
    _en_60      = _hoy + timedelta(days=60)

    _SOURCE_COLOR = {
        "INDEC": "#1B4332", "DGEyC CABA": "#1B4332",
        "BCRA": "#1A365D",
        "Fed": "#7B341E", "BLS": "#7B341E",
        "ECB": "#2A4365", "BoJ": "#63171B",
        "BCB": "#276749", "ForexFactory": "#44337A",
    }

    _DAYS_ES = {"Mon": "LUN", "Tue": "MAR", "Wed": "MIE",
                "Thu": "JUE", "Fri": "VIE", "Sat": "SAB", "Sun": "DOM"}
    _MONTHS_ES = {"Jan": "ENE", "Feb": "FEB", "Mar": "MAR", "Apr": "ABR",
                  "May": "MAY", "Jun": "JUN", "Jul": "JUL", "Aug": "AGO",
                  "Sep": "SEP", "Oct": "OCT", "Nov": "NOV", "Dec": "DIC"}

    def _fecha_header(date_obj):
        """Return 'LUN 13 ABR' style string."""
        s = pd.Timestamp(date_obj).strftime("%a %d %b")
        day, num, mon = s.split()
        return f"{_DAYS_ES.get(day, day)} {num} {_MONTHS_ES.get(mon, mon)}"

    _COUNTRY_FLAG = {
        "EE.UU.": "🇺🇸", "Taiwan": "🇹🇼", "China": "🇨🇳", "Brasil": "🇧🇷",
        "Alemania": "🇩🇪", "Reino Unido": "🇬🇧", "Francia": "🇫🇷",
        "México": "🇲🇽", "Argentina": "🇦🇷", "Japón": "🇯🇵",
    }

    def _render_cards(df_ev, mode="event"):
        """Card layout grouped by date, 4 columns per row."""
        if df_ev is None or df_ev.empty:
            st.info("Sin eventos próximos.")
            return
        df = df_ev.copy()
        df["_date"] = pd.to_datetime(df["date"]).dt.date
        unique_dates = sorted(df["_date"].unique())
        N = 4
        for row_i in range(0, len(unique_dates), N):
            row_dates = unique_dates[row_i:row_i + N]
            cols = st.columns(N)
            for col_i, date in enumerate(row_dates):
                with cols[col_i]:
                    header = _fecha_header(date)
                    st.markdown(
                        f"<div style='background:#1B3A6B;color:white;padding:5px 10px;"
                        f"border-radius:6px 6px 0 0;font-weight:700;font-size:13px;"
                        f"text-align:center'>{header}</div>",
                        unsafe_allow_html=True,
                    )
                    day_df = df[df["_date"] == date]
                    for _, ev in day_df.iterrows():
                        if mode == "earnings":
                            ticker  = str(ev.get("ticker", ""))
                            company = str(ev.get("company", ""))
                            country = str(ev.get("country", "—"))
                            flag    = _COUNTRY_FLAG.get(country, "")
                            eps_v   = ev.get("eps_estimate")
                            rev_v   = ev.get("revenue_estimate_B")
                            eps_str = f"EPS est. {eps_v:.2f}" if pd.notna(eps_v) else ""
                            rev_str = f" · Rev est. ${rev_v:.1f}B" if pd.notna(rev_v) else ""
                            st.markdown(
                                f"<div style='border:1px solid #E2E8F0;border-radius:4px;"
                                f"padding:7px 9px;margin:2px 0;background:#FAFAFA'>"
                                f"<span style='font-weight:700;font-size:13px'>{ticker}</span>"
                                f"<span style='font-size:13px;margin-left:4px'>{flag}</span>"
                                f"<span style='color:#718096;font-size:11px;margin-left:4px'>{country}</span><br>"
                                f"<span style='font-size:12px'>{company}</span><br>"
                                f"<span style='font-size:11px;color:#A0AEC0'>{eps_str}{rev_str}</span>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            event   = str(ev.get("event", ""))
                            source  = str(ev.get("source", ""))
                            def _val(v):
                                return None if (v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ("", "nan")) else str(v).strip()
                            prev   = _val(ev.get("previous"))
                            fc     = _val(ev.get("forecast"))
                            actual = _val(ev.get("actual"))
                            src_color = _SOURCE_COLOR.get(source, "#4A5568")
                            badge = (
                                f"<span style='background:{src_color};color:white;"
                                f"font-size:10px;padding:1px 5px;border-radius:3px;"
                                f"margin-right:4px'>{source}</span>"
                            )
                            # Build data row only if at least one value exists
                            _parts = []
                            if prev:
                                _parts.append(f"Ant: <b>{prev}</b>")
                            if fc:
                                _parts.append(f"Est: <b style='color:#2B6CB0'>{fc}</b>")
                            if actual:
                                _parts.append(f"<b style='color:#276749'>{actual}</b>")
                            data_row = (
                                f"<div style='font-size:11px;color:#718096;margin-top:2px'>"
                                + " &nbsp;·&nbsp; ".join(_parts)
                                + "</div>"
                            ) if _parts else ""
                            st.markdown(
                                f"<div style='border:1px solid #E2E8F0;border-radius:4px;"
                                f"padding:7px 9px;margin:2px 0;background:#FAFAFA'>"
                                f"{badge}"
                                f"<span style='font-size:12px;font-weight:600'>{event}</span>"
                                f"{data_row}"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Argentina ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Próximos Eventos — Argentina</div>', unsafe_allow_html=True)
    if _df_cal_ar is not None:
        _prox_ar = _df_cal_ar[
            (_df_cal_ar["date"].dt.date >= _hoy) &
            (_df_cal_ar["date"].dt.date <= _en_60)
        ].copy()
        _render_cards(_prox_ar, mode="event")
    else:
        st.info("Calendario argentino no disponible aún.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Internacional ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Calendario Internacional — Eventos Clave</div>', unsafe_allow_html=True)
    if _df_cal_int is not None:
        _prox_int = _df_cal_int[
            (_df_cal_int["date"].dt.date >= _hoy) &
            (_df_cal_int["date"].dt.date <= _en_60)
        ].copy()
        _render_cards(_prox_int, mode="event")
    else:
        st.info("Calendario internacional no disponible aún.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Balances empresariales ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">Próximos Balances Empresariales</div>', unsafe_allow_html=True)
    if _df_earn is not None and not _df_earn.empty:
        _earn_prox = _df_earn[_df_earn["date"].dt.date >= _hoy].head(40).copy()
        if not _earn_prox.empty:
            _render_cards(_earn_prox, mode="earnings")
        else:
            st.info("Sin balances programados en los próximos días.")
    else:
        st.info("Calendario de balances no disponible aún. Se genera con el próximo fetch diario.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 8 — PREMARKET
# ════════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    import json as _json

    _hoy_pm = datetime.today().date()
    _ayer_pm = _hoy_pm - timedelta(days=1)
    # Skip weekends
    while _ayer_pm.weekday() >= 5:
        _ayer_pm -= timedelta(days=1)

    # Cargar datos de mercado históricos (de mercados_data.csv)
    _df_mkt = cargar_mercados()

    # Cargar premarket_data.json si existe (generado por fetch_premarket.py)
    _pm_data = None
    _pm_path = "data/premarket_data.json"
    if os.path.exists(_pm_path):
        try:
            with open(_pm_path, "r") as _f:
                _pm_data = _json.load(_f)
        except Exception:
            _pm_data = None

    def _pm_card(label, value_str, change_str=None, change_val=None, color="#1B2A6B", invert=False):
        if change_val is not None:
            dlt_class = ("neg" if invert else "pos") if change_val > 0 else (("pos" if invert else "neg") if change_val < 0 else "neu")
        else:
            dlt_class = "neu"
        chg_html = f"<div style='font-size:11px'><span class='{dlt_class}'>{change_str}</span></div>" if change_str else ""
        return (
            f"<div style='border:1px solid #E2E8F0;border-radius:6px;padding:8px 10px;"
            f"background:#FAFAFA;text-align:center;margin:2px'>"
            f"<div style='font-size:11px;color:#718096'>{label}</div>"
            f"<div style='font-size:18px;font-weight:700;color:{color}'>{value_str}</div>"
            f"{chg_html}"
            f"</div>"
        )

    def _fmt_chg(val):
        if val is None:
            return "—", None
        return f"{val:+.2f}%", val

    # ── Fila 1: Mercados internacionales (ayer) ───────────────────────────────
    st.markdown('<div class="section-title">Mercados Internacionales — Cierre de Ayer</div>', unsafe_allow_html=True)

    if _df_mkt is not None and not _df_mkt.empty:
        _mkt_rec = _df_mkt.tail(2)
        def _mkt_chg(col):
            if col not in _mkt_rec.columns or len(_mkt_rec) < 2:
                return None, None, None
            last = _mkt_rec.iloc[-1][col]
            prev = _mkt_rec.iloc[-2][col]
            if pd.isna(last) or pd.isna(prev) or prev == 0:
                return None, None, None
            chg = (last - prev) / prev * 100
            return float(last), float(chg), _mkt_rec.iloc[-1]["fecha"].strftime("%d %b") if hasattr(_mkt_rec.iloc[-1]["fecha"], "strftime") else ""

        _pm_intl_cols = st.columns(6)
        _intl_items = [
            ("sp500",  "S&P 500",    "#1B2A6B", False, "${:.0f}"),
            ("nasdaq", "NASDAQ",     "#0070C0", False, "{:.0f}"),
            ("oro",    "Oro (USD)",  "#D69E2E", False, "${:.0f}"),
            ("wti",    "WTI (USD)",  "#276749", False, "${:.1f}"),
            ("vix",    "VIX",        "#9B2335", True,  "{:.1f}"),
            ("us10y",  "10yr EE.UU.","#553C9A", True,  "{:.2f}%"),
        ]
        for i, (col, label, color, invert, fmt) in enumerate(_intl_items):
            val, chg, fecha_str = _mkt_chg(col)
            with _pm_intl_cols[i]:
                val_str = fmt.format(val) if val is not None else "—"
                chg_str, chg_v = _fmt_chg(chg)
                st.markdown(_pm_card(label, val_str, chg_str, chg_v, color=color, invert=invert), unsafe_allow_html=True)
    else:
        st.info("Sin datos de mercado disponibles.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Fila 2: Argentina ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Argentina</div>', unsafe_allow_html=True)
    _pm_ar_cols = st.columns(5)

    # MERVAL
    with _pm_ar_cols[0]:
        if _df_mkt is not None and "merval" in _df_mkt.columns:
            _mkt_rec2 = _df_mkt.dropna(subset=["merval"]).tail(2)
            if len(_mkt_rec2) >= 1:
                _mv_last = float(_mkt_rec2.iloc[-1]["merval"])
                _mv_prev = float(_mkt_rec2.iloc[-2]["merval"]) if len(_mkt_rec2) >= 2 else None
                _mv_chg = ((_mv_last - _mv_prev) / _mv_prev * 100) if _mv_prev else None
                chg_str, chg_v = _fmt_chg(_mv_chg)
                st.markdown(_pm_card("MERVAL", f"${_mv_last:,.0f}", chg_str, chg_v, color="#1B2A6B"), unsafe_allow_html=True)

    # Dólar MEP
    with _pm_ar_cols[1]:
        if dfd is not None and "mep" in dfd.columns:
            _dol_rec = dfd.dropna(subset=["mep"]).tail(2)
            if len(_dol_rec) >= 1:
                _mep = float(_dol_rec.iloc[-1]["mep"])
                _mep_prev = float(_dol_rec.iloc[-2]["mep"]) if len(_dol_rec) >= 2 else None
                _mep_chg = ((_mep - _mep_prev) / _mep_prev * 100) if _mep_prev else None
                chg_str, chg_v = _fmt_chg(_mep_chg)
                st.markdown(_pm_card("Dólar MEP", f"${_mep:,.0f}", chg_str, chg_v, color="#276749"), unsafe_allow_html=True)

    # Dólar CCL
    with _pm_ar_cols[2]:
        if dfd is not None and "ccl" in dfd.columns:
            _dol_rec_ccl = dfd.dropna(subset=["ccl"]).tail(2)
            if len(_dol_rec_ccl) >= 1:
                _ccl = float(_dol_rec_ccl.iloc[-1]["ccl"])
                _ccl_prev = float(_dol_rec_ccl.iloc[-2]["ccl"]) if len(_dol_rec_ccl) >= 2 else None
                _ccl_chg = ((_ccl - _ccl_prev) / _ccl_prev * 100) if _ccl_prev else None
                chg_str, chg_v = _fmt_chg(_ccl_chg)
                st.markdown(_pm_card("Dólar CCL", f"${_ccl:,.0f}", chg_str, chg_v, color="#276749"), unsafe_allow_html=True)

    # Riesgo País
    with _pm_ar_cols[3]:
        if dfr is not None and "riesgo_pais" in dfr.columns:
            _rp_rec = dfr.dropna(subset=["riesgo_pais"]).tail(2)
            if len(_rp_rec) >= 1:
                _rp = float(_rp_rec.iloc[-1]["riesgo_pais"])
                _rp_prev = float(_rp_rec.iloc[-2]["riesgo_pais"]) if len(_rp_rec) >= 2 else None
                _rp_chg = _rp - _rp_prev if _rp_prev else None
                _rp_chg_str = f"{_rp_chg:+.0f} pb" if _rp_chg else None
                _rp_class = "neg" if (_rp_chg or 0) > 0 else ("pos" if (_rp_chg or 0) < 0 else "neu")
                chg_html = f"<div style='font-size:11px'><span class='{_rp_class}'>{_rp_chg_str}</span></div>" if _rp_chg_str else ""
                st.markdown(
                    f"<div style='border:1px solid #E2E8F0;border-radius:6px;padding:8px 10px;"
                    f"background:#FAFAFA;text-align:center;margin:2px'>"
                    f"<div style='font-size:11px;color:#718096'>Riesgo País</div>"
                    f"<div style='font-size:18px;font-weight:700;color:#9B2335'>{_rp:.0f} pb</div>"
                    f"{chg_html}</div>",
                    unsafe_allow_html=True,
                )

    # Fear & Greed
    with _pm_ar_cols[4]:
        if _pm_data and _pm_data.get("fear_greed"):
            _fg = _pm_data["fear_greed"]
            _fg_val = _fg["value"]
            _fg_label = _fg.get("label", "")
            _fg_color = "#276749" if _fg_val > 60 else ("#9B2335" if _fg_val < 40 else "#C05621")
            st.markdown(
                f"<div style='border:1px solid #E2E8F0;border-radius:6px;padding:8px 10px;"
                f"background:#FAFAFA;text-align:center;margin:2px'>"
                f"<div style='font-size:11px;color:#718096'>Fear & Greed</div>"
                f"<div style='font-size:18px;font-weight:700;color:{_fg_color}'>{_fg_val}</div>"
                f"<div style='font-size:11px;color:#A0AEC0'>{_fg_label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(_pm_card("Fear & Greed", "—", color="#C05621"), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Fila 3: Commodities & Futuros ────────────────────────────────────────
    st.markdown('<div class="section-title">Commodities</div>', unsafe_allow_html=True)
    if _df_mkt is not None and not _df_mkt.empty:
        _pm_comm_cols = st.columns(6)
        _comm_items = [
            ("brent",  "Brent (USD)", "#7B341E", False, "${:.1f}"),
            ("plata",  "Plata (USD)", "#718096", False, "${:.2f}"),
            ("soja",   "Soja (cBs/t)", "#276749", False, "${:.1f}"),
            ("maiz",   "Maíz (cBs/t)", "#D69E2E", False, "${:.1f}"),
            ("trigo",  "Trigo (cBs/t)", "#C05621", False, "${:.1f}"),
            ("eem",    "EEM ETF",     "#0070C0", False, "${:.2f}"),
        ]
        for i, (col, label, color, invert, fmt) in enumerate(_comm_items):
            val, chg, _ = _mkt_chg(col) if col in _df_mkt.columns else (None, None, None)
            with _pm_comm_cols[i]:
                val_str = fmt.format(val) if val is not None else "—"
                chg_str, chg_v = _fmt_chg(chg)
                st.markdown(_pm_card(label, val_str, chg_str, chg_v, color=color, invert=invert), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Fila 4: Eventos de hoy y mañana ───────────────────────────────────────
    _pm_cal_cols = st.columns(2)
    with _pm_cal_cols[0]:
        st.markdown('<div class="section-title">Eventos Argentina — Hoy / Próximos días</div>', unsafe_allow_html=True)
        _df_cal_ar_pm = cargar_calendario_ar()
        if _df_cal_ar_pm is not None:
            _prox_ar_pm = _df_cal_ar_pm[
                (_df_cal_ar_pm["date"].dt.date >= _hoy_pm) &
                (_df_cal_ar_pm["date"].dt.date <= _hoy_pm + timedelta(days=7))
            ].head(8)
            if not _prox_ar_pm.empty:
                _render_cards(_prox_ar_pm, mode="event")
            else:
                st.info("Sin eventos en los próximos 7 días.")

    with _pm_cal_cols[1]:
        st.markdown('<div class="section-title">Eventos Internacionales — Hoy / Próximos días</div>', unsafe_allow_html=True)
        _df_cal_int_pm = cargar_calendario_int()
        if _df_cal_int_pm is not None:
            _prox_int_pm = _df_cal_int_pm[
                (_df_cal_int_pm["date"].dt.date >= _hoy_pm) &
                (_df_cal_int_pm["date"].dt.date <= _hoy_pm + timedelta(days=7))
            ].head(8)
            if not _prox_int_pm.empty:
                _render_cards(_prox_int_pm, mode="event")
            else:
                st.info("Sin eventos internacionales en los próximos 7 días.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Fila 5: Noticias ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Noticias</div>', unsafe_allow_html=True)
    if _pm_data and _pm_data.get("news"):
        _news = _pm_data["news"]
        _nc1, _nc2, _nc3 = st.columns(3)
        _news_cols = [_nc1, _nc2, _nc3]
        _news_keys = list(_news.keys())
        for i, key in enumerate(_news_keys[:3]):
            feed = _news[key]
            with _news_cols[i]:
                st.markdown(
                    f"<div style='font-size:12px;font-weight:700;color:#1B3A6B;"
                    f"border-bottom:2px solid #1B3A6B;margin-bottom:6px;padding-bottom:3px'>"
                    f"{feed['label']}</div>",
                    unsafe_allow_html=True,
                )
                for article in feed.get("items", [])[:6]:
                    title = article.get("title", "")
                    link  = article.get("link", "")
                    pub   = article.get("published", "")[:16]
                    # Shorten date string
                    if "," in pub:
                        pub = pub.split(",")[-1].strip()[:12]
                    title_html = (
                        f'<a href="{link}" target="_blank" rel="noopener noreferrer" '
                        f'style="color:#2D3748;text-decoration:none">{title}</a>'
                        if link else title
                    )
                    st.markdown(
                        f"<div style='border-bottom:1px solid #EDF2F7;padding:5px 0'>"
                        f"<span style='font-size:12px;line-height:1.3'>{title_html}</span>"
                        f"<span style='font-size:10px;color:#A0AEC0;display:block'>{pub}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.info("Noticias no disponibles aún — se cargan con el próximo fetch diario (GitHub Actions).")

    if _pm_data:
        _pm_updated = _pm_data.get("updated_at", "")
        st.markdown(f"<div style='font-size:10px;color:#A0AEC0;margin-top:8px'>Datos actualizados: {_pm_updated}</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#A0AEC0; font-size:11px'>"
    "Fuentes: BCRA (API v4.0 & Excel ITCRM) · Ámbito Financiero (Riesgo País, MEP, CCL) · "
    "datos.gob.ar (EMAE, Fiscal, Comercio Exterior, Laborales) · "
    "Yahoo Finance (Mercados Internacionales) · INDEC · "
    "FRED / St. Louis Fed (Macro Global) · BCB · World Bank · IMF WEO · ForexFactory"
    "</div>",
    unsafe_allow_html=True
)
