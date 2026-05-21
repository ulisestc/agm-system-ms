from pydantic import BaseModel, Field, field_validator
from models import RolUsuario

# Estructura de los datos que vamos a RECIBIR cuando alguien se registre
class UsuarioCreate(BaseModel):
    email: str
    password: str
    rol: RolUsuario = RolUsuario.ALUMNO

    @field_validator("rol", mode="before")
    @classmethod
    def normalizar_rol(cls, value):
        if isinstance(value, RolUsuario):
            return value
        for rol in RolUsuario:
            if value in {rol.name, rol.value}:
                return rol
        return value

# Estructura de los datos que vamos a DEVOLVER (sin la contraseña)
class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: RolUsuario

    class Config:
        from_attributes = True  # Permite que Pydantic lea el formato de la base de datos


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    message: str
