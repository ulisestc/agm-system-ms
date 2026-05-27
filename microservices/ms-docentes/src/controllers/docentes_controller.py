"""
controllers/docentes_controller.py
Router FastAPI para el recurso /docentes.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas import ImportacionResponse
from src.services import docentes_service
from auth_middleware import get_current_user_rpc

router = APIRouter(prefix="/docentes", tags=["Docentes"], dependencies=[Depends(get_current_user_rpc)])


def _docente_dict(docente) -> dict:
    return {
        "id": docente.id,
        "nombre": docente.nombre,
        "apellido": "",
        "email": docente.email,
        "clave_empleado": "",
        "departamento": docente.departamento,
        "materias": [
            {
                "id": materia.id,
                "nrc": materia.nrc,
                "nombre_materia": materia.nombre_materia,
                "seccion": materia.seccion,
                "clave": materia.clave,
                "horario": materia.horario,
            }
            for materia in docente.materias
        ],
    }


def _resolver_archivo(archivo: UploadFile | None, file: UploadFile | None) -> UploadFile:
    resolved = archivo or file
    if resolved is None:
        raise HTTPException(status_code=400, detail="Se requiere un archivo PDF")
    if not resolved.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")
    return resolved


@router.post(
    "/importar",
    response_model=ImportacionResponse,
    summary="Importar programacion academica desde PDF",
)
async def importar_docentes(
    archivo: UploadFile = File(None, description="PDF de programacion academica"),
    file: UploadFile = File(None, description="Alias usado por algunos frontends"),
    db: Session = Depends(get_db),
):
    archivo = _resolver_archivo(archivo, file)
    contenido = await archivo.read()
    try:
        total = docentes_service.importar_docentes_desde_pdf(contenido, db)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {exc}")

    return ImportacionResponse(
        mensaje="Importacion de docentes completada",
        registros_importados=total,
    )


@router.post(
    "/importar-directorio",
    response_model=ImportacionResponse,
    summary="Importar informacion adicional de Personal Docente desde PDF",
)
async def importar_directorio_docentes(
    archivo: UploadFile = File(None, description="PDF de directorio de personal docente"),
    file: UploadFile = File(None, description="Alias usado por algunos frontends"),
    db: Session = Depends(get_db),
):
    archivo = _resolver_archivo(archivo, file)
    contenido = await archivo.read()
    try:
        total = docentes_service.importar_directorio_docentes_pdf(contenido, db)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF del directorio: {exc}")

    return ImportacionResponse(
        mensaje="Importacion del directorio docente completada",
        registros_importados=total,
    )


@router.get(
    "/",
    summary="Listar todos los docentes",
)
def listar_docentes(
    page: int = 1,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    docentes = docentes_service.buscar_docentes(db, search)
    return {"count": len(docentes), "next": None, "previous": None, "results": [_docente_dict(d) for d in docentes]}
