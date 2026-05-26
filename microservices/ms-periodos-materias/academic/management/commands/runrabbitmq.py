import os
import sys
from django.core.management.base import BaseCommand
from rabbitmq_manager import RabbitMQRpcServer
from academic.models import Periodo, Materia

def _periodo_to_dict(periodo: Periodo) -> dict:
    return {
        "id": periodo.id,
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio.isoformat(),
        "fecha_fin": periodo.fecha_fin.isoformat(),
        "plan_estudios": periodo.plan_estudios,
        "activo": periodo.activo,
    }

def _materia_to_dict(materia: Materia) -> dict:
    return {
        "id": materia.id,
        "nrc": materia.nrc,
        "nombre": materia.nombre,
        "seccion": materia.seccion,
        "clave": materia.clave,
        "docente_id": materia.docente_id,
        "docente_nombre": materia.docente_nombre,
        "horario": materia.horario,
        "periodo_id": materia.periodo_id,
        "activo": materia.activo,
    }

class PeriodosRpcHandlers:
    def get_periodo_by_id(self, data):
        periodo = Periodo.objects.filter(id=data.get("id")).first()
        if not periodo:
            return {"success": False, "message": "Periodo no encontrado."}
        return {
            "success": True,
            "data": _periodo_to_dict(periodo),
        }

    def get_periodo_activo(self, data):
        periodo = Periodo.objects.filter(activo=True).first()
        if not periodo:
            return {"success": False, "message": "No existe un periodo activo."}
        return {
            "success": True,
            "data": _periodo_to_dict(periodo),
        }

    def list_periodos(self, data):
        items = [_periodo_to_dict(p) for p in Periodo.objects.all()]
        return {
            "success": True,
            "data": items,
        }

    def get_materia_by_id(self, data):
        materia = Materia.objects.filter(id=data.get("id")).first()
        if not materia:
            return {"success": False, "message": "Materia no encontrada."}
        return {
            "success": True,
            "data": _materia_to_dict(materia),
        }

    def get_materia_by_nrc(self, data):
        materia = Materia.objects.filter(nrc=data.get("nrc")).first()
        if not materia:
            return {"success": False, "message": "Materia no encontrada."}
        return {
            "success": True,
            "data": _materia_to_dict(materia),
        }

    def list_materias(self, data):
        items = [_materia_to_dict(m) for m in Materia.objects.all()]
        return {
            "success": True,
            "data": items,
        }

    def list_materias_by_periodo(self, data):
        items = [_materia_to_dict(m) for m in Materia.objects.filter(periodo_id=data.get("periodo_id"))]
        return {
            "success": True,
            "data": items,
        }

    def list_materias_by_docente(self, data):
        items = [_materia_to_dict(m) for m in Materia.objects.filter(docente_id=data.get("docente_id"))]
        return {
            "success": True,
            "data": items,
        }

class Command(BaseCommand):
    help = "Run the RabbitMQ RPC server for ms-periodos-materias."

    def handle(self, *args, **options):
        handlers = PeriodosRpcHandlers()
        server = RabbitMQRpcServer(queue_name='rpc_periodos_queue')
        server.register_action('get_periodo_by_id', handlers.get_periodo_by_id)
        server.register_action('get_periodo_activo', handlers.get_periodo_activo)
        server.register_action('list_periodos', handlers.list_periodos)
        server.register_action('get_materia_by_id', handlers.get_materia_by_id)
        server.register_action('get_materia_by_nrc', handlers.get_materia_by_nrc)
        server.register_action('list_materias', handlers.list_materias)
        server.register_action('list_materias_by_periodo', handlers.list_materias_by_periodo)
        server.register_action('list_materias_by_docente', handlers.list_materias_by_docente)
        
        self.stdout.write(self.style.SUCCESS("RabbitMQ RPC server running on queue rpc_periodos_queue"))
        server.start()
