import requests
import sys
import os

# Añadir el directorio actual al path para importar el helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_auth_headers

BASE_URL = "http://localhost/api/docentes"

def test_docentes_full():
    print("====================================================")
    print("   TESTING MS-DOCENTES (Gestión de Personal)        ")
    print("====================================================\n")

    headers = get_auth_headers()
    if not headers:
        print("FAILED: No se pudo obtener token de autenticación")
        return

    # 1. Health Check
    print("[1] Verificando estado del servicio...", end=" ")
    res = requests.get(f"{BASE_URL}/")
    if res.status_code == 200:
        print("OK")
    else:
        print(f"FAILED ({res.status_code})")
        return

    # 2. Listar Docentes
    print("[2] Listando directorio docente...", end=" ")
    res = requests.get(f"{BASE_URL}/docentes/", headers=headers)
    if res.status_code == 200:
        print(f"OK ({len(res.json())} docentes encontrados)")
    else:
        print(f"FAILED ({res.status_code})")

    # 3. Listar Alumnos de una materia (usando una que exista o la de prueba)
    nrc_test = "25303"
    print(f"[3] Listando alumnos de materia {nrc_test}...", end=" ")
    res = requests.get(f"{BASE_URL}/alumnos/materia/{nrc_test}", headers=headers)
    if res.status_code == 200:
        alumnos = res.json()
        print(f"OK ({len(alumnos)} alumnos encontrados)")
    else:
        print(f"FAILED ({res.status_code})")
        alumnos = []

    # 4. Dar de baja (Comentado para no afectar otros tests)
    """
    if alumnos:
        alumno_id = alumnos[0]['id']
        print(f"[4] Dando de baja al alumno {alumno_id}...", end=" ")
        res = requests.delete(f"{BASE_URL}/alumnos/{alumno_id}/baja")
        if res.status_code == 200:
            print("OK")
        else:
            print(f"FAILED ({res.status_code})")
    """
    print("[4] Dar de baja SKIPPED (Mantenemos alumno activo para otros tests)")

    # 5. Intentar importar con archivo inválido (Validación)
    print("[5] Probando validación de tipo de archivo en importación...", end=" ")
    files = {'archivo': ('test.txt', b'fake content', 'text/plain')}
    res = requests.post(f"{BASE_URL}/docentes/importar", files=files)
    if res.status_code == 400:
        print("OK (Rechazó .txt correctamente)")
    else:
        print(f"FAILED (Permitió archivo no PDF: {res.status_code})")

    print("\n====================================================")
    print("   PRUEBAS DE MS-DOCENTES FINALIZADAS               ")
    print("====================================================")

if __name__ == "__main__":
    test_docentes_full()
