from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from pypdf import PdfReader

from .models import Materia, Periodo


NRC_RE = re.compile(r"^\d{4,6}$")
TIME_RE = re.compile(r"^\d{4}-\d{4}$")
SECTION_RE = re.compile(r"^(?:O{2}\d{1,3}|\d{3}|[A-Z]{1,3}\d{1,3})$")
HEADER_MARKERS = {
    "SECRETARÍA ACADÉMICA",
    "PROGRAMACIÓN ACADÉMICA",
    "INGENIERÍA EN TECNOLOGÍAS DE LA INFORMACIÓN",
    "PLAN SEMESTRAL",
    "NRC",
    "CLAVE",
    "MATERIA",
    "SECC",
    "DÍAS",
    "DIA",
    "HORA",
    "PROFESOR",
    "SALÓN",
    "SALON",
}
DAY_TOKENS = {"L", "M", "A", "J", "V", "S"}


@dataclass
class ImportRow:
    nrc: str
    nombre: str
    seccion: str
    clave: str
    docente_id: int
    docente_nombre: str
    horario: str


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text)
    return "\n".join(pages)


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _is_header_line(line: str) -> bool:
    upper = line.upper()
    return any(marker in upper for marker in HEADER_MARKERS)


def _looks_like_record_start(line: str) -> bool:
    if not line:
        return False
    first_token = line.split(" ", 1)[0]
    return bool(NRC_RE.match(first_token))


def _is_section_token(token: str) -> bool:
    return bool(SECTION_RE.match(token))


def _is_time_token(token: str) -> bool:
    return bool(TIME_RE.match(token))


def _is_day_token(token: str) -> bool:
    return token in DAY_TOKENS


def _is_salon_token(token: str) -> bool:
    if not token:
        return False
    upper = token.upper()
    return (
        upper in {"POR", "ASIGNAR", "MATERIA", "CRUZADA", "CON", "NRC"}
        or token[0].isdigit()
    )


def _fallback_docente_id(docente_text: str) -> int:
    digest = hashlib.sha1(docente_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 2_000_000_000 or 1


def _extract_docente_id(docente_text: str, docente_id_default: int | None) -> int:
    match = re.search(r"(\d+)", docente_text)
    if match:
        value = int(match.group(1))
        if value > 0:
            return value

    if docente_id_default is not None:
        return docente_id_default

    cleaned = docente_text.strip()
    if cleaned:
        return _fallback_docente_id(cleaned)
    return 1


def _clean_docente_nombre(docente_text: str) -> str:
    cleaned = re.sub(r"\b\d+\b", " ", docente_text).strip()
    return re.sub(r"\s{2,}", " ", cleaned)


def _split_record_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    for raw_line in text.splitlines():
        line = _normalize_line(raw_line)
        if not line or _is_header_line(line):
            continue

        if _looks_like_record_start(line):
            if current:
                blocks.append(" ".join(current))
            current = [line]
        elif current:
            current.append(line)

    if current:
        blocks.append(" ".join(current))

    return blocks


def _parse_record_block(block: str, docente_id_default: int | None = None) -> ImportRow | None:
    tokens = block.split()
    if len(tokens) < 8:
        return None

    if not NRC_RE.match(tokens[0]):
        return None

    nrc = tokens[0]

    if len(tokens) >= 3 and tokens[2].isdigit():
        clave = f"{tokens[1]} {tokens[2]}"
        cursor = 3
    else:
        clave = tokens[1] if len(tokens) > 1 else ""
        cursor = 2

    section_index = None
    for index in range(cursor, len(tokens)):
        if _is_section_token(tokens[index]):
            section_index = index
            break
    if section_index is None or section_index + 2 >= len(tokens):
        return None

    nombre = " ".join(tokens[cursor:section_index]).strip()
    if not nombre:
        return None

    seccion = tokens[section_index]
    day_token = tokens[section_index + 1]
    time_token = tokens[section_index + 2]
    if not _is_day_token(day_token) or not _is_time_token(time_token):
        return None

    remaining = tokens[section_index + 3 :]
    professor_tokens: list[str] = []
    for token in remaining:
        if _is_salon_token(token):
            break
        professor_tokens.append(token)

    docente_nombre = _clean_docente_nombre(" ".join(professor_tokens)) or "POR ASIGNAR"
    docente_id = _extract_docente_id(docente_nombre, docente_id_default)

    return ImportRow(
        nrc=nrc,
        nombre=nombre,
        seccion=seccion,
        clave=clave,
        docente_id=docente_id,
        docente_nombre=docente_nombre,
        horario=f"{day_token} {time_token}",
    )


def parse_materia_rows(text: str, docente_id_default: int | None = None) -> list[ImportRow]:
    aggregated: dict[str, ImportRow] = {}

    for block in _split_record_blocks(text):
        row = _parse_record_block(block, docente_id_default=docente_id_default)
        if not row:
            continue

        existing = aggregated.get(row.nrc)
        if existing is None:
            aggregated[row.nrc] = row
            continue

        existing_horarios = existing.horario.split(" ; ") if existing.horario else []
        if row.horario not in existing_horarios:
            existing_horarios.append(row.horario)
        existing.horario = " ; ".join([item for item in existing_horarios if item])
        if not existing.docente_nombre or existing.docente_nombre == "POR ASIGNAR":
            existing.docente_nombre = row.docente_nombre
        if not existing.docente_id:
            existing.docente_id = row.docente_id

    return list(aggregated.values())


def import_materias_from_text(
    text: str,
    periodo_id: int,
    docente_id_default: int | None = None,
) -> dict:
    if not Periodo.objects.filter(id=periodo_id).exists():
        raise ValueError("El periodo indicado no existe.")

    rows = parse_materia_rows(text, docente_id_default=docente_id_default)
    if not rows:
        raise ValueError("No se detectaron filas válidas para importar.")

    created = 0
    updated = 0
    skipped: list[dict] = []

    for row in rows:
        defaults = {
            "nombre": row.nombre,
            "seccion": row.seccion,
            "clave": row.clave,
            "docente_id": row.docente_id,
            "docente_nombre": row.docente_nombre,
            "horario": row.horario,
            "periodo_id": periodo_id,
            "activo": True,
        }

        try:
            _, created_flag = Materia.objects.update_or_create(
                nrc=row.nrc,
                defaults=defaults,
            )
        except Exception as exc:
            skipped.append({"nrc": row.nrc, "error": str(exc)})
            continue

        if created_flag:
            created += 1
        else:
            updated += 1

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "total_detected": len(rows),
    }


def import_materias_from_pdf(
    uploaded_file,
    periodo_id: int,
    docente_id_default: int | None = None,
) -> dict:
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    text = extract_text_from_pdf(uploaded_file)
    return import_materias_from_text(
        text,
        periodo_id=periodo_id,
        docente_id_default=docente_id_default,
    )
