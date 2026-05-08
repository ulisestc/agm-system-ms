"""
services/alumnos_service.py
Lógica de negocio para importación, consulta y baja de alumnos.
"""
import openpyxl
from io import BytesIO
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

import models


def importar_alumnos_desde_excel(contenido: bytes, nrc: str, db: Session) -> int:
    """
    Lee un archivo Excel con la lista de alumnos inscritos en un NRC.
    Columnas esperadas (A-D):
      Matrícula | Nombre | Email | NRC  (el NRC también puede tomarse del parámetro)

    Estrategia: upsert por (matricula, nrc) para tolerar reimportaciones.

    Returns:
        Número de alumnos nuevos importados.
    """
    wb = openpyxl.load_workbook(BytesIO(contenido), read_only=True, data_only=True)
    ws = wb.active

    registros_importados = 0
    primera_fila = True

    for fila in ws.iter_rows(values_only=True):
        # Saltar encabezado
        if primera_fila:
            primera_fila = False
            continue

        if not fila[0]:          # matrícula vacía → fila inválida
            continue

        matricula = str(fila[0]).strip()
        nombre    = str(fila[1]).strip() if fila[1] else ""
        email     = str(fila[2]).strip() if len(fila) > 2 and fila[2] else None
        nrc_fila  = str(fila[3]).strip() if len(fila) > 3 and fila[3] else nrc

        alumno = (
            db.query(models.Alumno)
            .filter(
                models.Alumno.matricula == matricula,
                models.Alumno.nrc == nrc_fila,
            )
            .first()
        )
        if not alumno:
            alumno = models.Alumno(
                matricula=matricula,
                nombre=nombre,
                email=email,
                nrc=nrc_fila,
                activo=True,
            )
            db.add(alumno)
            registros_importados += 1
        else:
            # Re-activar si estaba dado de baja (reimportación)
            alumno.nombre = nombre
            alumno.activo = True

    db.commit()
    return registros_importados


def listar_alumnos_por_materia(nrc: str, db: Session) -> List[models.Alumno]:
    """Retorna sólo alumnos ACTIVOS de un NRC."""
    return (
        db.query(models.Alumno)
        .filter(models.Alumno.nrc == nrc, models.Alumno.activo == True)
        .all()
    )


def dar_de_baja(alumno_id: int, db: Session) -> models.Alumno:
    """
    Baja lógica: marca el campo activo=False.
    No se elimina el registro para conservar historial.
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail=f"Alumno {alumno_id} no encontrado")
    if not alumno.activo:
        raise HTTPException(status_code=409, detail="El alumno ya está dado de baja")

    alumno.activo = False
    db.commit()
    db.refresh(alumno)
    return alumno
