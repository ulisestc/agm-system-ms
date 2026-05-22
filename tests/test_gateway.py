import requests
import sys

GATEWAY_URL = "http://localhost:80/api"

SERVICES_PATHS = {
    "Auth": "/auth/",
    "Periodos": "/periodos/",
    "Docentes": "/docentes/",
    "Asistencias": "/asistencias/",
    "Reportes": "/reportes/",
}

def test_gateway():
    print("====================================================")
    print("      AGM System - API GATEWAY ROUTING TEST        ")
    print("====================================================\n")

    results = {}
    for name, path in SERVICES_PATHS.items():
        url = f"{GATEWAY_URL}{path}"
        print(f"Probando ruta Gateway para {name}: {url}...", end=" ")
        try:
            # Intentamos un GET a la raíz del servicio a través del gateway
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                # 200, 404, 401 son "éxitos" de ruteo (el gateway llegó al MS)
                # 502, 504 indican que el gateway no pudo conectar con el MS
                print(f"OK (Status: {response.status_code})")
                results[name] = True
            else:
                print(f"ERROR (Status: {response.status_code})")
                results[name] = False
        except Exception as e:
            print(f"FALLO DE CONEXIÓN: {e}")
            results[name] = False

    print("\n" + "="*45)
    print(f"{'Servicio':<20} | {'Gateway Routing'}")
    print("-"*45)
    for name, res in results.items():
        status = "FUNCIONA" if res else "FALLA (502/Timeout)"
        print(f"{name:<20} | {status}")
    print("="*45)

    if not all(results.values()):
        print("\n⚠️ Se detectaron fallos en el ruteo del Gateway.")
        print("Causa probable: Puertos incorrectos en gateway/nginx.conf")
        # No salimos con error para permitir que el usuario vea el reporte completo
    else:
        print("\n✅ El Gateway está ruteando correctamente a todos los servicios.")

if __name__ == "__main__":
    test_gateway()
