from django import forms

from .models import CasoClinico, Paciente, RecienNacido


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
    class Meta:
        model = Paciente
        fields = [
            "rut",
            "nombre_completo",
            "fecha_nacimiento",
            "sexo",
            "telefono",
            "email",
            "direccion",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

class RecienNacidoForm(BaseClinicaForm):
    class Meta:
        model = RecienNacido
        fields = [
            "parto",
            "identificador",
            "sexo",
            "peso_gramos",
            "talla_cm",
            "apgar_1_min",
            "apgar_5_min",
            "condicion_inicial",
            "derivacion",
        ]


class CasoClinicoForm(BaseClinicaForm):
    class Meta:
        model = CasoClinico
        fields = [
            "paciente",
            "titulo",
            "resumen",
            "especialidad",
            "prioridad",
            "estado",
            "medico_responsable",
        ]
