import yfinance as yf
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime, timedelta

print("=== INICIO fetch_mercados.py ===")

os.makedirs("data", exist_ok=True)

HOY = datetime.today().strftime("%Y-%m-%d")
HACE_1_ANO = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

TICKERS = {
    "^GSPC":    "sp500",
    "^IXIC":    "nasdaq",
    "BZ=F":     "brent",
    "CL=F":     "wti",
    "GC=F":     "oro",
    "DX-Y.NYB": "dxy",
    "^TNX":     "us10y",
    "EEM":      "eem",
    "EMB":      "emb",
    "ZS=F":     "soja",
    "ZC=F":     "maiz",
    "ZW=F":     "trigo",
    "^MERV":    "merval",
}

def fetch_ticker(ticker, nombre):
    try:
        df = yf.download(ticker, start=HACE_1_ANO, end=HOY, progress=False, auto_adjust=True)
        if df.empty:
            print(f"  Sin datos — {nombre} ({ticker})")
            return None
        df = df[["Close"]].copy()
        df.columns = [nombre]
        df.index.name = "fecha"
        df = df.reset_index()
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)
        print(f"  OK {nombre} ({ticker}) — {len(df)} registros — ultimo: {df.iloc[-1][nombre]:.2f}")
        return df
    except Exception as e:
        print(f"  Excepcion en {nombre} ({ticker}): {e}")
        return None

df_final = None
for ticker, nombre in TICKERS.items():
    df = fetch_ticker(ticker, nombre)
    if df is not None:
        if df_final is None:
            df_final = df
        else:
            df_final = pd.merge(df_final, df, on="fecha", how="outer")

if df_final is not None:
    df_final.sort_values("fecha", inplace=True)
    df_final.reset_index(drop=True, inplace=True)
    df_final.to_csv("data/mercados_data.csv", index=False)
    print(f"\n  OK CSV guardado: {len(df_final)} filas hasta {HOY}")
    print(df_final.tail(3).to_string())
else:
    print("ERROR: No se pudieron obtener datos de ningún ticker")

print("=== FIN fetch_mercados.py ===")
