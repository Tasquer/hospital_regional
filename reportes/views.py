# reportes/views.py

import json
from datetime import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from clinica.models import Parto, RecienNacido

class ReportesObstetriciaView(LoginRequiredMixin, TemplateView):
    template_name = "reportes/dashboard_obstetricia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # --- 1. LÓGICA DE FILTRO DE FECHA ---
        
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_final_str = request.GET.get('fecha_final')

        # Querysets base
        partos_qs = Parto.objects.all()
        rn_qs = RecienNacido.objects.all()

        if fecha_inicio_str and fecha_final_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()
                
                partos_qs = partos_qs.filter(fecha_creacion__date__range=[fecha_inicio, fecha_final])
                rn_qs = rn_qs.filter(fecha_creacion__date__range=[fecha_inicio, fecha_final])
                
            except ValueError:
                pass
        
        context["fecha_inicio"] = fecha_inicio_str
        context["fecha_final"] = fecha_final_str


        # --- 2. CONSULTAS (usando los querysets filtrados) ---

        # 1. Totales Generales
        context["total_partos"] = partos_qs.count()
        context["total_recien_nacidos"] = rn_qs.count()

        # 2. Distribución Tipo de Parto (y datos para Gráfico)
        tipo_parto_map = dict(Parto.TipoPartoChoices.choices)
        partos_raw = partos_qs.values('tipo_parto').annotate(
            total=Count('id')
        ).order_by('tipo_parto')
        
        distribucion_tipo_parto_list = []
        chart_data_tipo_parto_list = [] 

        for item in partos_raw:
            # Obtenemos el nombre (p.ej. "Cesárea")
            display_name = tipo_parto_map.get(item['tipo_parto'], item['tipo_parto'])
            
            # ¡CORRECCIÓN AQUÍ!
            # Convertimos el objeto '__proxy__' a un string simple
            display_name_str = str(display_name)

            # Para la lista
            distribucion_tipo_parto_list.append({
                'tipo_display': display_name_str,
                'total': item['total']
            })
            
            # Para el gráfico (Esta era la línea que fallaba)
            chart_data_tipo_parto_list.append({
                'value': item['total'],
                'name': display_name_str  # Usamos el string simple
            })

        context["distribucion_tipo_parto"] = distribucion_tipo_parto_list
        # Esto ahora funcionará
        context["chart_data_tipo_parto"] = json.dumps(chart_data_tipo_parto_list)


        # 3. Distribución Sexo Recién Nacidos
        sexo_map = dict(RecienNacido.SexoChoices.choices)
        sexo_raw = rn_qs.values('sexo').annotate(
            total=Count('id')
        ).order_by('sexo')
        
        # ¡CORRECCIÓN AQUÍ TAMBIÉN! (Buena práctica)
        # Convertimos a string simple de inmediato
        context["distribucion_sexo_rn"] = [
            {
                'sexo_display': str(sexo_map.get(item['sexo'], item['sexo'])),
                'total': item['total']
            } for item in sexo_raw
        ]

        # 4. Estadísticas Vitales RN (Promedios)
        stats_vitales = rn_qs.aggregate(
            Avg('peso_gramos'),
            Avg('talla_cm'),
            Avg('apgar_5_min')
        )
        context["promedio_peso_rn"] = stats_vitales.get('peso_gramos__avg')
        context["promedio_talla_rn"] = stats_vitales.get('talla_cm__avg')
        context["promedio_apgar_rn"] = stats_vitales.get('apgar_5_min__avg')

        # 5. Conteo de Partos con Complicaciones
        context["total_complicaciones"] = partos_qs.filter(complicaciones=True).count()

        return context