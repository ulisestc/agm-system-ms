import requests
import uuid
import os
import sys
from io import BytesIO
import openpyxl

# Configuración de URLs (usando gateway para realismo)
GATEWAY_URL = "http://localhost"
AUTH_URL = f"{GATEWAY_URL}/api/auth"
PERIODOS_URL = f"{GATEWAY_URL}/api/periodos"
DOCENTES_URL = f"{GATEWAY_URL}/api/docentes"
ASISTENCIAS_URL = f"{GATEWAY_URL}/api/asistencias"

def create_excel_alumnos(nrc):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Matricula", "Nombre", "Email", "NRC"])
    alumnos = [
        ["20200001", "Juan Perez", "juan.perez@alumno.buap.mx", nrc],
        ["20200002", "Maria Garcia", "maria.garcia@alumno.buap.mx", nrc],
        ["20200003", "Pedro Lopez", "pedro.lopez@alumno.buap.mx", nrc],
        ["20200004", "Ana Martinez", "ana.martinez@alumno.buap.mx", nrc],
        ["20200005", "Luis Rodriguez", "luis.rodriguez@alumno.buap.mx", nrc],
    ]
    for alu in alumnos:
        ws.append(alu)
    
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    return excel_file

def seed():
    print("====================================================")
    print("   SEEDING SYNTHETIC DATA FOR AGM SYSTEM           ")
    print("====================================================\n")

    # 1. Crear Usuarios en Auth
    print("[1] Creando usuarios de prueba...", end=" ")
    docente_email = "docente@buap.mx"
    alumno_email = "alumno@buap.mx"
    password = "password123"

    # Ignoramos si ya existen (400)
    requests.post(f"{AUTH_URL}/usuarios/", json={"email": docente_email, "password": password, "rol": "DOCENTE"})
    requests.post(f"{AUTH_URL}/usuarios/", json={"email": alumno_email, "password": password, "rol": "ALUMNO"})
    print("OK")

    # 2. Login para obtener tokens
    print("[2] Obteniendo tokens...", end=" ")
    res_docente = requests.post(f"{AUTH_URL}/auth/login", data={"username": docente_email, "password": password})
    res_alumno = requests.post(f"{AUTH_URL}/auth/login", data={"username": alumno_email, "password": password})
    
    if res_docente.status_code != 200 or res_alumno.status_code != 200:
        print("FAILED")
        print(f"Docente: {res_docente.status_code}, Alumno: {res_alumno.status_code}")
        return

    docente_token = res_docente.json()["access_token"]
    alumno_token = res_alumno.json()["access_token"]
    print("OK")

    docente_headers = {"Authorization": f"Bearer {docente_token}"}
    alumno_headers = {"Authorization": f"Bearer {alumno_token}"}

    # 3. Crear Periodo
    print("[3] Creando periodo académico...", end=" ")
    periodo_payload = {
        "nombre": "Periodo Otoño 2026",
        "fecha_inicio": "2026-08-01",
        "fecha_fin": "2026-12-15",
        "plan_estudios": "ISC 2026",
        "activo": True
    }
    res_p = requests.post(f"{PERIODOS_URL}/api/periodos/", json=periodo_payload, headers=docente_headers)
    if res_p.status_code in [201, 400]: # 400 si ya existe
        periodo_id = res_p.json().get("data", {}).get("id") if res_p.status_code == 201 else 1 # Asumimos 1 si ya existía
        print("OK")
    else:
        print(f"FAILED ({res_p.status_code})")
        return

    # 4. Importar Docentes desde PDF
    print("[4] Importando directorio docente desde PDF...", end=" ")
    pdf_path = "docs/ejemplos/personal_docente.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            files = {"archivo": ("personal_docente.pdf", f, "application/pdf")}
            res_d = requests.post(f"{DOCENTES_URL}/docentes/importar", files=files, headers=docente_headers)
            if res_d.status_code == 200:
                print(f"OK ({res_d.json()['registros_importados']} registros)")
            else:
                print(f"FAILED ({res_d.status_code})")
    else:
        print("SKIPPED (PDF not found)")

    # 5. Crear Materia en Periodos-Materias (usando NRC de ejemplo 12345 o el del PDF)
    # El PDF de ejemplo suele tener NRCs como 25303, 25304, etc.
    nrc_test = "25303" 
    print(f"[5] Creando materia {nrc_test} en Periodos-Materias...", end=" ")
    materia_payload = {
        "nrc": nrc_test,
        "nombre": "Sistemas Microprocesados",
        "seccion": "001",
        "clave": "IREL-202",
        "docente_id": 1,
        "docente_nombre": "JUAN CARLOS PINEDA DE LA ROSA",
        "horario": "Lunes 08:00-10:00",
        "periodo_id": periodo_id,
        "activo": True
    }
    res_m = requests.post(f"{PERIODOS_URL}/api/materias/", json=materia_payload, headers=docente_headers)
    if res_m.status_code in [201, 400]:
        print("OK")
    else:
        print(f"FAILED ({res_m.status_code})")

    # 6. Importar Alumnos en Docentes
    print(f"[6] Importando alumnos para NRC {nrc_test}...", end=" ")
    excel_data = create_excel_alumnos(nrc_test)
    files = {"archivo": ("alumnos.xlsx", excel_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res_a = requests.post(f"{DOCENTES_URL}/alumnos/importar/{nrc_test}", files=files, headers=docente_headers)
    if res_a.status_code == 200:
        print(f"OK ({res_a.json()['registros_importados']} alumnos)")
    else:
        print(f"FAILED ({res_a.status_code})")

    print("\n====================================================")
    print("   SEEDING COMPLETED SUCCESSFULLY!                  ")
    print("====================================================")

if __name__ == "__main__":
    seed()
