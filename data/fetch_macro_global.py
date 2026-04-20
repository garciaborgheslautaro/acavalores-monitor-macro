#!/usr/bin/env python3
"""fetch_macro_global.py — Datos macro de EE.UU. y el mundo.

Fuentes (todas libres, sin API key):
- FRED direct CSV: Fed Funds, ECB, CPI, desempleo
- FRED IRSTCB01JPM156N: BoJ policy rate
- BCB API serie 4390: Meta Selic mensual
- BCB API serie 433: IPCA mensual (→ YoY)
- World Bank API: PIB growth por país

Estrategia: si una API falla, se conserva el CSV existente (seed data).
El script actualiza sólo las columnas que pudo obtener.
"""
import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

print("=== INICIO fetch_macro_global.py ===")
os.makedirs("data", exist_ok=True)

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
BCB_URL  = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados/ultimos/120?formato=json"
WB_URL   = "https://api.worldbank.org/v2/country/{}/indicator/{}?format=json&per_page=30&mrv=30"

CORTE = pd.Timestamp.now() - pd.DateOffset(years=10)


def fetch_fred(series_id, col):
    try:
        df = pd.read_csv(FRED_URL.format(series_id))
        df.columns = ["fecha", col]
        df["fecha"] = pd.to_datetime(df["fecha"])
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=[col])
        df = df[df["fecha"] >= CORTE].reset_index(drop=True)
        print(f"  OK FRED {series_id} ({col}) — {len(df)} registros, últ: {df.iloc[-1][col]:.2f}")
        return df
    except Exception as e:
        print(f"  ERROR FRED {series_id}: {e}")
        return None


def fetch_bcb(series_id, col):
    """Serie BCB SGS. 4390 = Meta Selic (% a.a.), 433 = IPCA mensual."""
    try:
        r = requests.get(BCB_URL.format(series_id), timeout=20)
        r.raise_for_status()
        data = r.json()
        rows = []
        for item in data:
            try:
                rows.append({
                    "fecha": pd.to_datetime(item["data"], format="%d/%m/%Y"),
                    col: float(str(item["valor"]).replace(",", ".")),
                })
            except Exception:
                pass
        if not rows:
            print(f"  ERROR BCB {series_id}: respuesta vacía")
            return None
        df = pd.DataFrame(rows).sort_values("fecha").reset_index(drop=True)
        df = df[df["fecha"] >= CORTE].reset_index(drop=True)
        print(f"  OK BCB {series_id} ({col}) — {len(df)} registros, últ: {df.iloc[-1][col]:.4f}")
        return df if not df.empty else None
    except Exception as e:
        print(f"  ERROR BCB {series_id}: {e}")
        return None


def fetch_worldbank(country, indicator, col):
    try:
        r = requests.get(WB_URL.format(country, indicator), timeout=15)
        data = r.json()
        if len(data) < 2 or not data[1]:
            return None
        rows = [{"fecha": pd.Timestamp(f"{item['date']}-01-01"), col: float(item["value"])}
                for item in data[1] if item["value"] is not None]
        df = pd.DataFrame(rows).sort_values("fecha").reset_index(drop=True)
        if df.empty:
            return None
        print(f"  OK WB {country} ({col}) — {len(df)} años, últ: {df.iloc[-1][col]:.1f}")
        return df
    except Exception as e:
        print(f"  ERROR WB {country}/{indicator}: {e}")
        return None


