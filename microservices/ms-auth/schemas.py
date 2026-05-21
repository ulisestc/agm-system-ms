from pydantic import BaseModel
from models import RolUsuario

# Estructura de los datos que vamos a RECIBIR cuando alguien se registre
class UsuarioCreate(BaseModel):
    email: str
    password: str
    rol: RolUsuario = RolUsuario.ALUMNO

# Estructura de los datos que vamos a DEVOLVER (sin la contraseña)
class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: RolUsuario

    class Config:
        from_attributes = True  # Permite que Pydantic lea el formato de la base de datos