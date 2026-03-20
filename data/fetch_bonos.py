#!/usr/bin/env python3
"""fetch_bonos.py — Precios de bonos soberanos argentinos desde Open BYMA Data (20 min delay).

No requiere token: inicializa sesión con cookies del dashboard, como hace PyOBD.
Ref: https://github.com/franco-lamas/PyOBD
"""

import json
import requests
import pandas as pd
from datetime import datetime
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TICKERS_OBJETIVO = {
    "GD29", "GD30", "GD35", "GD38", "GD41", "GD46",
    "AL29", "AL30", "AL35", "AE38", "AL41", "AL46",
}

BASE_URL = "https://open.bymadata.com.ar"
DASHBOARD_URL = f"{BASE_URL}/#/dashboard"
API_URL = f"{BASE_URL}/vanoms-be-core/rest/api/bymadata/free/public-bonds"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-platform": '"Windows"',
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
}


def get_session():
    """Inicializa sesión con cookies del dashboard (sin token)."""
    session = requests.Session()
    session.verify = False
    try:
        resp = session.get(DASHBOARD_URL, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)
        print(f"[fetch_bonos] Dashboard status={resp.status_code} cookies={list(session.cookies.keys())}")
    except Exception as e:
        print(f"[fetch_bonos] Advertencia al inicializar sesión: {e}")
    return session


def fetch_bonos():
    session = get_session()
    payload = json.dumps({"T2": True, "T1": False, "T0": False, "Content-Type": "application/json"})
    try:
        r = session.post(API_URL, data=payload, headers=HEADERS, timeout=20)
        print(f"[fetch_bonos] API status={r.status_code} len={len(r.text)}")
        print(f"[fetch_bonos] API preview: {r.text[:300]!r}")
        r.raise_for_status()
        body = r.json()
        if isinstance(body, list):
            return body
        return body.get("data", [])
    except Exception as e:
        print(f"[fetch_bonos] Error: {e}")
        return None


def parse_precio(item):
    for campo in ("trade_c", "ultimoPrecio", "c", "px_bid", "px_ask", "price"):
        v = item.get(campo)
        if v is not None:
            try:
                f = float(v)
                if f > 0:
                    return f
            except (TypeError, ValueError):
                pass
    return None


def parse_variacion(item):
    for campo in ("c_pct_change", "variacion", "var_pct", "change_pct"):
        v = item.get(campo)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def main():
    import sys
    print("=== INICIO fetch_bonos.py ===")
    items = fetch_bonos()

    if items is None:
        print("ERROR: No se pudo conectar a Open BYMA Data.")
        sys.exit(1)

    if not items:
        print("ERROR: Respuesta vacía de Open BYMA Data.")
        sys.exit(1)

    print(f"Total instrumentos recibidos: {len(items)}")
    print(f"Claves ejemplo: {list(items[0].keys())[:12]}")

    fecha_hoy = datetime.today().strftime("%Y-%m-%d")
    records = []

    for item in items:
        symbol = str(
            item.get("symbol") or item.get("descripcionTitulo") or item.get("denominacion") or ""
        ).strip().upper()

        ticker = None
        for t in TICKERS_OBJETIVO:
            if symbol == t or symbol.startswith(t + " ") or symbol.startswith(t + "-") or symbol.startswith(t + "/"):
                ticker = t
                break

        if ticker is None:
            continue

        precio = parse_precio(item)
        variacion = parse_variacion(item)
        volumen = item.get("tv") or item.get("montoOperado") or item.get("volume")

        if precio is not None:
            records.append({
                "fecha": fecha_hoy,
                "ticker": ticker,
                "precio": precio,
                "variacion_pct": variacion,
                "volumen": float(volumen) if volumen is not None else None,
            })

    if not records:
        print("ADVERTENCIA: No se encontraron bonos objetivo.")
        print(f"Symbols encontrados (muestra): {[str(i.get('symbol', ''))[:15] for i in items[:25]]}")
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
    print(f"\nGuardados {len(records)} bonos en {out_path}")
    for rec in sorted(records, key=lambda x: x["ticker"]):
        var_str = f"{rec['variacion_pct']:+.2f}%" if rec["variacion_pct"] is not None else "N/A"
        print(f"  {rec['ticker']:6s}: {rec['precio']:.2f}  ({var_str})")

    print("=== FIN fetch_bonos.py ===")


if __name__ == "__main__":
    main()
