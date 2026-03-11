import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

HOY = datetime.today().strftime("%Y-%m-%d")
HACE_2_ANOS = (datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d")

# API oficial BCRA v4.0 — sin token, pública y gratuita
BASE = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"
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
        url = f"{BASE}/{id_var}?desde={HACE_2_ANOS}&hasta={HOY}&limit={limit}&offset={offset}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            print(f"  [{nombre}] HTTP {r.status_code} — {url}")
            if r.status_code != 200:
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
    print(f"  Columnas: {df.columns.tolist()} | Primeras filas: {df.head(2).to_dict()}")

    # Normalizar columnas según lo que devuelva la API
    col_fecha = next((c for c in df.columns if "fecha" in c.lower() or c == "d"), None)
    col_valor = next((c for c in df.columns if "valor" in c.lower() or c == "v"), None)

    if not col_fecha or not col_valor:
        print(f"  No se encontraron columnas fecha/valor en {nombre}")
        return None

    df = df[[col_fecha, col_valor]].copy()
    df.columns = ["fecha", nombre]
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
