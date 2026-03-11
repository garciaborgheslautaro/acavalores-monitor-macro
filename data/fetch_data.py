import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

print("=== INICIO ===")

BASE = "https://api.bcra.gob.ar/estadisticas/v4.0"
HEADERS = {"Accept": "application/json"}
HOY = datetime.today().strftime("%Y-%m-%d")
HACE_1_ANO = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

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
    url = f"{BASE}/Monetarias/{id_var}?desde={HACE_1_ANO}&hasta={HOY}"
    print(f"Llamando: {url}")
    r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
    print(f"Status {nombre}: {r.status_code}")
    print(f"Body: {r.text[:300]}")
    if r.status_code != 200:
        return None
    results = r.json().get("results", [])
    if not results:
        return None
    df = pd.DataFrame(results)
    print(f"Columnas: {df.columns.tolist()}")
    col_fecha = next((c for c in df.columns if "echa" in c or c == "d"), None)
    col_valor = next((c for c in df.columns if "alor" in c or c == "v"), None)
    if not col_fecha or not col_valor:
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
    print(f"✅ CSV guardado: {len(df_final)} filas")
else:
    print("❌ No se pudieron obtener datos")

print("=== FIN ===")
```

Antes de hacer commit confirmame que el archivo empieza con:
```
import requests
import pandas as pd
import os
