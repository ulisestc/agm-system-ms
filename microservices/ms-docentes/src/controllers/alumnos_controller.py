"""
controllers/alumnos_controller.py
Router FastAPI para el recurso /alumnos.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import AlumnoResponse, ImportacionResponse, BajaResponse
from src.services import alumnos_service

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])


@router.post(
    "/importar/{materiaId}",
    response_model=ImportacionResponse,
    summary="Importar lista de alumnos desde Excel",
    description=(
        "Recibe un archivo Excel (.xlsx) con la lista de alumnos inscritos "
        "en la materia identificada por su NRC (materiaId)."
    ),
)
async def importar_alumnos(
    materiaId: str = Path(..., description="NRC de la materia"),
    archivo: UploadFile = File(..., description="Archivo Excel con alumnos"),
    db: Session = Depends(get_db),
):
    if not archivo.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos Excel (.xlsx / .xls)")

    contenido = await archivo.read()
    try:
        total = alumnos_service.importar_alumnos_desde_excel(contenido, materiaId, db)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al procesar el Excel: {exc}")

    return ImportacionResponse(
        mensaje=f"Importación de alumnos para NRC {materiaId} completada",
        registros_importados=total,
    )


@router.get(
    "/materia/{materiaId}",
    response_model=List[AlumnoResponse],
    summary="Listar alumnos activos de una materia",
)
def listar_alumnos(
    materiaId: str = Path(..., description="NRC de la materia"),
    db: Session = Depends(get_db),
):
    return alumnos_service.listar_alumnos_por_materia(materiaId, db)


@router.delete(
    "/{id}/baja",
    response_model=BajaResponse,
    summary="Dar de baja a un alumno de su materia",
    description="Baja lógica: el registro permanece en BD con activo=False para conservar historial.",
)
def dar_baja_alumno(
    id: int = Path(..., description="ID del alumno en la BD"),
    db: Session = Depends(get_db),
):
    alumno = alumnos_service.dar_de_baja(id, db)
    return BajaResponse(
        mensaje=f"Alumno {alumno.nombre} dado de baja correctamente",
        alumno_id=alumno.id,
        nrc=alumno.nrc,
    )
