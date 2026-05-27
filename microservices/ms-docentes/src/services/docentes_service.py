"""
services/docentes_service.py
Lógica de negocio para importación y consulta de docentes.
Separada del controlador para mantener la responsabilidad única.
"""
import pdfplumber
from io import BytesIO
from typing import List
from sqlalchemy.orm import Session

import models


# ── Utilidad interna: parsea una sola página del PDF ──────────────────────────
def _parsear_pagina(pagina) -> List[dict]:
    """
    Extrae filas de la tabla 'Programación Académica' de una página del PDF.
    El PDF de BUAP suele tener columnas en este orden:
      NRC | Clave | Nombre Materia | Sección | Docente | Horario
    Ajusta los índices si el PDF de tu institución es diferente.
    """
    registros = []
    tablas = pagina.extract_tables()
    for tabla in tablas:
        for fila in tabla:
            # Filtramos filas vacías o encabezados
            if not fila or not fila[0]:
                continue
            nrc = str(fila[0]).strip()
            if not nrc.isdigit():          # los NRC son numéricos
                continue
            registros.append({
                "nrc":            nrc,
                "clave":          str(fila[1]).strip() if len(fila) > 1 else "",
                "nombre_materia": str(fila[2]).strip() if len(fila) > 2 else "",
                "seccion":        str(fila[3]).strip() if len(fila) > 3 else "",
                "docente_nombre": str(fila[4]).strip() if len(fila) > 4 else "",
                "horario":        str(fila[5]).strip() if len(fila) > 5 else "",
            })
    return registros


def importar_docentes_desde_pdf(contenido: bytes, db: Session) -> int:
    """
    Procesa el PDF de programación académica y persiste los datos en PostgreSQL.
    Estrategia: upsert por nombre de docente + NRC para evitar duplicados en
    reimportaciones.

    Returns:
        Número de registros de materias importados.
    """
    registros_importados = 0

    with pdfplumber.open(BytesIO(contenido)) as pdf:
        filas = []
        for pagina in pdf.pages:
            filas.extend(_parsear_pagina(pagina))

    for fila in filas:
        nombre_docente = fila["docente_nombre"]
        if not nombre_docente:
            continue

        # 1. Buscar o crear el docente
        docente = (
            db.query(models.Docente)
            .filter(models.Docente.nombre == nombre_docente)
            .first()
        )
        if not docente:
            docente = models.Docente(nombre=nombre_docente)
            db.add(docente)
            db.flush()   # obtenemos el id sin hacer commit todavía

        # 2. Upsert de la materia del docente
        materia = (
            db.query(models.MateriaDocente)
            .filter(
                models.MateriaDocente.docente_id == docente.id,
                models.MateriaDocente.nrc == fila["nrc"],
            )
            .first()
        )
        if not materia:
            materia = models.MateriaDocente(
                docente_id=docente.id,
                nrc=fila["nrc"],
                nombre_materia=fila["nombre_materia"],
                seccion=fila["seccion"],
                clave=fila["clave"],
                horario=fila["horario"],
            )
            db.add(materia)
            registros_importados += 1
        else:
            # Actualiza datos si ya existía
            materia.nombre_materia = fila["nombre_materia"]
            materia.horario = fila["horario"]

    db.commit()
    return registros_importados


def listar_docentes(db: Session) -> List[models.Docente]:
    """Devuelve todos los docentes con sus materias (eager load automático)."""
    return db.query(models.Docente).all()


# ── Importación del Directorio "Personal Docente" ─────────────────────────────
import re

def _parsear_pagina_directorio(pagina) -> List[dict]:
    """
    Extrae texto de una página del PDF "Personal Docente" y lo parsea línea por línea.
    """
    registros = []
    texto = pagina.extract_text()
    if not texto:
        return registros
    
    lineas = texto.split('\n')
    started = False
    
    for line in lineas:
        line = line.strip()
        if not line:
            continue
        # Buscar el encabezado para empezar a parsear (o seguir si ya empezó)
        if "Nombre Correo" in line:
            started = True
            continue
        if not started:
            continue
        
        # Parsear con regex
        match = re.search(r'^(.*?)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*(.*)$', line)
        if match:
            nombre = match.group(1).strip()
            email = match.group(2).strip()
            rest = match.group(3).strip()
            ubicacion = rest.split()[0] if rest else ""
            
            registros.append({
                "nombre": nombre,
                "email": email,
                "ubicacion": ubicacion
            })
            
    return registros

def importar_directorio_docentes_pdf(contenido: bytes, db: Session) -> int:
    """
    Procesa el PDF de "Personal Docente" para actualizar/crear la información de los docentes
    (email y departamento/ubicación).
    
    Returns:
        Número de registros de docentes importados/actualizados.
    """
    registros_importados = 0

    with pdfplumber.open(BytesIO(contenido)) as pdf:
        filas = []
        for pagina in pdf.pages:
            filas.extend(_parsear_pagina_directorio(pagina))

    for fila in filas:
        nombre_docente = fila["nombre"]
        if not nombre_docente:
            continue

        # 1. Buscar o crear el docente
        docente = (
            db.query(models.Docente)
            .filter(models.Docente.nombre == nombre_docente)
            .first()
        )
        if not docente:
            docente = models.Docente(
                nombre=nombre_docente,
                email=fila["email"],
                departamento=fila["ubicacion"]
            )
            db.add(docente)
            registros_importados += 1
        else:
            # Actualiza datos si ya existía y si trajo nueva información
            # Se prioriza la nueva importación
            if fila["email"]:
                docente.email = fila["email"]
            if fila["ubicacion"]:
                docente.departamento = fila["ubicacion"]
            registros_importados += 1

    db.commit()
    return registros_importados
