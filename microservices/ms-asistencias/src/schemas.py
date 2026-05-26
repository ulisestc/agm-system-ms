from pydantic import BaseModel


class IniciarSesionRequest(BaseModel):
    materia_id: str
    docente_id: str


class RegistrarAsistenciaRequest(BaseModel):
    alumno_id: str
    materia_id: str
    token_qr: str


class GenerarQRRequest(BaseModel):
    alumno_id: str
    materia_id: str