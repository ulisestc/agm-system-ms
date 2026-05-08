from rest_framework import serializers

from .models import Periodo, Materia


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = "__all__"
        read_only_fields = ("creado_en", "actualizado_en")

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin debe ser mayor o igual a la fecha de inicio."}
            )
        return attrs


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"
        read_only_fields = ("creado_en", "actualizado_en")

    def validate_periodo_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("El identificador del periodo debe ser mayor que cero.")
        if not Periodo.objects.filter(id=value).exists():
            raise serializers.ValidationError("El periodo indicado no existe.")
        return value
