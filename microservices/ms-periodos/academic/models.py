from django.core.exceptions import ValidationError
from django.db import models, transaction


class Periodo(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    plan_estudios = models.CharField(max_length=180)
    activo = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activo", "-fecha_inicio", "nombre"]

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha de fin debe ser mayor o igual a la fecha de inicio."})

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            if self.activo:
                Periodo.objects.exclude(pk=self.pk).filter(activo=True).update(activo=False)
            super().save(*args, **kwargs)

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} ({estado})"
