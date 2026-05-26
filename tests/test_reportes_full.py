import requests
import sys
import uuid
import os

# Añadir el directorio actual al path para importar el helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_auth_headers

BASE_URL = "http://localhost/api/reportes"

def test_reportes_full():
    print("====================================================")
    print("   TESTING MS-REPORTES (Documentos y Estadísticas)  ")
    print("====================================================\n")

    admin_email = f"admin_{uuid.uuid4().hex[:4]}@buap.mx"
    headers = get_auth_headers(admin_email, "password123", role="Administrador")
    
    if not headers:
        print("Aborting: No headers/token.")
        sys.exit(1)
        
    materia_id = "25303" # NRC sembrado
    success = True

    # 1. Descargar Reporte PDF (Demo)
    print(f"[1] Descargando reporte PDF de calificaciones (materia {materia_id})...", end=" ")
    res = requests.get(f"{BASE_URL}/reportes/calificaciones/{materia_id}?formato=pdf", headers=headers)
    if res.status_code == 200 and res.headers.get('Content-Type') == 'application/pdf':
        print("OK (Recibido PDF)")
    else:
        print(f"FAILED ({res.status_code})")
        success = False

    # 2. Descargar Reporte Excel (Demo)
    print(f"[2] Descargando reporte Excel de asistencias (materia {materia_id})...", end=" ")
    res = requests.get(f"{BASE_URL}/reportes/asistencias/{materia_id}?formato=xls", headers=headers)
    if res.status_code == 200:
        print("OK (Recibido Excel)")
    else:
        print(f"FAILED ({res.status_code})")
        success = False

    # 3. Consultar Historial de Reportes
    print("[3] Consultando historial de reportes generados...", end=" ")
    res = requests.get(f"{BASE_URL}/reportes/historial", headers=headers)
    if res.status_code == 200:
        print(f"OK ({res.json()['data']['total']} reportes en historial)")
    else:
        print(f"FAILED ({res.status_code})")
        success = False

    # 4. Registrar Estadísticas (Admin only)
    print("[4] Registrando estadísticas de una materia...", end=" ")
    payload = {
        "materia_id": "MAT-999",
        "materia_nombre": "Test Materia",
        "materia_nrc": "99999",
        "periodo_nombre": "2026 Primavera",
        "docente_id": "123",
        "total_alumnos": 30,
        "promedio_general": 8.5,
        "porcentaje_aprobados": 83.3
    }
    res = requests.post(f"{BASE_URL}/estadisticas/registrar", json=payload, headers=headers)
    if res.status_code == 201:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        success = False

    print("\n====================================================")
    print("   PRUEBAS DE MS-REPORTES FINALIZADAS               ")
    print("====================================================")
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    test_reportes_full()
