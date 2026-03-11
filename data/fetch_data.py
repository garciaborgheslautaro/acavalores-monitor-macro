import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

HOY = datetime.today().strftime("%Y-%m-%d")
HACE_2_ANOS = (datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d")

# API oficial BCRA v4.0 — sin token, sin registro
BASE = "https://api.bcra.gob.ar/estadisticas/v4.0"
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

def fetch_variable(nombre, id_var):
    todos = []
    offset = 0
    limit = 3000
    while True:
        url = f"{BASE}/datosvariable/{id_var}/{HACE_2_ANOS}/{HOY}?limit={limit}&offset={offset}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} — {nombre}")
                break
            results = r.json().get("results", [])
            if not results:
                break
            todos.extend(results)
            if len(results) < limit:
                break
            offset += limit
        except Exception as e:
            print(f"  Error {nombre}: {e}")
            break

    if not todos:
        return None

    df = pd.DataFrame(todos)
    # Normalizar nombres de columnas según versión de la API
    if "fecha" in df.columns:
        df = df.rename(columns={"valor": nombre})
        df = df[["fecha", nombre]]
    elif "d" in df.columns:
        df = df.rename(columns={"d": "fecha", "v": nombre})
        df = df[["fecha", nombre]]
    else:
        print(f"  Columnas inesperadas: {df.columns.tolist()}")
        return None

    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.drop_duplicates("fecha").sort_values("fecha")

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
    print(f"\n✅ CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("❌ No se pudieron obtener datos")
