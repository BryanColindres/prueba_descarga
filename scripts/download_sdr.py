"""
Descarga el archivo EXACTO de valoración del SDR desde el FMI.

Este script está pensado para correr en GitHub Actions (o cualquier
entorno con salida libre a internet), NO en la red corporativa del
usuario -- así se evita el proxy restrictivo por completo.

Guarda:
  - data/sdr_valuation_history.xls  (archivo crudo tal como lo entrega el FMI)
  - data/sdr_valuation_history.csv  (versión parseada a CSV, si el formato lo permite)
"""

import csv
import io
from pathlib import Path

import requests

URL_PAGINA = "https://www.imf.org/external/np/fin/data/rms_sdrv.aspx"
URL_DESCARGA = f"{URL_PAGINA}?tsvflag=Y"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def download() -> bytes:
    session = requests.Session()
    session.headers.update(HEADERS)

    # 1. Visita la página normal primero para que el servidor entregue
    #    cookies de sesión válidas (igual que hace un navegador real).
    pagina = session.get(URL_PAGINA, timeout=30)
    pagina.raise_for_status()

    # 2. Ahora sí pide el archivo, con Referer apuntando a la página que
    #    "acabamos de visitar" y con las cookies ya en la sesión.
    session.headers.update({"Referer": URL_PAGINA})
    resp = session.get(URL_DESCARGA, timeout=30)
    resp.raise_for_status()
    return resp.content


def try_parse_to_csv(raw: bytes) -> str | None:
    """
    El archivo que entrega tsvflag=Y suele ser texto delimitado por
    tabulaciones a pesar del nombre ".xls". Intentamos parsearlo; si el
    formato no es el esperado, devolvemos None y solo se guarda el crudo.
    """
    try:
        text = raw.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(text), delimiter="\t")
        rows = list(reader)
        if not rows or len(rows[0]) < 2:
            return None

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output.getvalue()
    except Exception:
        return None


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    raw = download()
    (DATA_DIR / "sdr_valuation_history.xls").write_bytes(raw)
    print(f"Guardado: {DATA_DIR / 'sdr_valuation_history.xls'} ({len(raw)} bytes)")

    csv_text = try_parse_to_csv(raw)
    if csv_text:
        (DATA_DIR / "sdr_valuation_history.csv").write_text(csv_text, encoding="utf-8")
        print(f"Guardado: {DATA_DIR / 'sdr_valuation_history.csv'}")
    else:
        print("No se pudo parsear a CSV automáticamente; revisa el archivo crudo.")


if __name__ == "__main__":
    main()
