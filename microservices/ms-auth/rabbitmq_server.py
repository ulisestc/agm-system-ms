import logging
import jwt
from rabbitmq_manager import RabbitMQRpcServer
import models
from database import SessionLocal
from settings import ALGORITHM, SECRET_KEY

logger = logging.getLogger("[RabbitMQ-RPC ms-auth]")

def _rol_to_string(rol) -> str:
    if isinstance(rol, models.RolUsuario):
        return rol.value
    return str(rol)

def _normalize_role(rol: str) -> str:
    for rol_usuario in models.RolUsuario:
        if rol in {rol_usuario.name, rol_usuario.value}:
            return rol_usuario.value
    return rol

def _to_user_dict(usuario: models.Usuario):
    return {
        "id": usuario.id,
        "email": usuario.email,
        "rol": _rol_to_string(usuario.rol),
    }

class AuthRpcHandlers:
    def _get_user_from_token(self, token: str, db):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            usuario_id = payload.get("sub")
            if usuario_id is None:
                return None, "Token sin sujeto"

            usuario = db.query(models.Usuario).filter(
                models.Usuario.id == int(usuario_id)
            ).first()
            if usuario is None:
                return None, "Usuario no encontrado"

            return usuario, ""
        except jwt.ExpiredSignatureError:
            return None, "Token expirado"
        except (jwt.InvalidTokenError, ValueError):
            return None, "Token invalido"

    def validate_token(self, data):
        token = data.get("token")
        db = SessionLocal()
        try:
            usuario, error = self._get_user_from_token(token, db)
            if usuario is None:
                return {
                    "valid": False,
                    "error_message": error,
                }

            return {
                "valid": True,
                "user": _to_user_dict(usuario),
                "error_message": "",
            }
        finally:
            db.close()

    def get_user_by_id(self, data):
        user_id = data.get("user_id")
        db = SessionLocal()
        try:
            usuario = db.query(models.Usuario).filter(
                models.Usuario.id == user_id
            ).first()
            if usuario is None:
                return {
                    "found": False,
                    "error_message": "Usuario no encontrado",
                }

            return {
                "found": True,
                "user": _to_user_dict(usuario),
                "error_message": "",
            }
        finally:
            db.close()

    def check_role(self, data):
        token = data.get("token")
        required_role = data.get("required_role")
        
        if not required_role:
            return {
                "allowed": False,
                "error_message": "required_role es requerido",
            }

        db = SessionLocal()
        try:
            usuario, error = self._get_user_from_token(token, db)
            if usuario is None:
                return {
                    "allowed": False,
                    "error_message": error,
                }

            norm_role = _normalize_role(required_role)
            allowed = _rol_to_string(usuario.rol) == norm_role

            return {
                "allowed": allowed,
                "user": _to_user_dict(usuario),
                "error_message": "" if allowed else "Rol no autorizado",
            }
        finally:
            db.close()

def serve():
    handlers = AuthRpcHandlers()
    server = RabbitMQRpcServer(queue_name='rpc_auth_queue')
    server.register_action('validate_token', handlers.validate_token)
    server.register_action('get_user_by_id', handlers.get_user_by_id)
    server.register_action('check_role', handlers.check_role)
    server.start()

if __name__ == "__main__":
    serve()
