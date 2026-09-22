"""
Descarga la valoración del SDR ya actualizada desde TU repositorio de
GitHub (no desde el FMI directamente) -- esto corre en tu red corporativa
sin pasar por el proxy que bloquea imf.org.
"""

import requests

USUARIO = "BryanColindres"
REPO = "prueba_descarga"
RAMA = "main"  # o "master", según cómo se llame tu rama principal

RAW_BASE = f"https://raw.githubusercontent.com/{USUARIO}/{REPO}/{RAMA}/data"


def get_sdr_csv() -> str:
    url = f"{RAW_BASE}/sdr_valuation_history.csv"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def get_sdr_raw_bytes() -> bytes:
    url = f"{RAW_BASE}/sdr_valuation_history.xls"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


if __name__ == "__main__":
    texto_csv = get_sdr_csv()
    print(texto_csv[:2000])  # muestra las primeras líneas

    with open("sdr_valuation_history.csv", "w", encoding="utf-8") as f:
        f.write(texto_csv)
    print("\nGuardado localmente como sdr_valuation_history.csv")
