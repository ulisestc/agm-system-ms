import pika
import json
import time

# URL de RabbitMQ (usando localhost para el túnel o contenedor expuesto)
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"

def test_reset_password_real():
    print("====================================================")
    print("   SOLICITANDO RESET PASSWORD (BREVO API v5)        ")
    print("====================================================\n")

    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        exchange = 'events_exchange'
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

        # Simulamos el evento que enviaría ms-auth
        email_destino = "ulisestc27@gmail.com"
        token_falso = "TEST-API-V5-" + str(int(time.time()))
        
        print(f"[*] Publicando evento para: {email_destino}...", end=" ")
        
        message = {
            "email": email_destino,
            "token": token_falso
        }
        
        channel.basic_publish(
            exchange=exchange,
            routing_key='auth.reset_password',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2, # mensaje persistente
            )
        )
        print("OK")
        
        print("\n[!] Evento enviado. Si el MS está corriendo localmente, revisa sus logs.")
        print("[!] Si el MS está en Railway, revisa los logs de Railway.")
        
        connection.close()
        print("\n====================================================")

    except Exception as e:
        print(f"\n💥 ERROR RabbitMQ: {e}")

if __name__ == "__main__":
    test_reset_password_real()
