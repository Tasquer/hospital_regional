from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("clinica", "0007_vistaestadisticasrnmensual_y_mas"),
    ]

    operations = [
        migrations.AddField(
            model_name="paciente",
            name="contacto_emergencia_nombre",
            field=models.CharField(
                blank=True,
                max_length=120,
                verbose_name="Nombre contacto de emergencia",
            ),
        ),
        migrations.AddField(
            model_name="paciente",
            name="contacto_emergencia_telefono",
            field=models.CharField(
                blank=True,
                max_length=20,
                verbose_name="Teléfono contacto de emergencia",
            ),
        ),
        migrations.AddField(
            model_name="paciente",
            name="estado_atencion",
            field=models.CharField(
                choices=[
                    ("en_espera", "En espera"),
                    ("en_observacion", "En observación"),
                    ("atendido", "Atendido"),
                    ("derivado", "Derivado"),
                ],
                default="en_espera",
                max_length=20,
                verbose_name="Estado de atención",
            ),
        ),
        migrations.AddField(
            model_name="paciente",
            name="registrado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pacientes_registrados",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Registrado por",
            ),
        ),
        migrations.AddField(
            model_name="paciente",
            name="riesgo_obstetrico",
            field=models.CharField(
                choices=[
                    ("bajo", "Bajo"),
                    ("medio", "Medio"),
                    ("alto", "Alto"),
                ],
                default="bajo",
                max_length=10,
                verbose_name="Riesgo obstétrico",
            ),
        ),
    ]
