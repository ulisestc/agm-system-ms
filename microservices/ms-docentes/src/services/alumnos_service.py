"""
services/alumnos_service.py
Lógica de negocio para importación, consulta y baja de alumnos.
"""
import pdfplumber
import re
from io import BytesIO
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

import models


def importar_alumnos_desde_pdf(contenido: bytes, expected_nrc: str, db: Session) -> List[models.Alumno]:
    """
    Lee un archivo PDF con la lista de alumnos inscritos en un NRC.
    El PDF debe tener el formato "Resumen de lista de clase" de BUAP.
    Si el PDF contiene el NRC en el encabezado, lo usa automáticamente;
    si no, usa el expected_nrc recibido en la URL.

    Returns:
        Lista de nuevos objetos Alumno creados.
    """
    alumnos_nuevos = []

    with pdfplumber.open(BytesIO(contenido)) as pdf:
        current_nrc = None

        for pagina in pdf.pages:
            text = pagina.extract_text()
            if not text:
                continue

            # Extraer NRC del encabezado (solo en la primera página donde aparece)
            nrc_match = re.search(r'NRC:\s*(\d+)', text)
            if nrc_match:
                current_nrc = nrc_match.group(1)

            nrc_to_use = current_nrc if current_nrc else expected_nrc

            lines = text.split('\n')
            last_student = None

            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue

                # Línea de alumno: <num> <NOMBRE> <matricula-9-digits> **Inscrito por Web** <nivel> <creditos>
                match = re.search(
                    r'^(\d+)\s+(.*?)\s+(\d{9})\s+\*\*Inscrito por Web\*\*\s+(.+?)\s+([\d\.]+)',
                    line_str
                )
                if match:
                    nombre = match.group(2).strip()
                    matricula = match.group(3).strip()

                    alumno = (
                        db.query(models.Alumno)
                        .filter(
                            models.Alumno.matricula == matricula,
                            models.Alumno.nrc == nrc_to_use,
                        )
                        .first()
                    )
                    if not alumno:
                        alumno = models.Alumno(
                            matricula=matricula,
                            nombre=nombre,
                            email=None,  # El PDF no incluye email
                            nrc=nrc_to_use,
                            activo=True,
                        )
                        db.add(alumno)
                        alumnos_nuevos.append(alumno)
                    else:
                        alumno.nombre = nombre
                        alumno.activo = True

                    last_student = alumno

                elif last_student:
                    # Posible continuación del nombre en la siguiente línea
                    # (solo líneas en mayúsculas sin números ni keywords del PDF)
                    if (
                        not re.match(r'^\d+', line_str)
                        and 'Clase' not in line_str
                        and 'Página' not in line_str
                        and 'Regresar' not in line_str
                        and '©' not in line_str
                        and 'VERSIÓN' not in line_str
                        and re.match(r'^[A-Z\s\.,]+$', line_str)
                    ):
                        last_student.nombre += " " + line_str

    db.commit()
    for a in alumnos_nuevos:
        db.refresh(a)
    return alumnos_nuevos


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
