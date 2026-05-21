import logging
import os
from concurrent import futures

import grpc
import jwt

import auth_pb2
import auth_pb2_grpc
import models
from database import SessionLocal
from settings import ALGORITHM, SECRET_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[gRPC ms-auth]")


def _rol_to_string(rol) -> str:
    if isinstance(rol, models.RolUsuario):
        return rol.value
    return str(rol)


def _normalize_role(rol: str) -> str:
    for rol_usuario in models.RolUsuario:
        if rol in {rol_usuario.name, rol_usuario.value}:
            return rol_usuario.value
    return rol


def _to_user_message(usuario: models.Usuario):
    return auth_pb2.User(
        id=usuario.id,
        email=usuario.email,
        rol=_rol_to_string(usuario.rol),
    )


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
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

    def ValidateToken(self, request, context):
        logger.info("Peticion gRPC: ValidateToken")
        db = SessionLocal()
        try:
            usuario, error = self._get_user_from_token(request.token, db)
            if usuario is None:
                return auth_pb2.ValidateTokenResponse(
                    valid=False,
                    error_message=error,
                )

            return auth_pb2.ValidateTokenResponse(
                valid=True,
                user=_to_user_message(usuario),
                error_message="",
            )
        finally:
            db.close()

    def GetUserById(self, request, context):
        logger.info("Peticion gRPC: GetUserById | user_id=%s", request.user_id)
        db = SessionLocal()
        try:
            usuario = db.query(models.Usuario).filter(
                models.Usuario.id == request.user_id
            ).first()
            if usuario is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Usuario con id={request.user_id} no encontrado")
                return auth_pb2.GetUserByIdResponse(
                    found=False,
                    error_message="Usuario no encontrado",
                )

            return auth_pb2.GetUserByIdResponse(
                found=True,
                user=_to_user_message(usuario),
                error_message="",
            )
        finally:
            db.close()

    def CheckRole(self, request, context):
        logger.info("Peticion gRPC: CheckRole | required_role=%s", request.required_role)
        if not request.required_role:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("required_role es requerido")
            return auth_pb2.CheckRoleResponse(
                allowed=False,
                error_message="required_role es requerido",
            )

        db = SessionLocal()
        try:
            usuario, error = self._get_user_from_token(request.token, db)
            if usuario is None:
                return auth_pb2.CheckRoleResponse(
                    allowed=False,
                    error_message=error,
                )

            required_role = _normalize_role(request.required_role)
            allowed = _rol_to_string(usuario.rol) == required_role

            return auth_pb2.CheckRoleResponse(
                allowed=allowed,
                user=_to_user_message(usuario),
                error_message="" if allowed else "Rol no autorizado",
            )
        finally:
            db.close()


def serve():
    port = os.getenv("GRPC_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info("Servidor gRPC de ms-auth escuchando en 0.0.0.0:%s", port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
