from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Estadísticas

class EstadisticaMateriaCreate(BaseModel):

    materia_id:           str
    materia_nombre:       str
    materia_nrc:          str
    periodo_nombre:       str
    docente_id:           str
    total_alumnos:        int
    promedio_general:     float
    porcentaje_aprobados: float


class EstadisticaMateriaResponse(BaseModel):
    id:                   int
    materia_id:           str
    materia_nombre:       str
    materia_nrc:          str
    periodo_nombre:       str
    docente_id:           str
    total_alumnos:        int
    promedio_general:     float
    porcentaje_aprobados: float
    fecha_registro:       datetime

    class Config:
        from_attributes = True 


# Reportes
class ReporteGeneradoResponse(BaseModel):
    id:             int
    materia_id:     str
    docente_id:     Optional[str]
    tipo:           str
    formato:        str
    fecha_generado: datetime

    class Config:
        from_attributes = True


class RespuestaBase(BaseModel):
    success: bool
    message: str


class RespuestaEstadistica(RespuestaBase):
    data: Optional[EstadisticaMateriaResponse] = None


class RespuestaListaEstadisticas(RespuestaBase):
    data: Optional[List[EstadisticaMateriaResponse]] = None


class RespuestaReporte(RespuestaBase):
    data: Optional[ReporteGeneradoResponse] = None
