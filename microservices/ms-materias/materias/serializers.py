from rest_framework import serializers

from .models import Materia


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"
        read_only_fields = ("creado_en", "actualizado_en")

    def validate_periodo_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("El identificador del periodo debe ser mayor que cero.")
        return value

