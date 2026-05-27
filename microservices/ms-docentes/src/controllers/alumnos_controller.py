"""
controllers/alumnos_controller.py
Router FastAPI para el recurso /alumnos.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import AlumnoResponse, ImportacionResponse, BajaResponse
from src.services import alumnos_service
from src.notifications import send_baja_notif
import models
from auth_middleware import get_current_user_rpc

router = APIRouter(prefix="/alumnos", tags=["Alumnos"], dependencies=[Depends(get_current_user_rpc)])


@router.post(
    "/importar/{materiaId}",
    response_model=ImportacionResponse,
    summary="Importar lista de alumnos desde PDF",
    description=(
        "Recibe un archivo PDF con la lista de alumnos inscritos "
        "en la materia identificada por su NRC (materiaId). "
        "El PDF debe tener el formato de 'Resumen de lista de clase' de BUAP."
    ),
)
async def importar_alumnos(
    materiaId: str = Path(..., description="NRC de la materia"),
    archivo: UploadFile = File(..., description="Archivo PDF con la lista de alumnos"),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    if not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF (.pdf)")

    contenido = await archivo.read()
    try:
        alumnos_nuevos = alumnos_service.importar_alumnos_desde_pdf(contenido, materiaId, db)

        # Notificar Bienvenida
        if alumnos_nuevos:
            token = authorization.replace("Bearer ", "") if authorization else "no-token"
            materia = db.query(models.MateriaDocente).filter(models.MateriaDocente.nrc == materiaId).first()
            materia_nombre = materia.nombre_materia if materia else f"NRC {materiaId}"

            from src.notifications import send_bienvenida_notif
            for alu in alumnos_nuevos:
                alu_dict = {"id": alu.id, "nombre": alu.nombre, "email": alu.email, "matricula": alu.matricula}
                send_bienvenida_notif(alu_dict, materia_nombre, token)

    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al procesar el PDF: {str(exc)}")

    return ImportacionResponse(
        mensaje=f"Importación de alumnos para NRC {materiaId} completada",
        registros_importados=len(alumnos_nuevos),
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
    authorization: Optional[str] = Header(None)
):
    # 1. Realizar la baja en la BD
    alumno = alumnos_service.dar_de_baja(id, db)

    # 2. Obtener datos para la notificación enriquecida
    materia_docente = db.query(models.MateriaDocente).filter(models.MateriaDocente.nrc == alumno.nrc).first()

    if materia_docente and materia_docente.docente:
        docente = materia_docente.docente
        token = authorization.replace("Bearer ", "") if authorization else "no-token"

        alumno_dict = {"id": alumno.id, "nombre": alumno.nombre}
        docente_dict = {"id": docente.id, "nombre": docente.nombre, "email": docente.email}

        send_baja_notif(alumno_dict, docente_dict, token)

    return BajaResponse(
        mensaje=f"Alumno {alumno.nombre} dado de baja correctamente",
        alumno_id=alumno.id,
        nrc=alumno.nrc,
    )
