import json
import os
import logging
from concurrent import futures

import grpc

import reportes_pb2
import reportes_pb2_grpc
import grpc_client

from database import SessionLocal
from generadores import generar_excel_calificaciones, generar_pdf_calificaciones
from generadores import generar_excel_asistencias, generar_pdf_asistencias
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[gRPC ms-reportes]")

VALID_FORMATS = {"pdf", "xls"}


def _parse_datos(datos_json: str) -> dict | None:
    """Deserializa datos_json; devuelve None si está vacío o es inválido."""
    if not datos_json:
        return None
    try:
        return json.loads(datos_json)
    except json.JSONDecodeError:
        logger.warning("datos_json no es JSON válido; se usarán datos demo.")
        return None


def _validate_input(materia_id: str, formato: str) -> tuple[bool, str]:
    """Valida entrada gRPC. Retorna (es_válido, mensaje_error)."""
    if not materia_id or not materia_id.strip():
        return False, "materiaId es requerido"
    
    if formato.lower() not in VALID_FORMATS:
        return False, f"formato debe ser uno de {VALID_FORMATS}"
    
    return True, ""


class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):

    def GenerateCalificacionesReport(self, request, context):
        logger.info(
            f"Petición recibida: GenerateCalificacionesReport | "
            f"materia={request.materiaId} | formato={request.formato}"
        )
        
        # Validar entrada
        es_valido, error_msg = _validate_input(request.materiaId, request.formato)
        if not es_valido:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
            logger.warning(f"Validación fallida: {error_msg}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=error_msg,
            )
        
        try:
            # Obtener datos reales de la materia desde ms-periodos-materias
            materia_info = grpc_client.get_materia_by_id(int(request.materiaId))
            if not materia_info:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Materia {request.materiaId} no encontrada")
                logger.warning(f"Materia {request.materiaId} no encontrada en ms-periodos-materias")
                return reportes_pb2.ReportResponse(
                    success=False,
                    file_bytes=b"",
                    filename="",
                    content_type="",
                    error_message=f"Materia {request.materiaId} no encontrada",
                )
            
            # Usar datos pasados o combinar con datos de materia
            datos = _parse_datos(request.datos_json)
            if not datos:
                # Generar datos demo pero con info real de la materia
                datos = {
                    "materia_nombre": materia_info["nombre"],
                    "materia_nrc": materia_info["nrc"],
                    "periodo": "Período Activo",
                    "docente": materia_info["docente_nombre"],
                    "alumnos": [],  # Se pueden llenar desde otros servicios en futuro
                }
            else:
                # Asegurar que tiene datos de materia
                datos.setdefault("materia_nombre", materia_info["nombre"])
                datos.setdefault("materia_nrc", materia_info["nrc"])

            formato = request.formato.lower()
            if formato == "xls":
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
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"ID de materia inválido: {str(e)}")
            logger.error(f"Argumento inválido en GenerateCalificacionesReport: {e}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=str(e),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno: {str(e)}")
            logger.error(f"Error en GenerateCalificacionesReport: {e}", exc_info=True)
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
            f"materia={request.materiaId} | formato={request.formato}"
        )
        
        # Validar entrada
        es_valido, error_msg = _validate_input(request.materiaId, request.formato)
        if not es_valido:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
            logger.warning(f"Validación fallida: {error_msg}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=error_msg,
            )
        
        try:
            # Obtener datos reales de la materia desde ms-periodos-materias
            materia_info = grpc_client.get_materia_by_id(int(request.materiaId))
            if not materia_info:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Materia {request.materiaId} no encontrada")
                logger.warning(f"Materia {request.materiaId} no encontrada en ms-periodos-materias")
                return reportes_pb2.ReportResponse(
                    success=False,
                    file_bytes=b"",
                    filename="",
                    content_type="",
                    error_message=f"Materia {request.materiaId} no encontrada",
                )
            
            # Usar datos pasados o combinar con datos de materia
            datos = _parse_datos(request.datos_json)
            if not datos:
                # Generar datos demo pero con info real de la materia
                datos = {
                    "materia_nombre": materia_info["nombre"],
                    "materia_nrc": materia_info["nrc"],
                    "periodo": "Período Activo",
                    "docente": materia_info["docente_nombre"],
                    "sesiones": [],  # Se pueden llenar desde otros servicios en futuro
                }
            else:
                # Asegurar que tiene datos de materia
                datos.setdefault("materia_nombre", materia_info["nombre"])
                datos.setdefault("materia_nrc", materia_info["nrc"])

            formato = request.formato.lower()
            if formato == "xls":
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
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"ID de materia inválido: {str(e)}")
            logger.error(f"Argumento inválido en GenerateAsistenciasReport: {e}")
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=str(e),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno: {str(e)}")
            logger.error(f"Error en GenerateAsistenciasReport: {e}", exc_info=True)
            return reportes_pb2.ReportResponse(
                success=False,
                file_bytes=b"",
                filename="",
                content_type="",
                error_message=str(e),
            )

    def GetHistorialDocente(self, request, context):
        logger.info(f"Petición recibida: GetHistorialDocente | docente={request.docenteId}")
        
        # Validar entrada
        if not request.docenteId or not request.docenteId.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("docenteId es requerido")
            logger.warning("GetHistorialDocente: docenteId vacío")
            return reportes_pb2.HistorialDocenteResponse(
                success=False,
                periodos=[],
                error_message="docenteId es requerido",
            )
        
        db = None
        try:
            db = SessionLocal()
            registros = (
                db.query(models.EstadisticaMateria)
                .filter(models.EstadisticaMateria.docente_id == request.docenteId)
                .order_by(models.EstadisticaMateria.fecha_registro.desc())
                .all()
            )

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

            logger.info(f"GetHistorialDocente: {len(periodos)} registros encontrados para docente {request.docenteId}")
            
            return reportes_pb2.HistorialDocenteResponse(
                success=True,
                periodos=periodos,
                error_message="",
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error al consultar historial: {str(e)}")
            logger.error(f"Error en GetHistorialDocente para docente {request.docenteId}: {e}", exc_info=True)
            return reportes_pb2.HistorialDocenteResponse(
                success=False,
                periodos=[],
                error_message=str(e),
            )
        finally:
            if db:
                db.close()


def serve():
    port = os.getenv("GRPC_PORT", "50057")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reportes_pb2_grpc.add_ReportesServiceServicer_to_server(ReportesServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    logger.info(f"Servidor gRPC de ms-reportes escuchando en 0.0.0.0:{port}")
    logger.info("Cliente gRPC habilitado para consultar ms-periodos-materias")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
