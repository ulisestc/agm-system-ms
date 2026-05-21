import grpc
from django.conf import settings

from .models import Periodo, Materia

import periodosmaterias_pb2
import periodosmaterias_pb2_grpc


def _periodo_to_message(periodo: Periodo) -> periodosmaterias_pb2.PeriodoMessage:
    return periodosmaterias_pb2.PeriodoMessage(
        id=periodo.id,
        nombre=periodo.nombre,
        fecha_inicio=periodo.fecha_inicio.isoformat(),
        fecha_fin=periodo.fecha_fin.isoformat(),
        plan_estudios=periodo.plan_estudios,
        activo=periodo.activo,
    )


def _materia_to_message(materia: Materia) -> periodosmaterias_pb2.MateriaMessage:
    return periodosmaterias_pb2.MateriaMessage(
        id=materia.id,
        nrc=materia.nrc,
        nombre=materia.nombre,
        seccion=materia.seccion,
        clave=materia.clave,
        docente_id=materia.docente_id,
        docente_nombre=materia.docente_nombre,
        horario=materia.horario,
        periodo_id=materia.periodo_id,
        activo=materia.activo,
    )


class PeriodosMateriasService(periodosmaterias_pb2_grpc.PeriodosMateriasServiceServicer):
    def GetPeriodoById(self, request, context):
        periodo = Periodo.objects.filter(id=request.id).first()
        if not periodo:
            context.abort(grpc.StatusCode.NOT_FOUND, "Periodo no encontrado.")
        return periodosmaterias_pb2.PeriodoResponse(
            success=True,
            message="Periodo encontrado.",
            data=_periodo_to_message(periodo),
        )

    def GetPeriodoActivo(self, request, context):
        periodo = Periodo.objects.filter(activo=True).first()
        if not periodo:
            context.abort(grpc.StatusCode.NOT_FOUND, "No existe un periodo activo.")
        return periodosmaterias_pb2.PeriodoResponse(
            success=True,
            message="Periodo activo encontrado.",
            data=_periodo_to_message(periodo),
        )

    def ListPeriodos(self, request, context):
        items = [_periodo_to_message(periodo) for periodo in Periodo.objects.all()]
        return periodosmaterias_pb2.PeriodosResponse(
            success=True,
            message="Listado de periodos obtenido correctamente.",
            data=items,
        )

    def GetMateriaById(self, request, context):
        materia = Materia.objects.filter(id=request.id).first()
        if not materia:
            context.abort(grpc.StatusCode.NOT_FOUND, "Materia no encontrada.")
        return periodosmaterias_pb2.MateriaResponse(
            success=True,
            message="Materia encontrada.",
            data=_materia_to_message(materia),
        )

    def GetMateriaByNrc(self, request, context):
        materia = Materia.objects.filter(nrc=request.nrc).first()
        if not materia:
            context.abort(grpc.StatusCode.NOT_FOUND, "Materia no encontrada.")
        return periodosmaterias_pb2.MateriaResponse(
            success=True,
            message="Materia encontrada.",
            data=_materia_to_message(materia),
        )

    def ListMaterias(self, request, context):
        items = [_materia_to_message(materia) for materia in Materia.objects.all()]
        return periodosmaterias_pb2.MateriasResponse(
            success=True,
            message="Listado de materias obtenido correctamente.",
            data=items,
        )

    def ListMateriasByPeriodo(self, request, context):
        items = [_materia_to_message(materia) for materia in Materia.objects.filter(periodo_id=request.periodo_id)]
        return periodosmaterias_pb2.MateriasResponse(
            success=True,
            message="Listado de materias por periodo obtenido correctamente.",
            data=items,
        )

    def ListMateriasByDocente(self, request, context):
        items = [_materia_to_message(materia) for materia in Materia.objects.filter(docente_id=request.docente_id)]
        return periodosmaterias_pb2.MateriasResponse(
            success=True,
            message="Listado de materias por docente obtenido correctamente.",
            data=items,
        )


def grpc_port() -> int:
    return int(getattr(settings, "GRPC_PORT", 50052))
