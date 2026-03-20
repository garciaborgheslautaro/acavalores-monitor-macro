#!/usr/bin/env python3
"""fetch_bonos.py — Obtiene precios de bonos soberanos argentinos desde Open BYMA Data (20 min delay)."""

import re
import requests
import pandas as pd
from datetime import datetime
import os, json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TICKERS_OBJETIVO = {
    "GD29", "GD30", "GD35", "GD38", "GD41", "GD46",
    "AL29", "AL30", "AL35", "AE38", "AL41", "AL46",
}

BASE_URL = "https://open.bymadata.com.ar"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
}


# Token conocido — fallback si no se puede extraer del bundle
_FALLBACK_TOKEN = "dc826d4c2dde7519e882a250359a23a2"


def extract_token_from_bundle(session):
    """Extrae el token estático del bundle JS de Angular."""
    try:
        resp = session.get(BASE_URL, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)
        print(f"[fetch_bonos] HTML status={resp.status_code} len={len(resp.text)}")
        html = resp.text

        # Buscar bundle main.HASH.js — manejar src="/main.js", src="main.js", src="./main.js"
        match = re.search(r'src=["\']([^"\']*main\.[a-f0-9]+\.js)["\']', html)
        if not match:
            print(f"[fetch_bonos] Bundle no encontrado. HTML preview: {html[:300]!r}")
            return None

        bundle_path = match.group(1)
        if bundle_path.startswith("http"):
            bundle_url = bundle_path
        elif bundle_path.startswith("/"):
            bundle_url = BASE_URL + bundle_path
        else:
            bundle_url = f"{BASE_URL}/{bundle_path.lstrip('./')}"

        print(f"[fetch_bonos] Descargando bundle: {bundle_url}")
        js_resp = session.get(bundle_url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=30)
        print(f"[fetch_bonos] Bundle status={js_resp.status_code} len={len(js_resp.text)}")
        js = js_resp.text

        # El token es un string hex de 32 chars — buscar varios patrones posibles
        patterns = [
            r'"Token"\s*,\s*"([0-9a-f]{32})"',
            r"'Token'\s*,\s*'([0-9a-f]{32})'",
            r'Token\s*:\s*"([0-9a-f]{32})"',
            r"Token\s*:\s*'([0-9a-f]{32})'",
            r'[Tt]oken["\':,\s]+([0-9a-f]{32})',
        ]
        for pat in patterns:
            m = re.search(pat, js)
            if m:
                token = m.group(1)
                print(f"[fetch_bonos] Token extraído: {token}")
                return token

        # Debug: mostrar contexto alrededor de "Token" en el JS
        ctx = list(re.finditer(r'.{0,20}[Tt]oken.{0,40}', js))
        for c in ctx[:3]:
            print(f"[fetch_bonos] Contexto Token: {c.group()!r}")
        print("[fetch_bonos] Token no encontrado en bundle, usando fallback.")
    except Exception as e:
        print(f"[fetch_bonos] Error extrayendo token: {e}")
    return None


def get_session():
    """Obtiene una sesión con cookies y el token de autenticación."""
    session = requests.Session()
    session.verify = False
    token = extract_token_from_bundle(session) or _FALLBACK_TOKEN
    print(f"[fetch_bonos] Token a usar: {token}")
    return session, token


def fetch_open_byma():
    url = f"{BASE_URL}/vanoms-be-core/rest/api/bymadata/free/bonosoberanos"
    payload = {"excludeZeroPxAndQty": True, "T2": True, "T1": False, "T0": False}
    session, token = get_session()
    headers = dict(HEADERS)
    if token:
        headers["Token"] = token
    try:
        r = session.post(url, json=payload, headers=headers, timeout=15)
        print(f"[fetch_bonos] API status={r.status_code} len={len(r.text)}")
        print(f"[fetch_bonos] API preview: {r.text[:200]!r}")
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("data", [])
    except Exception as e:
        print(f"[fetch_bonos] Error fetching BYMA: {e}")
        return None


def parse_precio(item):
    for campo in ("trade_c", "ultimoPrecio", "c", "px_bid", "px_ask"):
        v = item.get(campo)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def parse_variacion(item):
    for campo in ("c_pct_change", "variacion", "var_pct"):
        v = item.get(campo)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def main():
    import sys
    print("Fetching sovereign bond prices from Open BYMA Data...")
    items = fetch_open_byma()

    if items is None:
        print("No se pudo obtener datos de BYMA.")
        sys.exit(1)

    if not items:
        print("Respuesta vacía de BYMA.")
        sys.exit(1)

    print(f"Respuesta: {len(items)} instrumentos. Ejemplo de claves: {list(items[0].keys())[:10]}")

    fecha_hoy = datetime.today().strftime("%Y-%m-%d")
    records = []

    for item in items:
        symbol = str(
            item.get("symbol") or item.get("descripcionTitulo") or item.get("denominacion") or ""
        ).strip().upper()

        # Identificar ticker
        ticker = None
        for t in TICKERS_OBJETIVO:
            if symbol == t or symbol.startswith(t + " ") or symbol.startswith(t + "-"):
                ticker = t
                break

        if ticker is None:
            continue

        precio = parse_precio(item)
        variacion = parse_variacion(item)
        volumen = item.get("tv") or item.get("montoOperado")

        if precio is not None and precio > 0:
            records.append({
                "fecha": fecha_hoy,
                "ticker": ticker,
                "precio": precio,
                "variacion_pct": variacion,
                "volumen": float(volumen) if volumen is not None else None,
            })

    if not records:
        print("No se encontraron bonos objetivo en la respuesta.")
        print(f"Symbols encontrados (muestra): {[str(i.get('symbol',''))[:10] for i in items[:20]]}")
        return

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
    print(f"Guardados {len(records)} precios en {out_path}")
    for rec in sorted(records, key=lambda x: x["ticker"]):
        var_str = f"{rec['variacion_pct']:+.2f}%" if rec["variacion_pct"] is not None else "N/A"
        print(f"  {rec['ticker']:6s}: {rec['precio']:.2f}  ({var_str})")


if __name__ == "__main__":
    main()
