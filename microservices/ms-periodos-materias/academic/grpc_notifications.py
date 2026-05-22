from functools import lru_cache

import grpc
from django.conf import settings

import notificaciones_pb2
import notificaciones_pb2_grpc


@lru_cache(maxsize=1)
def _get_channel():
    return grpc.insecure_channel(settings.MS_NOTIFICACIONES_URL)


def send_cierre_materia(materia_id: int) -> bool:
    stub = notificaciones_pb2_grpc.NotificacionesServiceStub(_get_channel())
    response = stub.SendCierreMateria(
        notificaciones_pb2.CierreMateriaRequest(materiaId=str(materia_id)),
        timeout=5,
    )
    return bool(response.success)
