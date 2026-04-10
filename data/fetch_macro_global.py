#!/usr/bin/env python3
"""fetch_macro_global.py — Datos macro de EE.UU. y el mundo.

Fuentes (todas libres, sin API key):
- FRED direct CSV: Fed Funds, ECB, BoJ, CPI, desempleo
- BCB API (Brasil): SELIC, IPCA
- World Bank API: PIB growth por país
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

CORTE = pd.Timestamp.now() - pd.DateOffset(years=7)


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
    try:
        r = requests.get(BCB_URL.format(series_id), timeout=15)
        data = r.json()
        rows = []
        for item in data:
            try:
                rows.append({
                    "fecha": pd.to_datetime(item["data"], format="%d/%m/%Y"),
                    col: float(item["valor"].replace(",", ".")),
                })
            except Exception:
                pass
        df = pd.DataFrame(rows).sort_values("fecha").reset_index(drop=True)
        df = df[df["fecha"] >= CORTE]
        print(f"  OK BCB {series_id} ({col}) — {len(df)} registros, últ: {df.iloc[-1][col]:.2f}")
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
        print(f"  OK WB {country} {indicator} ({col}) — {len(df)} años, últ: {df.iloc[-1][col]:.1f}")
        return df
    except Exception as e:
        print(f"  ERROR WB {country}/{indicator}: {e}")
        return None


def merge_series(dfs_dict):
    df_out = None
    for col, df in dfs_dict.items():
        if df is None or df.empty:
            continue
        df_m = df[["fecha", col]].copy()
        df_out = df_m if df_out is None else pd.merge(df_out, df_m, on="fecha", how="outer")
    if df_out is not None:
        df_out.sort_values("fecha", inplace=True)
        df_out.reset_index(drop=True, inplace=True)
    return df_out


# ── Tasas de política monetaria ────────────────────────────────────────────────
print("\n[Tasas]")
df_tasas = merge_series({
    "us_fed":    fetch_fred("FEDFUNDS",          "us_fed"),
    "ecb_rate":  fetch_fred("ECBDFR",            "ecb_rate"),
    "boj_rate":  fetch_fred("IRSTCB01JPM156N",   "boj_rate"),
    "selic":     fetch_bcb(11,                    "selic"),
})
if df_tasas is not None:
    df_tasas.to_csv("data/macro_tasas.csv", index=False)
    print(f"  → macro_tasas.csv ({len(df_tasas)} filas)")

# ── Inflación ──────────────────────────────────────────────────────────────────
print("\n[Inflación YoY]")

# US: calcular YoY desde índice
df_us_idx = fetch_fred("CPIAUCSL", "us_cpi_idx")
df_us_cpi = None
if df_us_idx is not None:
    df_us_cpi = df_us_idx.copy()
    df_us_cpi["us_cpi_yoy"] = df_us_cpi["us_cpi_idx"].pct_change(12) * 100
    df_us_cpi = df_us_cpi[["fecha", "us_cpi_yoy"]].dropna()

# Brasil: IPCA mensual (serie 433) → componer en 12 meses
df_br_monthly = fetch_bcb(433, "br_ipca_m")
df_br_cpi = None
if df_br_monthly is not None:
    df_br_monthly = df_br_monthly.set_index("fecha").resample("ME").last().reset_index()
    df_br_monthly["br_cpi_yoy"] = (
        (1 + df_br_monthly["br_ipca_m"] / 100)
        .rolling(12).apply(lambda x: x.prod(), raw=True) - 1
    ) * 100
    df_br_cpi = df_br_monthly[["fecha", "br_cpi_yoy"]].dropna()

df_infl = merge_series({
    "us_cpi_yoy": df_us_cpi,
    "eu_cpi_yoy": fetch_fred("CPHPTT01EZM659N", "eu_cpi_yoy"),
    "jp_cpi_yoy": fetch_fred("CPALTT01JPM659N", "jp_cpi_yoy"),
    "br_cpi_yoy": df_br_cpi,
    "cn_cpi_yoy": fetch_fred("CHNCPIALLMINMEI", "cn_cpi_yoy"),
})
if df_infl is not None:
    df_infl.to_csv("data/macro_inflacion.csv", index=False)
    print(f"  → macro_inflacion.csv ({len(df_infl)} filas)")

# ── Desempleo ──────────────────────────────────────────────────────────────────
print("\n[Desempleo]")
df_unemp = merge_series({
    "us_unrate": fetch_fred("UNRATE",            "us_unrate"),
    "eu_unrate": fetch_fred("LRHUTTTTEZM156S",   "eu_unrate"),
    "jp_unrate": fetch_fred("LRHUTTTTJPM156S",   "jp_unrate"),
})
if df_unemp is not None:
    df_unemp.to_csv("data/macro_desempleo.csv", index=False)
    print(f"  → macro_desempleo.csv ({len(df_unemp)} filas)")

# ── PIB — Crecimiento anual (World Bank) ───────────────────────────────────────
print("\n[PIB YoY — World Bank]")
IND_GDP = "NY.GDP.MKTP.KD.ZG"
df_gdp = merge_series({
    "us_gdp": fetch_worldbank("US", IND_GDP, "us_gdp"),
    "eu_gdp": fetch_worldbank("XC", IND_GDP, "eu_gdp"),
    "cn_gdp": fetch_worldbank("CN", IND_GDP, "cn_gdp"),
    "jp_gdp": fetch_worldbank("JP", IND_GDP, "jp_gdp"),
    "br_gdp": fetch_worldbank("BR", IND_GDP, "br_gdp"),
    "ar_gdp": fetch_worldbank("AR", IND_GDP, "ar_gdp"),
})
if df_gdp is not None:
    df_gdp.to_csv("data/macro_gdp.csv", index=False)
    print(f"  → macro_gdp.csv ({len(df_gdp)} filas)")

print("\n=== FIN fetch_macro_global.py ===")
