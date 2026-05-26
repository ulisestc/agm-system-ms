import requests
import openpyxl
from io import BytesIO
import sys
import os

# Importamos el cliente RabbitMQ RPC para probar la nueva comunicación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rabbitmq_manager import RabbitMQRpcClient

BASE_URL = "http://localhost:8003"
NRC_TEST = "10552"

def main():
    print("=== Iniciando Pruebas REST y RabbitMQ-RPC de MS-3 ===")

    # 1. Verificar si el servidor está vivo
    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"Health Check: {res.json()}")
    except Exception as e:
        print(f"Error conectando al servidor REST: {e}")
        return

    # 2. Crear un archivo Excel en memoria para importar alumnos
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Matricula", "Nombre", "Email", "NRC"])
    ws.append(["202010101", "Juan Perez", "juan@test.com", NRC_TEST])
    ws.append(["202010102", "Maria Gomez", "maria@test.com", NRC_TEST])

    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    # 3. Probar POST /alumnos/importar/{nrc}
    print(f"\n--- Probando Importación de Excel para NRC {NRC_TEST} ---")
    files = {"archivo": ("alumnos.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = requests.post(f"{BASE_URL}/alumnos/importar/{NRC_TEST}", files=files)
    print(f"Status: {res.status_code}")
    print(f"Respuesta: {res.json()}")

    # 4. Probar GET /alumnos/materia/{nrc}
    print(f"\n--- Probando Listar Alumnos del NRC {NRC_TEST} ---")
    res = requests.get(f"{BASE_URL}/alumnos/materia/{NRC_TEST}")
    print(f"Status: {res.status_code}")
    alumnos = res.json()
    print(f"Alumnos encontrados: {len(alumnos)}")
    
    # Obtener el ID del primer alumno insertado
    if not alumnos:
        print("No se importaron alumnos.")
        return
        
    alumno_id = str(alumnos[0]['id'])
    
    # 5. Probar el nuevo método RabbitMQ-RPC: is_alumno_en_materia
    print(f"\n--- Probando RabbitMQ-RPC: is_alumno_en_materia(alumno_id={alumno_id}, materia_id={NRC_TEST}) ---")
    try:
        # Nota: Usamos localhost porque estamos en el host, no en la red docker
        rpc_client = RabbitMQRpcClient(url="amqp://guest:guest@localhost:5672")
        
        resp = rpc_client.call(
            queue_name='rpc_docentes_queue',
            action='is_alumno_en_materia',
            data={"alumnoId": alumno_id, "materiaId": NRC_TEST}
        )
        print(f"Resultado RPC is_alumno_en_materia: {resp.get('result')} (Esperado: True)")
    except Exception as e:
        print(f"Error en RabbitMQ-RPC: {e}")

    # 6. Probar DELETE /alumnos/{id}/baja
    print(f"\n--- Probando Dar de Baja al alumno con ID {alumno_id} ---")
    res = requests.delete(f"{BASE_URL}/alumnos/{alumno_id}/baja")
    print(f"Status: {res.status_code}")
    
    # Verificar RPC de nuevo
    print(f"\n--- Probando RPC nuevamente tras baja: is_alumno_en_materia(alumno_id={alumno_id}, materia_id={NRC_TEST}) ---")
    try:
        resp = rpc_client.call(
            queue_name='rpc_docentes_queue',
            action='is_alumno_en_materia',
            data={"alumnoId": alumno_id, "materiaId": NRC_TEST}
        )
        print(f"Resultado RPC is_alumno_en_materia: {resp.get('result')} (Esperado: False)")
    except Exception as e:
        print(f"Error en RabbitMQ-RPC: {e}")

if __name__ == "__main__":
    main()
