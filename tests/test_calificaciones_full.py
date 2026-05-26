import requests
import uuid
import sys

BASE_URL = "http://localhost:8004"

def test_calificaciones_full():
    print("====================================================")
    print("   TESTING MS-CALIFICACIONES (Gestión de Notas)     ")
    print("====================================================\n")

    materia_id = f"MAT-{uuid.uuid4().hex[:4].upper()}"
    alumno_id = "202610101"

    # 1. Health Check
    print("[1] Verificando salud del servicio...", end=" ")
    res = requests.get(f"{BASE_URL}/")
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        return

    # 2. Crear Actividad
    print(f"[2] Creando actividad para materia {materia_id}...", end=" ")
    actividad_payload = {
        "materia_id": materia_id,
        "nombre": "Examen Parcial 1",
        "ponderacion": 30
    }
    res = requests.post(f"{BASE_URL}/actividades", json=actividad_payload)
    if res.status_code == 200:
        actividad_id = res.json()["data"]["actividad_id"]
        print(f"OK (ID: {actividad_id})")
    else:
        print(f"FAILED ({res.status_code})")
        return

    # 3. Listar Actividades
    print(f"[3] Listando actividades de la materia {materia_id}...", end=" ")
    res = requests.get(f"{BASE_URL}/actividades/{materia_id}")
    if res.status_code == 200:
        print(f"OK (Ponderación total: {res.json()['data']['total_ponderacion_registrada']}%)")
    else:
        print(f"FAILED ({res.status_code})")

    # 4. Calcular Promedio (Sin notas aún)
    print(f"[4] Calculando promedio inicial para alumno {alumno_id}...", end=" ")
    res = requests.get(f"{BASE_URL}/calificaciones/{materia_id}/{alumno_id}/promedio")
    if res.status_code == 200:
        print(f"OK (Promedio: {res.json()['data']['promedio_final']})")
    else:
        print(f"FAILED ({res.status_code})")

    print("\n====================================================")
    print("   PRUEBAS DE MS-CALIFICACIONES FINALIZADAS         ")
    print("====================================================")

if __name__ == "__main__":
    test_calificaciones_full()
