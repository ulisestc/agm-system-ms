import requests
import uuid
import sys
import os

# Añadir el directorio actual al path para importar el helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_auth_headers

BASE_URL = "http://localhost/api/periodos/api"

def test_periodos_materias_full():
    print("====================================================")
    print("   TESTING MS-PERIODOS-MATERIAS (CRUD Académico)    ")
    print("====================================================\n")

    headers = get_auth_headers()
    if not headers:
        print("FAILED: No se pudo obtener token de autenticación")
        return

    # 1. Crear Periodo
    print("[1] Creando periodo...", end=" ")
    periodo_name = f"Verano {uuid.uuid4().hex[:4].upper()}"
    periodo_payload = {
        "nombre": periodo_name,
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-07-30",
        "plan_estudios": "ISC 2026",
        "activo": False
    }
    res = requests.post(f"{BASE_URL}/periodos/", json=periodo_payload, headers=headers)
    if res.status_code == 201:
        periodo_id = res.json()["data"]["id"]
        print(f"OK (ID: {periodo_id})")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        return

    # 2. Activar Periodo
    print(f"[2] Activando periodo {periodo_id}...", end=" ")
    res = requests.post(f"{BASE_URL}/periodos/{periodo_id}/activar/", headers=headers)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")

    # 3. Consultar Periodo Activo
    print("[3] Consultando periodo activo...", end=" ")
    res = requests.get(f"{BASE_URL}/periodos/activo/", headers=headers)
    if res.status_code == 200:
        print(f"OK (Nombre: {res.json()['data']['nombre']})")
    else:
        print(f"FAILED ({res.status_code})")

    # 4. Crear Materia
    print("[4] Creando materia vinculada...", end=" ")
    nrc = f"NRC-{uuid.uuid4().hex[:4].upper()}"
    materia_payload = {
        "nrc": nrc,
        "nombre": "Arquitectura de Software",
        "seccion": "002",
        "clave": "ARQ-402",
        "docente_id": 456,
        "docente_nombre": "Dr. Gomez",
        "horario": "Viernes 10:00-14:00",
        "periodo_id": periodo_id,
        "activo": True
    }
    res = requests.post(f"{BASE_URL}/materias/", json=materia_payload, headers=headers)
    if res.status_code == 201:
        materia_id = res.json()["data"]["id"]
        print(f"OK (NRC: {nrc})")
    else:
        print(f"FAILED ({res.status_code})")

    # 5. Listar materias por periodo
    print(f"[5] Listando materias del periodo {periodo_id}...", end=" ")
    res = requests.get(f"{BASE_URL}/materias/por-periodo/{periodo_id}/", headers=headers)
    if res.status_code == 200:
        print(f"OK (Total: {len(res.json()['data'])})")
    else:
        print(f"FAILED ({res.status_code})")

    # 6. Actualizar Materia
    print(f"[6] Actualizando sección de la materia {materia_id}...", end=" ")
    res = requests.patch(f"{BASE_URL}/materias/{materia_id}/", json={"seccion": "003"}, headers=headers)
    if res.status_code == 200:
        print("OK (Nueva sección: 003)")
    else:
        print(f"FAILED ({res.status_code})")

    # 7. Eliminar Materia (Limpieza opcional)
    print(f"[7] Eliminando materia de prueba {materia_id}...", end=" ")
    res = requests.delete(f"{BASE_URL}/materias/{materia_id}/", headers=headers)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")

    print("\n====================================================")
    print("   PRUEBAS DE MS-PERIODOS-MATERIAS FINALIZADAS      ")
    print("====================================================")

if __name__ == "__main__":
    test_periodos_materias_full()
