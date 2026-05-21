"""
grpc_client.py

Cliente gRPC para ms-reportes.
Proporciona funciones para consultar datos de otros microservicios vía gRPC.

Servicios consultados:
  - ms-periodos-materias:50052 → obtener información de materias y períodos
"""
import grpc
import os
import logging

try:
    import periodosmaterias_pb2
    import periodosmaterias_pb2_grpc
except ImportError:
    raise ImportError(
        "Falta generar stubs de gRPC. Ejecuta: python generate_grpc.py"
    )

logger = logging.getLogger("[gRPC-Client ms-reportes]")


def get_materia_by_id(materia_id: int) -> dict | None:
    """
    Consulta ms-periodos-materias para obtener información de una materia.
    
    Args:
        materia_id: ID de la materia
        
    Returns:
        Dict con datos de la materia o None si no se encontró
    """
    ms_periodos_url = os.getenv("MS_PERIODOS_URL", "ms-periodos-materias:50052")
    
    try:
        with grpc.insecure_channel(ms_periodos_url) as channel:
            stub = periodosmaterias_pb2_grpc.PeriodosMateriasServiceStub(channel)
            request = periodosmaterias_pb2.MateriaIdRequest(id=materia_id)
            response = stub.GetMateriaById(request)
            
            if response.success:
                return {
                    "id": response.data.id,
                    "nrc": response.data.nrc,
                    "nombre": response.data.nombre,
                    "seccion": response.data.seccion,
                    "clave": response.data.clave,
                    "docente_id": response.data.docente_id,
                    "docente_nombre": response.data.docente_nombre,
                    "horario": response.data.horario,
                    "periodo_id": response.data.periodo_id,
                    "activo": response.data.activo,
                }
            else:
                logger.warning(f"GetMateriaById falló: {response.message}")
                return None
    except grpc.RpcError as e:
        logger.error(
            f"Error gRPC consultando GetMateriaById(id={materia_id}): "
            f"{e.code()} - {e.details()}"
        )
        return None
    except Exception as e:
        logger.error(f"Error inesperado en get_materia_by_id: {e}")
        return None


def get_materia_by_nrc(nrc: str) -> dict | None:
    """
    Consulta ms-periodos-materias para obtener información de una materia por NRC.
    
    Args:
        nrc: NRC (código de registro) de la materia
        
    Returns:
        Dict con datos de la materia o None si no se encontró
    """
    ms_periodos_url = os.getenv("MS_PERIODOS_URL", "ms-periodos-materias:50052")
    
    try:
        with grpc.insecure_channel(ms_periodos_url) as channel:
            stub = periodosmaterias_pb2_grpc.PeriodosMateriasServiceStub(channel)
            request = periodosmaterias_pb2.MateriaByNrcRequest(nrc=nrc)
            response = stub.GetMateriaByNrc(request)
            
            if response.success:
                return {
                    "id": response.data.id,
                    "nrc": response.data.nrc,
                    "nombre": response.data.nombre,
                    "seccion": response.data.seccion,
                    "clave": response.data.clave,
                    "docente_id": response.data.docente_id,
                    "docente_nombre": response.data.docente_nombre,
                    "horario": response.data.horario,
                    "periodo_id": response.data.periodo_id,
                    "activo": response.data.activo,
                }
            else:
                logger.warning(f"GetMateriaByNrc falló: {response.message}")
                return None
    except grpc.RpcError as e:
        logger.error(
            f"Error gRPC consultando GetMateriaByNrc(nrc={nrc}): "
            f"{e.code()} - {e.details()}"
        )
        return None
    except Exception as e:
        logger.error(f"Error inesperado en get_materia_by_nrc: {e}")
        return None


def get_periodo_activo() -> dict | None:
    """
    Consulta ms-periodos-materias para obtener el período activo actual.
    
    Returns:
        Dict con datos del período o None si no hay período activo
    """
    ms_periodos_url = os.getenv("MS_PERIODOS_URL", "ms-periodos-materias:50052")
    
    try:
        with grpc.insecure_channel(ms_periodos_url) as channel:
            stub = periodosmaterias_pb2_grpc.PeriodosMateriasServiceStub(channel)
            request = periodosmaterias_pb2.Empty()
            response = stub.GetPeriodoActivo(request)
            
            if response.success:
                return {
                    "id": response.data.id,
                    "nombre": response.data.nombre,
                    "fecha_inicio": response.data.fecha_inicio,
                    "fecha_fin": response.data.fecha_fin,
                    "plan_estudios": response.data.plan_estudios,
                    "activo": response.data.activo,
                }
            else:
                logger.warning(f"GetPeriodoActivo falló: {response.message}")
                return None
    except grpc.RpcError as e:
        logger.error(
            f"Error gRPC consultando GetPeriodoActivo: "
            f"{e.code()} - {e.details()}"
        )
        return None
    except Exception as e:
        logger.error(f"Error inesperado en get_periodo_activo: {e}")
        return None


def get_materias_by_docente(docente_id: int) -> list[dict] | None:
    """
    Consulta ms-periodos-materias para obtener todas las materias de un docente.
    
    Args:
        docente_id: ID del docente
        
    Returns:
        Lista de dicts con datos de materias o None si error
    """
    ms_periodos_url = os.getenv("MS_PERIODOS_URL", "ms-periodos-materias:50052")
    
    try:
        with grpc.insecure_channel(ms_periodos_url) as channel:
            stub = periodosmaterias_pb2_grpc.PeriodosMateriasServiceStub(channel)
            request = periodosmaterias_pb2.MateriaByDocenteRequest(docente_id=docente_id)
            response = stub.ListMateriasByDocente(request)
            
            if response.success:
                return [
                    {
                        "id": m.id,
                        "nrc": m.nrc,
                        "nombre": m.nombre,
                        "seccion": m.seccion,
                        "clave": m.clave,
                        "docente_id": m.docente_id,
                        "docente_nombre": m.docente_nombre,
                        "horario": m.horario,
                        "periodo_id": m.periodo_id,
                        "activo": m.activo,
                    }
                    for m in response.data
                ]
            else:
                logger.warning(f"ListMateriasByDocente falló: {response.message}")
                return None
    except grpc.RpcError as e:
        logger.error(
            f"Error gRPC consultando ListMateriasByDocente(docente_id={docente_id}): "
            f"{e.code()} - {e.details()}"
        )
        return None
    except Exception as e:
        logger.error(f"Error inesperado en get_materias_by_docente: {e}")
        return None
