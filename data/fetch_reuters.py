#!/usr/bin/env python3
"""fetch_reuters.py — Actualización local vía Eikon Desktop (Reuters/LSEG).

USO:
    1. Abrí Eikon Desktop (debe estar corriendo)
    2. Ejecutá: python data/fetch_reuters.py
    3. El script actualiza los CSVs y hace git push automáticamente

QUÉ ACTUALIZA:
    - earnings_data.csv  : fechas de balance + EPS/Revenue estimate + actual
    - calendario_argentina.csv   : forecasts de consenso para IPC CABA e IPC Nacional
    - calendario_internacional.csv : forecasts de consenso (NFP, CPI, tasas)

REQUISITOS:
    pip install eikon pandas
"""

import eikon as ek
import pandas as pd
import os
import subprocess
from datetime import datetime, timedelta

print("=== INICIO fetch_reuters.py ===")
print("Conectando a Eikon Desktop...")

# ── Conexión ──────────────────────────────────────────────────────────────────
# Si tenés App Key, descomentá la siguiente línea:
# ek.set_app_key("XXXX-XXXXXXXX-XXXXXXXX-XXXXXXXXXXXX")
# Sin App Key funciona directamente si Eikon Desktop está abierto.

try:
    # Test de conexión
    ek.get_data("AAPL.O", ["TR.CompanyName"])
    print("  OK — Conexión a Eikon establecida")
except Exception as e:
    print(f"  ERROR conectando a Eikon: {e}")
    print("  Verificá que Eikon Desktop esté abierto y corriendo.")
    exit(1)

HOY    = datetime.today().date()
FUTURO = HOY + timedelta(days=120)

# ── RICs de Reuters para tickers de nuestra lista ─────────────────────────────
# Formato: ticker_local -> RIC de Reuters
TICKER_RIC = {
    # ADRs argentinos (NYSE)
    "GGAL":  "GGAL.N",
    "BMA":   "BMA.N",
    "BBAR":  "BBAR.N",
    "SUPV":  "SUPV.N",
    "VIST":  "VIST.N",
    "CEPU":  "CEPU.N",
    "TGS":   "TGS.N",
    "LOMA":  "LOMA.N",
    "CRES":  "CRES.O",
    "PAM":   "PAM.N",
    "EDN":   "EDN.N",
    "IRCP":  "IRCP.N",
    # EE.UU.
    "AAPL":  "AAPL.O",
    "MSFT":  "MSFT.O",
    "GOOGL": "GOOGL.O",
    "NVDA":  "NVDA.O",
    "META":  "META.O",
    "AMZN":  "AMZN.O",
    "TSLA":  "TSLA.O",
    "JPM":   "JPM.N",
    "BAC":   "BAC.N",
    "GS":    "GS.N",
    "XOM":   "XOM.N",
    "CVX":   "CVX.N",
    "V":     "V.N",
    "JNJ":   "JNJ.N",
    "WMT":   "WMT.N",
    # Asia / Europa / LatAm
    "TSM":   "TSM.N",
    "BABA":  "BABA.N",
    "VALE":  "VALE.N",
    "PBR":   "PBR.N",
    "ITUB":  "ITUB.N",
    "SAP":   "SAP.N",
    "SHEL":  "SHEL.N",
    "TTE":   "TTE.N",
    "ARCO":  "ARCO.O",
}

PAIS_POR_TICKER = {
    "GGAL": "Argentina", "BMA": "Argentina", "BBAR": "Argentina",
    "SUPV": "Argentina", "VIST": "Argentina", "CEPU": "Argentina",
    "TGS": "Argentina",  "LOMA": "Argentina", "CRES": "Argentina",
    "PAM": "Argentina",  "EDN": "Argentina",  "IRCP": "Argentina",
    "AAPL": "EE.UU.", "MSFT": "EE.UU.", "GOOGL": "EE.UU.",
    "NVDA": "EE.UU.", "META": "EE.UU.", "AMZN": "EE.UU.",
    "TSLA": "EE.UU.", "JPM": "EE.UU.", "BAC": "EE.UU.",
    "GS": "EE.UU.", "XOM": "EE.UU.", "CVX": "EE.UU.",
    "V": "EE.UU.", "JNJ": "EE.UU.", "WMT": "EE.UU.",
    "TSM": "Taiwan", "BABA": "China",
    "VALE": "Brasil", "PBR": "Brasil", "ITUB": "Brasil",
    "SAP": "Alemania", "SHEL": "Reino Unido",
    "TTE": "Francia", "ARCO": "México",
}

