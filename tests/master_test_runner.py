import subprocess
import sys
import os

# Lista de scripts de prueba en orden lógico
TEST_SCRIPTS = [
    "test_gateway.py",
    "test_auth_full.py",
    "test_periodos_full.py",
    "test_docentes_full.py",
    "test_asistencias_full.py",
    "test_calificaciones_full.py",
    "test_reportes_full.py",
    "test_notificaciones_full.py"
]

def run_all_tests():
    print("====================================================")
    print("   AGM SYSTEM - MASTER TEST RUNNER                 ")
    print("====================================================\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    results = []

    for script in TEST_SCRIPTS:
        script_path = os.path.join(base_dir, script)
        print(f"\n🚀 EJECUTANDO: {script}")
        print("-" * 50)
        
        try:
            # Ejecutamos el script y capturamos salida
            process = subprocess.run([sys.executable, script_path], cwd=base_dir)
            if process.returncode == 0:
                results.append((script, "✅ PASSED"))
            else:
                results.append((script, "❌ FAILED"))
        except Exception as e:
            results.append((script, f"💥 ERROR: {e}"))

    print("\n" + "="*50)
    print("           RESUMEN FINAL DE PRUEBAS")
    print("="*50)
    for script, status in results:
        print(f"{script:<30} | {status}")
    print("="*50)

    # Verificar si hubo fallos
    if any("PASSED" not in r[1] for r in results):
        print("\n⚠️ Algunas pruebas fallaron. Revisa los logs arriba.")
        sys.exit(1)
    else:
        print("\n🎉 ¡Todas las suites de prueba pasaron exitosamente!")

if __name__ == "__main__":
    run_all_tests()
