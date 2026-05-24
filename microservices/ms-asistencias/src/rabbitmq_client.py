import logging
from src.rabbitmq_manager import RabbitMQRpcClient

logger = logging.getLogger("[RabbitMQ-Client ms-asistencias]")
rpc_client = RabbitMQRpcClient()

def validar_alumno_en_materia(alumno_id: str, materia_id: str) -> bool:
    """Consulta al MS-Docentes vía RabbitMQ RPC para validar inscripción"""
    try:
        response = rpc_client.call(
            queue_name='rpc_docentes_queue',
            action='is_alumno_en_materia',
            data={
                "alumnoId": alumno_id,
                "materiaId": materia_id
            }
        )
        return response.get("result", False)
    except Exception as e:
        logger.error(f"Error al llamar a MS-Docentes vía RPC: {e}")
        return False
