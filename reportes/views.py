# reportes/views.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from clinica.models import Parto, RecienNacido

class ReportesObstetriciaView(LoginRequiredMixin, TemplateView):
    template_name = "reportes/dashboard_obstetricia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- Consultas para Reportes de Obstetricia ---

        # 1. Totales Generales
        context["total_partos"] = Parto.objects.count()
        context["total_recien_nacidos"] = RecienNacido.objects.count()

        # 2. Distribución Tipo de Parto
        tipo_parto_map = dict(Parto.TipoPartoChoices.choices)
        partos_raw = Parto.objects.values('tipo_parto').annotate(
            total=Count('id')
        ).order_by('tipo_parto')
        
        context["distribucion_tipo_parto"] = [
            {
                'tipo_display': tipo_parto_map.get(item['tipo_parto'], item['tipo_parto']),
                'total': item['total']
            } for item in partos_raw
        ]

        # 3. Distribución Sexo Recién Nacidos
        sexo_map = dict(RecienNacido.SexoChoices.choices)
        sexo_raw = RecienNacido.objects.values('sexo').annotate(
            total=Count('id')
        ).order_by('sexo')
        
        context["distribucion_sexo_rn"] = [
            {
                'sexo_display': sexo_map.get(item['sexo'], item['sexo']),
                'total': item['total']
            } for item in sexo_raw
        ]

        # 4. Estadísticas Vitales RN (Promedios) - ¡VERSIÓN CORREGIDA!
        # Usamos los nombres de campo correctos del modelo
        stats_vitales = RecienNacido.objects.aggregate(
            Avg('peso_gramos'),
            Avg('talla_cm'),
            Avg('apgar_5_min')  # Usamos el APGAR de 5 minutos
        )
        
        # Actualizamos las claves para que coincidan con la consulta de 'aggregate'
        context["promedio_peso_rn"] = stats_vitales.get('peso_gramos__avg')
        context["promedio_talla_rn"] = stats_vitales.get('talla_cm__avg')
        context["promedio_apgar_rn"] = stats_vitales.get('apgar_5_min__avg')

        # 5. Conteo de Partos con Complicaciones
        context["total_complicaciones"] = Parto.objects.filter(complicaciones=True).count()

        return context