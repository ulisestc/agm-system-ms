import json
import os
import logging
from concurrent import futures

import grpc

import reportes_pb2
import reportes_pb2_grpc

from database import SessionLocal
from generadores import generar_excel_calificaciones, generar_pdf_calificaciones
from generadores import generar_excel_asistencias, generar_pdf_asistencias
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[gRPC ms-reportes]")


def _parse_datos(datos_json: str) -> dict | None:
    """Deserializa datos_json; devuelve None si está vacío o es inválido."""
    if not datos_json:
        return None
    try:
        return json.loads(datos_json)
    except json.JSONDecodeError:
        logger.warning("datos_json no es JSON válido; se usarán datos demo.")
        return None


class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):

    def GenerateCalificacionesReport(self, request, context):
        logger.info(
            f"Petición recibida: GenerateCalificacionesReport | "
            f"materia={request.materiaId} | formato={request.formato} | "
            f"datos={'sí' if request.datos_json else 'demo'}"
        )
        try:
            datos = _parse_datos(request.datos_json)

            if request.formato == "xls":
                file_bytes, filename = generar_excel_calificaciones(request.materiaId, datos)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                file_bytes, filename = generar_pdf_calificaciones(request.materiaId, datos)
                content_type = "application/pdf"

            return reportes_pb2.ReportResponse(
                success=True,
                file_bytes=file_bytes,
                filename=filename,
                content_type=content_type,
                error_message="",
            )
        except Exception as e:
            logger.error(f"Error en GenerateCalificacionesReport: {e}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=str(e),
            )

    def GenerateAsistenciasReport(self, request, context):
        logger.info(
            f"Petición recibida: GenerateAsistenciasReport | "
            f"materia={request.materiaId} | formato={request.formato} | "
            f"datos={'sí' if request.datos_json else 'demo'}"
        )
        try:
            datos = _parse_datos(request.datos_json)

            if request.formato == "xls":
                file_bytes, filename = generar_excel_asistencias(request.materiaId, datos)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                file_bytes, filename = generar_pdf_asistencias(request.materiaId, datos)
                content_type = "application/pdf"

            return reportes_pb2.ReportResponse(
                success=True,
                file_bytes=file_bytes,
                filename=filename,
                content_type=content_type,
                error_message="",
            )
        except Exception as e:
            logger.error(f"Error en GenerateAsistenciasReport: {e}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=str(e),
            )

    def GetHistorialDocente(self, request, context):
        logger.info(f"Petición recibida: GetHistorialDocente | docente={request.docenteId}")
        try:
            db = SessionLocal()
            registros = (
                db.query(models.EstadisticaMateria)
                .filter(models.EstadisticaMateria.docente_id == request.docenteId)
                .order_by(models.EstadisticaMateria.fecha_registro.desc())
                .all()
            )
            db.close()

            periodos = [
                reportes_pb2.StatsPeriodo(
                    periodo_nombre=r.periodo_nombre,
                    materia_nombre=r.materia_nombre,
                    materia_nrc=r.materia_nrc,
                    total_alumnos=r.total_alumnos,
                    promedio_general=r.promedio_general,
                    porcentaje_aprobados=r.porcentaje_aprobados,
                )
                for r in registros
            ]

            return reportes_pb2.HistorialDocenteResponse(
                success=True,
                periodos=periodos,
                error_message="",
            )
        except Exception as e:
            logger.error(f"Error en GetHistorialDocente: {e}")
            return reportes_pb2.HistorialDocenteResponse(
                success=False,
                periodos=[],
                error_message=str(e),
            )


def serve():
    port = os.getenv("GRPC_PORT", "50057")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reportes_pb2_grpc.add_ReportesServiceServicer_to_server(ReportesServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info(f"Servidor gRPC de ms-reportes escuchando en puerto {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
