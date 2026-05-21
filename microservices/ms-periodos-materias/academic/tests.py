from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Periodo, Materia


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


class MateriaAPITests(APITestCase):
    def setUp(self):
        self.periodo = Periodo.objects.create(
            nombre="2026 Primavera",
            fecha_inicio="2026-01-10",
            fecha_fin="2026-05-30",
            plan_estudios="ISC 2026",
            activo=True,
        )

    def test_create_and_list_materia(self):
        response = self.client.post(
            "/api/materias/",
            {
                "nrc": "12345",
                "nombre": "Servicios Web",
                "seccion": "001",
                "clave": "ISW-302",
                "docente_id": 10,
                "docente_nombre": "Dra. López",
                "horario": "Lunes 10:00-12:00",
                "periodo_id": self.periodo.id,
                "activo": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        listado = self.client.get("/api/materias/")
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        self.assertEqual(listado.data["data"]["results"][0]["nrc"], "12345")

    def test_list_materia_with_periodo_name(self):
        Materia.objects.create(
            nrc="54321",
            nombre="Arquitectura de Software",
            seccion="001",
            clave="ASW-401",
            docente_id=11,
            docente_nombre="Dr. Ruiz",
            horario="Martes 10:00-12:00",
            periodo_id=self.periodo.id,
        )

        response = self.client.get("/api/materias/con-periodo/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["periodo_nombre"], "2026 Primavera")
        self.assertEqual(response.data["data"][0]["nrc"], "54321")
