from dataclasses import dataclass
import os

import jwt

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int | None
    email: str | None
    rol: str | None

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)


class RabbitMQJWTAuthentication(BaseAuthentication):
    """
    Autenticación DRF que valida el Bearer token localmente usando la
    misma SECRET_KEY con la que ms-auth firma los JWT.

    Si no hay header Authorization → retorna None (endpoint público).
    Si el token es inválido → lanza AuthenticationFailed.
    Si es válido → retorna (user, token).
    """

    secret_key = os.getenv("SECRET_KEY", "clave_super_secreta_desarrollo_agm")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # Sin token: las permission_classes decidirán

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return None

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("El token ha caducado.") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationFailed(
                "Token inválido o expirado."
            ) from exc

        user = AuthenticatedUser(
            id=int(payload.get("sub")) if payload.get("sub") is not None else None,
            email=payload.get("email"),
            rol=payload.get("rol"),
        )
        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
