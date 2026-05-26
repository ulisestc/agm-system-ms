import logging
import os
import sys

# Añadir el directorio raíz al path para importar rabbitmq_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rabbitmq_manager import RabbitMQManager, RabbitMQRpcClient

logger = logging.getLogger("[ms-periodos-materias notifications]")
rabbitmq = RabbitMQManager()
rpc_client = RabbitMQRpcClient()

def send_cierre_materia(materia_id: int, materia_nombre: str, nrc: str, auth_token: str) -> bool:
    """Obtiene alumnos y publica un evento de cierre de materia en RabbitMQ"""
    try:
        # 1. Obtener alumnos vía RPC desde ms-docentes
        logger.info(f"Obteniendo alumnos para NRC: {nrc}")
        rpc_resp = rpc_client.call('rpc_docentes_queue', 'get_alumnos_by_materia', {'materiaId': nrc})
        
        alumnos_emails = []
        if rpc_resp and 'alumnos' in rpc_resp:
            alumnos_emails = [a['email'] for a in rpc_resp['alumnos'] if a.get('email')]
        
        # 2. Publicar evento enriquecido
        message = {
            "materiaId": str(materia_id),
            "materiaNombre": materia_nombre,
            "alumnosEmails": alumnos_emails,
            "auth_token": auth_token
        }
        rabbitmq.publish_event(
            exchange='events_exchange',
            routing_key='periodos.materia_cerrada',
            message=message
        )
        logger.info(f"Notificacion cierre_materia enviada para materia: {materia_id} ({len(alumnos_emails)} alumnos)")
        return True
    except Exception as e:
        logger.error(f"Error enviando notificacion cierre_materia: {e}")
        return False
