import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
HOY = datetime.today().strftime("%Y-%m-%d")

# API alternativa — sin autenticación, sin límites de fecha
BASE = "https://api.estadisticasbcra.com"

ENDPOINTS = {
    "reservas":              "/reservas",
    "base_monetaria":        "/base",
    "tc_oficial":            "/usd_of",
    "tc_minorista":          "/usd_of_minorista",
    "depositos":             "/depositos",
    "prestamos":             "/prestamos",
    "plazo_fijo":            "/plazo_fijo",
    "cuentas_corrientes":    "/cuentas_corrientes",
    "cajas_ahorro":          "/cajas_ahorro",
    "tasa_depositos_30d":    "/tasa_depositos_30_dias",
    "tasa_prestamos_pers":   "/tasa_prestamos_personales",
    "tasa_adelantos_cc":     "/tasa_adelantos_cuenta_corriente",
}

os.makedirs("data", exist_ok=True)

def fetch_serie(nombre, endpoint):
    url = BASE + endpoint
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data)
        df.columns = ["fecha", nombre]
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.drop_duplicates(subset="fecha").sort_values("fecha")
        print(f"✅ {nombre} — {len(df)} registros")
        return df
    except Exception as e:
        print(f"❌ {nombre} — Error: {e}")
        return None

df_final = None
for nombre, endpoint in ENDPOINTS.items():
    df = fetch_serie(nombre, endpoint)
    if df is not None:
        df_final = df if df_final is None else pd.merge(df_final, df, on="fecha", how="outer")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.to_csv("data/bcra_data.csv", index=False)
    print(f"\n✅ CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("❌ No se pudieron obtener datos")
