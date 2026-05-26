import os
import logging
from rabbitmq_manager import RabbitMQRpcClient

logger = logging.getLogger("[RabbitMQ-Client ms-reportes]")
rpc_client = RabbitMQRpcClient()

def get_materia_by_id(materia_id: int) -> dict | None:
    """Consulta ms-periodos-materias vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_periodos_queue',
            action='get_materia_by_id',
            data={"id": materia_id}
        )
        if response.get("success"):
            return response.get("data")
        return None
    except Exception as e:
        logger.error(f"Error calling get_materia_by_id: {e}")
        return None

def get_materia_by_nrc(nrc: str) -> dict | None:
    """Consulta ms-periodos-materias vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_periodos_queue',
            action='get_materia_by_nrc',
            data={"nrc": nrc}
        )
        if response.get("success"):
            return response.get("data")
        return None
    except Exception as e:
        logger.error(f"Error calling get_materia_by_nrc: {e}")
        return None

def get_periodo_activo() -> dict | None:
    """Consulta ms-periodos-materias vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_periodos_queue',
            action='get_periodo_activo',
            data={}
        )
        if response.get("success"):
            return response.get("data")
        return None
    except Exception as e:
        logger.error(f"Error calling get_periodo_activo: {e}")
        return None

def get_materias_by_docente(docente_id: int) -> list[dict] | None:
    """Consulta ms-periodos-materias vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_periodos_queue',
            action='list_materias_by_docente',
            data={"docente_id": docente_id}
        )
        if response.get("success"):
            return response.get("data")
        return None
    except Exception as e:
        logger.error(f"Error calling get_materias_by_docente: {e}")
        return None

def get_alumnos_by_materia(materia_id: str) -> list[dict] | None:
    """Consulta ms-docentes vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_docentes_queue',
            action='get_alumnos_by_materia',
            data={"materiaId": materia_id}
        )
        if response.get("success"):
            return response.get("alumnos")
        return None
    except Exception as e:
        logger.error(f"Error calling get_alumnos_by_materia: {e}")
        return None

def get_estadisticas_asistencia(materia_id: str) -> dict | None:
    """Consulta ms-asistencias vía RPC"""
    try:
        response = rpc_client.call(
            queue_name='rpc_asistencias_queue',
            action='get_estadisticas_asistencia',
            data={"materiaId": materia_id}
        )
        if response.get("success"):
            return response
        return None
    except Exception as e:
        logger.error(f"Error calling get_estadisticas_asistencia: {e}")
        return None

def construir_sesiones_asistencia(alumnos: list, materia_id: str) -> list:
    """
    Combina datos de alumnos con sus asistencias reales.
    Si no hay datos, devuelve una estructura vacía/demo.
    """
    sesiones = []
    try:
        for alumno in alumnos:
            resp = rpc_client.call(
                queue_name='rpc_asistencias_queue',
                action='get_asistencia_alumno',
                data={
                    "alumnoId": alumno["id"],
                    "materiaId": materia_id
                }
            )
            if resp.get("success"):
                asistencias = resp.get("asistencias", [])
                sesiones.append({
                    "alumno_id": alumno["id"],
                    "alumno_nombre": alumno["nombre"],
                    "asistencias": asistencias
                })
            else:
                sesiones.append({
                    "alumno_id": alumno["id"],
                    "alumno_nombre": alumno["nombre"],
                    "asistencias": []
                })
        return sesiones
    except Exception as e:
        logger.error(f"Error construyendo sesiones de asistencia: {e}")
        return []
