import requests
import warnings
warnings.filterwarnings("ignore")

tests = [
    "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/1/2025-01-01/2026-03-11",
    "https://api.bcra.gob.ar/estadisticas/v3.0/datosvariable/1/2025-01-01/2026-03-11",
    "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/1?desde=2025-01-01&hasta=2026-03-11",
    "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables",
    "https://api.bcra.gob.ar/estadisticas/v3.0/principalesvariables",
]

for url in tests:
    try:
        r = requests.get(url, timeout=15, verify=False,
                        headers={"Accept": "application/json"})
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        print(f"Status: {r.status_code}")
        print(f"Respuesta: {r.text[:500]}")
    except Exception as e:
        print(f"\nURL: {url}")
        print(f"Excepción: {e}")
