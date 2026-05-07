from django.core.exceptions import ValidationError
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Materia


class MateriaAPITests(APITestCase):
    @patch("materias.serializers.get_periodos_client_from_settings")
    def test_create_and_filter_by_periodo(self, mock_get_client):
        class FakeClient:
            def get_periodo_by_id(self, periodo_id):
                return None

        mock_get_client.return_value = FakeClient()
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
                "periodo_id": 1,
                "activo": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        filtered = self.client.get("/api/materias/?periodo_id=1")
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered.data["data"]["results"]), 1)
        self.assertEqual(filtered.data["data"]["results"][0]["nrc"], "12345")

    @patch("materias.views.get_periodos_client_from_settings")
    def test_list_with_periodo_name(self, mock_get_client):
        Materia.objects.create(
            nrc="54321",
            nombre="Arquitectura de Software",
            seccion="001",
            clave="ASW-401",
            docente_id=11,
            docente_nombre="Dr. Ruiz",
            horario="Martes 10:00-12:00",
            periodo_id=7,
        )

        class FakeClient:
            def get_periodo_name_by_id(self, periodo_id):
                return "2026 Primavera"

        mock_get_client.return_value = FakeClient()

        response = self.client.get("/api/materias/con-periodo/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["periodo_nombre"], "2026 Primavera")
        self.assertEqual(response.data["data"][0]["nrc"], "54321")

    def test_unique_nrc_validation(self):
        Materia.objects.create(
            nrc="99999",
            nombre="Bases de Datos",
            seccion="002",
            clave="BDD-101",
            docente_id=20,
            docente_nombre="Ing. Pérez",
            horario="Martes 12:00-14:00",
            periodo_id=2,
        )
        duplicate = Materia(
            nrc="99999",
            nombre="Redes",
            seccion="003",
            clave="RED-201",
            docente_id=30,
            docente_nombre="Mtra. García",
            horario="Miércoles 08:00-10:00",
            periodo_id=2,
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
