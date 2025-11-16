from django.contrib import admin
from .models import Paciente, CasoClinico


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre_completo", "telefono", "email", "activo", "fecha_creacion")
    list_filter = ("activo", "sexo", "fecha_creacion")
    search_fields = ("rut", "nombre_completo")
    ordering = ("nombre_completo",)
    date_hierarchy = "fecha_creacion"


@admin.register(CasoClinico)
class CasoClinicoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "paciente",
        "especialidad",
        "prioridad",
        "estado",
        "medico_responsable",
        "fecha_creacion",
    )
    list_filter = ("prioridad", "estado", "especialidad", "medico_responsable", "fecha_creacion")
    search_fields = ("titulo", "paciente__rut", "paciente__nombre_completo")
    ordering = ("-fecha_creacion",)
    date_hierarchy = "fecha_creacion"
    autocomplete_fields = ("paciente", "medico_responsable")
    list_select_related = ("paciente", "medico_responsable")

# Register your models here.