NOMBRE_POR_TICKER = {
    "GGAL": "Grupo Galicia", "BMA": "Banco Macro", "BBAR": "BBVA Argentina",
    "SUPV": "Supervielle", "VIST": "Vista Oil & Gas", "CEPU": "Central Puerto",
    "TGS": "Transportadora Gas Sur", "LOMA": "Loma Negra", "CRES": "Cresud",
    "PAM": "Pampa Energía", "EDN": "Edenor", "IRCP": "IRSA Propiedades",
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "NVDA": "NVIDIA", "META": "Meta", "AMZN": "Amazon",
    "TSLA": "Tesla", "JPM": "JPMorgan", "BAC": "Bank of America",
    "GS": "Goldman Sachs", "XOM": "ExxonMobil", "CVX": "Chevron",
    "V": "Visa", "JNJ": "Johnson & Johnson", "WMT": "Walmart",
    "TSM": "TSMC", "BABA": "Alibaba",
    "VALE": "Vale", "PBR": "Petrobras", "ITUB": "Itaú Unibanco",
    "SAP": "SAP", "SHEL": "Shell", "TTE": "TotalEnergies", "ARCO": "Arca Continental",
}

# ── Earnings via Eikon ────────────────────────────────────────────────────────
print("\n[Earnings — Eikon]")

rics = list(TICKER_RIC.values())
tickers = list(TICKER_RIC.keys())

fields = [
    "TR.EarningsReleaseDate",     # próxima fecha de resultados
    "TR.EPSMean",                 # EPS consenso (media de analistas)
    "TR.RevenueMean",             # Revenue consenso
    "TR.EPSActValue",             # EPS actual (si ya reportó)
]

records = []
try:
    df_ek, err = ek.get_data(rics, fields)
    if err:
        print(f"  Advertencia: {err}")

    # Mapear RIC → ticker local
    ric_to_ticker = {v: k for k, v in TICKER_RIC.items()}

    for _, row in df_ek.iterrows():
        ric = row.get("Instrument", "")
        ticker = ric_to_ticker.get(ric, ric)

        raw_date = row.get("TR.EarningsReleaseDate") or row.get("Earnings Release Date")
        if pd.isna(raw_date) or raw_date is None:
            print(f"  Sin fecha: {ticker}")
            continue

        try:
            ed = pd.Timestamp(raw_date).date()
        except Exception:
            print(f"  Fecha inválida {ticker}: {raw_date}")
            continue

        if ed < HOY or ed > FUTURO:
            print(f"  Fuera de rango {ticker}: {ed}")
            continue

        def _float(val):
            try:
                v = float(val)
                return v if not pd.isna(v) else None
            except Exception:
                return None

        eps_mean  = _float(row.get("TR.EPSMean") or row.get("EPS Mean"))
        rev_mean  = _float(row.get("TR.RevenueMean") or row.get("Revenue Mean"))
        eps_act   = _float(row.get("TR.EPSActValue") or row.get("EPS Actual Value"))

        records.append({
            "date":               ed,
            "ticker":             ticker,
            "company":            NOMBRE_POR_TICKER.get(ticker, ticker),
            "country":            PAIS_POR_TICKER.get(ticker, "—"),
            "eps_estimate":       eps_mean,
            "revenue_estimate_B": rev_mean / 1e9 if rev_mean else None,
            "eps_actual":         eps_act,
        })
        print(f"  OK {ticker}: {ed} | EPS est {eps_mean} | Rev est {rev_mean}")

except Exception as e:
    print(f"  ERROR obteniendo earnings: {e}")

