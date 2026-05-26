import pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")

def test_notificaciones_rabbitmq():
    print("====================================================")
    print("   TESTING MS-NOTIFICACIONES (RabbitMQ Events)      ")
    print("====================================================\n")

    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        exchange = 'events_exchange'
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

        # 1. Probar Reset Password (Pub/Sub)
        print("[1] Publicando evento Reset Password...", end=" ")
        msg_reset = {
            "email": "test_user@buap.mx",
            "token": "secure-token-123"
        }
        channel.basic_publish(
            exchange=exchange,
            routing_key='auth.reset_password',
            body=json.dumps(msg_reset),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("OK (Evento encolado)")

        # 2. Probar Bienvenida (Pub/Sub + RPC interno)
        # Nota: Esto provocará que ms-notificaciones llame vía RPC a ms-docentes y ms-periodos
        print("[2] Publicando evento Bienvenida...", end=" ")
        msg_welcome = {
            "alumnoId": "1",
            "materiaId": "1",
            "claveUnica": "TEST-RABBIT"
        }
        channel.basic_publish(
            exchange=exchange,
            routing_key='periodos.bienvenida',
            body=json.dumps(msg_welcome),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("OK (Evento encolado)")

        connection.close()
        print("\n====================================================")
        print("   PRUEBAS DE MS-NOTIFICACIONES FINALIZADAS         ")
        print("====================================================")

    except Exception as e:
        print(f"\n💥 ERROR RabbitMQ: {e}")

if __name__ == "__main__":
    test_notificaciones_rabbitmq()
