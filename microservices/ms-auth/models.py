from sqlalchemy import Column, Integer, String, Enum
import enum
from database import Base

# Definimos los roles exactos que exige el manual
class RolUsuario(str, enum.Enum):
    ADMIN = "Administrador"
    DOCENTE = "Docente"
    ALUMNO = "Alumno"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.ALUMNO, nullable=False)