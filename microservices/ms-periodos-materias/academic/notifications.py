import logging
import os
import sys

# Añadir el directorio raíz al path para importar rabbitmq_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rabbitmq_manager import RabbitMQManager

logger = logging.getLogger("[ms-periodos-materias notifications]")
rabbitmq = RabbitMQManager()

def send_cierre_materia(materia_id: int) -> bool:
    """Publica un evento de cierre de materia en RabbitMQ"""
    try:
        message = {
            "materiaId": str(materia_id)
        }
        rabbitmq.publish_event(
            exchange='events_exchange',
            routing_key='periodos.materia_cerrada',
            message=message
        )
        logger.info(f"Notificacion cierre_materia enviada a RabbitMQ para materia: {materia_id}")
        return True
    except Exception as e:
        logger.error(f"Error enviando notificacion cierre_materia: {e}")
        return False
