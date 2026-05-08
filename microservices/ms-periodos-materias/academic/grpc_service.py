import grpc
from django.conf import settings

from .models import Periodo

import periodos_pb2
import periodos_pb2_grpc


def _periodo_to_message(periodo: Periodo) -> periodos_pb2.PeriodoMessage:
    return periodos_pb2.PeriodoMessage(
        id=periodo.id,
        nombre=periodo.nombre,
        fecha_inicio=periodo.fecha_inicio.isoformat(),
        fecha_fin=periodo.fecha_fin.isoformat(),
        plan_estudios=periodo.plan_estudios,
        activo=periodo.activo,
    )


class PeriodosService(periodos_pb2_grpc.PeriodosServiceServicer):
    def GetPeriodoById(self, request, context):
        periodo = Periodo.objects.filter(id=request.id).first()
        if not periodo:
            context.abort(grpc.StatusCode.NOT_FOUND, "Periodo no encontrado.")
        return periodos_pb2.PeriodoResponse(
            success=True,
            message="Periodo encontrado.",
            data=_periodo_to_message(periodo),
        )

    def GetPeriodoActivo(self, request, context):
        periodo = Periodo.objects.filter(activo=True).first()
        if not periodo:
            context.abort(grpc.StatusCode.NOT_FOUND, "No existe un periodo activo.")
        return periodos_pb2.PeriodoResponse(
            success=True,
            message="Periodo activo encontrado.",
            data=_periodo_to_message(periodo),
        )

    def ListPeriodos(self, request, context):
        items = [_periodo_to_message(periodo) for periodo in Periodo.objects.all()]
        return periodos_pb2.PeriodosResponse(
            success=True,
            message="Listado de periodos obtenido correctamente.",
            data=items,
        )


def grpc_port() -> int:
    return int(getattr(settings, "GRPC_PORT", 50051))
