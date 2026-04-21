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
    # FOMC — tasa efectiva Fed Funds (midpoint rango objetivo)
    # Sep 2025: 4.25→4.00% | Dec 2025: 4.00→3.75% | Mar 2026: 3.75→3.50%
    {"date": "2026-01-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "3.83%", "forecast": "3.83%", "actual": "3.83%"},
    {"date": "2026-03-18", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "3.83%", "forecast": "3.63%", "actual": "3.63%"},
    {"date": "2026-04-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "3.63%", "forecast": "3.63%", "actual": ""},
    {"date": "2026-06-10", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "3.63%", "forecast": "3.38%", "actual": ""},
    {"date": "2026-07-29", "time": "14:00", "currency": "USD", "event": "FOMC — Decisión de tasa", "impact": "High", "source": "Fed", "previous": "", "forecast": "", "actual": ""},
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
for col in ["previous", "forecast", "actual", "time"]:
    if col in df_combined.columns:
        df_combined[col] = df_combined[col].fillna("")
df_combined.to_csv(CSV_INT, index=False)
print(f"  → calendario_internacional.csv ({len(df_combined)} eventos)")

# ── Calendario Argentina (INDEC + BCRA) ────────────────────────────────────────
EVENTOS_AR = [
    # ── IPC CABA (DGEyC GCBA) ──────────────────────────────────────────────────
    {"date": "2026-01-09", "event": "IPC CABA (dic 2025)",  "source": "DGEyC CABA", "impact": "High", "previous": "2.5%",  "forecast": "2.7%",  "actual": "2.8%"},
    {"date": "2026-02-10", "event": "IPC CABA (ene 2026)",  "source": "DGEyC CABA", "impact": "High", "previous": "2.8%",  "forecast": "2.7%",  "actual": "3.1%"},
    {"date": "2026-03-10", "event": "IPC CABA (feb 2026)",  "source": "DGEyC CABA", "impact": "High", "previous": "3.1%",  "forecast": "2.5%",  "actual": "2.4%"},
    {"date": "2026-04-09", "event": "IPC CABA (mar 2026)",  "source": "DGEyC CABA", "impact": "High", "previous": "2.4%",  "forecast": "3.7%",  "actual": ""},
    {"date": "2026-05-11", "event": "IPC CABA (abr 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-06-08", "event": "IPC CABA (may 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-07-09", "event": "IPC CABA (jun 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-08-10", "event": "IPC CABA (jul 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-09-07", "event": "IPC CABA (ago 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-10-09", "event": "IPC CABA (sep 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-11-09", "event": "IPC CABA (oct 2026)",  "source": "DGEyC CABA", "impact": "High"},
    {"date": "2026-12-08", "event": "IPC CABA (nov 2026)",  "source": "DGEyC CABA", "impact": "High"},
    # ── IPC Nacional (INDEC) — fechas exactas calendario INDEC 2026 ────────────
    {"date": "2026-01-14", "event": "IPC Nacional (dic 2025)", "source": "INDEC", "impact": "High", "previous": "2.4%", "forecast": "2.5%", "actual": "2.7%"},
    {"date": "2026-02-13", "event": "IPC Nacional (ene 2026)", "source": "INDEC", "impact": "High", "previous": "2.7%", "forecast": "2.5%", "actual": "2.9%"},
    {"date": "2026-03-13", "event": "IPC Nacional (feb 2026)", "source": "INDEC", "impact": "High", "previous": "2.9%", "forecast": "2.4%", "actual": "2.4%"},
    {"date": "2026-04-14", "event": "IPC Nacional (mar 2026)", "source": "INDEC", "impact": "High", "previous": "2.4%", "forecast": "3.5%", "actual": ""},
    {"date": "2026-05-11", "event": "IPC Nacional (abr 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-06-11", "event": "IPC Nacional (may 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-07-14", "event": "IPC Nacional (jun 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-08-13", "event": "IPC Nacional (jul 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-09-07", "event": "IPC Nacional (ago 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-10-13", "event": "IPC Nacional (sep 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-11-13", "event": "IPC Nacional (oct 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-12-11", "event": "IPC Nacional (nov 2026)", "source": "INDEC", "impact": "High"},
    # ── SIPM — Inflación Mayorista (INDEC) ────────────────────────────────────
    {"date": "2026-01-19", "event": "Inflación Mayorista SIPM (dic 2025)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-02-19", "event": "Inflación Mayorista SIPM (ene 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-03-13", "event": "Inflación Mayorista SIPM (feb 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-04-16", "event": "Inflación Mayorista SIPM (mar 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-05-14", "event": "Inflación Mayorista SIPM (abr 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-06-15", "event": "Inflación Mayorista SIPM (may 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-07-16", "event": "Inflación Mayorista SIPM (jun 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-08-14", "event": "Inflación Mayorista SIPM (jul 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-09-11", "event": "Inflación Mayorista SIPM (ago 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-10-14", "event": "Inflación Mayorista SIPM (sep 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-11-17", "event": "Inflación Mayorista SIPM (oct 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-12-14", "event": "Inflación Mayorista SIPM (nov 2026)", "source": "INDEC", "impact": "Medium"},
    # ── EMAE (Estimador Mensual de Actividad Económica — INDEC) ───────────────
    {"date": "2026-01-22", "event": "EMAE (nov 2025)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-02-24", "event": "EMAE (dic 2025)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-03-24", "event": "EMAE (ene 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-04-28", "event": "EMAE (feb 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-05-25", "event": "EMAE (mar 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-06-24", "event": "EMAE (abr 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-07-22", "event": "EMAE (may 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-08-20", "event": "EMAE (jun 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-09-18", "event": "EMAE (jul 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-10-21", "event": "EMAE (ago 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-11-20", "event": "EMAE (sep 2026)",  "source": "INDEC", "impact": "High"},
    {"date": "2026-12-18", "event": "EMAE (oct 2026)",  "source": "INDEC", "impact": "High"},
    # ── Intercambio Comercial / Balanza Comercial (INDEC) ─────────────────────
    {"date": "2026-01-20", "event": "Intercambio Comercial (dic 2025)", "source": "INDEC", "impact": "High"},
    {"date": "2026-02-23", "event": "Intercambio Comercial (ene 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-03-19", "event": "Intercambio Comercial (feb 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-04-16", "event": "Intercambio Comercial (mar 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-05-18", "event": "Intercambio Comercial (abr 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-06-18", "event": "Intercambio Comercial (may 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-07-20", "event": "Intercambio Comercial (jun 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-08-19", "event": "Intercambio Comercial (jul 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-09-17", "event": "Intercambio Comercial (ago 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-10-23", "event": "Intercambio Comercial (sep 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-11-19", "event": "Intercambio Comercial (oct 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-12-17", "event": "Intercambio Comercial (nov 2026)", "source": "INDEC", "impact": "High"},
    # ── Balanza de Pagos (INDEC, trimestral) ──────────────────────────────────
    {"date": "2026-04-15", "event": "Balanza de Pagos (Q4 2025)", "source": "INDEC", "impact": "High"},
    {"date": "2026-06-23", "event": "Balanza de Pagos (Q1 2026)", "source": "INDEC", "impact": "High"},
    {"date": "2026-12-23", "event": "Balanza de Pagos (Q3 2026)", "source": "INDEC", "impact": "High"},
    # ── Índice de Salarios (INDEC) ────────────────────────────────────────────
    {"date": "2026-01-26", "event": "Índice de Salarios (nov 2025)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-03-19", "event": "Índice de Salarios (ene 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-05-24", "event": "Índice de Salarios (mar 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-07-27", "event": "Índice de Salarios (may 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-08-21", "event": "Índice de Salarios (jun 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-10-21", "event": "Índice de Salarios (ago 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-11-24", "event": "Índice de Salarios (sep 2026)", "source": "INDEC", "impact": "Medium"},
    {"date": "2026-12-30", "event": "Índice de Salarios (oct 2026)", "source": "INDEC", "impact": "Medium"},
    # ── PBI Trimestral / Cuentas Nacionales (INDEC) ───────────────────────────
    {"date": "2026-03-19", "event": "PBI — Q4 2025", "source": "INDEC", "impact": "High"},
    {"date": "2026-06-18", "event": "PBI — Q1 2026", "source": "INDEC", "impact": "High"},
    {"date": "2026-09-17", "event": "PBI — Q2 2026", "source": "INDEC", "impact": "High"},
    {"date": "2026-12-17", "event": "PBI — Q3 2026", "source": "INDEC", "impact": "High"},
    # ── EPH (Encuesta Permanente de Hogares, trimestral) ──────────────────────
    {"date": "2026-03-26", "event": "EPH — Mercado de Trabajo Q4 2025", "source": "INDEC", "impact": "High"},
    {"date": "2026-06-25", "event": "EPH — Mercado de Trabajo Q1 2026", "source": "INDEC", "impact": "High"},
    {"date": "2026-09-24", "event": "EPH — Mercado de Trabajo Q2 2026", "source": "INDEC", "impact": "High"},
    {"date": "2026-12-10", "event": "EPH — Mercado de Trabajo Q3 2026", "source": "INDEC", "impact": "High"},
    # ── BCRA — REM (fechas exactas calendario BCRA 2026) ─────────────────────
    {"date": "2026-01-07", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-02-05", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-03-05", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-04-08", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-05-07", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-06-04", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-07-06", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-08-06", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-09-04", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-10-06", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    {"date": "2026-11-05", "event": "REM — Expectativas de Mercado", "source": "BCRA", "impact": "High"},
    # ── BCRA — Informe Monetario Mensual ──────────────────────────────────────
    {"date": "2026-01-08", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-02-06", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-03-06", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-04-09", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-05-08", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-06-05", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-07-07", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-08-07", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-09-09", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-10-07", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-11-09", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-12-09", "event": "Informe Monetario Mensual", "source": "BCRA", "impact": "Medium"},
    # ── BCRA — Informe del Mercado de Cambios y Balance Cambiario ─────────────
    {"date": "2026-01-30", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-02-27", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-03-27", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-04-24", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-05-29", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-06-26", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-07-31", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-08-28", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-09-25", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-10-30", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-11-27", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
    {"date": "2026-12-31", "event": "Informe Mercado de Cambios y Balance Cambiario", "source": "BCRA", "impact": "Medium"},
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

# Llenar NaN con "" para que el CSV no tenga "nan"
for col in ["previous", "forecast", "actual", "time"]:
    if col in df_ar.columns:
        df_ar[col] = df_ar[col].fillna("")
df_ar.to_csv(CSV_AR, index=False)
print(f"  → calendario_argentina.csv ({len(df_ar)} eventos)")

print("=== FIN fetch_calendario.py ===")
