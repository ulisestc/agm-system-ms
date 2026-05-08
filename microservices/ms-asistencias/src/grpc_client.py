import grpc
import os
import logging
from src import alumnosdocentes_pb2
from src import alumnosdocentes_pb2_grpc

logger = logging.getLogger("[gRPC-Client ms-asistencias]")

def validar_alumno_en_materia(alumno_id: str, materia_id: str) -> bool:
    ms_docentes_url = os.getenv("MS_DOCENTES_URL", "ms-docentes:50053")
    
    try:
        with grpc.insecure_channel(ms_docentes_url) as channel:
            stub = alumnosdocentes_pb2_grpc.DocentesAlumnosServiceStub(channel)
            request = alumnosdocentes_pb2.AlumnoMateriaRequest(
                alumnoId=alumno_id,
                materiaId=materia_id
            )
            response = stub.IsAlumnoEnMateria(request)
            return response.result
    except Exception as e:
        logger.error(f"Error al conectar con MS-Docentes: {e}")
        return False