from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from src.database import Base

class SesionAsistencia(Base):
    """Guarda el registro histórico de las sesiones creadas por los docentes"""
    __tablename__ = "sesiones_asistencia"
    
    id = Column(String, primary_key=True, index=True)
    materia_id = Column(String, index=True, nullable=False)
    docente_id = Column(String, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    activa = Column(Boolean, default=True)

class RegistroAsistencia(Base):
    """Guarda si el alumno llegó puntual, con retardo o tiene falta"""
    __tablename__ = "registros_asistencia"
    
    id = Column(Integer, primary_key=True, index=True)
    sesion_id = Column(String, ForeignKey("sesiones_asistencia.id"), nullable=False)
    alumno_id = Column(String, index=True, nullable=False)
    materia_id = Column(String, index=True, nullable=False)
    estado = Column(String, nullable=False)  # "Presente", "Retardo"
    hora_registro = Column(DateTime(timezone=True), server_default=func.now())