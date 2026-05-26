import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rabbitmq_manager import RabbitMQRpcClient

logger = logging.getLogger("[ms-periodos auth_client]")

_rpc_client = None

def _get_client():
    """Singleton para reutilizar la conexión RabbitMQ."""
    global _rpc_client
    if _rpc_client is None:
        _rpc_client = RabbitMQRpcClient()
    return _rpc_client


def validate_token(token: str) -> dict:
    """
    Llama a rpc_auth_queue con la acción validate_token.
    Devuelve: {"valid": bool, "user": {...}, "error_message": str}
    """
    try:
        return _get_client().call(
            queue_name="rpc_auth_queue",
            action="validate_token",
            data={"token": token},
        )
    except Exception as exc:
        logger.error("Error llamando validate_token: %s", exc)
        return {"valid": False, "error_message": str(exc)}


def check_role(token: str, required_role: str) -> dict:
    """
    Llama a rpc_auth_queue con la acción check_role.
    Devuelve: {"allowed": bool, "user": {...}, "error_message": str}
    """
    try:
        return _get_client().call(
            queue_name="rpc_auth_queue",
            action="check_role",
            data={"token": token, "required_role": required_role},
        )
    except Exception as exc:
        logger.error("Error llamando check_role: %s", exc)
        return {"allowed": False, "error_message": str(exc)}