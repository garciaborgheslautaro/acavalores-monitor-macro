#!/usr/bin/env python3
"""fetch_premarket.py — Datos de mercado para el panel Premarket.

Fuentes:
- yfinance: índices, futuros, commodities, VIX, forex
- Fear & Greed Index API: alternative.me/fng
- BCRA API: dólar oficial
- Ámbito Financiero: dólar CCL/MEP, riesgo país

El resultado se guarda en data/premarket_data.json para ser leído por app.py.
"""

import json
import os
import requests
from datetime import datetime, timedelta

print("=== INICIO fetch_premarket.py ===")
os.makedirs("data", exist_ok=True)

result = {}

# ── Mercados vía yfinance ──────────────────────────────────────────────────────
try:
    import yfinance as yf

    SYMBOLS = {
        # Índices
        "^GSPC":   {"name": "S&P 500",         "type": "index"},
        "^IXIC":   {"name": "NASDAQ",           "type": "index"},
        "^DJI":    {"name": "Dow Jones",        "type": "index"},
        "^MERV":   {"name": "MERVAL",           "type": "index"},
        "^VIX":    {"name": "VIX",              "type": "index"},
        # Futuros EE.UU.
        "ES=F":    {"name": "S&P 500 Fut",      "type": "future"},
        "NQ=F":    {"name": "NASDAQ Fut",       "type": "future"},
        "YM=F":    {"name": "Dow Jones Fut",    "type": "future"},
        # Commodities
        "GC=F":    {"name": "Oro",              "type": "commodity"},
        "CL=F":    {"name": "Petróleo WTI",     "type": "commodity"},
        "BZ=F":    {"name": "Brent",            "type": "commodity"},
        # Forex
        "DX-Y.NYB": {"name": "DXY (Dólar)",    "type": "forex"},
        "EURUSD=X": {"name": "EUR/USD",         "type": "forex"},
        "USDBRL=X": {"name": "USD/BRL",         "type": "forex"},
        # Bonos
        "^TNX":    {"name": "10yr Treasury",    "type": "bond"},
        "^IRX":    {"name": "3m Treasury",      "type": "bond"},
        # ETFs Argentina
        "ARGT":    {"name": "ARGT ETF",         "type": "ar"},
        "GD30=F":  {"name": "GD30 Fut",         "type": "ar"},
    }

    market_data = []
    for symbol, meta in SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d", interval="1d")
            if hist.empty or len(hist) < 1:
                continue
            last_row = hist.iloc[-1]
            prev_row = hist.iloc[-2] if len(hist) >= 2 else None
            price = float(last_row["Close"])
            prev  = float(prev_row["Close"]) if prev_row is not None else None
            chg   = ((price - prev) / prev * 100) if prev else None
            market_data.append({
                "symbol":  symbol,
                "name":    meta["name"],
                "type":    meta["type"],
                "price":   price,
                "prev":    prev,
                "change_pct": chg,
                "date":    last_row.name.strftime("%Y-%m-%d") if hasattr(last_row.name, "strftime") else str(last_row.name)[:10],
            })
        except Exception as e:
            print(f"  ERROR {symbol}: {e}")

    result["market"] = market_data
    print(f"  OK yfinance — {len(market_data)} símbolos")

except ImportError:
    print("  yfinance no instalado — saltando datos de mercado")
    result["market"] = []

# ── Fear & Greed Index ────────────────────────────────────────────────────────
try:
    r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
    fng_data = r.json()
    fng = fng_data["data"][0]
    result["fear_greed"] = {
        "value":       int(fng["value"]),
        "label":       fng["value_classification"],
        "timestamp":   fng["timestamp"],
    }
    print(f"  OK Fear&Greed: {fng['value']} ({fng['value_classification']})")
except Exception as e:
    print(f"  ERROR Fear&Greed: {e}")
    result["fear_greed"] = None

# ── Noticias financieras — RSS feeds ─────────────────────────────────────────
print("\n[Noticias]")

def _parse_rss(url, max_items=8, timeout=15):
    """Parse RSS feed and return list of {title, link, published}."""
    try:
        import xml.etree.ElementTree as ET
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        ns = {"media": "http://search.yahoo.com/mrss/"}
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            # Clean Google News redirect titles (remove source suffix)
            if " - " in title:
                title = title.rsplit(" - ", 1)[0].strip()
            if title and link:
                items.append({"title": title, "link": link, "published": pub})
        return items
    except Exception as e:
        print(f"  ERROR RSS {url[:60]}: {e}")
        return []

NEWS_FEEDS = {
    "mercados_us": (
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^IXIC&region=US&lang=en-US",
        "Mercados EE.UU."
    ),
    "noticias_us": (
        "https://news.google.com/rss/search?q=stock+market+economy&hl=en&gl=US&ceid=US:en",
        "Economía Global"
    ),
    "argentina": (
        "https://news.google.com/rss/search?q=argentina+economia+dolar+mercado&hl=es&gl=AR&ceid=AR:es",
        "Argentina"
    ),
}

news_result = {}
for key, (url, label) in NEWS_FEEDS.items():
    items = _parse_rss(url)
    news_result[key] = {"label": label, "items": items}
    print(f"  {label}: {len(items)} noticias")

result["news"] = news_result

# ── Metadata ──────────────────────────────────────────────────────────────────
result["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
result["updated_date"] = datetime.now().strftime("%Y-%m-%d")

with open("data/premarket_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print(f"\n→ premarket_data.json guardado")
print("=== FIN fetch_premarket.py ===")
