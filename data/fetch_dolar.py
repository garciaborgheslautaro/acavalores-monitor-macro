import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime

print("=== INICIO fetch_dolar.py ===")

os.makedirs("data", exist_ok=True)

HOY = datetime.today().strftime("%Y-%m-%d")
CSV = "data/dolar_data.csv"

def fetch_dolarapi(casa, nombre):
    url = f"https://dolarapi.com/v1/dolares/{casa}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        d = r.json()
        valor = (d["compra"] + d["venta"]) / 2
        print(f"  OK {nombre} — {valor:.2f}")
        return valor
    except Exception as e:
        print(f"  Error en {nombre}: {e}")
        return None

# Fetch valores del dia
mep = fetch_dolarapi("bolsa", "mep")
ccl = fetch_dolarapi("contadoconliqui", "ccl")

if mep is None and ccl is None:
    print("  Sin datos nuevos, no se actualiza el CSV")
else:
    fila_nueva = {"fecha": HOY, "mep": mep, "ccl": ccl}
    df_nuevo = pd.DataFrame([fila_nueva])
    df_nuevo["fecha"] = pd.to_datetime(df_nuevo["fecha"])

    if os.path.exists(CSV):
        df_hist = pd.read_csv(CSV, parse_dates=["fecha"])
        df_final = pd.concat([df_hist, df_nuevo]).drop_duplicates("fecha", keep="last")
    else:
        df_final = df_nuevo

    df_final.sort_values("fecha", inplace=True)
    df_final.reset_index(drop=True, inplace=True)
    df_final.to_csv(CSV, index=False)
    print(f"\n  OK CSV actualizado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())

print("=== FIN fetch_dolar.py ===")
