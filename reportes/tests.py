from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clinica.models import Paciente, Parto, RecienNacido


class ReportesDashboardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="usuario", password="segura123")
        self.staff = User.objects.create_user(username="staff", password="segura123", is_staff=True)
        paciente = Paciente.objects.create(
            rut="22.222.222-2",
            nombre_completo="Paciente Reporte",
            fecha_nacimiento="1985-06-01",
            sexo=Paciente.SexoChoices.FEMENINO,
        )
        parto = Parto.objects.create(
            paciente=paciente,
            fecha_hora=timezone.now(),
            tipo_parto=Parto.TipoPartoChoices.VAGINAL,
            personal_responsable=self.staff,
        )
        RecienNacido.objects.create(
            parto=parto,
            identificador="RN-RPT",
            sexo=RecienNacido.SexoChoices.MASCULINO,
            peso_gramos=3200,
            talla_cm=50,
            apgar1=8,
            apgar5=9,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("reportes:dashboard_obstetricia"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_staff(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reportes:dashboard_obstetricia"))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_view_dashboard(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("reportes:dashboard_obstetricia"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_partos"], 1)
        self.assertContains(response, "Dashboard de Obstetricia")
