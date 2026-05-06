import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import grpc
import logging
from concurrent import futures
from sqlalchemy.orm import Session

# Importamos los archivos generados por protoc
from src import asistencias_pb2
from src import asistencias_pb2_grpc

from src.database import SessionLocal
from src.models import RegistroAsistencia, SesionAsistencia

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[gRPC ms-asistencias]")

class AsistenciasServicer(asistencias_pb2_grpc.AsistenciasServiceServicer):
    
    def GetAsistenciaAlumno(self, request, context):
        logger.info(f"Petición gRPC: GetAsistenciaAlumno | alumno={request.alumnoId} | materia={request.materiaId}")
        db: Session = SessionLocal()
        try:
            registros = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.alumno_id == request.alumnoId,
                RegistroAsistencia.materia_id == request.materiaId
            ).all()
            
            lista_asistencias = [
                asistencias_pb2.AsistenciaRecord(
                    estado=r.estado,
                    hora_registro=r.hora_registro.strftime("%Y-%m-%d %H:%M:%S")
                ) for r in registros
            ]
            return asistencias_pb2.AsistenciaListResponse(asistencias=lista_asistencias)
        finally:
            db.close()

    def GetEstadisticasAsistencia(self, request, context):
        logger.info(f"Petición gRPC: GetEstadisticasAsistencia | materia={request.materiaId}")
        db: Session = SessionLocal()
        try:
            total_sesiones = db.query(SesionAsistencia).filter(SesionAsistencia.materia_id == request.materiaId).count()
            total_asistencias = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.materia_id == request.materiaId, 
                RegistroAsistencia.estado == "Presente"
            ).count()
            total_retardos = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.materia_id == request.materiaId, 
                RegistroAsistencia.estado == "Retardo"
            ).count()
            
            return asistencias_pb2.EstadisticasResponse(
                total_sesiones=total_sesiones,
                total_asistencias=total_asistencias,
                total_retardos=total_retardos
            )
        finally:
            db.close()

def serve():
    port = os.getenv("GRPC_PORT", "50055")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    asistencias_pb2_grpc.add_AsistenciasServiceServicer_to_server(AsistenciasServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info(f"Servidor gRPC de ms-asistencias escuchando en puerto {port}")
    server.wait_for_termination()