from django.core.exceptions import ValidationError
from django.db import models


class Materia(models.Model):
    nrc = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=160)
    seccion = models.CharField(max_length=20)
    clave = models.CharField(max_length=40, blank=True, default="")
    docente_id = models.PositiveIntegerField()
    docente_nombre = models.CharField(max_length=160, blank=True, default="")
    horario = models.CharField(max_length=120, blank=True, default="")
    periodo_id = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en", "nombre"]
        indexes = [
            models.Index(fields=["nrc"]),
            models.Index(fields=["periodo_id"]),
            models.Index(fields=["docente_id"]),
        ]

    def clean(self):
        if not self.nrc.strip():
            raise ValidationError({"nrc": "El NRC no puede estar vacío."})
        if not self.nombre.strip():
            raise ValidationError({"nombre": "El nombre de la materia no puede estar vacío."})
        if not self.seccion.strip():
            raise ValidationError({"seccion": "La sección no puede estar vacía."})
        if self.docente_id <= 0:
            raise ValidationError({"docente_id": "El identificador del docente debe ser mayor que cero."})
        if self.periodo_id <= 0:
            raise ValidationError({"periodo_id": "El identificador del periodo debe ser mayor que cero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nrc} - {self.nombre}"
