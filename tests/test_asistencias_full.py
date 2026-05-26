import requests
import uuid
import time
import sys
import os

# Añadir el directorio actual al path para importar el helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_auth_headers, get_token

BASE_URL = "http://localhost/api/asistencias"

def test_ms_asistencias_full_flow():
    print("====================================================")
    print("   TESTING MS-ASISTENCIAS (Flow Completo)           ")
    print("====================================================\n")

    materia_id = "25303" # NRC de la materia de prueba sembrada
    docente_id = "1"
    alumno_id = "1" # ID del alumno sembrado
    
    # Headers para Docente
    headers_docente = get_auth_headers("docente@buap.mx", "password123")
    # Headers para Alumno
    headers_alumno = get_auth_headers("alumno@buap.mx", "password123")

    if not headers_docente or not headers_alumno:
        print("FAILED: No se pudieron obtener tokens")
        return

    success = True

    # 1. Iniciar Sesión (Docente)
    print(f"[1] Iniciando sesión para materia {materia_id} (Docente)...", end=" ")
    # Nos aseguramos que no haya una sesión previa abierta (limpieza)
    requests.delete(f"{BASE_URL}/sesiones/{materia_id}/cerrar", headers=headers_docente)

    payload = {
        "materia_id": materia_id,
        "docente_id": docente_id
    }
    res = requests.post(f"{BASE_URL}/sesiones/iniciar", json=payload, headers=headers_docente)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        return

    # 2. Generar Token QR (Alumno)
    print(f"[2] Generando token QR para alumno {alumno_id}...", end=" ")
    payload_qr = {
        "alumno_id": alumno_id,
        "materia_id": materia_id
    }
    res = requests.post(f"{BASE_URL}/qr/generar", json=payload_qr, headers=headers_alumno)
    if res.status_code == 200:
        token_qr = res.json()["data"]["token_qr"]
        print(f"OK (Token: {token_qr[:8]}...)")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        return

    # 3. Registrar asistencia (Alumno/Docente)
    print(f"[3] Registrando asistencia con el QR generado...", end=" ")
    payload_asistencia = {
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "token_qr": token_qr
    }
    res = requests.post(f"{BASE_URL}/asistencias/registrar", json=payload_asistencia, headers=headers_alumno)
    if res.status_code == 200:
        print(f"OK (Estado: {res.json()['data']['estado']})")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        success = False

    # 4. Anti-replay (usar el mismo token de nuevo)
    print("[4] Probando Anti-replay con el mismo token...", end=" ")
    res = requests.post(f"{BASE_URL}/asistencias/registrar", json=payload_asistencia, headers=headers_alumno)
    if res.status_code in [400, 404]: # 404 porque el token se borró de redis tras el primer uso
        print("OK (Bloqueado correctamente)")
    else:
        print(f"FAILED (Se permitió re-uso de token: {res.status_code})")
        success = False

    # 5. Consultar asistencias de hoy (Docente)
    print("[5] Consultando asistencias de hoy (Docente)...", end=" ")
    res = requests.get(f"{BASE_URL}/asistencias/{materia_id}/hoy", headers=headers_docente)
    if res.status_code == 200:
        registros = res.json()['data']['registros']
        print(f"OK (Registros encontrados: {len(registros)})")
    else:
        print(f"FAILED ({res.status_code})")
        success = False

    # 6. Cerrar sesión (Docente)
    print("[6] Cerrando sesión forzosamente...", end=" ")
    res = requests.delete(f"{BASE_URL}/sesiones/{materia_id}/cerrar", headers=headers_docente)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        success = False

    print("\n====================================================")
    print("   PRUEBAS DE MS-ASISTENCIAS FINALIZADAS            ")
    print("====================================================")
    
    if not success:
        sys.exit(1)

    print("\n====================================================")
    print("   PRUEBAS DE MS-ASISTENCIAS FINALIZADAS            ")
    print("====================================================")
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    test_ms_asistencias_full_flow()
