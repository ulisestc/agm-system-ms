"""
schemas.py – Contratos de datos (Pydantic) para el MS-3: Docentes & Alumnos
Separados en Request / Response siguiendo el patrón de ms-auth.
"""
from pydantic import BaseModel
from typing import Optional, List


# ──────────────────────────────────────────────────────────────────────────────
# DOCENTES
# ──────────────────────────────────────────────────────────────────────────────

class MateriaDocenteResponse(BaseModel):
    id: int
    nrc: str
    nombre_materia: str
    seccion: Optional[str] = None
    clave: Optional[str] = None
    horario: Optional[str] = None

    class Config:
        from_attributes = True


class DocenteResponse(BaseModel):
    id: int
    nombre: str
    email: Optional[str] = None
    departamento: Optional[str] = None
    materias: List[MateriaDocenteResponse] = []

    class Config:
        from_attributes = True


class ImportacionResponse(BaseModel):
    """Respuesta genérica para operaciones de importación."""
    mensaje: str
    registros_importados: int


# ──────────────────────────────────────────────────────────────────────────────
# ALUMNOS
# ──────────────────────────────────────────────────────────────────────────────

class AlumnoResponse(BaseModel):
    id: int
    matricula: str
    nombre: str
    email: Optional[str] = None
    nrc: str
    activo: bool

    class Config:
        from_attributes = True


class BajaResponse(BaseModel):
    """Confirmación de baja de materia."""
    mensaje: str
    alumno_id: int
    nrc: str
