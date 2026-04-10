#!/usr/bin/env python3
"""fetch_earnings.py — Calendario de presentación de balances.

Usa yfinance para obtener próximas fechas de earnings de empresas
argentinas (ADRs) y globales.
"""
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

print("=== INICIO fetch_earnings.py ===")
os.makedirs("data", exist_ok=True)

CSV = "data/earnings_data.csv"

# Empresas argentinas (ADRs en NYSE/NASDAQ)
EMPRESAS_AR = {
    "GGAL":  "Grupo Galicia",
    "BMA":   "Banco Macro",
    "BBAR":  "BBVA Argentina",
    "SUPV":  "Supervielle",
    "VIST":  "Vista Oil & Gas",
    "CEPU":  "Central Puerto",
    "TGS":   "Transportadora Gas Sur",
    "LOMA":  "Loma Negra",
    "CRES":  "Cresud",
    "PAM":   "Pampa Energía",
    "EDN":   "Edenor",
    "IRCP":  "IRSA Propiedades",
}

# Empresas globales con país de origen
EMPRESAS_GLOBAL = {
    # EE.UU.
    "AAPL":  ("Apple",             "EE.UU."),
    "MSFT":  ("Microsoft",         "EE.UU."),
    "GOOGL": ("Alphabet",          "EE.UU."),
    "NVDA":  ("NVIDIA",            "EE.UU."),
    "META":  ("Meta",              "EE.UU."),
    "AMZN":  ("Amazon",            "EE.UU."),
    "TSLA":  ("Tesla",             "EE.UU."),
    "JPM":   ("JPMorgan",          "EE.UU."),
    "BAC":   ("Bank of America",   "EE.UU."),
    "GS":    ("Goldman Sachs",     "EE.UU."),
    "XOM":   ("ExxonMobil",        "EE.UU."),
    "CVX":   ("Chevron",           "EE.UU."),
    "V":     ("Visa",              "EE.UU."),
    "JNJ":   ("Johnson & Johnson", "EE.UU."),
    "WMT":   ("Walmart",           "EE.UU."),
    # Asia
    "TSM":   ("TSMC",              "Taiwan"),
    "BABA":  ("Alibaba",           "China"),
    # Brasil
    "VALE":  ("Vale",              "Brasil"),
    "PBR":   ("Petrobras",         "Brasil"),
    "ITUB":  ("Itaú Unibanco",     "Brasil"),
    # Europa
    "SAP":   ("SAP",               "Alemania"),
    "SHEL":  ("Shell",             "Reino Unido"),
    "TTE":   ("TotalEnergies",     "Francia"),
    "ARCO":  ("Arca Continental",  "México"),
}

HOY    = datetime.today().date()
FUTURO = HOY + timedelta(days=120)

records = []

for ticker, entry in {**{t: (n, "Argentina") for t, n in EMPRESAS_AR.items()},
                       **EMPRESAS_GLOBAL}.items():
    nombre, pais = entry
    try:
        t = yf.Ticker(ticker)
        cal = t.calendar
        if cal is None:
            continue

        # yfinance 1.0: calendar puede ser dict o DataFrame
        if isinstance(cal, pd.DataFrame):
            if cal.empty:
                continue
            # Transponer si viene con fechas como columnas
            cal = cal.T if "Earnings Date" not in cal.columns else cal

        if isinstance(cal, dict):
            ed_raw = cal.get("Earnings Date")
        else:
            ed_raw = cal.get("Earnings Date") if hasattr(cal, "get") else None

        if ed_raw is None:
            continue

        # Normalizar a lista
        if not isinstance(ed_raw, (list, pd.Series)):
            ed_raw = [ed_raw]

        for ed in ed_raw:
            try:
                ed_date = pd.Timestamp(ed).date()
            except Exception:
                continue
            if ed_date < HOY or ed_date > FUTURO:
                continue

            eps_est = None
            rev_est = None
            if isinstance(cal, dict):
                eps_raw = cal.get("EPS Estimate")
                rev_raw = cal.get("Revenue Estimate")
                eps_est = float(eps_raw) if eps_raw is not None else None
                rev_est = float(rev_raw) / 1e9 if rev_raw is not None else None

            records.append({
                "date":             ed_date,
                "ticker":           ticker,
                "company":          nombre,
                "country":          pais,
                "eps_estimate":     eps_est,
                "revenue_estimate_B": rev_est,
                "eps_actual":       None,
            })
            print(f"  OK {ticker} ({nombre}): {ed_date}")
            break  # solo la próxima fecha

    except Exception as e:
        print(f"  Sin datos {ticker}: {e}")

if records:
    df_new = pd.DataFrame(records)
    df_new["date"] = pd.to_datetime(df_new["date"])
    df_new.sort_values("date", inplace=True)

    if os.path.exists(CSV):
        df_old = pd.read_csv(CSV, parse_dates=["date"])
        # Conservar histórico pasado + reemplazar futuros con datos frescos
        df_old_past = df_old[df_old["date"].dt.date < HOY]
        df_combined = pd.concat([df_old_past, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["ticker", "date"], keep="last")
        df_combined.sort_values("date", inplace=True)
        df_combined.reset_index(drop=True, inplace=True)
    else:
        df_combined = df_new

    df_combined.to_csv(CSV, index=False)
    print(f"\n  → earnings_data.csv ({len(df_combined)} registros, {len(records)} nuevos)")
else:
    print("  Sin datos de earnings disponibles (yfinance puede estar bloqueado o mercado cerrado)")

print("=== FIN fetch_earnings.py ===")
