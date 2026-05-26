from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from src.database import Base

class Actividad(Base):
    __tablename__ = "actividades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    materia_id = Column(String, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    ponderacion = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    calificaciones = relationship("Calificacion", back_populates="actividad", cascade="all, delete-orphan")

class Calificacion(Base):
    __tablename__ = "calificaciones"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actividad_id = Column(String, ForeignKey("actividades.id"), nullable=False)
    alumno_id = Column(String, nullable=False, index=True)
    valor = Column(Float, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    actividad = relationship("Actividad", back_populates="calificaciones")