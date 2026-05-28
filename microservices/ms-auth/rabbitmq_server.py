import logging
import jwt
import sys
import secrets
import string
from passlib.context import CryptContext
from rabbitmq_manager import RabbitMQRpcServer
import models
from database import SessionLocal
from settings import ALGORITHM, SECRET_KEY

# Asegurar que los logs salgan a stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("[RabbitMQ-RPC ms-auth]")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        except (jwt.InvalidTokenError, ValueError) as e:
            return None, f"Token invalido: {str(e)}"

    def validate_token(self, data):
        token = data.get("token")
        print(f"--> [RPC] Validando token: {token[:20]}...", flush=True)
        db = SessionLocal()
        try:
            usuario, error = self._get_user_from_token(token, db)
            
            if usuario is None:
                print(f"--> [RPC] Validacion fallida: {error}", flush=True)
                return {
                    "valid": False,
                    "error_message": error,
                }

            print(f"--> [RPC] Validacion exitosa: {usuario.email}", flush=True)
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

    def crear_usuario(self, data):
        email = data.get("email")
        rol_str = data.get("rol")
        password = data.get("password")
        
        if not email or not rol_str:
            return {"success": False, "error_message": "email y rol son requeridos"}
            
        db = SessionLocal()
        try:
            # Verificar si ya existe
            db_user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
            if db_user:
                return {"success": False, "error_message": "Este correo ya esta registrado"}
                
            # Normalizar rol
            rol_final = None
            for r in models.RolUsuario:
                if rol_str.lower() == r.name.lower() or rol_str == r.value:
                    rol_final = r
                    break
            
            if not rol_final:
                return {"success": False, "error_message": f"Rol invalido: {rol_str}"}
                
            # Generar password si no se provee
            if not password:
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for i in range(8))
            
            nuevo_usuario = models.Usuario(
                email=email,
                password_hash=pwd_context.hash(password),
                rol=rol_final
            )
            
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            
            return {
                "success": True,
                "user": _to_user_dict(nuevo_usuario),
                "password": password # Enviamos de vuelta el password plano para notificarlo
            }
        except Exception as e:
            return {"success": False, "error_message": str(e)}
        finally:
            db.close()

def serve():
    handlers = AuthRpcHandlers()
    server = RabbitMQRpcServer(queue_name='rpc_auth_queue')
    server.register_action('validate_token', handlers.validate_token)
    server.register_action('get_user_by_id', handlers.get_user_by_id)
    server.register_action('check_role', handlers.check_role)
    server.register_action('crear_usuario', handlers.crear_usuario)
    print("--> [RPC] Servidor Auth iniciado en rpc_auth_queue", flush=True)
    server.start()

if __name__ == "__main__":
    serve()
