import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# La API del BCRA acepta máximo 1 año por consulta — hacemos 2 tramos y los unimos
HOY = datetime.today().strftime("%Y-%m-%d")
HACE_1_ANO = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
HACE_2_ANOS = (datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d")

BASE_BCRA = "https://api.bcra.gob.ar/estadisticas/v2.0"
HEADERS = {"Accept": "application/json"}

VARIABLES = {
    "reservas":       1,
    "base_monetaria": 15,
    "tc_oficial":     4,
    "depositos":      17,
    "creditos":       18,
    "tasa_politica":  6,
    "m2_privado":     25,
}

os.makedirs("data", exist_ok=True)

def fetch_tramo(id_var, desde, hasta):
    url = f"{BASE_BCRA}/datosvariable/{id_var}/{desde}/{hasta}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"  Error tramo {desde}/{hasta}: {e}")
        return []

def fetch_variable(nombre, id_var):
    try:
        # Tramo 1: hace 2 años → hace 1 año
        datos1 = fetch_tramo(id_var, HACE_2_ANOS, HACE_1_ANO)
        # Tramo 2: hace 1 año → hoy
        datos2 = fetch_tramo(id_var, HACE_1_ANO, HOY)
        datos = datos1 + datos2
        if not datos:
            return None
        df = pd.DataFrame(datos)[["fecha", "valor"]]
        df.columns = ["fecha", nombre]
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.drop_duplicates(subset="fecha")
        return df
    except Exception as e:
        print(f"Error en {nombre}: {e}")
        return None

df_final = None
for nombre, id_var in VARIABLES.items():
    df = fetch_variable(nombre, id_var)
    if df is not None:
        df_final = df if df_final is None else pd.merge(df_final, df, on="fecha", how="outer")
        print(f"✅ {nombre} — {len(df)} registros")
    else:
        print(f"❌ {nombre} — sin datos")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.to_csv("data/bcra_data.csv", index=False)
    print(f"\n✅ Archivo guardado: {len(df_final)} registros hasta {HOY}")
else:
    print("❌ No se pudieron obtener datos")
