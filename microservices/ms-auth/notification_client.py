import logging
import json
import pika
from settings import MS_NOTIFICACIONES_URL, NOTIFICACIONES_TIMEOUT_SECONDS, RABBITMQ_URL

logger = logging.getLogger("[ms-auth notifications]")


def send_reset_password_email(email: str, token: str) -> bool:
    # Intentar via RabbitMQ primero (Asincrono)
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='notifications_queue', durable=True)
        
        message = {
            "type": "reset_password",
            "data": {
                "email": email,
                "token": token
            }
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='notifications_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistente
            )
        )
        connection.close()
        logger.info("Notificacion reset_password enviada a RabbitMQ para: %s", email)
        return True
    except Exception as rb_exc:
        logger.warning("Fallo envio a RabbitMQ, intentando gRPC: %s", rb_exc)

    # Fallback a gRPC (Sincrono)
    if not MS_NOTIFICACIONES_URL:
        logger.info("MS_NOTIFICACIONES_URL no configurado; se omite notificacion gRPC.")
        return False

    try:
        import grpc
        import notificaciones_pb2
        import notificaciones_pb2_grpc

        with grpc.insecure_channel(MS_NOTIFICACIONES_URL) as channel:
            stub = notificaciones_pb2_grpc.NotificacionesServiceStub(channel)
            response = stub.SendResetPassword(
                notificaciones_pb2.ResetPasswordRequest(email=email, token=token),
                timeout=NOTIFICACIONES_TIMEOUT_SECONDS,
            )
            if not response.success:
                logger.warning("ms-notificaciones rechazo el correo: %s", response.error_message)
            return bool(response.success)
    except Exception as exc:
        logger.warning("No se pudo enviar correo de recuperacion por gRPC: %s", exc)
        return False
