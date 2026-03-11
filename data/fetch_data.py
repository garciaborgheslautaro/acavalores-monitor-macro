import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# ── Configuración ──────────────────────────────────────────
HOY = datetime.today().strftime("%Y-%m-%d")
HACE_5_ANOS = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")
BASE_BCRA = "https://api.bcra.gob.ar/estadisticas/v2.0"

HEADERS = {"Accept": "application/json"}

VARIABLES = {
    "reservas":         1,   # Reservas internacionales
    "base_monetaria":   15,  # Base monetaria
    "tc_oficial":       4,   # Tipo de cambio oficial (mayorista)
    "depositos":        17,  # Depósitos totales
    "creditos":         18,  # Créditos totales
    "tasa_politica":    6,   # Tasa de política monetaria
    "m2_privado":       25,  # M2 sector privado
}

os.makedirs("data", exist_ok=True)

def fetch_variable(nombre, id_var):
    url = f"{BASE_BCRA}/datosvariable/{id_var}/{HACE_5_ANOS}/{HOY}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        datos = r.json().get("results", [])
        df = pd.DataFrame(datos)[["fecha", "valor"]]
        df.columns = ["fecha", nombre]
        df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except Exception as e:
        print(f"Error en {nombre}: {e}")
        return None

# Descarga y merge de todas las variables
df_final = None
for nombre, id_var in VARIABLES.items():
    df = fetch_variable(nombre, id_var)
    if df is not None:
        df_final = df if df_final is None else pd.merge(df_final, df, on="fecha", how="outer")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.to_csv("data/bcra_data.csv", index=False)
    print(f"✅ Datos guardados: {len(df_final)} registros hasta {HOY}")
else:
    print("❌ No se pudieron obtener datos")
