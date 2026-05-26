from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APITestCase

from .authentication import AuthenticatedUser

# Mock global de RabbitMQ para evitar errores de conexión al importar
with patch("rabbitmq_manager.RabbitMQManager._connect", return_value=None), \
     patch("rabbitmq_manager.RabbitMQRpcClient._connect", return_value=None):
    from .models import Periodo, Materia

class PeriodoAPITests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(
            user=AuthenticatedUser(id=1, email="admin@agm.buap.mx", rol="Administrador")
        )

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
        self.client.force_authenticate(
            user=AuthenticatedUser(id=1, email="admin@agm.buap.mx", rol="Administrador")
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

    @patch("academic.views.send_cierre_materia", return_value=True)
    def test_close_materia_triggers_notificacion_event(self, mocked_send):
        materia = Materia.objects.create(
            nrc="67890",
            nombre="Redes",
            seccion="001",
            clave="RED-301",
            docente_id=12,
            docente_nombre="Ing. Pérez",
            horario="Miércoles 10:00-12:00",
            periodo_id=self.periodo.id,
            activo=True,
        )

        response = self.client.post(f"/api/materias/{materia.id}/cerrar/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(Materia.objects.get(id=materia.id).activo)
        mocked_send.assert_called_once_with(
            materia_id=materia.id,
            materia_nombre=materia.nombre,
            nrc=materia.nrc,
            auth_token="no-token",
        )

    def test_import_materias_from_text(self):
        response = self.client.post(
            "/api/materias/importar/",
            {
                "periodo_id": self.periodo.id,
                "docente_id_default": 15,
                "texto": (
                    "12345  Servicios Web  001  10 Dra. Lopez  Lunes 10:00-12:00\n"
                    "23456  Arquitectura de Software  002  11 Ing. Ruiz  Martes 12:00-14:00"
                ),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["created"], 2)
        self.assertEqual(Materia.objects.filter(periodo_id=self.periodo.id).count(), 2)
        self.assertEqual(Materia.objects.get(nrc="12345").docente_id, 10)
        self.assertEqual(Materia.objects.get(nrc="12345").docente_nombre, "Dra. Lopez")
