import json
import os
import logging
from rabbitmq_manager import RabbitMQRpcServer
import rabbitmq_client

from database import SessionLocal
from generadores import generar_excel_calificaciones, generar_pdf_calificaciones
from generadores import generar_excel_asistencias, generar_pdf_asistencias
import models

logger = logging.getLogger("[RabbitMQ-RPC ms-reportes]")
VALID_FORMATS = {"pdf", "xls"}

def _parse_datos(datos_json: str) -> dict | None:
    if not datos_json:
        return None
    try:
        return json.loads(datos_json)
    except json.JSONDecodeError:
        logger.warning("datos_json no es JSON válido; se usarán datos demo.")
        return None

def _validate_input(materia_id: str, formato: str) -> tuple[bool, str]:
    if not materia_id or not materia_id.strip():
        return False, "materiaId es requerido"
    if formato.lower() not in VALID_FORMATS:
        return False, f"formato debe ser uno de {VALID_FORMATS}"
    return True, ""

class ReportesRpcHandlers:
    def generate_calificaciones_report(self, data):
        materia_id = data.get("materiaId")
        formato = data.get("formato")
        
        es_valido, error_msg = _validate_input(materia_id, formato)
        if not es_valido:
            return {"success": False, "error_message": error_msg}
        
        try:
            materia_info = rabbitmq_client.get_materia_by_id(int(materia_id))
            if not materia_info:
                return {"success": False, "error_message": f"Materia {materia_id} no encontrada"}
            
            datos = _parse_datos(data.get("datos_json"))
            if not datos:
                alumnos = rabbitmq_client.get_alumnos_by_materia(materia_id) or []
                datos = {
                    "materia_nombre": materia_info["nombre"],
                    "materia_nrc":    materia_info["nrc"],
                    "periodo":        "Período Activo",
                    "docente":        materia_info["docente_nombre"],
                    "alumnos": [
                        {
                            "matricula":        a["id"],
                            "nombre":           a["nombre"],
                            "promedio_real":    0,
                            "calificacion_final": 0,
                        }
                        for a in alumnos
                    ],
                }
            else:
                datos.setdefault("materia_nombre", materia_info["nombre"])
                datos.setdefault("materia_nrc", materia_info["nrc"])

            if formato.lower() == "xls":
                file_bytes, filename = generar_excel_calificaciones(materia_id, datos)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                file_bytes, filename = generar_pdf_calificaciones(materia_id, datos)
                content_type = "application/pdf"

            import base64
            return {
                "success": True,
                "file_bytes": base64.b64encode(file_bytes).decode('utf-8'),
                "filename": filename,
                "content_type": content_type,
                "error_message": "",
            }
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    def generate_asistencias_report(self, data):
        materia_id = data.get("materiaId")
        formato = data.get("formato")
        
        es_valido, error_msg = _validate_input(materia_id, formato)
        if not es_valido:
            return {"success": False, "error_message": error_msg}
        
        try:
            materia_info = rabbitmq_client.get_materia_by_id(int(materia_id))
            if not materia_info:
                return {"success": False, "error_message": f"Materia {materia_id} no encontrada"}
            
            datos = _parse_datos(data.get("datos_json"))
            if not datos:
                datos = {
                    "materia_nombre": materia_info["nombre"],
                    "materia_nrc": materia_info["nrc"],
                    "periodo": "Período Activo",
                    "docente": materia_info["docente_nombre"],
                    "sesiones": [],
                }
            else:
                datos.setdefault("materia_nombre", materia_info["nombre"])
                datos.setdefault("materia_nrc", materia_info["nrc"])

            if formato.lower() == "xls":
                file_bytes, filename = generar_excel_asistencias(materia_id, datos)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                file_bytes, filename = generar_pdf_asistencias(materia_id, datos)
                content_type = "application/pdf"

            import base64
            return {
                "success": True,
                "file_bytes": base64.b64encode(file_bytes).decode('utf-8'),
                "filename": filename,
                "content_type": content_type,
                "error_message": "",
            }
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    def get_historial_docente(self, data):
        docente_id = data.get("docenteId")
        if not docente_id:
            return {"success": False, "error_message": "docenteId es requerido"}
        
        db = SessionLocal()
        try:
            registros = (
                db.query(models.EstadisticaMateria)
                .filter(models.EstadisticaMateria.docente_id == docente_id)
                .order_by(models.EstadisticaMateria.fecha_registro.desc())
                .all()
            )

            periodos = [
                {
                    "periodo_nombre": r.periodo_nombre,
                    "materia_nombre": r.materia_nombre,
                    "materia_nrc": r.materia_nrc,
                    "total_alumnos": r.total_alumnos,
                    "promedio_general": r.promedio_general,
                    "porcentaje_aprobados": r.porcentaje_aprobados,
                }
                for r in registros
            ]
            
            return {
                "success": True,
                "periodos": periodos,
                "error_message": "",
            }
        except Exception as e:
            return {"success": False, "error_message": str(e)}
        finally:
            db.close()

def serve():
    handlers = ReportesRpcHandlers()
    server = RabbitMQRpcServer(queue_name='rpc_reportes_queue')
    server.register_action('generate_calificaciones_report', handlers.generate_calificaciones_report)
    server.register_action('generate_asistencias_report', handlers.generate_asistencias_report)
    server.register_action('get_historial_docente', handlers.get_historial_docente)
    server.start()

if __name__ == "__main__":
    serve()
