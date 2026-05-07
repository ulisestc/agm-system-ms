from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings

from .models import Materia
from .grpc_client import get_periodos_client_from_settings
from .pagination import APIPageNumberPagination
from .serializers import MateriaSerializer


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    pagination_class = APIPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        periodo_id = params.get("periodo_id")
        docente_id = params.get("docente_id")
        search = params.get("search")
        activo = params.get("activo")

        if periodo_id:
            queryset = queryset.filter(periodo_id=periodo_id)
        if docente_id:
            queryset = queryset.filter(docente_id=docente_id)
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() in {"1", "true", "yes"})
        return queryset

    def _success(self, data=None, message="Operación completada correctamente.", code=status.HTTP_200_OK):
        return Response({"success": True, "data": data, "message": message}, status=code)

    def _error(self, message, code):
        return Response({"success": False, "data": None, "message": message}, status=code)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return self._success(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self._success(serializer.data, "Materia creada correctamente.", status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return self._success(self.get_serializer(instance).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self._success(serializer.data, "Materia actualizada correctamente.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self._success(None, "Materia eliminada correctamente.")

    @action(detail=False, methods=["get"], url_path="por-periodo/(?P<periodo_id>[^/.]+)")
    def por_periodo(self, request, periodo_id=None):
        materias = self.get_queryset().filter(periodo_id=periodo_id)
        serializer = self.get_serializer(materias, many=True)
        return self._success(serializer.data, f"Materias del periodo {periodo_id}.")

    @action(detail=False, methods=["get"], url_path="con-periodo")
    def con_periodo(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        client = get_periodos_client_from_settings(settings)
        periodos_cache = {}
        data = []

        for materia in queryset:
            periodo_nombre = periodos_cache.get(materia.periodo_id)
            if periodo_nombre is None:
                try:
                    periodo_nombre = client.get_periodo_name_by_id(materia.periodo_id)
                except Exception:
                    periodo_nombre = ""
                periodos_cache[materia.periodo_id] = periodo_nombre

            item = self.get_serializer(materia).data
            item["periodo_nombre"] = periodo_nombre
            data.append(item)

        return self._success(data, "Materias con nombre de periodo obtenidas correctamente.")
