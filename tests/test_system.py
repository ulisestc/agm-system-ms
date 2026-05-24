import requests
import subprocess
import os
import sys
import socket

# Obtener la ruta base del proyecto (un nivel arriba de /tests)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuración de servicios y sus endpoints de salud
SERVICES = {
    "MS-Auth": {
        "url": "http://localhost:8000/",
        "test_script": "test_auth.py",
        "cwd": os.path.join(BASE_DIR, "microservices/ms-auth")
    },
    "MS-Periodos-Materias": {
        "url": "http://localhost:8001/api/periodos/",
        "test_command": [sys.executable, "manage.py", "test"],
        "cwd": os.path.join(BASE_DIR, "microservices/ms-periodos-materias")
    },
    "MS-Docentes": {
        "url": "http://localhost:8003/",
        "test_script": "test_api.py",
        "cwd": os.path.join(BASE_DIR, "microservices/ms-docentes")
    },
    "MS-Calificaciones": {
        "url": "http://localhost:8004/",
    },
    "MS-Asistencias": {
        "url": "http://localhost:8005/",
    },
    "MS-Reportes": {
        "url": "http://localhost:8007/",
    },
    "RabbitMQ (Broker)": {
        "host": "localhost",
        "port": 5672,
        "type": "tcp"
    }
}

def check_tcp_port(host, port):
    print(f"Checking TCP port {port} for {host}...", end=" ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print("OPEN")
            return True
        else:
            print("CLOSED")
            return False
    except Exception:
        print("ERROR")
        return False
    finally:
        sock.close()

def check_health(name, config):
    if config.get("type") == "tcp":
        return check_tcp_port(config["host"], config["port"])
    
    url = config.get("url")
    print(f"Checking health of {name} at {url}...", end=" ")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code in [200, 201]:
            print("UP")
            return True
        else:
            print(f"DOWN (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException:
        print("UNREACHABLE")
        return False

def run_test_script(name, config):
    cwd = config.get("cwd")
    if not cwd:
        return None

    print(f"\n>>> Running specific tests for {name}...")
    
    # Check if dependencies are likely to be missing
    if name == "MS-Docentes":
        try:
            import openpyxl
        except ImportError:
            print(f"⚠ Skipping {name} tests: 'openpyxl' dependency missing in host.")
            return "SKIPPED (Missing openpyxl)"
    
    if name == "MS-Periodos-Materias":
        # Check if django is available if running manage.py
        try:
            import django
        except ImportError:
            print(f"⚠ Skipping {name} tests: 'django' dependency missing in host.")
            return "SKIPPED (Missing django)"

    if "test_script" in config:
        cmd = [sys.executable, config["test_script"]]
    elif "test_command" in config:
        cmd = config["test_command"]
    else:
        return None

    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {name} tests passed.")
            return True
        else:
            print(f"✗ {name} tests failed.")
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error running tests for {name}: {e}")
        return False

def test_asistencias_basic():
    print("Running basic functional test for MS-Asistencias...", end=" ")
    url = "http://localhost:8005/sesiones/iniciar"
    payload = {
        "materia_id": "TEST123",
        "docente_id": "DOC123"
    }
    try:
        # Probamos iniciar una sesión (puede fallar si ya existe, pero queremos ver si responde)
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 400]: # 400 is fine if session already exists
            print("OK (Responsive)")
            return True
        else:
            print(f"FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("====================================================")
    print("   AGM System - Comprehensive Microservices Test    ")
    print("====================================================\n")

    results = {}
    
    for name, config in SERVICES.items():
        health = check_health(name, config)
        results[name] = {"health": health, "tests": None}
        
        if health:
            if name == "MS-Asistencias":
                results[name]["tests"] = test_asistencias_basic()
            elif "test_script" in config or "test_command" in config:
                test_success = run_test_script(name, config)
                results[name]["tests"] = test_success
            else:
                print(f"No dedicated tests found for {name}, health check passed.")

    print("\n" + "="*72)
    print(f"{'Service':<25} | {'Health':<10} | {'Tests':<20}")
    print("-"*72)
    for name, res in results.items():
        health_str = "UP" if res["health"] else "DOWN"
        test_res = res["tests"]
        if test_res is True:
            test_str = "PASSED"
        elif test_res is False:
            test_str = "FAILED"
        elif isinstance(test_res, str):
            test_str = test_res
        else:
            test_str = "N/A"
        print(f"{name:<25} | {health_str:<10} | {test_str:<20}")
    print("="*72)

    # Exit with error code if any test failed
    failed = False
    for res in results.values():
        if res["tests"] is False:
            failed = True
    
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
