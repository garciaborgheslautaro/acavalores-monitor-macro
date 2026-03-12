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
 
# ── Variables confirmadas en API v4.0 ────────────────────────────────────────
# ID 1   = Reservas internacionales (USD MM)
# ID 4   = TC Oficial Mayorista COM A3500
# ID 5   = TC Oficial Minorista BNA
# ID 7   = BADLAR bancos privados (% TNA)
# ID 15  = Base Monetaria ($ MM)
# ID 17  = Depositos totales ($ MM)
# ID 18  = Creditos totales ($ MM)
# ID 25  = M2 privado - PM 30 dias - var interanual (%)
# ID 26  = Prestamos al sector privado ($ MM)
# ID 27  = Inflacion mensual IPC (%) — dato mensual
# ID 28  = Inflacion interanual IPC (%) — dato mensual
# ID 29  = REM inflacion esperada 12m mediana (% i.a.) — dato mensual
# ID 44  = TAMAR bancos privados (% TNA)
# ID 78  = Compras netas de divisas BCRA (USD MM)
# ID 108 = Depositos en dolares sector privado (USD MM)
# ID 197 = M2 transaccional sector privado ($ MM)
 
VARIABLES = {
    1:   "reservas",
    4:   "tc_mayorista",
    5:   "tc_minorista",
    7:   "badlar",
    15:  "base_monetaria",
    17:  "depositos",
    18:  "creditos",
    25:  "m2_privado",
    26:  "prestamos_priv",
    27:  "inflacion_mensual",
    28:  "inflacion_interanual",
    29:  "rem_inflacion",
    44:  "tamar",
    78:  "compras_usd_bcra",
    108: "depositos_usd",
    197: "m2_transaccional",
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
    print(f"\n  OK CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("ERROR: No se pudieron obtener datos de ninguna variable")
 
# ── Riesgo País — Ámbito ─────────────────────────────────────────────────────
print("\n  Descargando Riesgo País...")
try:
    HACE_5_ANOS = (datetime.today() - timedelta(days=365*5)).strftime("%Y-%m-%d")
    r_rp = requests.get(
        f"https://mercados.ambito.com/riesgopais/historico-general/{HACE_5_ANOS}/{HOY}",
        headers={"User-Agent": "Mozilla/5.0"}, timeout=20
    )
    data_rp = r_rp.json()
    df_rp = pd.DataFrame(data_rp[1:], columns=["fecha", "riesgo_pais"])
    df_rp["fecha"] = pd.to_datetime(df_rp["fecha"], format="%d-%m-%Y")
    df_rp["riesgo_pais"] = df_rp["riesgo_pais"].str.replace(",", ".").astype(float)
    df_rp = df_rp.drop_duplicates("fecha").sort_values("fecha").reset_index(drop=True)
    df_rp.to_csv("data/riesgo_pais_data.csv", index=False, encoding="utf-8")
    print(f"  OK Riesgo País — {len(df_rp)} registros hasta {df_rp['fecha'].max().strftime('%d/%m/%Y')}")
except Exception as e:
    print(f"  Error Riesgo País: {e}")
 
# ── ITCRM — descarga directa del Excel del BCRA ──────────────────────────────
print("\n  Descargando ITCRM...")
try:
    url_itcrm = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx"
    r_itcrm = requests.get(url_itcrm, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, verify=False)
    with open("data/itcrm_temp.xlsx", "wb") as f:
        f.write(r_itcrm.content)
    df_itcrm = pd.read_excel("data/itcrm_temp.xlsx", header=1)
    df_itcrm.columns = ["fecha"] + [c.strip() for c in df_itcrm.columns[1:]]
    df_itcrm = df_itcrm[["fecha", "ITCRM"]].copy()
    df_itcrm.columns = ["fecha", "itcrm"]
    df_itcrm["fecha"] = pd.to_datetime(df_itcrm["fecha"], errors="coerce")
    df_itcrm["itcrm"] = pd.to_numeric(df_itcrm["itcrm"], errors="coerce")
    df_itcrm = df_itcrm.dropna(subset=["fecha", "itcrm"])
    df_itcrm = df_itcrm.drop_duplicates("fecha").sort_values("fecha").reset_index(drop=True)
    df_itcrm.to_csv("data/itcrm_data.csv", index=False)
    print(f"  OK ITCRM — {len(df_itcrm)} registros hasta {df_itcrm['fecha'].max().strftime('%d/%m/%Y')}")
    import os; os.remove("data/itcrm_temp.xlsx")
except Exception as e:
    print(f"  Error ITCRM: {e}")
 
print("=== FIN fetch_data.py ===")
