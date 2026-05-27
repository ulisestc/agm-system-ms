import requests
import sys
import os

BASE_URL = "http://localhost:8003"
NRC_TEST = "50130"

def main():
    print("=== Iniciando Prueba PDF upload ===")

    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"Health Check: {res.json()}")
    except Exception as e:
        print(f"Error conectando al servidor REST: {e}")
        return

    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "alumnos.pdf")
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"\n--- Probando Importación de PDF para NRC {NRC_TEST} ---")
    with open(pdf_path, 'rb') as f:
        files = {"archivo": ("alumnos.pdf", f, "application/pdf")}
        res = requests.post(f"{BASE_URL}/alumnos/importar/{NRC_TEST}", files=files)
        print(f"Status: {res.status_code}")
        print(f"Respuesta: {res.json()}")

    print(f"\n--- Probando Listar Alumnos del NRC {NRC_TEST} ---")
    res = requests.get(f"{BASE_URL}/alumnos/materia/{NRC_TEST}")
    print(f"Status: {res.status_code}")
    alumnos = res.json()
    print(f"Alumnos encontrados: {len(alumnos)}")
    for a in alumnos[:3]:
        print(f" - {a['nombre']} ({a['matricula']})")

if __name__ == "__main__":
    main()
