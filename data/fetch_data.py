import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings("ignore")

HOY = datetime.today().strftime("%Y-%m-%d")
HACE_1_ANO = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

# Usamos estadisticasbcra.com — API alternativa sin límite de fechas ni paginación
BASE = "https://api.estadisticasbcra.com"

# Esta API requiere token gratuito — usamos los endpoints que NO lo requieren
# Para la API oficial del BCRA usamos paginación con limit/offset
BASE_BCRA = "https://api.bcra.gob.ar/estadisticas/v2.0"
HEADERS_BCRA = {"Accept": "application/json"}

VARIABLES_BCRA = {
    "reservas":       1,
    "base_monetaria": 15,
    "tc_oficial":     4,
    "depositos":      17,
    "creditos":       18,
    "tasa_politica":  6,
    "m2_privado":     25,
}

os.makedirs("data", exist_ok=True)

def fetch_variable_paginada(nombre, id_var, desde, hasta, limit=1000):
    """Descarga una variable del BCRA con paginación automática."""
    todos = []
    offset = 0
    while True:
        url = f"{BASE_BCRA}/datosvariable/{id_var}/{desde}/{hasta}?limit={limit}&offset={offset}"
        try:
            r = requests.get(url, headers=HEADERS_BCRA, timeout=20, verify=False)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} en {nombre} (offset={offset})")
                break
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            todos.extend(results)
            # Si devolvió menos que el límite, ya terminamos
            if len(results) < limit:
                break
            offset += limit
        except Exception as e:
            print(f"  Error en {nombre}: {e}")
            break

    if not todos:
        return None

    df = pd.DataFrame(todos)
    # La API puede devolver 'fecha'/'valor' o 'd'/'v' según versión
    if "fecha" in df.columns and "valor" in df.columns:
        df = df[["fecha", "valor"]]
    elif "d" in df.columns and "v" in df.columns:
        df = df[["d", "v"]]
        df.columns = ["fecha", "valor"]
    else:
        print(f"  Columnas inesperadas en {nombre}: {df.columns.tolist()}")
        return None

    df.columns = ["fecha", nombre]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.drop_duplicates(subset="fecha").sort_values("fecha")
    return df

# Descarga con dos tramos de 1 año para mayor cobertura histórica
TRAMOS = [
    ((datetime.today() - timedelta(days=730)).strftime("%Y-%m-%d"),
     (datetime.today() - timedelta(days=366)).strftime("%Y-%m-%d")),
    ((datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d"),
     HOY),
]

df_final = None
for nombre, id_var in VARIABLES_BCRA.items():
    partes = []
    for desde, hasta in TRAMOS:
        df_tramo = fetch_variable_paginada(nombre, id_var, desde, hasta)
        if df_tramo is not None:
            partes.append(df_tramo)

    if partes:
        df_var = pd.concat(partes).drop_duplicates(subset="fecha").sort_values("fecha")
        df_final = df_var if df_final is None else pd.merge(df_final, df_var, on="fecha", how="outer")
        print(f"✅ {nombre} — {len(df_var)} registros")
    else:
        print(f"❌ {nombre} — sin datos")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.to_csv("data/bcra_data.csv", index=False)
    print(f"\n✅ CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("❌ No se pudieron obtener datos de ninguna variable")
