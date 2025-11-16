from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Paciente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rut", models.CharField(max_length=12, unique=True, verbose_name="RUT")),
                ("nombre_completo", models.CharField(max_length=255, verbose_name="Nombre completo")),
                ("fecha_nacimiento", models.DateField(verbose_name="Fecha de nacimiento")),
                (
                    "sexo",
                    models.CharField(
                        choices=[("M", "Masculino"), ("F", "Femenino"), ("O", "Otro")],
                        max_length=1,
                        verbose_name="Sexo",
                    ),
                ),
                ("telefono", models.CharField(blank=True, max_length=20, verbose_name="Teléfono")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Correo electrónico")),
                ("direccion", models.CharField(blank=True, max_length=255, verbose_name="Dirección")),
                ("activo", models.BooleanField(default=True, verbose_name="Activo")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")),
            ],
            options={
                "verbose_name": "Paciente",
                "verbose_name_plural": "Pacientes",
                "ordering": ["nombre_completo"],
            },
        ),
        migrations.CreateModel(
            name="CasoClinico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=255, verbose_name="Título")),
                ("resumen", models.TextField(verbose_name="Resumen")),
                ("especialidad", models.CharField(max_length=100, verbose_name="Especialidad")),
                (
                    "prioridad",
                    models.CharField(
                        choices=[("baja", "Baja"), ("media", "Media"), ("alta", "Alta")],
                        default="media",
                        max_length=10,
                        verbose_name="Prioridad",
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[("abierto", "Abierto"), ("en_estudio", "En estudio"), ("cerrado", "Cerrado")],
                        default="abierto",
                        max_length=15,
                        verbose_name="Estado",
                    ),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")),
                (
                    "medico_responsable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="casos_clinicos_asignados",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Médico responsable",
                    ),
                ),
                (
                    "paciente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="casos_clinicos",
                        to="clinica.paciente",
                        verbose_name="Paciente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Caso clínico",
                "verbose_name_plural": "Casos clínicos",
                "ordering": ["-fecha_creacion"],
            },
        ),
    ]
