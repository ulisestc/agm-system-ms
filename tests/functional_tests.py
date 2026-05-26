import requests
import uuid
import sys
import os

# Añadir el directorio actual al path para importar el helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_helper import get_auth_headers, get_token

# Configuración de URLs de servicios vía Gateway
SERVICES = {
    "auth": "http://localhost/api/auth",
    "periodos": "http://localhost/api/periodos/api",
    "docentes": "http://localhost/api/docentes",
    "asistencias": "http://localhost/api/asistencias",
    "calificaciones": "http://localhost/api/calificaciones",
    "reportes": "http://localhost/api/reportes",
}

class FunctionalTester:
    def __init__(self):
        self.session = requests.Session()
        self.docente_email = "docente@buap.mx"
        self.docente_pass = "password123"
        self.alumno_email = "alumno@buap.mx"
        self.alumno_pass = "password123"
        self.periodo_id = None
        self.materia_nrc = "25303" # NRC sembrado

    def print_step(self, msg):
        print(f"\n[STEP] {msg}")

    def setup_auth(self):
        self.print_step("Configurando Autenticación")
        token = get_token(self.docente_email, self.docente_pass)
        if not token:
            print("ERROR: No se pudo obtener token para el docente")
            sys.exit(1)
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        print(f"Token obtenido para {self.docente_email}")

    def test_periodos_materias(self):
        self.print_step("Probando MS-Periodos-Materias")
        
        # 1. Consultar Periodos
        res = self.session.get(f"{SERVICES['periodos']}/periodos/")
        print(f"Listar Periodos: {res.status_code}")
        assert res.status_code == 200
        data = res.json().get("data", {})
        # Si es paginado, los resultados están en 'results'
        periodos = data.get("results", []) if isinstance(data, dict) else data
        
        if periodos:
            self.periodo_id = periodos[0]["id"]
            print(f"Usando Periodo ID: {self.periodo_id}")

        # 2. Consultar Materias
        res = self.session.get(f"{SERVICES['periodos']}/materias/")
        print(f"Listar Materias: {res.status_code}")
        assert res.status_code == 200

    def test_docentes_alumnos(self):
        self.print_step("Probando MS-Docentes")
        
        # 1. Listar Docentes
        res = self.session.get(f"{SERVICES['docentes']}/docentes/")
        print(f"Listar Docentes: {res.status_code}")
        assert res.status_code == 200

        # 2. Listar Alumnos de la materia sembrada
        res = self.session.get(f"{SERVICES['docentes']}/alumnos/materia/{self.materia_nrc}")
        print(f"Listar Alumnos (NRC {self.materia_nrc}): {res.status_code}")
        assert res.status_code == 200
        alumnos = res.json()
        if alumnos:
            self.alumno_test_id = str(alumnos[0]["id"])
            print(f"Usando Alumno ID: {self.alumno_test_id} ({alumnos[0]['nombre']})")

    def test_asistencias_flow(self):
        self.print_step("Probando Flujo de Asistencia (MS-Asistencias)")
        
        # 1. Iniciar Sesión (Docente)
        payload_init = {"materia_id": self.materia_nrc, "docente_id": "1"}
        self.session.delete(f"{SERVICES['asistencias']}/sesiones/{self.materia_nrc}/cerrar")
        res = self.session.post(f"{SERVICES['asistencias']}/sesiones/iniciar", json=payload_init)
        print(f"Iniciar Sesión: {res.status_code}")
        assert res.status_code == 200

        # 2. Generar QR (Alumno)
        token_alumno = get_token(self.alumno_email, self.alumno_pass)
        headers_alumno = {"Authorization": f"Bearer {token_alumno}"}
        payload_qr = {"alumno_id": self.alumno_test_id, "materia_id": self.materia_nrc}
        res = requests.post(f"{SERVICES['asistencias']}/qr/generar", json=payload_qr, headers=headers_alumno)
        print(f"Generar QR: {res.status_code}")
        assert res.status_code == 200
        token_qr = res.json()["data"]["token_qr"]

        # 3. Registrar Asistencia
        payload_reg = {
            "alumno_id": self.alumno_test_id,
            "materia_id": self.materia_nrc,
            "token_qr": token_qr
        }
        res = requests.post(f"{SERVICES['asistencias']}/asistencias/registrar", json=payload_reg, headers=headers_alumno)
        print(f"Registrar Asistencia: {res.status_code}")
        assert res.status_code == 200

    def run_all(self):
        print("====================================================")
        print("   AGM System - SYSTEM WIDE FUNCTIONAL TESTS       ")
        print("====================================================")
        
        try:
            self.setup_auth()
            self.test_periodos_materias()
            self.test_docentes_alumnos()
            self.test_asistencias_flow()
            print("\n✅ ¡TODAS LAS PRUEBAS FUNCIONALES PASARON!")
        except AssertionError as e:
            print(f"\n❌ FALLA EN LAS PRUEBAS: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 ERROR INESPERADO: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    tester = FunctionalTester()
    tester.run_all()
