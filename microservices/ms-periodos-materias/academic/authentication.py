from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from academic.auth_client import validate_token


class RabbitMQJWTAuthentication(BaseAuthentication):
    """
    Autenticación DRF que valida el Bearer token llamando a ms-auth
    via RabbitMQ RPC (rpc_auth_queue → validate_token).

    Si no hay header Authorization → retorna None (endpoint público).
    Si el token es inválido → lanza AuthenticationFailed.
    Si es válido → retorna (user_dict, token).
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # Sin token: las permission_classes decidirán

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return None

        result = validate_token(token)

        if not result.get("valid"):
            raise AuthenticationFailed(
                result.get("error_message", "Token inválido o expirado.")
            )

        user = result.get("user")  # {"id": ..., "email": ..., "rol": ...}
        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"