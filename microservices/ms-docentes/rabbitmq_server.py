import logging
from rabbitmq_manager import RabbitMQRpcServer
from database import SessionLocal
import models

logger = logging.getLogger("[RabbitMQ-RPC ms-docentes]")

class DocentesRpcHandlers:
    def get_alumno(self, data):
        alumno_id = data.get("alumnoId")
        db = SessionLocal()
        try:
            alumno = db.query(models.Alumno).filter(models.Alumno.id == int(alumno_id)).first()
            if alumno:
                return {
                    "success": True,
                    "data": {"nombre": alumno.nombre, "email": alumno.email}
                }
            return {"success": False, "message": "Alumno no encontrado"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def get_alumnos_by_materia(self, data):
        materia_id = data.get("materiaId")
        db = SessionLocal()
        try:
            alumnos = (
                db.query(models.Alumno)
                .filter(
                    models.Alumno.nrc == materia_id,
                    models.Alumno.activo == True,
                )
                .all()
            )
            return {
                "success": True,
                "alumnos": [
                    {"id": str(a.id), "nombre": a.nombre, "email": a.email or ""}
                    for a in alumnos
                ]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def get_alumno_by_id(self, data):
        alumno_id = data.get("id")
        db = SessionLocal()
        try:
            alumno = db.query(models.Alumno).filter(
                models.Alumno.id == int(alumno_id)
            ).first()
            if not alumno:
                return {"success": False, "message": "Alumno no encontrado"}
            return {
                "success": True,
                "data": {
                    "id": str(alumno.id),
                    "nombre": alumno.nombre,
                    "email": alumno.email or "",
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def get_docente_by_id(self, data):
        docente_id = data.get("id")
        db = SessionLocal()
        try:
            docente = db.query(models.Docente).filter(
                models.Docente.id == int(docente_id)
            ).first()
            if not docente:
                return {"success": False, "message": "Docente no encontrado"}
            return {
                "success": True,
                "data": {
                    "id": str(docente.id),
                    "nombre": docente.nombre,
                    "email": docente.email or "",
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def is_alumno_en_materia(self, data):
        alumno_id = data.get("alumnoId")
        materia_id = data.get("materiaId")
        db = SessionLocal()
        try:
            alumno = db.query(models.Alumno).filter(
                models.Alumno.id == int(alumno_id),
                models.Alumno.nrc == materia_id,
                models.Alumno.activo == True
            ).first()
            return {"success": True, "result": bool(alumno)}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    def is_docente_en_materia(self, data):
        docente_id = data.get("docenteId")
        materia_id = data.get("materiaId")
        db = SessionLocal()
        try:
            materia = db.query(models.MateriaDocente).filter(
                models.MateriaDocente.docente_id == int(docente_id),
                models.MateriaDocente.nrc == materia_id
            ).first()
            return {"success": True, "result": bool(materia)}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

def serve():
    handlers = DocentesRpcHandlers()
    server = RabbitMQRpcServer(queue_name='rpc_docentes_queue')
    server.register_action('get_alumno', handlers.get_alumno)
    server.register_action('get_alumnos_by_materia', handlers.get_alumnos_by_materia)
    server.register_action('get_alumno_by_id', handlers.get_alumno_by_id)
    server.register_action('get_docente_by_id', handlers.get_docente_by_id)
    server.register_action('is_alumno_en_materia', handlers.is_alumno_en_materia)
    server.register_action('is_docente_en_materia', handlers.is_docente_en_materia)
    server.start()

if __name__ == "__main__":
    serve()
