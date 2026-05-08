"""
controllers/docentes_controller.py
Router FastAPI para el recurso /docentes.
Recibe la solicitud HTTP, valida datos y delega al servicio.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import DocenteResponse, ImportacionResponse
from src.services import docentes_service

router = APIRouter(prefix="/docentes", tags=["Docentes"])


@router.post(
    "/importar",
    response_model=ImportacionResponse,
    summary="Importar directorio docente desde PDF",
    description=(
        "Recibe el PDF oficial de programación académica y extrae automáticamente "
        "NRC, nombre de materia, sección, clave, docente asignado y horario."
    ),
)
async def importar_docentes(
    archivo: UploadFile = File(..., description="PDF de programación académica"),
    db: Session = Depends(get_db),
):
    if not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    contenido = await archivo.read()
    try:
        total = docentes_service.importar_docentes_desde_pdf(contenido, db)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {exc}")

    return ImportacionResponse(
        mensaje="Importación de docentes completada",
        registros_importados=total,
    )


@router.get(
    "/",
    response_model=List[DocenteResponse],
    summary="Listar todos los docentes",
)
def listar_docentes(db: Session = Depends(get_db)):
    return docentes_service.listar_docentes(db)
