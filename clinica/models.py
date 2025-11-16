from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Paciente(models.Model):
    class SexoChoices(models.TextChoices):
        MASCULINO = "M", _("Masculino")
        FEMENINO = "F", _("Femenino")
        OTRO = "O", _("Otro")

    rut = models.CharField(_("RUT"), max_length=12, unique=True)
    nombre_completo = models.CharField(_("Nombre completo"), max_length=255)
    fecha_nacimiento = models.DateField(_("Fecha de nacimiento"))
    sexo = models.CharField(_("Sexo"), max_length=1, choices=SexoChoices.choices)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    email = models.EmailField(_("Correo electrónico"), blank=True)
    direccion = models.CharField(_("Dirección"), max_length=255, blank=True)
    activo = models.BooleanField(_("Activo"), default=True)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)

    class Meta:
        ordering = ["nombre_completo"]
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


class CasoClinico(models.Model):
    class PrioridadChoices(models.TextChoices):
        BAJA = "baja", _("Baja")
        MEDIA = "media", _("Media")
        ALTA = "alta", _("Alta")

    class EstadoChoices(models.TextChoices):
        ABIERTO = "abierto", _("Abierto")
        EN_ESTUDIO = "en_estudio", _("En estudio")
        CERRADO = "cerrado", _("Cerrado")

    paciente = models.ForeignKey(
        Paciente,
        verbose_name=_("Paciente"),
        related_name="casos_clinicos",
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(_("Título"), max_length=255)
    resumen = models.TextField(_("Resumen"))
    especialidad = models.CharField(_("Especialidad"), max_length=100)
    prioridad = models.CharField(
        _("Prioridad"),
        max_length=10,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA,
    )
    estado = models.CharField(
        _("Estado"),
        max_length=15,
        choices=EstadoChoices.choices,
        default=EstadoChoices.ABIERTO,
    )
    medico_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Médico responsable"),
        related_name="casos_clinicos_asignados",
        on_delete=models.PROTECT,
    )
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = _("Caso clínico")
        verbose_name_plural = _("Casos clínicos")

    def __str__(self):
        return f"{self.titulo} - {self.paciente}"
