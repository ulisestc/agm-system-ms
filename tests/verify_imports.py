import requests
import os
import sys
from dotenv import load_dotenv

# Add current directory to path for auth_helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_token, GATEWAY_URL

# Configuración de URLs de servicios vía Gateway (Production)
SERVICES = {
    "auth": f"{GATEWAY_URL}/auth",
    "periodos": f"{GATEWAY_URL}/periodos/api",
    "docentes": f"{GATEWAY_URL}/docentes",
    "calificaciones": f"{GATEWAY_URL}/calificaciones",
}

def test_imports():
    print("====================================================")
    print("   AGM SYSTEM - MASTER IMPORT VERIFICATION          ")
    print("====================================================\n")

    # 1. Autenticación
    print("[STEP 1] Autenticando como Administrador...")
    admin_email = "admin@buap.mx"
    password = "password123"
    token = get_token(admin_email, password, "Administrador")
    if not token:
        print("  [X] ERROR: No se pudo obtener token.")
        return
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Autenticado.\n")

    # 2. Periodo Activo
    print("[STEP 2] Asegurando Periodo Activo...")
    res_p = requests.get(f"{SERVICES['periodos']}/periodos/activo/", headers=headers)
    periodo_id = None
    if res_p.status_code == 200:
        periodo_id = res_p.json()["data"]["id"]
    else:
        p_payload = {"nombre": "Primavera 2026", "fecha_inicio": "2026-01-01", "fecha_fin": "2026-06-30", "plan_estudios": "ITI", "activo": True}
        res_p = requests.post(f"{SERVICES['periodos']}/periodos/", json=p_payload, headers=headers)
        periodo_id = res_p.json()["data"]["id"]
    print(f"  [OK] Usando Periodo ID: {periodo_id}\n")

    # 3. Importar PROGRAMACIÓN ACADÉMICA (Materias) -> MS-2
    print("[STEP 3] Importando Programación (MS-Periodos)...")
    pdf_materias = "docs/materias.pdf"
    with open(pdf_materias, "rb") as f:
        files = {"archivo": ("materias.pdf", f, "application/pdf")}
        data = {"periodo_id": periodo_id}
        res = requests.post(f"{SERVICES['periodos']}/materias/importar/", files=files, data=data, headers=headers)
        print(f"  Status: {res.status_code}")
        if res.status_code in [200, 201]:
            print(f"  [OK] Materias creadas en Periodos.")

    # 4. Importar PROGRAMACIÓN ACADÉMICA (Docentes) -> MS-3
    print("\n[STEP 4] Importando Asignaciones Docentes (MS-Docentes)...")
    with open(pdf_materias, "rb") as f:
        files = {"archivo": ("materias.pdf", f, "application/pdf")}
        # Este endpoint crea los registros de Docente a partir de la programación
        res = requests.post(f"{SERVICES['docentes']}/docentes/importar", files=files, headers=headers)
        print(f"  Status: {res.status_code}")
        if res.status_code == 200:
            print(f"  [OK] Docentes creados/vinculados: {res.json().get('registros_importados')}")

    # 5. Importar DIRECTORIO DOCENTE (Emails/Ubicación) -> MS-3
    print("\n[STEP 5] Actualizando Directorio Docente (MS-Docentes)...")
    pdf_directorio = "docs/personal_docente.pdf"
    with open(pdf_directorio, "rb") as f:
        files = {"archivo": ("personal_docente.pdf", f, "application/pdf")}
        # Este endpoint ACTUALIZA los emails usando normalización de nombres
        res = requests.post(f"{SERVICES['docentes']}/docentes/importar-directorio", files=files, headers=headers)
        print(f"  Status: {res.status_code}")
        if res.status_code == 200:
            print(f"  [OK] Directorio actualizado: {res.json().get('registros_importados')} registros.")

    # 6. Importar ALUMNOS (con Emails desde hipervínculos) -> MS-3
    print("\n[STEP 6] Importando Alumnos (MS-Docentes)...")
    pdf_alumnos = "docs/alumnos.pdf"
    nrc_test = "50130"
    with open(pdf_alumnos, "rb") as f:
        files = {"archivo": ("alumnos.pdf", f, "application/pdf")}
        res = requests.post(f"{SERVICES['docentes']}/alumnos/importar/{nrc_test}", files=files, headers=headers)
        print(f"  Status: {res.status_code}")
        if res.status_code == 200:
            print(f"  [OK] Alumnos e Emails extraídos correctamente.")

    # 7. Importar CALIFICACIONES (Excel Flexible) -> MS-4
    print("\n[STEP 7] Importando Calificaciones (MS-Calificaciones)...")
    # Crear actividad
    act_payload = {"materia_id": nrc_test, "nombre": "Final Test", "ponderacion": 100}
    res_act = requests.post(f"{SERVICES['calificaciones']}/actividades", json=act_payload, headers=headers)
    if res_act.status_code in [200, 201]:
        act_id = res_act.json()["data"]["actividad_id"]
        excel_path = "docs/calificaciones.xlsx"
        with open(excel_path, "rb") as f:
            files = {"file": ("calificaciones.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"actividad_id": act_id}
            res = requests.post(f"{SERVICES['calificaciones']}/calificaciones/importar", files=files, data=data, headers=headers)
            print(f"  Status: {res.status_code}")
            if res.status_code == 200:
                print(f"  [OK] Calificaciones REALES procesadas.")

    print("\n====================================================")
    print("          FIN DE LA VERIFICACIÓN MAESTRA           ")
    print("====================================================")

if __name__ == "__main__":
    test_imports()
