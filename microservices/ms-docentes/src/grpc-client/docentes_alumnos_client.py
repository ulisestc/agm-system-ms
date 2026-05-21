"""
grpc-client/docentes_alumnos_client.py
Cliente gRPC reutilizable para que OTROS microservicios (ms-asistencias,
ms-calificaciones, ms-reportes, ms-notificaciones) llamen al MS-3.

Uso desde otro servicio:
    from ms_docentes_client import DocentesAlumnosClient

    client = DocentesAlumnosClient()
    alumnos  = client.get_alumnos_by_materia("12345")
    alumno   = client.get_alumno_by_id("7")
    en_materia = client.is_alumno_en_materia("7", "12345")
"""
import os
import grpc
from dotenv import load_dotenv

from src.grpc_generated import alumnosdocentes_pb2
from src.grpc_generated import alumnosdocentes_pb2_grpc

load_dotenv()

# Dirección del servidor MS-3 (configurable por variable de entorno)
MS3_GRPC_HOST = os.getenv("MS3_GRPC_HOST", "localhost")
MS3_GRPC_PORT = os.getenv("MS3_GRPC_PORT", "50053")


class DocentesAlumnosClient:
    """Abstracción del canal gRPC hacia el MS-3."""

    def __init__(self):
        channel = grpc.insecure_channel(f"{MS3_GRPC_HOST}:{MS3_GRPC_PORT}")
        self._stub = alumnosdocentes_pb2_grpc.DocentesAlumnosServiceStub(channel)

    def get_alumnos_by_materia(self, materia_id: str) -> list:
        """GetAlumnosByMateria(materiaId) → [AlumnoInfo]"""
        req = alumnosdocentes_pb2.MateriaIdRequest(materiaId=materia_id)
        resp = self._stub.GetAlumnosByMateria(req)
        return list(resp.alumnos)

    def get_alumno_by_id(self, alumno_id: str):
        """GetAlumnoById(alumnoId) → AlumnoInfo"""
        req = alumnosdocentes_pb2.IdRequest(id=alumno_id)
        return self._stub.GetAlumnoById(req)

    def is_alumno_en_materia(self, alumno_id: str, materia_id: str) -> bool:
        """
        IsAlumnoEnMateria(alumnoId, materiaId) → bool
        Implementado localmente consultando GetAlumnoById y comparando el NRC.
        """
        try:
            alumno = self.get_alumno_by_id(alumno_id)
            # Verificar que el alumno pertenece a la materia solicitada
            alumnos_materia = self.get_alumnos_by_materia(materia_id)
            return any(str(a.id) == str(alumno_id) for a in alumnos_materia)
        except grpc.RpcError:
            return False

    def get_docente_by_id(self, docente_id: str):
        """GetDocenteById(docenteId) → DocenteInfo (usado por ms-notificaciones)"""
        req = alumnosdocentes_pb2.IdRequest(id=docente_id)
        return self._stub.GetDocenteById(req)
