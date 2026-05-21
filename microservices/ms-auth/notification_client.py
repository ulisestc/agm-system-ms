import logging

from settings import MS_NOTIFICACIONES_URL, NOTIFICACIONES_TIMEOUT_SECONDS

logger = logging.getLogger("[ms-auth notifications]")


def send_reset_password_email(email: str, token: str) -> bool:
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
