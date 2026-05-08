from rest_framework import serializers
from django.conf import settings

from .models import Materia
from .grpc_client import get_periodos_client_from_settings


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"
        read_only_fields = ("creado_en", "actualizado_en")

    def validate_periodo_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("El identificador del periodo debe ser mayor que cero.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "periodo_id" in attrs:
            periodo_id = attrs["periodo_id"]
            try:
                client = get_periodos_client_from_settings(settings)
                client.get_periodo_by_id(periodo_id)
            except Exception as exc:
                raise serializers.ValidationError({"periodo_id": f"El periodo {periodo_id} no existe o no está disponible por gRPC: {exc}"})
        return attrs
