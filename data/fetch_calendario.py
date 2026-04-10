#!/usr/bin/env python3
"""fetch_calendario.py — Calendario de eventos económicos.

Fuentes:
- ForexFactory JSON feed (eventos internacionales próximas semanas)
- Hardcoded: reuniones FOMC, ECB, BoJ 2026
- Hardcoded: releases INDEC + reuniones BCRA 2026
"""
import requests
import pandas as pd
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

print("=== INICIO fetch_calendario.py ===")
os.makedirs("data", exist_ok=True)

HOY = datetime.today()
CSV_INT = "data/calendario_internacional.csv"
CSV_AR  = "data/calendario_argentina.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.forexfactory.com",
    "Accept": "application/json",
}

MONEDAS = {"USD", "EUR", "CNY", "JPY", "BRL"}
IMPACTO = {"High"}

# ── Calendario internacional — ForexFactory ────────────────────────────────────
eventos_ff = []
for semana in ["thisweek", "nextweek", "week2", "week3"]:
    try:
        r = requests.get(
            f"https://nfs.faireconomy.media/ff_calendar_{semana}.json",
            headers=HEADERS, timeout=15
        )
        if r.status_code != 200:
            print(f"  ForexFactory {semana}: HTTP {r.status_code}")
            continue
        for ev in r.json():
            if ev.get("impact") not in IMPACTO:
                continue
            if ev.get("currency") not in MONEDAS:
                continue
            eventos_ff.append({
                "date":     ev.get("date", ""),
                "time":     ev.get("time", ""),
                "currency": ev.get("currency", ""),
                "event":    ev.get("title", ""),
                "impact":   ev.get("impact", ""),
                "previous": ev.get("previous", ""),
                "forecast": ev.get("forecast", ""),
                "actual":   ev.get("actual", ""),
                "source":   "ForexFactory",
            })
        print(f"  OK ForexFactory {semana}")
    except Exception as e:
        print(f"  Error ForexFactory {semana}: {e}")

