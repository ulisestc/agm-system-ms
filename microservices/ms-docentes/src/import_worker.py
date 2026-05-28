"""
import_worker.py
Consume la cola `docentes_import_jobs_queue` y ejecuta, en background,
la creación de usuarios en ms-auth + envío de notificaciones por cada
registro importado desde PDF.

Se ejecuta en un hilo daemon propio con sus propias conexiones a RabbitMQ,
por lo que no comparte estado con el hilo de FastAPI ni con el servidor RPC.
"""
import json
import logging
import os
import time
import sys

import pika

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models
from rabbitmq_manager import RabbitMQRpcClient, RabbitMQManager

logger = logging.getLogger("[ImportWorker]")
QUEUE_NAME = "docentes_import_jobs_queue"


# ── Conexiones propias del worker (no compartidas con otros hilos) ────────────

def _make_rpc_client() -> RabbitMQRpcClient:
    return RabbitMQRpcClient()


def _make_publisher() -> RabbitMQManager:
    return RabbitMQManager()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_user(rpc: RabbitMQRpcClient, email: str, rol: str) -> dict:
    try:
        return rpc.call("rpc_auth_queue", "crear_usuario", {"email": email, "rol": rol})
    except Exception as e:
        logger.error(f"RPC crear_usuario falló para {email}: {e}")
        return {"success": False, "error_message": str(e)}


def _notify_docente(pub: RabbitMQManager, docente: dict, password: str, token: str):
    try:
        pub.publish_event(
            exchange="events_exchange",
            routing_key="docentes.bienvenida",
            message={
                "docenteId": str(docente["id"]),
                "docenteNombre": docente["nombre"],
                "docenteEmail": docente["email"],
                "claveUnica": password,
                "auth_token": token,
            },
        )
    except Exception as e:
        logger.error(f"Error notificando docente {docente['email']}: {e}")


def _notify_alumno(pub: RabbitMQManager, alumno: dict, materia_nombre: str, password: str, token: str):
    try:
        pub.publish_event(
            exchange="events_exchange",
            routing_key="periodos.bienvenida",
            message={
                "alumnoId": str(alumno["id"]),
                "alumnoNombre": alumno["nombre"],
                "alumnoEmail": alumno["email"],
                "materiaNombre": materia_nombre,
                "claveUnica": password,
                "auth_token": token,
            },
        )
    except Exception as e:
        logger.error(f"Error notificando alumno {alumno['email']}: {e}")


# ── Procesadores de jobs ──────────────────────────────────────────────────────

def _procesar_docentes(data: dict, rpc: RabbitMQRpcClient, pub: RabbitMQManager):
    docente_ids: list = data.get("docente_ids", [])
    token: str = data.get("token", "no-token")
    whitelist: list = data.get("whitelist", [])

    db = SessionLocal()
    try:
        ok = skipped = errors = 0
        for doc_id in docente_ids:
            docente = db.query(models.Docente).filter(models.Docente.id == doc_id).first()
            if not docente or not docente.email:
                skipped += 1
                continue

            res = _create_user(rpc, docente.email, "Docente")
            if not res.get("success"):
                logger.warning(f"No se creó usuario para {docente.email}: {res.get('error_message')}")
                errors += 1
                continue

            ok += 1
            if not whitelist or docente.email.lower() in whitelist:
                _notify_docente(
                    pub,
                    {"id": docente.id, "nombre": docente.nombre, "email": docente.email},
                    res["password"],
                    token,
                )
            else:
                logger.info(f"Notificación omitida (whitelist): {docente.email}")

        logger.info(
            f"Job docentes terminado — creados:{ok} sin_email:{skipped} errores:{errors}"
        )
    finally:
        db.close()


def _procesar_alumnos(data: dict, rpc: RabbitMQRpcClient, pub: RabbitMQManager):
    alumno_ids: list = data.get("alumno_ids", [])
    token: str = data.get("token", "no-token")
    whitelist: list = data.get("whitelist", [])
    materia_nombre: str = data.get("materia_nombre", "")

    db = SessionLocal()
    try:
        ok = skipped = errors = 0
        for alu_id in alumno_ids:
            alumno = db.query(models.Alumno).filter(models.Alumno.id == alu_id).first()
            if not alumno or not alumno.email:
                skipped += 1
                continue

            res = _create_user(rpc, alumno.email, "Alumno")
            if not res.get("success"):
                logger.warning(f"No se creó usuario para {alumno.email}: {res.get('error_message')}")
                errors += 1
                continue

            ok += 1
            if not whitelist or alumno.email.lower() in whitelist:
                _notify_alumno(
                    pub,
                    {
                        "id": alumno.id,
                        "nombre": alumno.nombre,
                        "email": alumno.email,
                        "matricula": alumno.matricula,
                    },
                    materia_nombre,
                    res["password"],
                    token,
                )
            else:
                logger.info(f"Notificación omitida (whitelist): {alumno.email}")

        logger.info(
            f"Job alumnos terminado — creados:{ok} sin_email:{skipped} errores:{errors}"
        )
    finally:
        db.close()


# ── Callback del consumidor ───────────────────────────────────────────────────

def _make_callback(rpc: RabbitMQRpcClient, pub: RabbitMQManager):
    def on_message(ch, method, _properties, body):
        try:
            data = json.loads(body)
            job_type = data.get("job_type")
            logger.info(f"Job recibido: {job_type}")

            if job_type == "crear_usuarios_docentes":
                _procesar_docentes(data, rpc, pub)
            elif job_type == "crear_usuarios_alumnos":
                _procesar_alumnos(data, rpc, pub)
            else:
                logger.warning(f"Tipo de job desconocido: {job_type}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error fatal en job: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    return on_message


# ── Bucle principal con reconexión ────────────────────────────────────────────

def serve():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
    logger.info("ImportWorker iniciando…")

    while True:
        try:
            rpc = _make_rpc_client()
            pub = _make_publisher()

            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=_make_callback(rpc, pub),
            )
            logger.info(f"Consumiendo cola '{QUEUE_NAME}'")
            channel.start_consuming()
        except Exception as e:
            logger.error(f"Conexión perdida, reintentando en 5s: {e}")
            time.sleep(5)
