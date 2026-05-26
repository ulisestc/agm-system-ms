import logging
from src.rabbitmq_manager import RabbitMQRpcClient

logger = logging.getLogger("[RabbitMQ-Client ms-calificaciones]")
rpc_client = RabbitMQRpcClient()


def validar_propiedad_materia(docente_id: str, materia_id: str) -> bool:
    """Consulta si el docente es dueño de la materia vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_docentes_queue',
            action='is_docente_en_materia',
            data={
                "docenteId": docente_id,
                "materiaId": materia_id
            }
        )
        return response.get("result", False)
    except Exception as e:
        logger.error(f"Error al validar propiedad de materia: {e}")
        return False