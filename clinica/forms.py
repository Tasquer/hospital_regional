from django import forms
from .models import CasoClinico, Paciente, RecienNacido, Parto, Alta, Consultorio, Nacionalidad, PuebloOriginario

INPUT_CLASS = "w-full rounded-2xl border border-gray-200/70 bg-white px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-400/40"
CHECKBOX_CLASS = "h-4 w-4 rounded border-white/30 bg-transparent text-indigo-500 focus:ring-indigo-500"

class BaseClinicaForm(forms.ModelForm):
    """
    Asigna de forma consistente las clases Tailwind a los widgets
    para mantener la coherencia visual del dashboard.
    """
    textarea_extra = " min-h-[10rem]"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            base_class = INPUT_CLASS

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = CHECKBOX_CLASS
                continue

            if isinstance(widget, forms.Textarea):
                base_class += self.textarea_extra

            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = f"{base_class} pr-10"
            else:
                widget.attrs["class"] = base_class

            if not widget.attrs.get("placeholder"):
                widget.attrs["placeholder"] = field.label

            style = widget.attrs.get("style", "")
            widget.attrs["style"] = f"{style} color:#111827; background-color:#ffffff;".strip()


class PacienteForm(BaseClinicaForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuración de campos FK para que se vean bonitos
        self.fields["consultorio"].queryset = Consultorio.objects.filter(activo=True)
        self.fields["consultorio"].empty_label = "Sin derivación / No aplica"
        
        self.fields["nacionalidad"].queryset = Nacionalidad.objects.filter(activo=True)
        self.fields["nacionalidad"].empty_label = "Selecciona nacionalidad"
        
        self.fields["pueblo_originario"].queryset = PuebloOriginario.objects.filter(activo=True)
        self.fields["pueblo_originario"].empty_label = "Sin adscripción"

        ayuda = {
            "rut": "Ej: 12.345.678-9",
            "dv": "Dígito verificador (0-9 o K)",
            "telefono": "Ej: +56 9 1234 5678",
            "contacto_emergencia_telefono": "Ej: +56 9 8765 4321",
            "direccion": "Ej: Calle 123, Comuna",
            "email": "Ej: paciente@mail.com",
            "contacto_emergencia_nombre": "Nombre y parentesco del contacto",
        }
        for name, texto in ayuda.items():
            if name in self.fields:
                self.fields[name].help_text = texto

    class Meta:
        model = Paciente
        fields = [
            "rut", "dv", "nombres", "apellido_paterno", "apellido_materno",
            "nombre_completo", "fecha_nacimiento", "sexo", "telefono",
            "email", "direccion", "contacto_emergencia_nombre",
            "contacto_emergencia_telefono", "estado_civil",
            "nivel_educacional", 
            # Campos corregidos (FK directas)
            "consultorio", "nacionalidad", "pueblo_originario",
            "estado_atencion", "riesgo_obstetrico", "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get("rut")
        apellido_paterno = cleaned_data.get("apellido_paterno")
        apellido_materno = cleaned_data.get("apellido_materno")
        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")

        if rut:
            qs = Paciente.objects.filter(rut__iexact=rut)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("rut", "Ya existe un paciente registrado con este RUT.")

        criterios_suficientes = apellido_paterno and fecha_nacimiento
        if criterios_suficientes:
            posibles = Paciente.objects.filter(
                apellido_paterno__iexact=apellido_paterno,
                fecha_nacimiento=fecha_nacimiento,
            )
            if apellido_materno:
                posibles = posibles.filter(apellido_materno__iexact=apellido_materno)
            if self.instance.pk:
                posibles = posibles.exclude(pk=self.instance.pk)
            if posibles.exists():
                similares = ", ".join(f"{p.nombre_completo or p.full_name} ({p.rut})" for p in posibles[:3])
                self.add_error(None, f"Existen pacientes similares registrados: {similares}. Verifica antes de guardar.")

        return cleaned_data


class PartoForm(BaseClinicaForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["personal_responsable"].required = True
        self.fields["paciente"].queryset = Paciente.objects.filter(activo=True).order_by("apellido_paterno", "apellido_materno", "nombres")

    class Meta:
        model = Parto
        fields = [
            "paciente", "fecha_hora", "fecha_ingreso", 
            "tipo_parto", # FK directa
            "posicion_parto", "posicion_parto_otro", "sala",
            "edad_materna_parto", "paridad", "control_prenatal",
            "preeclampsia_severa", "eclampsia", "sepsis",
            "infeccion_ovular", "detalle_otra_patologia",
            "ligadura_tardia_cordon", "contacto_piel_piel",
            "duracion_contacto_min", "lactancia_primera_hora",
            "alojamiento_conjunto", "vdrl_positivo",
            "hepatitis_b_positivo", "vih_positivo", "complicaciones",
            "observaciones", "duracion_trabajo_parto_min",
            "personal_responsable",
        ]
        widgets = {
            "fecha_hora": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "fecha_ingreso": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ["paciente", "fecha_hora", "tipo_parto", "personal_responsable"]
        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "Este campo es obligatorio.")
        return cleaned_data


class RecienNacidoForm(BaseClinicaForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parto"].queryset = Parto.objects.select_related("paciente").order_by("-fecha_hora")

    class Meta:
        model = RecienNacido
        fields = [
            "parto", "identificador", "sexo", "peso_gramos",
            "talla_cm", "perimetro_cefalico_cm", "apgar1", "apgar5",
            "edad_gestacional_semanas", "reanimacion",
            "tiene_malformacion", "malformacion_detalle",
            "condicion_inicial", "derivacion", "diagnostico_alta",
        ]

    def clean(self):
        cleaned_data = super().clean()
        for field in ("apgar1", "apgar5"):
            value = cleaned_data.get(field)
            if value is not None and not 0 <= value <= 10:
                self.add_error(field, "El puntaje APGAR debe estar entre 0 y 10.")

        for field in ("peso_gramos", "talla_cm"):
            value = cleaned_data.get(field)
            if value is not None and value <= 0:
                self.add_error(field, "Debe ser mayor a 0.")

        edad_gestacional = cleaned_data.get("edad_gestacional_semanas")
        if edad_gestacional is not None and not 20 <= edad_gestacional <= 45:
            self.add_error("edad_gestacional_semanas", "La edad gestacional debe estar entre 20 y 45 semanas.")
        return cleaned_data


class AltaForm(BaseClinicaForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk or 'parto' in self.initial:
            self.fields["parto"].disabled = True
            widget = self.fields["parto"].widget
            current_classes = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{current_classes} bg-gray-100 cursor-not-allowed opacity-75".strip()

    class Meta:
        model = Alta
        fields = [
            "parto", "fecha_alta", "tipo_alta", "condicion_egreso",
            "requiere_seguimiento", "proxima_cita", "observaciones",
        ]
        widgets = {
            "fecha_alta": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "proxima_cita": forms.DateInput(attrs={"type": "date"}),
            "condicion_egreso": forms.Textarea(attrs={"rows": 4}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }


class CasoClinicoForm(BaseClinicaForm):
    class Meta:
        model = CasoClinico
        fields = [
            "paciente", "titulo", "resumen", "especialidad",
            "prioridad", "estado", "medico_responsable",
        ]