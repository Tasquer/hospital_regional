from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import PacienteForm
from .models import Alta, Paciente, Parto, RecienNacido


class ClinicaViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="medica",
            password="segura123",
            is_staff=True,
        )
        self.personal = User.objects.create_user(
            username="profesional",
            password="profesional123",
        )
        self.paciente = Paciente.objects.create(
            rut="11.111.111-1",
            nombre_completo="Paciente Test",
            apellido_paterno="Test",
            fecha_nacimiento="1990-01-01",
            sexo=Paciente.SexoChoices.FEMENINO,
        )
        self.parto = Parto.objects.create(
            paciente=self.paciente,
            fecha_hora=timezone.now(),
            tipo_parto=Parto.TipoPartoChoices.VAGINAL,
            personal_responsable=self.personal,
        )

    def login(self):
        self.client.force_login(self.user)

    def _paciente_form_data(self, **overrides):
        data = {
            "rut": "22.222.222-2",
            "dv": "2",
            "nombres": "Nueva",
            "apellido_paterno": "Paciente",
            "apellido_materno": "Prueba",
            "nombre_completo": "Nueva Paciente Prueba",
            "fecha_nacimiento": "1992-02-02",
            "sexo": Paciente.SexoChoices.FEMENINO,
            "telefono": "",
            "email": "",
            "direccion": "",
            "contacto_emergencia_nombre": "",
            "contacto_emergencia_telefono": "",
            "estado_civil": Paciente.EstadoCivilChoices.OTRO,
            "nivel_educacional": Paciente.NivelEducacionalChoices.OTRO,
            "consultorio": "",
            "nacionalidad_catalogo": "",
            "pueblo_originario_catalogo": "",
            "estado_atencion": Paciente.EstadoAtencionChoices.EN_ESPERA,
            "riesgo_obstetrico": Paciente.RiesgoObstetricoChoices.BAJO,
            "activo": True,
        }
        data.update(overrides)
        return data

    def test_parto_list_requires_login(self):
        response = self.client.get(reverse("clinica:parto_list"))
        self.assertEqual(response.status_code, 302)
        self.login()
        response = self.client.get(reverse("clinica:parto_list"))
        self.assertEqual(response.status_code, 200)

    def test_parto_create_with_valid_data(self):
        self.login()
        data = {
            "paciente": self.paciente.pk,
            "fecha_hora": "2024-01-01 10:00",
            "tipo_parto": Parto.TipoPartoChoices.CESAREA,
            "posicion_parto": Parto.PosicionPartoChoices.SENTADA,
            "sala": "Pabellón 1",
            "duracion_trabajo_parto_min": 120,
            "personal_responsable": self.personal.pk,
        }
        response = self.client.post(reverse("clinica:parto_create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Parto.objects.count(), 2)

    def test_recien_nacido_create_and_validation(self):
        self.login()
        data = {
            "parto": self.parto.pk,
            "identificador": "RN-01",
            "sexo": RecienNacido.SexoChoices.FEMENINO,
            "peso_gramos": 3200,
            "talla_cm": 50,
            "apgar1": 8,
            "apgar5": 9,
            "reanimacion": RecienNacido.ReanimacionChoices.NINGUNA,
            "edad_gestacional_semanas": 39,
        }
        response = self.client.post(reverse("clinica:recien_nacido_create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.parto.recien_nacidos.count(), 1)

        data["apgar1"] = 12
        response = self.client.post(reverse("clinica:recien_nacido_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("El puntaje APGAR debe estar entre 0 y 10.", response.context["form"].errors["apgar1"])

    def test_alta_requires_recien_nacido(self):
        self.login()
        data = {
            "parto": self.parto.pk,
            "fecha_alta": "2024-01-02 09:30",
            "tipo_alta": "medica",
            "condicion_egreso": "Egreso sin complicaciones",
        }
        response = self.client.post(reverse("clinica:alta_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se puede registrar un alta")
        self.assertEqual(Alta.objects.count(), 0)

    def test_alta_creation_success_when_rn_exists(self):
        self.login()
        rn = RecienNacido.objects.create(
            parto=self.parto,
            identificador="RN-02",
            sexo=RecienNacido.SexoChoices.MASCULINO,
            peso_gramos=3000,
            talla_cm=48,
            apgar1=7,
            apgar5=9,
        )
        data = {
            "parto": self.parto.pk,
            "fecha_alta": "2024-01-02 09:30",
            "tipo_alta": "medica",
            "condicion_egreso": "Madre y RN estables",
            "requiere_seguimiento": True,
            "proxima_cita": "2024-01-10",
        }
        response = self.client.post(reverse("clinica:alta_create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Alta.objects.count(), 1)
        self.assertEqual(Alta.objects.first().parto, self.parto)
        rn.refresh_from_db()

    def test_trazabilidad_view_renders(self):
        self.login()
        RecienNacido.objects.create(
            parto=self.parto,
            identificador="RN-03",
            sexo=RecienNacido.SexoChoices.FEMENINO,
            peso_gramos=3100,
            talla_cm=49,
            apgar1=9,
            apgar5=10,
        )
        Alta.objects.create(
            parto=self.parto,
            fecha_alta=timezone.now(),
            tipo_alta="medica",
            profesional_responsable=self.user,
            condicion_egreso="Egreso sin novedades",
        )
        response = self.client.get(reverse("clinica:paciente_trazabilidad", args=[self.paciente.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clinica/paciente_trazabilidad_detail.html")
        self.assertContains(response, "Parto 1")

    def test_paciente_form_blocks_duplicate_rut(self):
        form = PacienteForm(data=self._paciente_form_data(rut=self.paciente.rut))
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe un paciente registrado con este RUT.", form.errors["rut"])

    def test_paciente_form_warns_similar_patient(self):
        form = PacienteForm(
            data=self._paciente_form_data(
                rut="55.555.555-5",
                apellido_paterno="Test",
                fecha_nacimiento="1990-01-01",
                apellido_materno="",
                nombres="Otra",
            )
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(any("Existen pacientes similares" in msg for msg in form.non_field_errors()))

    def test_paciente_list_filters_by_query_and_estado(self):
        self.login()
        Paciente.objects.create(
            rut="99.999.999-9",
            nombre_completo="Camila López",
            fecha_nacimiento="1995-05-05",
            sexo=Paciente.SexoChoices.FEMENINO,
            estado_atencion=Paciente.EstadoAtencionChoices.ATENDIDO,
            riesgo_obstetrico=Paciente.RiesgoObstetricoChoices.ALTO,
            apellido_paterno="Lopez",
        )
        response = self.client.get(
            reverse("clinica:paciente_list"),
            {
                "q": "Lopez",
                "estado_atencion": Paciente.EstadoAtencionChoices.ATENDIDO,
            },
        )
        self.assertEqual(response.status_code, 200)
        pacientes_page = response.context["pacientes"]
        self.assertEqual(pacientes_page.paginator.count, 1)
        self.assertContains(response, "Camila López")
        self.assertNotContains(response, "Paciente Test")
