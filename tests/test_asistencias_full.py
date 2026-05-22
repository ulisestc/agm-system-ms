import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:8005"  # Probamos directamente al puerto del MS
# Si prefieres probar vía Gateway, cambia a: "http://localhost/api/asistencias"

def test_ms_asistencias_full_flow():
    print("====================================================")
    print("   TESTING MS-ASISTENCIAS (Flow Completo)           ")
    print("====================================================\n")

    materia_id = "TEST-123" # NRC que asignamos al alumno de prueba
    docente_id = "DOC-123"
    alumno_id = "1" # ID numérico del alumno que creamos manualmente (en lugar de matrícula)
    
    # 1. Iniciar Sesión
    print(f"[1] Iniciando sesión para materia {materia_id}...", end=" ")
    # Nos aseguramos que no haya una sesión previa abierta (limpieza)
    requests.delete(f"{BASE_URL}/sesiones/{materia_id}/cerrar")

    payload = {
        "materia_id": materia_id,
        "docente_id": docente_id
    }
    res = requests.post(f"{BASE_URL}/sesiones/iniciar", json=payload)
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)
        return

    # 2. Intentar iniciar sesión duplicada (debe fallar)
    print("[2] Probando validación de sesión duplicada...", end=" ")
    res = requests.post(f"{BASE_URL}/sesiones/iniciar", json=payload)
    if res.status_code == 400:
        print("OK (Bloqueado correctamente)")
    else:
        print(f"FAILED (Se permitió duplicar sesión: {res.status_code})")

    # 3. Registrar asistencia (Happy Path)
    print(f"[3] Registrando asistencia para alumno {alumno_id}...", end=" ")
    token_qr = f"QR-{uuid.uuid4().hex}"
    payload_asistencia = {
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "token_qr": token_qr
    }
    res = requests.post(f"{BASE_URL}/asistencias/registrar", json=payload_asistencia)
    if res.status_code == 200:
        print(f"OK (Estado: {res.json()['data']['estado']})")
    else:
        print(f"FAILED ({res.status_code})")
        print(res.text)

    # 4. Anti-replay (usar el mismo token de nuevo)
    print("[4] Probando Anti-replay con el mismo token...", end=" ")
    res = requests.post(f"{BASE_URL}/asistencias/registrar", json=payload_asistencia)
    if res.status_code == 400:
        print("OK (Bloqueado correctamente)")
    else:
        print(f"FAILED (Se permitió re-uso de token: {res.status_code})")

    # 5. Consultar asistencias de hoy
    print("[5] Consultando asistencias de hoy...", end=" ")
    res = requests.get(f"{BASE_URL}/asistencias/{materia_id}/hoy")
    if res.status_code == 200:
        registros = res.json()['data']['registros']
        print(f"OK (Registros encontrados: {len(registros)})")
    else:
        print(f"FAILED ({res.status_code})")

    # 6. Cerrar sesión
    print("[6] Cerrando sesión forzosamente...", end=" ")
    res = requests.delete(f"{BASE_URL}/sesiones/{materia_id}/cerrar")
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")

    # 7. Registrar tras cierre (debe fallar)
    print("[7] Probando registro tras cierre de sesión...", end=" ")
    token_qr_2 = f"QR-{uuid.uuid4().hex}"
    payload_asistencia["token_qr"] = token_qr_2
    res = requests.post(f"{BASE_URL}/asistencias/registrar", json=payload_asistencia)
    if res.status_code == 404:
        print("OK (Bloqueado correctamente)")
    else:
        print(f"FAILED (Se permitió registro tras cierre: {res.status_code})")

    print("\n====================================================")
    print("   PRUEBAS DE MS-ASISTENCIAS FINALIZADAS            ")
    print("====================================================")

if __name__ == "__main__":
    test_ms_asistencias_full_flow()
