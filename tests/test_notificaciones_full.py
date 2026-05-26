import pika
import json
import os
import time

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")

def test_notificaciones_rabbitmq():
    print("====================================================")
    print("   TESTING MS-NOTIFICACIONES (Robust Test)          ")
    print("====================================================\n")

    # Mock token - en un entorno real debe ser un JWT válido de ms-auth
    MOCK_TOKEN = "invalid-or-expired-token"

    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        exchange = 'events_exchange'
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

        # 1. Probar Reset Password (No requiere auth_token)
        print("[1] Publicando Reset Password...", end=" ")
        msg_reset = {
            "email": "alumno_test@buap.mx",
            "token": "reset-token-xyz"
        }
        channel.basic_publish(
            exchange=exchange,
            routing_key='auth.reset_password',
            body=json.dumps(msg_reset)
        )
        print("OK")
        time.sleep(1) # Pequeña espera para ver logs

        # 2. Probar Bienvenida (Enriquecido + Token)
        # Este fallará en la validación del token si no es un JWT real,
        # pero el servicio NO debe colapsar.
        print("[2] Publicando Bienvenida (Token inválido)...", end=" ")
        msg_welcome = {
            "alumnoId": "100",
            "alumnoNombre": "Juan Perez",
            "alumnoEmail": "juan.perez@buap.mx",
            "materiaNombre": "Servicios Web",
            "claveUnica": "ABC-123",
            "auth_token": MOCK_TOKEN
        }
        channel.basic_publish(
            exchange=exchange,
            routing_key='periodos.bienvenida',
            body=json.dumps(msg_welcome)
        )
        print("OK")
        time.sleep(1)

        # 3. Probar Baja
        print("[3] Publicando Baja (Token inválido)...", end=" ")
        msg_baja = {
            "alumnoId": "100",
            "alumnoNombre": "Juan Perez",
            "docenteId": "50",
            "docenteNombre": "Dra. Maria Lopez",
            "docenteEmail": "maria.lopez@buap.mx",
            "auth_token": MOCK_TOKEN
        }
        channel.basic_publish(
            exchange=exchange,
            routing_key='docentes.baja',
            body=json.dumps(msg_baja)
        )
        print("OK")
        time.sleep(1)

        connection.close()
        print("\n====================================================")
        print("   PRUEBAS FINALIZADAS (Revisar logs del MS)        ")
        print("====================================================")

    except Exception as e:
        print(f"\n💥 ERROR RabbitMQ: {e}")

if __name__ == "__main__":
    test_notificaciones_rabbitmq()
