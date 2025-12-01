from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Catálogos normativos utilizados en REM A24
# ---------------------------------------------------------------------------
class Consultorio(models.Model):
    nombre = models.CharField(_("Nombre del consultorio"), max_length=120, unique=True)
    comuna = models.CharField(_("Comuna"), max_length=60, blank=True)
    activo = models.BooleanField(_("Activo"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = _("Consultorio")
        verbose_name_plural = _("Consultorios")
        indexes = [
            models.Index(fields=["activo"], name="idx_consultorio_activo"),
        ]

    def __str__(self):
        if self.comuna:
            return f"{self.nombre} ({self.comuna})"
        return self.nombre


class Nacionalidad(models.Model):
    codigo = models.CharField(_("Código"), max_length=3, primary_key=True)
    nombre = models.CharField(_("Nombre"), max_length=60, unique=True)
    activo = models.BooleanField(_("Activo"), default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = _("Nacionalidad")
        verbose_name_plural = _("Nacionalidades")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class PuebloOriginario(models.Model):
    nombre = models.CharField(_("Pueblo originario"), max_length=60, unique=True)
    activo = models.BooleanField(_("Activo"), default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = _("Pueblo originario")
        verbose_name_plural = _("Pueblos originarios")

    def __str__(self):
        return self.nombre


class TipoParto(models.Model):
    nombre = models.CharField(_("Tipo de parto"), max_length=50, unique=True)
    descripcion = models.CharField(_("Descripción"), max_length=200, blank=True)
    activo = models.BooleanField(_("Activo"), default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = _("Tipo de parto (catálogo)")
        verbose_name_plural = _("Tipos de parto (catálogo)")

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Modelos clínicos principales
# ---------------------------------------------------------------------------
class Paciente(models.Model):
    class SexoChoices(models.TextChoices):
        MASCULINO = "M", _("Masculino")
        FEMENINO = "F", _("Femenino")
        OTRO = "O", _("Otro")

    class EstadoCivilChoices(models.TextChoices):
        SOLTERA = "soltera", _("Soltera")
        CASADA = "casada", _("Casada")
        VIUDA = "viuda", _("Viuda")
        DIVORCIADA = "divorciada", _("Divorciada")
        CONVIVIENTE = "conviviente", _("Conviviente")
        OTRO = "otro", _("Otro")

    class NivelEducacionalChoices(models.TextChoices):
        NINGUNA = "ninguna", _("Ninguna")
        BASICA = "basica", _("Básica")
        MEDIA = "media", _("Media")
        TECNICA = "tecnica", _("Técnica")
        UNIVERSITARIA = "universitaria", _("Universitaria")
        OTRO = "otro", _("Otro")

    class EstadoAtencionChoices(models.TextChoices):
        EN_ESPERA = "en_espera", _("En espera")
        EN_OBSERVACION = "en_observacion", _("En observación")
        ATENDIDO = "atendido", _("Atendido")
        DERIVADO = "derivado", _("Derivado")

    class RiesgoObstetricoChoices(models.TextChoices):
        BAJO = "bajo", _("Bajo")
        MEDIO = "medio", _("Medio")
        ALTO = "alto", _("Alto")

    rut = models.CharField(_("RUT"), max_length=12, unique=True)
    dv = models.CharField(_("Dígito verificador"), max_length=1, blank=True)
    nombres = models.CharField(_("Nombres"), max_length=100, blank=True)
    apellido_paterno = models.CharField(_("Apellido paterno"), max_length=100, blank=True)
    apellido_materno = models.CharField(_("Apellido materno"), max_length=100, blank=True)
    nombre_completo = models.CharField(_("Nombre completo"), max_length=255, blank=True)
    fecha_nacimiento = models.DateField(_("Fecha de nacimiento"))
    sexo = models.CharField(_("Sexo"), max_length=1, choices=SexoChoices.choices)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    email = models.EmailField(_("Correo electrónico"), blank=True)
    direccion = models.CharField(_("Dirección"), max_length=255, blank=True)
    
    estado_civil = models.CharField(
        _("Estado civil"),
        max_length=20,
        choices=EstadoCivilChoices.choices,
        default=EstadoCivilChoices.OTRO,
        blank=True,
    )
    nivel_educacional = models.CharField(
        _("Nivel educacional"),
        max_length=20,
        choices=NivelEducacionalChoices.choices,
        default=NivelEducacionalChoices.OTRO,
        blank=True,
    )

    # --- CAMPOS CORREGIDOS (FK son las oficiales ahora) ---
    consultorio = models.ForeignKey(
        Consultorio,
        verbose_name=_("Consultorio de referencia"),
        related_name="pacientes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="consultorio_id",
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Registrado por"),
        related_name="pacientes_registrados",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    nacionalidad = models.ForeignKey(
        Nacionalidad,
        verbose_name=_("Nacionalidad"),
        related_name="pacientes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="nacionalidad_codigo",
    )
    pueblo_originario = models.ForeignKey(
        PuebloOriginario,
        verbose_name=_("Pueblo originario"),
        related_name="pacientes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="pueblo_originario_id",
    )
    # ------------------------------------------------------

    activo = models.BooleanField(_("Activo"), default=True)
    estado_atencion = models.CharField(
        _("Estado de atención"),
        max_length=20,
        choices=EstadoAtencionChoices.choices,
        default=EstadoAtencionChoices.EN_ESPERA,
    )
    riesgo_obstetrico = models.CharField(
        _("Riesgo obstétrico"),
        max_length=10,
        choices=RiesgoObstetricoChoices.choices,
        default=RiesgoObstetricoChoices.BAJO,
    )
    contacto_emergencia_nombre = models.CharField(
        _("Nombre contacto de emergencia"),
        max_length=120,
        blank=True,
    )
    contacto_emergencia_telefono = models.CharField(
        _("Teléfono contacto de emergencia"),
        max_length=20,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["nombres", "apellido_paterno", "apellido_materno"]
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")
        indexes = [
            models.Index(fields=["fecha_nacimiento"], name="idx_paciente_fecha_nac"),
            models.Index(fields=["nombres", "apellido_paterno"], name="idx_paciente_nombre"),
        ]

    def __str__(self):
        nombre = self.nombre_completo or self.full_name
        return f"{nombre.strip()} ({self.rut})"

    @property
    def full_name(self):
        partes = [self.nombres, self.apellido_paterno, self.apellido_materno]
        return " ".join(p for p in partes if p)

    def save(self, *args, **kwargs):
        if not self.nombre_completo:
            self.nombre_completo = self.full_name.strip()
        super().save(*args, **kwargs)


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
    class PosicionPartoChoices(models.TextChoices):
        SEMISENTADA = "semisentada", _("Semisentada")
        SENTADA = "sentada", _("Sentada")
        LITOTOMIA = "litotomia", _("Litotomía")
        CUADRUPEDA = "cuadrupeda", _("Cuadrúpeda")
        DE_PIE = "de_pie", _("De pie")
        CUCLILLA = "cuclilla", _("Cuclilla")
        OTRO = "otro", _("Otro")

    paciente = models.ForeignKey(
        Paciente,
        verbose_name=_("Madre"),
        related_name="partos",
        on_delete=models.CASCADE,
    )
    fecha_hora = models.DateTimeField(_("Fecha y hora del parto"))
    fecha_ingreso = models.DateTimeField(_("Fecha y hora de ingreso"), null=True, blank=True)
    
    # CAMBIO: Usamos la FK al catálogo como oficial
    tipo_parto = models.ForeignKey(
        TipoParto,
        verbose_name=_("Tipo de parto"),
        related_name="episodios",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="tipo_parto_id",
        help_text=_("Referencia a catálogo nacional de tipos de parto."),
    )
    
    posicion_parto = models.CharField(
        _("Posición durante el parto"),
        max_length=20,
        choices=PosicionPartoChoices.choices,
        blank=True,
    )
    posicion_parto_otro = models.CharField(
        _("Detalle de posición (si 'Otro')"),
        max_length=100,
        blank=True,
    )
    sala = models.CharField(_("Sala / pabellón"), max_length=50, blank=True)
    edad_materna_parto = models.PositiveSmallIntegerField(
        _("Edad materna al parto"),
        null=True,
        blank=True,
        validators=[MinValueValidator(10), MaxValueValidator(60)],
    )
    paridad = models.PositiveSmallIntegerField(_("Paridad"), null=True, blank=True)
    control_prenatal = models.BooleanField(_("Control prenatal"), default=True)
    preeclampsia_severa = models.BooleanField(_("Preeclampsia severa"), default=False)
    eclampsia = models.BooleanField(_("Eclampsia"), default=False)
    sepsis = models.BooleanField(_("Sepsis"), default=False)
    infeccion_ovular = models.BooleanField(_("Infección ovular"), default=False)
    detalle_otra_patologia = models.TextField(_("Otras patologías"), blank=True)
    ligadura_tardia_cordon = models.BooleanField(_("Ligadura tardía del cordón"), default=False)
    contacto_piel_piel = models.BooleanField(_("Contacto piel con piel"), default=False)
    duracion_contacto_min = models.PositiveSmallIntegerField(
        _("Duración contacto piel con piel (min)"), null=True, blank=True
    )
    lactancia_primera_hora = models.BooleanField(_("Lactancia en primera hora"), default=False)
    alojamiento_conjunto = models.BooleanField(_("Alojamiento conjunto"), default=False)
    vdrl_positivo = models.BooleanField(_("VDRL positivo"), default=False)
    hepatitis_b_positivo = models.BooleanField(_("Hepatitis B positivo"), default=False)
    vih_positivo = models.BooleanField(_("VIH positivo"), default=False)
    complicaciones = models.TextField(_("Complicaciones"), blank=True)
    observaciones = models.TextField(_("Observaciones"), blank=True)
    duracion_trabajo_parto_min = models.PositiveIntegerField(
        _("Duración del trabajo de parto (min)"), null=True, blank=True
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
        indexes = [
            models.Index(fields=["fecha_hora"], name="idx_parto_fecha"),
            models.Index(fields=["paciente"], name="idx_parto_paciente"),
            models.Index(fields=["edad_materna_parto"], name="idx_parto_edad_materna"),
        ]

    def __str__(self):
        madre = self.paciente.nombre_completo or self.paciente.full_name
        return _("Parto de %(madre)s el %(fecha)s") % {
            "madre": madre,
            "fecha": self.fecha_hora.strftime("%d/%m/%Y"),
        }

    @property
    def alta_registrada(self):
        try:
            return self.alta
        except Alta.DoesNotExist:  # type: ignore[name-defined]
            return None


class RecienNacido(models.Model):
    class SexoChoices(models.TextChoices):
        MASCULINO = "M", _("Masculino")
        FEMENINO = "F", _("Femenino")
        INDETERMINADO = "I", _("Indeterminado")

    class ReanimacionChoices(models.TextChoices):
        NINGUNA = "Ninguna", _("Ninguna")
        BASICA = "Básica", _("Básica")
        AVANZADA = "Avanzada", _("Avanzada")

    parto = models.ForeignKey(
        Parto,
        related_name="recien_nacidos",
        verbose_name=_("Episodio de parto"),
        on_delete=models.CASCADE,
        db_column="episodio_parto_id",
    )
    identificador = models.CharField(_("Identificador interno"), max_length=20, blank=True)
    sexo = models.CharField(_("Sexo"), max_length=1, choices=SexoChoices.choices)
    peso_gramos = models.PositiveIntegerField(
        _("Peso (g)"), validators=[MinValueValidator(400), MaxValueValidator(6500)]
    )
    talla_cm = models.PositiveIntegerField(_("Talla (cm)"))
    perimetro_cefalico_cm = models.DecimalField(
        _("Perímetro cefálico (cm)"), max_digits=4, decimal_places=1, blank=True, null=True
    )
    apgar1 = models.PositiveSmallIntegerField(
        _("APGAR al minuto 1"),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    apgar5 = models.PositiveSmallIntegerField(
        _("APGAR al minuto 5"),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    edad_gestacional_semanas = models.PositiveSmallIntegerField(
        _("Edad gestacional (semanas)"),
        validators=[MinValueValidator(20), MaxValueValidator(45)],
        null=True,
        blank=True,
    )
    reanimacion = models.CharField(
        _("Reanimación"), max_length=15, choices=ReanimacionChoices.choices, default=ReanimacionChoices.NINGUNA
    )
    tiene_malformacion = models.BooleanField(_("Presenta malformación"), default=False)
    malformacion_detalle = models.TextField(_("Detalle malformación"), blank=True)
    condicion_inicial = models.TextField(_("Condición inicial"), blank=True)
    derivacion = models.TextField(_("Derivación / destino"), blank=True)
    diagnostico_alta = models.CharField(_("Diagnóstico de alta"), max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        ordering = ["parto", "id"]
        verbose_name = _("Recién nacido")
        verbose_name_plural = _("Recién nacidos")
        indexes = [
            models.Index(fields=["peso_gramos"], name="idx_rn_peso"),
            models.Index(fields=["edad_gestacional_semanas"], name="idx_rn_edad_gest"),
        ]

    def __str__(self):
        sexo = self.get_sexo_display()
        return _("RN %(id)s - %(peso)s g (%(sexo)s)") % {
            "id": self.identificador or self.pk,
            "peso": self.peso_gramos,
            "sexo": sexo,
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
    condicion_egreso = models.TextField(_("Condición al egreso"))
    requiere_seguimiento = models.BooleanField(_("Requiere seguimiento"), default=False)
    proxima_cita = models.DateField(_("Fecha de próxima cita / control"), null=True, blank=True)
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


class EventoClinicoRN(models.Model):
    class TipoEventoChoices(models.TextChoices):
        PROFILAXIS = "Profilaxis Ocular", _("Profilaxis ocular")
        HEPATITIS_B = "Vacuna Hepatitis B", _("Vacuna Hepatitis B")
        BCG = "Vacuna BCG", _("Vacuna BCG")
        TAMIZAJE_AUDITIVO = "Tamizaje Auditivo", _("Tamizaje auditivo")
        TAMIZAJE_PKU = "Tamizaje PKU/TSH", _("Tamizaje PKU/TSH")
        TAMIZAJE_CARDIO = "Tamizaje Cardiopatías", _("Tamizaje cardiopatías")

    recien_nacido = models.ForeignKey(
        RecienNacido,
        verbose_name=_("Recién nacido"),
        related_name="eventos_clinicos",
        on_delete=models.CASCADE,
    )
    tipo_evento = models.CharField(_("Tipo de evento"), max_length=40, choices=TipoEventoChoices.choices)
    fecha_hora = models.DateTimeField(_("Fecha y hora"), auto_now_add=True)
    resultado = models.CharField(_("Resultado"), max_length=100, blank=True)
    observaciones = models.TextField(_("Observaciones"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Evento clínico RN")
        verbose_name_plural = _("Eventos clínicos RN")
        constraints = [
            models.UniqueConstraint(
                fields=["recien_nacido", "tipo_evento"],
                name="uq_evento_por_rn",
            )
        ]

    def __str__(self):
        return f"{self.tipo_evento} - RN {self.recien_nacido_id}"


# ---------------------------------------------------------------------------
# Modelos de solo lectura para vistas SQL (no gestionadas por Django)
# ---------------------------------------------------------------------------
class VistaRemMensual(models.Model):
    mes = models.CharField(max_length=7)
    rut_paciente = models.CharField(max_length=12)
    nombre_completo = models.CharField(max_length=255)
    edad_materna_parto = models.PositiveSmallIntegerField()
    tipo_parto = models.CharField(max_length=50)
    sexo_rn = models.CharField(max_length=15)
    peso_gramos = models.IntegerField()
    edad_gestacional_semanas = models.IntegerField()
    apgar1 = models.IntegerField()
    apgar5 = models.IntegerField()
    ligadura_tardia_cordon = models.BooleanField()
    contacto_piel_piel = models.BooleanField()
    lactancia_primera_hora = models.BooleanField()
    alojamiento_conjunto = models.BooleanField()
    control_prenatal = models.BooleanField()

    class Meta:
        managed = False
        db_table = "vista_rem_mensual"
        verbose_name = _("Vista REM mensual")
        verbose_name_plural = _("Vista REM mensual")


class VistaIndicadoresCalidadMensual(models.Model):
    mes = models.CharField(max_length=7, primary_key=True)
    total_partos = models.IntegerField()
    porc_ligadura_tardia = models.DecimalField(max_digits=5, decimal_places=2)
    porc_contacto_piel = models.DecimalField(max_digits=5, decimal_places=2)
    porc_lactancia_temprana = models.DecimalField(max_digits=5, decimal_places=2)
    porc_alojamiento_conjunto = models.DecimalField(max_digits=5, decimal_places=2)
    porc_control_prenatal = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = "vista_indicadores_calidad_mensual"
        verbose_name = _("Indicadores de calidad mensuales")
        verbose_name_plural = _("Indicadores de calidad mensuales")


class VistaEstadisticasRnMensual(models.Model):
    mes = models.CharField(max_length=7, primary_key=True)
    total_rn = models.IntegerField()
    peso_promedio = models.IntegerField()
    edad_gestacional_promedio = models.DecimalField(max_digits=4, decimal_places=1)
    rn_bajo_peso = models.IntegerField()
    rn_apgar_bajo = models.IntegerField()
    rn_con_malformacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = "vista_estadisticas_rn_mensual"
        verbose_name = _("Estadísticas RN mensuales")
        verbose_name_plural = _("Estadísticas RN mensuales")