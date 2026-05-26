import logging
from rabbitmq_manager import RabbitMQManager

logger = logging.getLogger("[ms-auth notifications]")
rabbitmq = RabbitMQManager()

def send_reset_password_email(email: str, token: str) -> bool:
    """Publica un evento de restablecimiento de contraseña en RabbitMQ"""
    try:
        message = {
            "email": email,
            "token": token
        }
        rabbitmq.publish_event(
            exchange='events_exchange',
            routing_key='auth.reset_password',
            message=message
        )
        logger.info("Notificacion reset_password enviada a RabbitMQ para: %s", email)
        return True
    except Exception as rb_exc:
        logger.error("Error enviando notificacion a RabbitMQ: %s", rb_exc)
        return False