# ── Hardcoded: reuniones bancos centrales 2026 ─────────────────────────────────
REUNIONES_2026 = [
    # FOMC — tasa objetivo Fed Funds (rango superior)
    {"date": "2026-01-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "4.50%", "forecast": "4.50%", "actual": "4.50%"},
    {"date": "2026-03-18", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "4.50%", "forecast": "4.50%", "actual": "4.50%"},
    {"date": "2026-04-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "4.50%", "forecast": "4.50%", "actual": ""},
    {"date": "2026-06-10", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "4.50%", "forecast": "4.25%", "actual": ""},
    {"date": "2026-07-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "4.25%", "forecast": "", "actual": ""},
    {"date": "2026-09-16", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-10-28", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-12-09", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "", "forecast": "", "actual": ""},
    # NFP (miles de empleos)
    {"date": "2026-02-06", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "307K", "forecast": "170K", "actual": "151K"},
    {"date": "2026-03-06", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "151K", "forecast": "160K", "actual": "177K"},
    {"date": "2026-04-03", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "177K", "forecast": "140K", "actual": "228K"},
    {"date": "2026-05-01", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "228K", "forecast": "180K", "actual": ""},
    {"date": "2026-06-05", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-07-10", "time": "08:30", "currency": "USD", "event": "Nóminas no agrícolas (NFP)", "impact": "High", "source": "BLS", "previous": "", "forecast": "", "actual": ""},
    # CPI EE.UU. (interanual)
    {"date": "2026-02-11", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (ene)", "impact": "High", "source": "BLS", "previous": "2.9%", "forecast": "2.9%", "actual": "3.0%"},
    {"date": "2026-03-11", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (feb)", "impact": "High", "source": "BLS", "previous": "3.0%", "forecast": "2.9%", "actual": "2.8%"},
    {"date": "2026-04-10", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (mar)", "impact": "High", "source": "BLS", "previous": "2.8%", "forecast": "2.6%", "actual": ""},
    {"date": "2026-05-12", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (abr)", "impact": "High", "source": "BLS", "previous": "2.6%", "forecast": "", "actual": ""},
    {"date": "2026-06-10", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (may)", "impact": "High", "source": "BLS", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-07-14", "time": "08:30", "currency": "USD", "event": "CPI EE.UU. (jun)", "impact": "High", "source": "BLS", "previous": "", "forecast": "", "actual": ""},
    # ECB — tasa de depósito
    {"date": "2026-01-30", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "3.00%", "forecast": "2.75%", "actual": "2.75%"},
    {"date": "2026-03-06", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "2.75%", "forecast": "2.50%", "actual": "2.50%"},
    {"date": "2026-04-17", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "2.50%", "forecast": "2.25%", "actual": ""},
    {"date": "2026-06-05", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "2.25%", "forecast": "2.00%", "actual": ""},
    {"date": "2026-07-24", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-09-11", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-10-23", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-12-04", "time": "08:15", "currency": "EUR", "event": "ECB — Decisión de tasa", "impact": "High", "source": "ECB", "previous": "", "forecast": "", "actual": ""},
    # BoJ — overnight call rate
    {"date": "2026-01-24", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "0.25%", "forecast": "0.50%", "actual": "0.50%"},
    {"date": "2026-03-19", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "0.50%", "forecast": "0.50%", "actual": "0.50%"},
    {"date": "2026-05-01", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "0.50%", "forecast": "0.75%", "actual": ""},
    {"date": "2026-06-17", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-07-31", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-09-19", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-10-30", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-12-19", "time": "03:00", "currency": "JPY", "event": "BoJ — Decisión de tasa", "impact": "High", "source": "BoJ", "previous": "", "forecast": "", "actual": ""},
    # COPOM — Meta Selic (% a.a.)
    {"date": "2026-01-28", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "13.25%", "forecast": "14.75%", "actual": "14.75%"},
    {"date": "2026-03-18", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "14.75%", "forecast": "15.25%", "actual": "14.75%"},
    {"date": "2026-05-06", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "14.75%", "forecast": "14.75%", "actual": ""},
    {"date": "2026-06-17", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-07-29", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-09-16", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-10-28", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-12-09", "time": "18:00", "currency": "BRL", "event": "COPOM — Decisión SELIC", "impact": "High", "source": "BCB", "previous": "", "forecast": "", "actual": ""},
]

# Combinar ForexFactory + hardcoded
df_hc = pd.DataFrame(REUNIONES_2026)
df_hc["date"] = pd.to_datetime(df_hc["date"])

if eventos_ff:
    df_ff = pd.DataFrame(eventos_ff)
    df_ff["date"] = pd.to_datetime(df_ff["date"], errors="coerce")
    df_ff = df_ff.dropna(subset=["date"])
    df_new_int = pd.concat([df_ff, df_hc], ignore_index=True)
else:
    df_new_int = df_hc

df_new_int = df_new_int.drop_duplicates(subset=["date", "currency", "event"], keep="first")

if os.path.exists(CSV_INT):
    df_old = pd.read_csv(CSV_INT, parse_dates=["date"])
    # Mantener pasados del CSV viejo + nuevos del fetch actual
    df_pasados = df_old[df_old["date"] < pd.Timestamp(HOY.date())]
    df_combined = pd.concat([df_pasados, df_new_int], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=["date", "currency", "event"], keep="last")
else:
    df_combined = df_new_int

df_combined.sort_values("date", inplace=True)
df_combined.reset_index(drop=True, inplace=True)
df_combined.to_csv(CSV_INT, index=False)
print(f"  → calendario_internacional.csv ({len(df_combined)} eventos)")

# ── Calendario Argentina (INDEC + BCRA) ────────────────────────────────────────
EVENTOS_AR = [
    # IPC Nacional (INDEC) — aprox día 14 de cada mes
    # previous = mes anterior, actual = dato publicado, forecast = estimado de mercado
    {"date": "2026-01-14", "event": "IPC Nacional (dic 2025)", "source": "INDEC", "impact": "High", "previous": "2.4%", "forecast": "2.5%", "actual": "2.7%"},
    {"date": "2026-02-13", "event": "IPC Nacional (ene 2026)", "source": "INDEC", "impact": "High", "previous": "2.7%", "forecast": "2.5%", "actual": "2.9%"},
    {"date": "2026-03-13", "event": "IPC Nacional (feb 2026)", "source": "INDEC", "impact": "High", "previous": "2.9%", "forecast": "2.4%", "actual": "2.4%"},
    {"date": "2026-04-14", "event": "IPC Nacional (mar 2026)", "source": "INDEC", "impact": "High", "previous": "2.4%", "forecast": "3.5%", "actual": ""},
    {"date": "2026-05-14", "event": "IPC Nacional (abr 2026)", "source": "INDEC", "impact": "High", "previous": "3.5%", "forecast": "", "actual": ""},
    {"date": "2026-06-11", "event": "IPC Nacional (may 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-07-14", "event": "IPC Nacional (jun 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-08-13", "event": "IPC Nacional (jul 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-09-10", "event": "IPC Nacional (ago 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-10-14", "event": "IPC Nacional (sep 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-11-12", "event": "IPC Nacional (oct 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    {"date": "2026-12-11", "event": "IPC Nacional (nov 2026)", "source": "INDEC", "impact": "High", "previous": "", "forecast": "", "actual": ""},
    # EMAE
    {"date": "2026-03-24", "event": "EMAE (ene 2026)",  "source": "INDEC", "impact": "Medium"},
    {"date": "2026-04-23", "event": "EMAE (feb 2026)",  "source": "INDEC", "impact": "Medium"},
    {"date": "2026-05-21", "event": "EMAE (mar 2026)",  "source": "INDEC", "impact": "Medium"},
    {"date": "2026-06-23", "event": "EMAE (abr 2026)",  "source": "INDEC", "impact": "Medium"},
    {"date": "2026-07-23", "event": "EMAE (may 2026)",  "source": "INDEC", "impact": "Medium"},
    {"date": "2026-08-20", "event": "EMAE (jun 2026)",  "source": "INDEC", "impact": "Medium"},
    # Comercio exterior
    {"date": "2026-02-19", "event": "Comercio Exterior (dic 2025)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-03-19", "event": "Comercio Exterior (ene 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-04-16", "event": "Comercio Exterior (feb 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-05-19", "event": "Comercio Exterior (mar 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-06-18", "event": "Comercio Exterior (abr 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-07-16", "event": "Comercio Exterior (may 2026)", "source": "INDEC", "impact": "Medium"},
    # PBI trimestral
    {"date": "2026-03-19", "event": "PBI — Q4 2025",  "source": "INDEC", "impact": "High"},
    {"date": "2026-06-18", "event": "PBI — Q1 2026",  "source": "INDEC", "impact": "High"},
    {"date": "2026-09-17", "event": "PBI — Q2 2026",  "source": "INDEC", "impact": "High"},
    {"date": "2026-12-17", "event": "PBI — Q3 2026",  "source": "INDEC", "impact": "High"},
    # BCRA reuniones de política monetaria
    {"date": "2026-01-30", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-03-20", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-05-08", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-06-19", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-08-07", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-09-18", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-10-30", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
    {"date": "2026-12-11", "event": "BCRA — Política Monetaria", "source": "BCRA", "impact": "High"},
]
for ev in EVENTOS_AR:
    ev.setdefault("actual", "")
    ev.setdefault("previous", "")
    ev.setdefault("forecast", "")
    ev["currency"] = "ARS"

df_ar = pd.DataFrame(EVENTOS_AR)
df_ar["date"] = pd.to_datetime(df_ar["date"])

# Rellenar "actual" para IPC con datos existentes de BCRA CSV
try:
    bcra = pd.read_csv("data/bcra_data.csv", parse_dates=["fecha"]) if os.path.exists("data/bcra_data.csv") else None
    if bcra is not None and "inflacion_mensual" in bcra.columns:
        datos_cpi = bcra[["fecha", "inflacion_mensual"]].dropna()
        for idx, row in df_ar.iterrows():
            if "IPC Nacional" in row["event"] and row["date"] <= pd.Timestamp.now():
                # Buscar dato de inflación del mes correspondiente
                candidatos = datos_cpi[datos_cpi["fecha"].dt.to_period("M") == row["date"].to_period("M")]
                if not candidatos.empty:
                    val = candidatos["inflacion_mensual"].values[-1]
                    df_ar.at[idx, "actual"] = f"{val:.1f}%"
except Exception as e:
    print(f"  No se pudieron rellenar actuals AR: {e}")

df_ar.to_csv(CSV_AR, index=False)
print(f"  → calendario_argentina.csv ({len(df_ar)} eventos)")

print("=== FIN fetch_calendario.py ===")
