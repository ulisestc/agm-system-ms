"""
grpc_server.py
Servidor gRPC interno del MS-3.
Implementa los métodos definidos en /proto/alumnosdocentes.proto
para ser consumidos por otros microservicios (ms-asistencias, ms-calificaciones, etc.)
"""
import os
import grpc
from concurrent import futures
from dotenv import load_dotenv

# Código generado por grpcio-tools a partir de alumnosdocentes.proto
from src.grpc_generated import alumnosdocentes_pb2
from src.grpc_generated import alumnosdocentes_pb2_grpc

from database import SessionLocal
import models

load_dotenv()
GRPC_PORT = os.getenv("GRPC_PORT", "50053")


class DocentesAlumnosServicer(alumnosdocentes_pb2_grpc.DocentesAlumnosServiceServicer):
    """
    Implementación de los 3 métodos gRPC del contrato proto:
      1. GetAlumnosByMateria(materiaId) → [AlumnoInfo]
      2. GetAlumnoById(alumnoId)        → AlumnoInfo
      3. GetDocenteById(docenteId)      → DocenteInfo   (requerido por ms-notificaciones)
    El método IsAlumnoEnMateria se resuelve en el cliente llamando a GetAlumnoById
    y comprobando el NRC, pero se documenta aquí como patrón de referencia.
    """

    def _get_db(self):
        """Crea una sesión de BD para cada llamada gRPC (equivalente a get_db en FastAPI)."""
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise

    # ── 1. GetAlumnosByMateria ─────────────────────────────────────────────────
    def GetAlumnosByMateria(self, request, context):
        db = SessionLocal()
        try:
            alumnos = (
                db.query(models.Alumno)
                .filter(
                    models.Alumno.nrc == request.materiaId,
                    models.Alumno.activo == True,
                )
                .all()
            )
            lista = [
                alumnosdocentes_pb2.AlumnoInfo(
                    id=str(a.id),
                    nombre=a.nombre,
                    email=a.email or "",
                )
                for a in alumnos
            ]
            return alumnosdocentes_pb2.AlumnosListResponse(alumnos=lista)
        finally:
            db.close()

    # ── 2. GetAlumnoById ──────────────────────────────────────────────────────
    def GetAlumnoById(self, request, context):
        db = SessionLocal()
        try:
            alumno = db.query(models.Alumno).filter(
                models.Alumno.id == int(request.id)
            ).first()
            if not alumno:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Alumno con id={request.id} no encontrado")
                return alumnosdocentes_pb2.AlumnoInfo()
            return alumnosdocentes_pb2.AlumnoInfo(
                id=str(alumno.id),
                nombre=alumno.nombre,
                email=alumno.email or "",
            )
        finally:
            db.close()

    # ── 3. GetDocenteById ─────────────────────────────────────────────────────
    def GetDocenteById(self, request, context):
        db = SessionLocal()
        try:
            docente = db.query(models.Docente).filter(
                models.Docente.id == int(request.id)
            ).first()
            if not docente:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Docente con id={request.id} no encontrado")
                return alumnosdocentes_pb2.DocenteInfo()
            return alumnosdocentes_pb2.DocenteInfo(
                id=str(docente.id),
                nombre=docente.nombre,
                email=docente.email or "",
            )
        finally:
            db.close()

    # ── 4. IsAlumnoEnMateria ──────────────────────────────────────────────────
    def IsAlumnoEnMateria(self, request, context):
        db = SessionLocal()
        try:
            alumno = db.query(models.Alumno).filter(
                models.Alumno.id == int(request.alumnoId),
                models.Alumno.nrc == request.materiaId,
                models.Alumno.activo == True
            ).first()
            return alumnosdocentes_pb2.BoolResponse(result=bool(alumno))
        finally:
            db.close()


def serve():
    """Arranca el servidor gRPC en un pool de hilos."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    alumnosdocentes_pb2_grpc.add_DocentesAlumnosServiceServicer_to_server(
        DocentesAlumnosServicer(), server
    )
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    print(f"[gRPC] MS-3 escuchando en puerto {GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