if records:
    df_new = pd.DataFrame(records)
    df_new["date"] = pd.to_datetime(df_new["date"])
    df_new.sort_values("date", inplace=True)

    csv_earn = "data/earnings_data.csv"
    if os.path.exists(csv_earn):
        df_old = pd.read_csv(csv_earn, parse_dates=["date"])
        df_old_past = df_old[df_old["date"].dt.date < HOY]
        df_combined = pd.concat([df_old_past, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=["ticker", "date"], keep="last")
    else:
        df_combined = df_new

    df_combined.sort_values("date", inplace=True)
    df_combined.reset_index(drop=True, inplace=True)
    df_combined.to_csv(csv_earn, index=False)
    print(f"  → earnings_data.csv actualizado ({len(df_combined)} registros)")
else:
    print("  Sin datos de earnings de Eikon — earnings_data.csv sin cambios")

# ── Calendario económico internacional — consensos via Eikon ──────────────────
print("\n[Calendario Internacional — Consensos Eikon]")

# RICs de indicadores económicos de alto impacto
# Formato: (RIC, nombre_evento, currency)
ECO_RICS = [
    # EE.UU.
    ("USNFAR=ECI",  "Nóminas no agrícolas (NFP)",  "USD"),
    ("USCPIY=ECI",  "CPI EE.UU. (YoY)",            "USD"),
    # Eurozona
    ("EZCPIY=ECI",  "CPI Eurozona (YoY)",           "EUR"),
    # Japón
    ("JPCPIY=ECI",  "CPI Japón (YoY)",              "JPY"),
    # Brasil
    ("BRIPCA=ECI",  "IPCA Brasil (YoY)",            "BRL"),
    # China
    ("CNCPIY=ECI",  "CPI China (YoY)",              "CNY"),
]

eco_fields = [
    "RT.ActualValue",
    "RT.ForecastMedian",
    "RT.PreviousActualValue",
    "RT.ReleaseDate",
]

eco_records = []
for ric, event_name, currency in ECO_RICS:
    try:
        df_eco, err = ek.get_data(ric, eco_fields)
        if df_eco is None or df_eco.empty:
            print(f"  Sin datos: {ric}")
            continue
        row = df_eco.iloc[0]
        release_raw = row.get("RT.ReleaseDate") or row.get("Release Date")
        if pd.isna(release_raw):
            continue
        release_date = pd.Timestamp(release_raw).date()
        actual  = row.get("RT.ActualValue") or row.get("Actual Value")
        fc      = row.get("RT.ForecastMedian") or row.get("Forecast Median")
        prev    = row.get("RT.PreviousActualValue") or row.get("Previous Actual Value")

        def _fmt(v):
            try:
                return f"{float(v):.1f}%" if v and not pd.isna(v) else ""
            except Exception:
                return ""

        eco_records.append({
            "date":     release_date,
            "currency": currency,
            "event":    event_name,
            "impact":   "High",
            "source":   "Reuters",
            "previous": _fmt(prev),
            "forecast": _fmt(fc),
            "actual":   _fmt(actual),
        })
        print(f"  OK {ric}: {release_date} | prev={_fmt(prev)} | fc={_fmt(fc)} | actual={_fmt(actual)}")
    except Exception as e:
        print(f"  ERROR {ric}: {e}")

if eco_records:
    csv_int = "data/calendario_internacional.csv"
    df_int = pd.read_csv(csv_int, parse_dates=["date"]) if os.path.exists(csv_int) else pd.DataFrame()

    df_eco_new = pd.DataFrame(eco_records)
    df_eco_new["date"] = pd.to_datetime(df_eco_new["date"])

    if not df_int.empty:
        # Actualizar solo filas donde source != "Reuters" o agregar nuevas
        df_no_reuters = df_int[df_int.get("source", "") != "Reuters"]
        df_combined_int = pd.concat([df_no_reuters, df_eco_new], ignore_index=True)
        df_combined_int = df_combined_int.drop_duplicates(
            subset=["date", "currency", "event"], keep="last"
        )
    else:
        df_combined_int = df_eco_new

    df_combined_int.sort_values("date", inplace=True)
    df_combined_int.reset_index(drop=True, inplace=True)
    for col in ["previous", "forecast", "actual", "time"]:
        if col in df_combined_int.columns:
            df_combined_int[col] = df_combined_int[col].fillna("")
    df_combined_int.to_csv(csv_int, index=False)
    print(f"  → calendario_internacional.csv actualizado ({len(eco_records)} eventos Reuters)")

# ── Calendario Argentina — consensos IPC ─────────────────────────────────────
print("\n[Calendario Argentina — IPC Consenso Eikon]")

AR_ECO_RICS = [
    ("ARCPIY=ECI",  "IPC Nacional"),    # IPC Argentina YoY (si existe en Reuters)
    ("ARCPIM=ECI",  "IPC Nacional"),    # IPC Argentina mensual
]

for ric, event_prefix in AR_ECO_RICS:
    try:
        df_ar_eco, _ = ek.get_data(ric, eco_fields)
        if df_ar_eco is None or df_ar_eco.empty:
            continue
        row = df_ar_eco.iloc[0]
        release_raw = row.get("RT.ReleaseDate") or row.get("Release Date")
        if pd.isna(release_raw):
            continue
        release_date = pd.Timestamp(release_raw).date()
        fc   = row.get("RT.ForecastMedian") or row.get("Forecast Median")
        prev = row.get("RT.PreviousActualValue") or row.get("Previous Actual Value")

        # Actualizar el forecast en calendario_argentina.csv
        csv_ar = "data/calendario_argentina.csv"
        if os.path.exists(csv_ar):
            df_ar_cal = pd.read_csv(csv_ar, parse_dates=["date"])
            mask = (
                df_ar_cal["event"].str.contains(event_prefix, na=False) &
                (df_ar_cal["date"].dt.date == release_date)
            )
            if mask.any():
                if fc and not pd.isna(fc):
                    df_ar_cal.loc[mask, "forecast"] = f"{float(fc):.1f}%"
                if prev and not pd.isna(prev):
                    df_ar_cal.loc[mask, "previous"] = f"{float(prev):.1f}%"
                df_ar_cal.to_csv(csv_ar, index=False)
                print(f"  OK {ric}: consenso actualizado para {release_date}")
            else:
                print(f"  Sin match en calendario_argentina para {release_date}")
    except Exception as e:
        print(f"  ERROR {ric}: {e}")

# ── Git push automático ───────────────────────────────────────────────────────
print("\n[Git push]")
try:
    # Detectar branch actual
    branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()

    subprocess.run(["git", "add",
        "data/earnings_data.csv",
        "data/calendario_internacional.csv",
        "data/calendario_argentina.csv",
    ], check=True)

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True
    )
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m",
            f"Reuters: actualización earnings + calendario ({datetime.today().strftime('%Y-%m-%d')})"
        ], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        print(f"  Cambios pusheados a {branch}")
    else:
        print("  Sin cambios para pushear")

except subprocess.CalledProcessError as e:
    print(f"  ERROR en git: {e}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== FIN fetch_reuters.py ===")