def update_csv(csv_path, new_data_dict):
    """
    Actualiza un CSV existente con datos nuevos de forma segura:
    - El seed (CSV existente) es AUTORITATIVO para todas sus fechas
    - Solo se agregan filas con fechas ESTRICTAMENTE posteriores al seed
    - Nunca se sobreescriben datos del seed con datos de APIs (evita stale data)
    """
    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path, parse_dates=["fecha"])
        seed_last_date = df_old["fecha"].max()
    else:
        df_old = None
        seed_last_date = pd.Timestamp("2000-01-01")

    # Solo tomar datos de APIs para fechas POSTERIORES al seed
    df_new = None
    for col, df_src in new_data_dict.items():
        if df_src is None or df_src.empty:
            continue
        df_m = df_src[df_src["fecha"] > seed_last_date][["fecha", col]].copy()
        if df_m.empty:
            continue
        if df_new is None:
            df_new = df_m
        else:
            df_new = pd.merge(df_new, df_m, on="fecha", how="outer")

    if df_new is None or df_new.empty:
        print(f"  Sin datos nuevos posteriores a {seed_last_date.date()} — conservando seed")
        return

    # Append: seed intacto + nuevas filas al final
    df_out = pd.concat([df_old, df_new], ignore_index=True) if df_old is not None else df_new
    df_out.sort_values("fecha", inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    df_out.to_csv(csv_path, index=False)
    print(f"  → {csv_path} ({len(df_out)} filas, {len(df_new)} nuevas)")


# ── Tasas de política monetaria ────────────────────────────────────────────────
print("\n[Tasas]")

df_fed   = fetch_fred("FEDFUNDS",        "us_fed")
df_ecb   = fetch_fred("ECBDFR",          "ecb_rate")
df_boj   = fetch_fred("IRSTCB01JPM156N", "boj_rate")   # BoJ discount/call rate
df_selic = fetch_bcb(4390,               "selic")       # Meta Selic

# Para tasas: ffill porque cambian poco (decisiones de banco central)
def rate_series_ffill(df_rate, col):
    if df_rate is None:
        return None
    # Resamplear a mensual y forward-fill
    df_m = df_rate.set_index("fecha").resample("MS").last()[[col]].ffill().reset_index()
    return df_m

df_fed_m   = rate_series_ffill(df_fed,   "us_fed")
df_ecb_m   = rate_series_ffill(df_ecb,   "ecb_rate")
df_boj_m   = rate_series_ffill(df_boj,   "boj_rate")
df_selic_m = rate_series_ffill(df_selic, "selic")

update_csv("data/macro_tasas.csv", {
    "us_fed":   df_fed_m,
    "ecb_rate": df_ecb_m,
    "boj_rate": df_boj_m,
    "selic":    df_selic_m,
})

# ── Inflación ──────────────────────────────────────────────────────────────────
print("\n[Inflación YoY]")

# US: YoY desde índice CPI
df_us_cpi = None
df_us_idx = fetch_fred("CPIAUCSL", "us_cpi_idx")
if df_us_idx is not None:
    df_us_cpi = df_us_idx.copy()
    df_us_cpi["us_cpi_yoy"] = df_us_cpi["us_cpi_idx"].pct_change(12) * 100
    df_us_cpi = df_us_cpi[["fecha", "us_cpi_yoy"]].dropna()

# EU: HICP YoY — Eurostat via FRED
df_eu_cpi = fetch_fred("CP0000EZ17M086NEST", "eu_cpi_yoy")   # índice → calc YoY
if df_eu_cpi is not None:
    df_eu_cpi["eu_cpi_yoy"] = df_eu_cpi["eu_cpi_yoy"].pct_change(12) * 100
    df_eu_cpi = df_eu_cpi[["fecha","eu_cpi_yoy"]].dropna()
else:
    # Fallback: serie YoY directa
    df_eu_cpi = fetch_fred("CPHPTT01EZM659N", "eu_cpi_yoy")

# JP: YoY directo FRED
df_jp_cpi = fetch_fred("CPALTT01JPM659N", "jp_cpi_yoy")

# Brasil: IPCA — IBGE API (fuente oficial, más confiable que BCB serie 433)
df_br_cpi = None
try:
    # IBGE: agregado 1737, variável 63 = IPCA variação mensal %
    ibge_url = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/-60/variaveis/63?localidades=N1[all]"
    r_ibge = requests.get(ibge_url, timeout=20)
    r_ibge.raise_for_status()
    ibge_data = r_ibge.json()
    rows_ibge = []
    for item in ibge_data[0]["resultados"][0]["series"][0]["serie"].items():
        periodo, val = item
        try:
            rows_ibge.append({
                "fecha": pd.Timestamp(f"{periodo[:4]}-{periodo[4:]}-01"),
                "br_ipca_m": float(val),
            })
        except Exception:
            pass
    if rows_ibge:
        df_ibge = pd.DataFrame(rows_ibge).sort_values("fecha").reset_index(drop=True)
        df_ibge["br_cpi_yoy"] = (
            (1 + df_ibge["br_ipca_m"] / 100)
            .rolling(12).apply(lambda x: x.prod(), raw=True) - 1
        ) * 100
        df_br_cpi = df_ibge[["fecha", "br_cpi_yoy"]].dropna()
        print(f"  OK IBGE IPCA — {len(df_br_cpi)} registros, últ: {df_br_cpi.iloc[-1]['br_cpi_yoy']:.2f}%")
except Exception as e:
    print(f"  ERROR IBGE IPCA: {e} — usando BCB fallback")
    df_br_m = fetch_bcb(433, "br_ipca_m")
    if df_br_m is not None:
        df_br_m = df_br_m.set_index("fecha").resample("ME").last().reset_index()
        df_br_m["br_cpi_yoy"] = (
            (1 + df_br_m["br_ipca_m"] / 100)
            .rolling(12).apply(lambda x: x.prod(), raw=True) - 1
        ) * 100
        df_br_cpi = df_br_m[["fecha", "br_cpi_yoy"]].dropna()

# China: índice → YoY
df_cn_cpi = None
df_cn_idx = fetch_fred("CHNCPIALLMINMEI", "cn_cpi_idx")
if df_cn_idx is not None:
    df_cn_cpi = df_cn_idx.copy()
    df_cn_cpi["cn_cpi_yoy"] = df_cn_cpi["cn_cpi_idx"].pct_change(12) * 100
    df_cn_cpi = df_cn_cpi[["fecha", "cn_cpi_yoy"]].dropna()

update_csv("data/macro_inflacion.csv", {
    "us_cpi_yoy": df_us_cpi,
    "eu_cpi_yoy": df_eu_cpi,
    "jp_cpi_yoy": df_jp_cpi,
    "br_cpi_yoy": df_br_cpi,
    "cn_cpi_yoy": df_cn_cpi,
})

# ── Desempleo ──────────────────────────────────────────────────────────────────
print("\n[Desempleo]")
update_csv("data/macro_desempleo.csv", {
    "us_unrate": fetch_fred("UNRATE",           "us_unrate"),
    "eu_unrate": fetch_fred("LRHUTTTTEZM156S",  "eu_unrate"),
    "jp_unrate": fetch_fred("LRHUTTTTJPM156S",  "jp_unrate"),
    "uk_unrate": fetch_fred("LRHUTTTTGBM156S",  "uk_unrate"),
    "br_unrate": fetch_fred("LRHUTTTTBRM156S",  "br_unrate"),
})

# ── PIB — Crecimiento anual (World Bank + IMF proyecciones) ───────────────────
print("\n[PIB YoY — World Bank + IMF]")
IND_GDP = "NY.GDP.MKTP.KD.ZG"
update_csv("data/macro_gdp.csv", {
    "world_gdp": fetch_worldbank("WLD", IND_GDP, "world_gdp"),
    "us_gdp": fetch_worldbank("US", IND_GDP, "us_gdp"),
    "eu_gdp": fetch_worldbank("XC", IND_GDP, "eu_gdp"),
    "cn_gdp": fetch_worldbank("CN", IND_GDP, "cn_gdp"),
    "jp_gdp": fetch_worldbank("JP", IND_GDP, "jp_gdp"),
    "br_gdp": fetch_worldbank("BR", IND_GDP, "br_gdp"),
    "ar_gdp": fetch_worldbank("AR", IND_GDP, "ar_gdp"),
})

# IMF WEO API — proyecciones 2025-2027
def fetch_imf_gdp():
    try:
        url = "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/WORLD/USA/EUQ/CHN/JPN/BRA/ARG"
        r = requests.get(url, timeout=20)
        data = r.json()
        vals = data.get("values", {}).get("NGDP_RPCH", {})
        country_map = {"WORLD": "world_gdp", "USA": "us_gdp", "EUQ": "eu_gdp", "CHN": "cn_gdp",
                       "JPN": "jp_gdp", "BRA": "br_gdp", "ARG": "ar_gdp"}
        rows = {}
        for imf_code, col in country_map.items():
            for year, val in vals.get(imf_code, {}).items():
                yr = int(year)
                if yr < 2020:
                    continue
                key = f"{yr}-01-01"
                if key not in rows:
                    rows[key] = {"fecha": pd.Timestamp(key)}
                rows[key][col] = float(val)
        if not rows:
            return None
        df_imf = pd.DataFrame(list(rows.values())).sort_values("fecha").reset_index(drop=True)
        print(f"  OK IMF GDP — {len(df_imf)} años, hasta {df_imf['fecha'].max().year}")
        return df_imf
    except Exception as e:
        print(f"  ERROR IMF GDP: {e}")
        return None

df_imf = fetch_imf_gdp()
if df_imf is not None:
    # Upsert IMF data into macro_gdp.csv for years not yet in WB data
    df_gdp_cur = pd.read_csv("data/macro_gdp.csv", parse_dates=["fecha"])
    wb_last = df_gdp_cur["fecha"].max()
    df_imf_new = df_imf[df_imf["fecha"] > wb_last]
    if not df_imf_new.empty:
        df_gdp_out = pd.concat([df_gdp_cur, df_imf_new], ignore_index=True)
        df_gdp_out.sort_values("fecha", inplace=True)
        df_gdp_out.to_csv("data/macro_gdp.csv", index=False)
        print(f"  → macro_gdp.csv actualizado con {len(df_imf_new)} años IMF")
    else:
        print("  Sin años nuevos de IMF posteriores al seed")

# ── Breakeven Inflation EE.UU. (TIPS-implied) ────────────────────────────────
print("\n[Breakeven Inflation]")
update_csv("data/macro_breakeven.csv", {
    "be_10y": fetch_fred("T10YIE", "be_10y"),
    "be_5y":  fetch_fred("T5YIE",  "be_5y"),
    "be_2y":  fetch_fred("T2YIE",  "be_2y"),
})

# ── PCE — Deflactor consumo personal EE.UU. ───────────────────────────────────
print("\n[PCE]")
df_pce_idx = fetch_fred("PCEPI", "pce_idx")
df_pce = None
if df_pce_idx is not None:
    df_pce = df_pce_idx.copy()
    df_pce["us_pce_yoy"] = df_pce["pce_idx"].pct_change(12) * 100
    df_pce = df_pce[["fecha", "us_pce_yoy"]].dropna()

df_cpce_idx = fetch_fred("PCEPILFE", "cpce_idx")
df_core_pce = None
if df_cpce_idx is not None:
    df_core_pce = df_cpce_idx.copy()
    df_core_pce["us_core_pce_yoy"] = df_core_pce["cpce_idx"].pct_change(12) * 100
    df_core_pce = df_core_pce[["fecha", "us_core_pce_yoy"]].dropna()

update_csv("data/macro_pce.csv", {
    "us_pce_yoy":      df_pce,
    "us_core_pce_yoy": df_core_pce,
})

# ── Yields — Bonos del Tesoro EE.UU. (diario, full overwrite) ────────────────
print("\n[Yields]")
# DGS10/DGS2 son diarias — hacemos overwrite completo para no quedar con seed mensual
df_10y = fetch_fred("DGS10", "us_10y")
df_2y  = fetch_fred("DGS2",  "us_2y")
if df_10y is not None and df_2y is not None:
    df_yields_out = pd.merge(df_10y, df_2y, on="fecha", how="outer").sort_values("fecha")
    df_yields_out.to_csv("data/macro_yields.csv", index=False)
    print(f"  → macro_yields.csv overwrite ({len(df_yields_out)} filas diarias)")
elif df_10y is not None or df_2y is not None:
    # Solo uno disponible — usar update_csv para no perder lo existente
    update_csv("data/macro_yields.csv", {"us_10y": df_10y, "us_2y": df_2y})
else:
    print("  Sin datos de yields — conservando CSV existente")

# ── Mercado Laboral EE.UU. ────────────────────────────────────────────────────
print("\n[Mercado Laboral EE.UU.]")

def fetch_fred_level(series_id, col):
    """Fetch FRED series as level (not monthly resampled)."""
    try:
        df = pd.read_csv(FRED_URL.format(series_id))
        df.columns = ["fecha", col]
        df["fecha"] = pd.to_datetime(df["fecha"])
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=[col])
        df = df[df["fecha"] >= CORTE].reset_index(drop=True)
        # Resample monthly
        df = df.set_index("fecha").resample("MS").last()[[col]].ffill().reset_index()
        print(f"  OK FRED {series_id} ({col}) — {len(df)} registros, últ: {df.iloc[-1][col]:.1f}")
        return df
    except Exception as e:
        print(f"  ERROR FRED {series_id}: {e}")
        return None

