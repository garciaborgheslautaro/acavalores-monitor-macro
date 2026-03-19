import requests
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

print("=== INICIO fetch_actividad.py ===")

os.makedirs("data", exist_ok=True)

BASE    = "https://apis.datos.gob.ar/series/api/series/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
HOY     = datetime.today().strftime("%Y-%m-%d")
HACE_5  = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")
CSV     = "data/actividad_data.csv"

# ── Series confirmadas — datos.gob.ar ────────────────────────────────────────
# 143.3_NO_PR_2004_A_21         = EMAE serie original (Base 2004)
# 143.3_NO_PR_2004_A_31         = EMAE desestacionalizado (Base 2004) — ~155 puntos
# 453.1_SERIE_ORIGNAL_0_0_14_46= IPI industria manufacturera (nivel general)
# 77.3_IET_0_A_25              = Exportaciones totales FOB (USD MM)
# 78.3_IIT_0_A_25              = Importaciones totales FOB (USD MM)
# 452.3_RESULTADO_RIO_0_M_18_54= Resultado fiscal primario ($ MM)
# 378.9_RESULTADO_017_0_M_18_90= Resultado fiscal financiero ($ MM)
# 172.3_TL_RECAION_M_0_0_17   = Recaudación total AFIP/ARCA ($ MM)
# 455.1_SALON_VENTTAS_0_M_12_82= Ventas supermercados — salón ($ MM)
# 38.3_ANIU_1994_M_27           = Patentamiento utilitarios (unidades reales)
# 158.1_REPTE_0_0_5            = RIPTE nominal ($ por trabajador)

SERIES = {
    "143.3_NO_PR_2004_A_21":         "emae",
    "143.3_NO_PR_2004_A_31":         "emae_desest",
    "453.1_SERIE_ORIGNAL_0_0_14_46": "ipi",
    "77.3_IET_0_A_25":               "exportaciones",
    "78.3_IIT_0_A_25":               "importaciones",
    "452.3_RESULTADO_RIO_0_M_18_54": "resultado_primario",
    "378.9_RESULTADO_017_0_M_18_90": "resultado_financiero",
    "172.3_TL_RECAION_M_0_0_17":     "recaudacion",
    "455.1_SALON_VENTTAS_0_M_12_82": "ventas_supermercados",
    "38.3_ANIU_1994_M_27":           "patentamiento",
    "158.1_REPTE_0_0_5":             "ripte",
}

def fetch_serie(serie_id, nombre):
    try:
        r = requests.get(BASE, headers=HEADERS, params={
            "ids":        serie_id,
            "start_date": HACE_5,
            "end_date":   HOY,
            "limit":      1000,
            "sort":       "asc",
            "format":     "json",
        }, timeout=15)
        data = r.json()
        filas = data.get("data", [])
        if not filas:
            print(f"  Sin datos — {nombre} ({serie_id})")
            return None
        df = pd.DataFrame(filas, columns=["fecha", nombre])
        df["fecha"] = pd.to_datetime(df["fecha"])
        ultimo = df.dropna(subset=[nombre]).iloc[-1]
        print(f"  OK {nombre} — {len(df)} registros — último: {ultimo['fecha'].date()} → {ultimo[nombre]:,.1f}")
        return df
    except Exception as e:
        print(f"  Error en {nombre} ({serie_id}): {e}")
        return None

# Fetch todas las series
df_final = None
for serie_id, nombre in SERIES.items():
    df = fetch_serie(serie_id, nombre)
    if df is not None:
        if df_final is None:
            df_final = df
        else:
            df_final = pd.merge(df_final, df, on="fecha", how="outer")

if df_final is not None:
    # Calcular balanza comercial
    if "exportaciones" in df_final.columns and "importaciones" in df_final.columns:
        df_final["balanza_comercial"] = df_final["exportaciones"] - df_final["importaciones"]
        print("  OK balanza_comercial calculada")

    # Calcular ventas supermercados en miles de millones para legibilidad
    if "ventas_supermercados" in df_final.columns:
        df_final["ventas_supermercados"] = df_final["ventas_supermercados"] / 1_000

    # Calcular recaudacion en miles de millones
    if "recaudacion" in df_final.columns:
        df_final["recaudacion"] = df_final["recaudacion"] / 1_000

    # Calcular resultado primario/financiero en miles de millones
    for col in ["resultado_primario", "resultado_financiero"]:
        if col in df_final.columns:
            df_final[col] = df_final[col] / 1_000

    df_final.sort_values("fecha", inplace=True)
    df_final.reset_index(drop=True, inplace=True)

    # Merge con CSV existente si existe
    if os.path.exists(CSV):
        df_hist = pd.read_csv(CSV, parse_dates=["fecha"])
        df_final = pd.concat([df_hist, df_final]).drop_duplicates("fecha", keep="last")
        df_final.sort_values("fecha", inplace=True)
        df_final.reset_index(drop=True, inplace=True)

    df_final.to_csv(CSV, index=False)
    print(f"\n  OK CSV guardado: {len(df_final)} filas hasta {df_final['fecha'].max().date()}")
    print(df_final.tail(3).to_string())
else:
    print("ERROR: No se pudieron obtener datos")

print("=== FIN fetch_actividad.py ===")
