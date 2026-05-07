from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Periodo
from .pagination import APIPageNumberPagination
from .serializers import PeriodoSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer
    pagination_class = APIPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        activo = self.request.query_params.get("activo")
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
        return self._success(serializer.data, "Periodo creado correctamente.", status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return self._success(self.get_serializer(instance).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self._success(serializer.data, "Periodo actualizado correctamente.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self._success(None, "Periodo eliminado correctamente.")

    @action(detail=False, methods=["get"], url_path="activo")
    def activo(self, request):
        periodo = Periodo.objects.filter(activo=True).first()
        if not periodo:
            return self._error("No existe un periodo activo.", status.HTTP_404_NOT_FOUND)
        return self._success(self.get_serializer(periodo).data, "Periodo activo encontrado.")

    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        periodo = self.get_object()
        periodo.activo = True
        periodo.save()
        return self._success(self.get_serializer(periodo).data, "Periodo activado correctamente.")
