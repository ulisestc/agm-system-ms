import logging
from src.rabbitmq_manager import RabbitMQRpcServer
from src.database import SessionLocal
from src.models import RegistroAsistencia, SesionAsistencia

logger = logging.getLogger("[RabbitMQ-RPC ms-asistencias]")

class AsistenciasRpcHandlers:
    def get_asistencia_alumno(self, data):
        alumno_id = data.get("alumnoId")
        materia_id = data.get("materiaId")
        db = SessionLocal()
        try:
            registros = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.alumno_id == alumno_id,
                RegistroAsistencia.materia_id == materia_id
            ).all()
            
            return {
                "success": True,
                "asistencias": [
                    {
                        "estado": r.estado,
                        "hora_registro": r.hora_registro.strftime("%Y-%m-%d %H:%M:%S")
                    } for r in registros
                ]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def get_estadisticas_asistencia(self, data):
        materia_id = data.get("materiaId")
        db = SessionLocal()
        try:
            total_sesiones = db.query(SesionAsistencia).filter(SesionAsistencia.materia_id == materia_id).count()
            total_asistencias = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.materia_id == materia_id, 
                RegistroAsistencia.estado == "Presente"
            ).count()
            total_retardos = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.materia_id == materia_id, 
                RegistroAsistencia.estado == "Retardo"
            ).count()
            
            return {
                "success": True,
                "total_sesiones": total_sesiones,
                "total_asistencias": total_asistencias,
                "total_retardos": total_retardos
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

def serve():
    handlers = AsistenciasRpcHandlers()
    server = RabbitMQRpcServer(queue_name='rpc_asistencias_queue')
    server.register_action('get_asistencia_alumno', handlers.get_asistencia_alumno)
    server.register_action('get_estadisticas_asistencia', handlers.get_estadisticas_asistencia)
    server.start()

if __name__ == "__main__":
    serve()
