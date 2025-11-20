from django.contrib import admin

from .models import Alta, CasoClinico, Paciente, Parto, RecienNacido


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


@admin.register(Parto)
class PartoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "fecha_hora", "tipo_parto", "personal_responsable")
    list_filter = ("tipo_parto", "fecha_hora")
    search_fields = ("paciente__nombre_completo", "paciente__rut")
    ordering = ("-fecha_hora",)
    autocomplete_fields = ("paciente", "personal_responsable")
    date_hierarchy = "fecha_hora"
    list_select_related = ("paciente", "personal_responsable")


@admin.register(RecienNacido)
class RecienNacidoAdmin(admin.ModelAdmin):
    list_display = ("identificador", "parto", "sexo", "peso_gramos", "apgar1", "apgar5")
    list_filter = ("sexo", "parto__tipo_parto")
    search_fields = ("identificador", "parto__paciente__nombre_completo", "parto__paciente__rut")
    ordering = ("parto", "identificador")
    autocomplete_fields = ("parto",)
    list_select_related = ("parto", "parto__paciente")


@admin.register(Alta)
class AltaAdmin(admin.ModelAdmin):
    list_display = (
        "parto",
        "fecha_alta",
        "tipo_alta",
        "profesional_responsable",
        "requiere_seguimiento",
    )
    list_filter = ("tipo_alta", "requiere_seguimiento", "fecha_alta")
    search_fields = ("parto__paciente__nombre_completo", "parto__paciente__rut")
    ordering = ("-fecha_alta",)
    autocomplete_fields = ("parto", "profesional_responsable")
    date_hierarchy = "fecha_alta"
    list_select_related = ("parto", "parto__paciente", "profesional_responsable")

# Register your models here.
