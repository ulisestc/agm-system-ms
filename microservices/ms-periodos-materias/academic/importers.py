import re
from dataclasses import dataclass

from pypdf import PdfReader

from .models import Materia, Periodo


SECTION_RE = re.compile(r"^(?:\d{1,3}[A-Za-z]?|[A-Za-z]{1,3}\d{1,3})$")
CLAVE_RE = re.compile(r"^[A-Z]{2,10}-?\d{2,5}$")
NRC_RE = re.compile(r"(?<!\d)(\d{4,6})(?!\d)")


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


def _split_columns(line: str) -> list[str]:
    normalized = line.replace("|", " ")
    parts = [part.strip() for part in re.split(r"\t+|\s{2,}", normalized) if part.strip()]
    if len(parts) <= 1:
        parts = [part.strip() for part in normalized.split() if part.strip()]
    return parts


def _find_section_index(parts: list[str]) -> int | None:
    for index, part in enumerate(parts[1:], start=1):
        if SECTION_RE.match(part):
            return index
    return None


def _extract_docente_id(docente_text: str, docente_id_default: int | None) -> int | None:
    match = re.search(r"(\d+)", docente_text)
    if match:
        value = int(match.group(1))
        if value > 0:
            return value
    return docente_id_default


def _clean_docente_nombre(docente_text: str) -> str:
    cleaned = re.sub(r"\b\d+\b", " ", docente_text).strip()
    return re.sub(r"\s{2,}", " ", cleaned)


def parse_materia_line(line: str, docente_id_default: int | None = None) -> ImportRow | None:
    raw = line.strip()
    if not raw:
        return None

    upper = raw.upper()
    if any(keyword in upper for keyword in {"NRC", "MATERIA", "SECCION", "SECCIÓN", "DOCENTE", "HORARIO"}):
        return None

    nrc_match = NRC_RE.search(raw)
    if not nrc_match:
        return None

    parts = _split_columns(raw)
    if len(parts) < 3:
        return None

    if parts[0] != nrc_match.group(1):
        # Normaliza el NRC al inicio para evitar formatos mixtos.
        parts = [nrc_match.group(1)] + [part for part in parts if part != nrc_match.group(1)]

    nrc = parts[0]
    section_index = _find_section_index(parts)

    if section_index is None and len(parts) >= 5:
        section_index = 2

    if section_index is None or section_index + 1 >= len(parts):
        return None

    nombre_chunks = parts[1:section_index]
    clave = ""
    filtered_nombre_chunks = []
    for chunk in nombre_chunks:
        if not clave and CLAVE_RE.match(chunk):
            clave = chunk
            continue
        filtered_nombre_chunks.append(chunk)

    nombre = " ".join(filtered_nombre_chunks).strip() or parts[1].strip()
    seccion = parts[section_index].strip()

    docente_chunk = parts[section_index + 1].strip() if section_index + 1 < len(parts) else ""
    horario_chunks = parts[section_index + 2 :] if section_index + 2 < len(parts) else []
    horario = " ".join(horario_chunks).strip()

    docente_id = _extract_docente_id(docente_chunk, docente_id_default)
    if docente_id is None:
        return None

    docente_nombre = _clean_docente_nombre(docente_chunk) or docente_chunk
    if not horario and len(parts) > section_index + 1:
        # Si el formato vino comprimido, al menos intenta conservar el resto del texto.
        horario = " ".join(parts[section_index + 1 :]).strip()

    return ImportRow(
        nrc=nrc,
        nombre=nombre,
        seccion=seccion,
        clave=clave,
        docente_id=docente_id,
        docente_nombre=docente_nombre,
        horario=horario,
    )


def parse_materia_rows(text: str, docente_id_default: int | None = None) -> list[ImportRow]:
    rows: list[ImportRow] = []
    for line in text.splitlines():
        row = parse_materia_line(line, docente_id_default=docente_id_default)
        if row:
            rows.append(row)
    return rows


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
    text = extract_text_from_pdf(uploaded_file)
    return import_materias_from_text(text, periodo_id=periodo_id, docente_id_default=docente_id_default)
