import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

print("=== INICIO fetch_data.py ===")

BASE = "https://api.bcra.gob.ar/estadisticas/v4.0"
HEADERS = {"Accept": "application/json"}
HOY = datetime.today().strftime("%Y-%m-%d")
HACE_1_ANO = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

os.makedirs("data", exist_ok=True)

# ── Variables con IDs conocidos y confirmados ────────────────────────────────
# ID 1  = Reservas internacionales (USD MM)
# ID 4  = TC Oficial Mayorista COM A3500
# ID 5  = TC Oficial Minorista BNA
# ID 15 = Base Monetaria ($ MM)
# ID 17 = Depositos totales ($ MM)
# ID 18 = Creditos totales ($ MM)
# ID 25 = M2 privado - PM 30 dias - var interanual (%)
# ID 27 = BADLAR bancos privados (% TNA)
# ID 28 = TAMAR (% TNA)
# ID 30 = Depositos en dolares sector privado (USD MM)
# ID 31 = Inflacion mensual IPC (%)
# ID 32 = Inflacion interanual IPC (%)
# ID 45 = REM - Inflacion esperada proximos 12 meses mediana (% i.a.)

VARIABLES = {
    1:  "reservas",
    4:  "tc_mayorista",
    5:  "tc_minorista",
    15: "base_monetaria",
    17: "depositos",
    18: "creditos",
    25: "m2_privado",
    7: "badlar",
    44: "tamar",
    30: "depositos_usd",
    31: "inflacion_mensual",
    32: "inflacion_interanual",
    45: "rem_inflacion",
}

def fetch_variable(id_var, nombre):
    url = f"{BASE}/Monetarias/{id_var}?desde={HACE_1_ANO}&hasta={HOY}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} — {nombre} (id={id_var})")
            return None
        data = r.json()
        resultados = data.get("results", [])
        if not resultados:
            print(f"  Sin resultados — {nombre}")
            return None
        # La v4.0 devuelve results como lista con un objeto que tiene "detalle"
        if isinstance(resultados[0], dict) and "detalle" in resultados[0]:
            detalle = resultados[0]["detalle"]
        else:
            detalle = resultados
        df = pd.DataFrame(detalle)
        if "fecha" not in df.columns or "valor" not in df.columns:
            print(f"  Columnas inesperadas en {nombre}: {df.columns.tolist()}")
            return None
        df = df[["fecha", "valor"]].copy()
        df.columns = ["fecha", nombre]
        df["fecha"] = pd.to_datetime(df["fecha"])
        df = df.drop_duplicates("fecha").sort_values("fecha")
        print(f"  OK {nombre} — {len(df)} registros")
        return df
    except Exception as e:
        print(f"  Excepcion en {nombre}: {e}")
        return None

df_final = None
for id_var, nombre in VARIABLES.items():
    df = fetch_variable(id_var, nombre)
    if df is not None:
        if df_final is None:
            df_final = df
        else:
            df_final = pd.merge(df_final, df, on="fecha", how="outer")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.reset_index(drop=True, inplace=True)
    df_final.to_csv("data/bcra_data.csv", index=False)
    print(f"\n OK CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("ERROR: No se pudieron obtener datos de ninguna variable")

print("=== FIN fetch_data.py ===")