# PAYEMS: Non-farm payrolls (level, in thousands) — need monthly change
df_payems = None
df_payems_lvl = fetch_fred("PAYEMS", "payems")
if df_payems_lvl is not None:
    df_payems = df_payems_lvl.copy()
    df_payems["nfp"] = df_payems["payems"].diff()
    df_payems = df_payems[["fecha", "nfp"]].dropna()

df_quits       = fetch_fred_level("JTSQUR", "quit_rate")    # Quit Rate %
df_jobopenings = fetch_fred_level("JTSJOL", "job_openings")  # Job Openings millions

# NFP viene de FRED PAYEMS (fuente oficial BLS) — full overwrite para que siempre
# refleje revisiones del BLS y no quede atado al seed manual del CSV.
if df_payems is not None:
    # Merge con quit_rate y job_openings (pueden tener lag de 1-2 meses)
    df_labor_new = df_payems.copy()
    for df_side, col in [(df_quits, "quit_rate"), (df_jobopenings, "job_openings")]:
        if df_side is not None and not df_side.empty:
            df_labor_new = pd.merge(df_labor_new, df_side, on="fecha", how="left")
        else:
            df_labor_new[col] = float("nan")
    # Si el CSV existente tiene datos de quit_rate/job_openings más recientes (o el
    # overwrite de FRED no los trajo), conservar los del seed para esas fechas.
    if os.path.exists("data/macro_labor.csv"):
        df_old_labor = pd.read_csv("data/macro_labor.csv", parse_dates=["fecha"])
        for col in ["quit_rate", "job_openings"]:
            if col in df_old_labor.columns:
                fill_map = df_old_labor.dropna(subset=[col]).set_index("fecha")[col]
                mask_nan = df_labor_new[col].isna()
                df_labor_new.loc[mask_nan, col] = df_labor_new.loc[mask_nan, "fecha"].map(fill_map)
    df_labor_new.sort_values("fecha", inplace=True)
    df_labor_new.to_csv("data/macro_labor.csv", index=False)
    print(f"  → macro_labor.csv overwrite ({len(df_labor_new)} filas, NFP desde FRED PAYEMS)")
else:
    update_csv("data/macro_labor.csv", {
        "quit_rate":    df_quits,
        "job_openings": df_jobopenings,
    })

print("\n=== FIN fetch_macro_global.py ===")
