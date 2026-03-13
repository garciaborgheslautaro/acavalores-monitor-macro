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
    "vix":                  "#E53E3E",
    "plata":                "#A0AEC0",
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

def mini_chart(df_plot, col, color, key, label="", fecha_str=""):
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

def mini_chart_barras(df_plot, col, key, label="", fecha_str=""):
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
        mini_chart_barras(df_plot, col, key=key or col, label=label, fecha_str=fecha_str or "")

def row_card(df_plot, col, label, prefijo="", sufijo="", decimales=2, color=None, key=None, invertir_colores=False, df_full=None, es_porcentaje=False, solo_ult_dato=False, pp_todos=False):
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
                if solo_ult_dato or es_porcentaje or pp_todos:
                    return f'<span class="{clase}">{flecha} {abs(v):.2f} p.p.</span>'
                return f'<span class="{clase}">{flecha} {abs(v):.2f}%</span>'

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
        mini_chart(df_plot, col, color, key=key or col, label=label, fecha_str=fecha_str or "")

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

    _st_l, _st_c = st.columns([1, 9])
    with _st_c:
        st.markdown('<div class="section-title">Competitividad & Riesgo</div>', unsafe_allow_html=True)
    if dfi is not None:
        dfi_f = dfi[(dfi["fecha"].dt.date >= desde) & (dfi["fecha"].dt.date <= hasta)]
        row_card(dfi_f, "itcrm", "ITCRM (base 17-12-15=100)", decimales=2, color=COLORES["itcrm"], key="t0_itcrm", df_full=dfi)
    if dfr is not None:
        dfr_f = dfr[(dfr["fecha"].dt.date >= desde) & (dfr["fecha"].dt.date <= hasta)]
        row_card(dfr_f, "riesgo_pais", "Riesgo País EMBI", sufijo=" pb", decimales=0, color=COLORES["riesgo_pais"], key="t0_riesgo", invertir_colores=True, df_full=dfr, pp_todos=True)

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

    val_tamar, fecha_tamar, var_ult_tamar, var_30_tamar, var_365_tamar = _get_pp("tamar", df_f, df)
    val_badlar, fecha_badlar, var_ult_badlar, var_30_badlar, var_365_badlar = _get_pp("badlar", df_f, df)

    def _d_tasa(v, pp=False):
        if v is None: return '<span class="neu">-</span>'
        clase = "pos" if v >= 0 else "neg"
        flecha = "▲" if v >= 0 else "▼"
        unidad = " p.p." if pp else "%"
        return f'<span class="{clase}">{flecha} {abs(v):.2f}{unidad}</span>'

    fmt_tamar = f"{val_tamar:,.2f}" if val_tamar is not None else "-"
    fmt_badlar = f"{val_badlar:,.2f}" if val_badlar is not None else "-"

    col_esp_l_t, col_card_t, col_chart_t, col_esp_r_t = st.columns([1, 2, 4, 3])
    with col_card_t:
        st.markdown(f"""
        <div class="row-card">
            <div class="var-label">Tasas de Interés (% TNA)</div>
            <div style="margin-bottom:10px">
                <div style="font-size:13px;font-weight:700;color:#1B2A6B">TAMAR: {fmt_tamar}%</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_tasa(var_ult_tamar, pp=True)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_tasa(var_30_tamar, pp=True)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_tasa(var_365_tamar, pp=True)}</div>
                </div>
            </div>
            <div>
                <div style="font-size:13px;font-weight:700;color:#1B2A6B">BADLAR: {fmt_badlar}%</div>
                <div class="var-delta-row">
                    <div class="delta-item"><span class="delta-label">vs últ. dato</span>{_d_tasa(var_ult_badlar, pp=True)}</div>
                    <div class="delta-item"><span class="delta-label">vs 30d</span>{_d_tasa(var_30_badlar, pp=True)}</div>
                    <div class="delta-item"><span class="delta-label">vs 365d</span>{_d_tasa(var_365_badlar, pp=True)}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_chart_t:
        fig_tasas = go.Figure()
        for col_t, lab_t, color_t in [("tamar", "TAMAR", COLORES["tamar"]), ("badlar", "BADLAR", COLORES["badlar"])]:
            if col_t in df_f.columns:
                dp = df_f[["fecha", col_t]].dropna()
                fig_tasas.add_trace(go.Scatter(x=dp["fecha"], y=dp[col_t], mode="lines",
                    name=lab_t, line=dict(color=color_t, width=2),
                    hovertemplate="%{x|%d/%m/%Y}<br>" + lab_t + ": %{y:,.2f}%<extra></extra>"))
        layout_t = dict(LAYOUT_BASE)
        layout_t["height"] = 340
        layout_t["showlegend"] = True
        layout_t["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9))
        layout_t["title"] = dict(text=f"<b>TAMAR y BADLAR (% TNA)</b>  <span style='font-size:10px;color:#718096'>últ. dato: {fecha_tamar or '-'}</span>", font=dict(size=14, color="#2D3748"), x=0, xanchor="left", pad=dict(l=5))
        layout_t["margin"] = dict(l=10, r=10, t=40, b=10)
        fig_tasas.update_layout(**layout_t)
        st.plotly_chart(fig_tasas, use_container_width=True, key="t1_tasas")

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
        cer_hoy = df_prest["cer"].iloc[-1]
        df_prest["prestamos_constantes"] = df_prest["prestamos_priv"] * cer_hoy / df_prest["cer"]
        row_card(df_prest, "prestamos_constantes", "Préstamos al Sector Privado ($ MM constantes de hoy)",
                 prefijo="$ ", sufijo=" MM", decimales=0, key="t2_prest_const")

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
        row_card(dfm_f, "nasdaq", "Nasdaq 100 (NDX)", decimales=2, color=COLORES["nasdaq"], key="t4_nasdaq", df_full=dfm)

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
# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#A0AEC0; font-size:11px'>"
    "Fuentes: BCRA (API v4.0 & Excel ITCRM) · Ámbito Financiero (Riesgo País, MEP, CCL) · "
    "Bluelytics (Dólar Blue) · Yahoo Finance (Mercados Internacionales) · INDEC"
    "</div>",
    unsafe_allow_html=True
)
