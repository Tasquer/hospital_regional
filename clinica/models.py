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


class Parto(models.Model):
    class TipoPartoChoices(models.TextChoices):
        VAGINAL = "vaginal", _("Vaginal")
        CESAREA = "cesarea", _("Cesárea")
        INSTRUMENTAL = "instrumental", _("Instrumental")
        OTRO = "otro", _("Otro")

    paciente = models.ForeignKey(
        Paciente,
        verbose_name=_("Madre"),
        related_name="partos",
        on_delete=models.CASCADE,
    )
    fecha_hora = models.DateTimeField(_("Fecha y hora del parto"))
    tipo_parto = models.CharField(
        _("Tipo de parto"),
        max_length=20,
        choices=TipoPartoChoices.choices,
        default=TipoPartoChoices.VAGINAL,
    )
    sala = models.CharField(_("Sala / pabellón"), max_length=50, blank=True)
    complicaciones = models.TextField(_("Complicaciones"), blank=True)
    duracion_trabajo_parto_min = models.PositiveIntegerField(
        _("Duración del trabajo de parto (min)"),
        null=True,
        blank=True,
    )
    personal_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Profesional responsable"),
        related_name="partos_asignados",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["-fecha_hora"]
        verbose_name = _("Parto")
        verbose_name_plural = _("Partos")

    def __str__(self):
        return _("Parto de %(madre)s el %(fecha)s") % {
            "madre": self.paciente.nombre_completo,
            "fecha": self.fecha_hora.strftime("%d/%m/%Y"),
        }


class RecienNacido(models.Model):
    class SexoChoices(models.TextChoices):
        MASCULINO = "M", _("Masculino")
        FEMENINO = "F", _("Femenino")
        OTRO = "O", _("Otro")

    parto = models.ForeignKey(
        Parto,
        related_name="recien_nacidos",
        verbose_name=_("Parto"),
        on_delete=models.CASCADE,
    )
    identificador = models.CharField(_("Identificador del RN"), max_length=20)
    sexo = models.CharField(
        _("Sexo"),
        max_length=1,
        choices=SexoChoices.choices,
    )
    peso_gramos = models.PositiveIntegerField(_("Peso (g)"))
    talla_cm = models.PositiveIntegerField(_("Talla (cm)"))
    apgar_1_min = models.PositiveSmallIntegerField(_("APGAR 1 min"))
    apgar_5_min = models.PositiveSmallIntegerField(_("APGAR 5 min"))
    condicion_inicial = models.TextField(_("Condición inicial"), blank=True)
    derivacion = models.TextField(_("Derivación / destino"), blank=True)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["parto", "identificador"]
        verbose_name = _("Recién nacido")
        verbose_name_plural = _("Recién nacidos")

    def __str__(self):
        return _("RN %(ident)s - %(peso)s g (%(sexo)s)") % {
            "ident": self.identificador,
            "peso": self.peso_gramos,
            "sexo": self.sexo,
        }


class Alta(models.Model):
    class TipoAltaChoices(models.TextChoices):
        MEDICA = "medica", _("Alta médica")
        TRASLADO = "traslado", _("Traslado")
        FALLECIMIENTO = "fallecimiento", _("Fallecimiento")
        OTRO = "otro", _("Otro")

    parto = models.OneToOneField(
        Parto,
        verbose_name=_("Parto"),
        related_name="alta",
        on_delete=models.CASCADE,
    )
    fecha_alta = models.DateTimeField(_("Fecha y hora de alta"))
    tipo_alta = models.CharField(
        _("Tipo de alta"),
        max_length=20,
        choices=TipoAltaChoices.choices,
        default=TipoAltaChoices.MEDICA,
    )
    profesional_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Profesional responsable"),
        related_name="altas_emitidas",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    condicion_egreso = models.TextField(
        _("Condición al egreso"),
        help_text=_("Describir el estado clínico de madre y RN al momento del alta."),
    )
    requiere_seguimiento = models.BooleanField(_("Requiere seguimiento"), default=False)
    proxima_cita = models.DateField(
        _("Fecha de próxima cita / control"),
        null=True,
        blank=True,
    )
    observaciones = models.TextField(_("Observaciones adicionales"), blank=True)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["-fecha_alta"]
        verbose_name = _("Alta clínica")
        verbose_name_plural = _("Altas clínicas")

    def __str__(self):
        return _("Alta de %(madre)s el %(fecha)s") % {
            "madre": self.parto.paciente.nombre_completo,
            "fecha": self.fecha_alta.strftime("%d/%m/%Y %H:%M"),
        }
