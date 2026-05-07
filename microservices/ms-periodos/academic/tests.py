from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Periodo


class PeriodoAPITests(APITestCase):
    def test_create_periodo_and_retrieve_active(self):
        response = self.client.post(
            "/api/periodos/",
            {
                "nombre": "2026 Primavera",
                "fecha_inicio": "2026-01-10",
                "fecha_fin": "2026-05-30",
                "plan_estudios": "ISC 2026",
                "activo": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        activo = self.client.get("/api/periodos/activo/")
        self.assertEqual(activo.status_code, status.HTTP_200_OK)
        self.assertEqual(activo.data["data"]["nombre"], "2026 Primavera")

    def test_only_one_periodo_remains_active(self):
        Periodo.objects.create(
            nombre="A",
            fecha_inicio="2026-01-01",
            fecha_fin="2026-02-01",
            plan_estudios="Plan A",
            activo=True,
        )
        Periodo.objects.create(
            nombre="B",
            fecha_inicio="2026-03-01",
            fecha_fin="2026-04-01",
            plan_estudios="Plan B",
            activo=True,
        )
        activos = Periodo.objects.filter(activo=True)
        self.assertEqual(activos.count(), 1)
        self.assertEqual(activos.first().nombre, "B")

    def test_date_validation(self):
        periodo = Periodo(
            nombre="Inválido",
            fecha_inicio="2026-05-30",
            fecha_fin="2026-01-10",
            plan_estudios="Plan X",
        )
        with self.assertRaises(ValidationError):
            periodo.full_clean()
