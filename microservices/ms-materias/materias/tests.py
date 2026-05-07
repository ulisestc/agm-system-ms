from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Materia


class MateriaAPITests(APITestCase):
    def test_create_and_filter_by_periodo(self):
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
