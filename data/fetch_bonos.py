#!/usr/bin/env python3
"""fetch_bonos.py — Precios históricos de bonos soberanos argentinos desde Open BYMA Data.

Usa el endpoint de series históricas (GET) que funciona independientemente
del horario de mercado. Ref: https://github.com/franco-lamas/PyOBD
"""

import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TICKERS_OBJETIVO = [
    "GD29", "GD30", "GD35", "GD38", "GD41", "GD46",
    "AL29", "AL30", "AL35", "AE38", "AL41", "AL46",
]

# Variantes de settlement a probar por orden
SETTLEMENTS = ["48HS", "CI", ""]

BASE_URL = "https://open.bymadata.com.ar"
HIST_URL = f"{BASE_URL}/vanoms-be-core/rest/api/bymadata/free/chart/historical-series/history"
DASHBOARD_URL = f"{BASE_URL}/#/dashboard"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": BASE_URL,
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": BASE_URL + "/",
    "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

# Zona horaria Buenos Aires (UTC-3)
TZ_AR = timezone(timedelta(hours=-3))


def date_to_ts(date_str):
    """Convierte 'YYYY-MM-DD' a Unix timestamp en zona AR."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=TZ_AR)
    return int(dt.timestamp())


def get_session():
    session = requests.Session()
    session.verify = False
    session.headers.update(HEADERS)
    try:
        session.get(DASHBOARD_URL, timeout=15)
    except Exception as e:
        print(f"  Advertencia inicializando sesión: {e}")
    return session


def fetch_hist(session, symbol, desde, hasta):
    """Devuelve DataFrame con columnas [date, open, high, low, close, volume] o None."""
    params = {
        "symbol": symbol,
        "resolution": "D",
        "from": date_to_ts(desde),
        "to": date_to_ts(hasta),
    }
    try:
        r = session.get(HIST_URL, params=params, timeout=15)
        if r.status_code != 200:
            return None
        body = r.json()
        # La API devuelve {"s":"ok","t":[...],"o":[...],"h":[...],"l":[...],"c":[...],"v":[...]}
        if body.get("s") != "ok" or not body.get("t"):
            return None
        df = pd.DataFrame({
            "fecha": [datetime.fromtimestamp(ts, tz=TZ_AR).date() for ts in body["t"]],
            "close": body["c"],
            "open":  body.get("o", [None]*len(body["t"])),
            "high":  body.get("h", [None]*len(body["t"])),
            "low":   body.get("l", [None]*len(body["t"])),
            "volume": body.get("v", [None]*len(body["t"])),
        })
        df = df[df["close"].notna() & (df["close"] > 0)]
        return df if not df.empty else None
    except Exception as e:
        print(f"    Error en {symbol}: {e}")
        return None


def main():
    import sys
    print("=== INICIO fetch_bonos.py ===")

    session = get_session()

    hasta = datetime.now(TZ_AR).strftime("%Y-%m-%d")
    desde = (datetime.now(TZ_AR) - timedelta(days=10)).strftime("%Y-%m-%d")

    records = []
    for ticker in TICKERS_OBJETIVO:
        encontrado = False
        for settlement in SETTLEMENTS:
            symbol = f"{ticker} {settlement}".strip()
            df = fetch_hist(session, symbol, desde, hasta)
            if df is not None:
                ultimo = df.sort_values("fecha").iloc[-1]
                precio = float(ultimo["close"])
                # Calcular variación respecto al día anterior
                variacion = None
                if len(df) >= 2:
                    prev = float(df.sort_values("fecha").iloc[-2]["close"])
                    if prev > 0:
                        variacion = round((precio - prev) / prev * 100, 4)
                records.append({
                    "fecha": str(ultimo["fecha"]),
                    "ticker": ticker,
                    "precio": round(precio, 4),
                    "variacion_pct": variacion,
                    "volumen": float(ultimo["volume"]) if ultimo["volume"] is not None else None,
                })
                print(f"  OK {ticker:6s} [{symbol}]: {precio:.2f}  ({f'{variacion:+.2f}%' if variacion is not None else 'N/A'})")
                encontrado = True
                break
        if not encontrado:
            print(f"  SIN DATOS: {ticker}")

    if not records:
        print("ERROR: No se pudo obtener datos de ningún bono.")
        sys.exit(1)

    df_new = pd.DataFrame(records)
    out_path = os.path.join(os.path.dirname(__file__), "bonos_data.csv")

    if os.path.exists(out_path):
        df_old = pd.read_csv(out_path)
        df_combined = (
            pd.concat([df_old, df_new])
            .drop_duplicates(subset=["fecha", "ticker"], keep="last")
            .sort_values(["ticker", "fecha"])
            .reset_index(drop=True)
        )
    else:
        df_combined = df_new

    df_combined.to_csv(out_path, index=False)
    print(f"\nGuardados {len(records)} bonos → {out_path}")
    print("=== FIN fetch_bonos.py ===")


if __name__ == "__main__":
    main()
