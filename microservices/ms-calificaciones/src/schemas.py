from pydantic import BaseModel
from typing import List, Optional

class ActividadBase(BaseModel):
    materia_id: str
    nombre: str
    ponderacion: float

class ActividadCreate(ActividadBase):
    pass

class CalificacionBase(BaseModel):
    alumno_id: str
    valor: float

class CalificacionCreate(CalificacionBase):
    actividad_id: str


class PonderacionItem(BaseModel):
    nombre: str
    ponderacion: float


class PonderacionesCreate(BaseModel):
    ponderaciones: list[PonderacionItem]