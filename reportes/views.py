# reportes/views.py

import json
from datetime import datetime
from statistics import pstdev

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Q
from django.views.generic import TemplateView
from clinica.models import Paciente, Parto, RecienNacido

class ReportesObstetriciaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "reportes/dashboard_obstetricia.html"

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # --- 1. LÓGICA DE FILTRO DE FECHA ---
        
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_final_str = request.GET.get('fecha_final')

        # Querysets base
        partos_qs = Parto.objects.all()
        rn_qs = RecienNacido.objects.all()
        
        # Obtenemos los IDs de los pacientes que tuvieron partos
        pacientes_id_base = partos_qs.values_list('paciente_id', flat=True).distinct()
        pacientes_qs = Paciente.objects.filter(id__in=pacientes_id_base)


        if fecha_inicio_str and fecha_final_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()
                
                # Filtramos Partos y RN por fecha (usando fecha_creacion de tu modelo)
                partos_qs = partos_qs.filter(fecha_creacion__date__range=[fecha_inicio, fecha_final])
                rn_qs = rn_qs.filter(fecha_creacion__date__range=[fecha_inicio, fecha_final])
                
                # Volvemos a filtrar pacientes basado en los partos YA filtrados por fecha
                pacientes_id_filtrados = partos_qs.values_list('paciente_id', flat=True).distinct()
                pacientes_qs = Paciente.objects.filter(id__in=pacientes_id_filtrados)

            except ValueError:
                pass
        
        context["fecha_inicio"] = fecha_inicio_str
        context["fecha_final"] = fecha_final_str


        # --- 2. CONSULTAS (usando los querysets filtrados) ---

        # 1. Totales Generales
        context["total_partos"] = partos_qs.count()
        context["total_recien_nacidos"] = rn_qs.count()
        context["total_pacientes"] = pacientes_qs.count()

        # 2. Distribución Tipo de Parto (y datos para Gráfico)
        tipo_parto_map = dict(Parto.TipoPartoChoices.choices)
        partos_raw = partos_qs.values('tipo_parto').annotate(
            total=Count('id')
        ).order_by('tipo_parto')
        
        distribucion_tipo_parto_list = []
        chart_data_tipo_parto_list = [] 

        for item in partos_raw:
            display_name_str = str(tipo_parto_map.get(item['tipo_parto'], item['tipo_parto']))
            distribucion_tipo_parto_list.append({'tipo_display': display_name_str,'total': item['total']})
            chart_data_tipo_parto_list.append({'value': item['total'],'name': display_name_str})

        context["distribucion_tipo_parto"] = distribucion_tipo_parto_list
        context["chart_data_tipo_parto"] = json.dumps(chart_data_tipo_parto_list)

        # 3. Distribución Sexo Recién Nacidos
        sexo_map = dict(RecienNacido.SexoChoices.choices)
        sexo_raw = rn_qs.values('sexo').annotate(total=Count('id')).order_by('sexo')
        context["distribucion_sexo_rn"] = [
            {'sexo_display': str(sexo_map.get(item['sexo'], item['sexo'])),'total': item['total']} 
            for item in sexo_raw
        ]

        # 4. Estadísticas Vitales RN (Promedios Y Desviación Estándar - Punto 1)
        stats_vitales = rn_qs.aggregate(
            Avg('peso_gramos'),
            Avg('talla_cm'),
            Avg('apgar5'),
        )
        context["promedio_peso_rn"] = stats_vitales.get('peso_gramos__avg')
        context["promedio_talla_rn"] = stats_vitales.get('talla_cm__avg')
        context["promedio_apgar_rn"] = stats_vitales.get('apgar5__avg')

        rn_stats = list(
            rn_qs.values_list("peso_gramos", "talla_cm", "apgar5")
        )

        def _stddev(index):
            serie = [row[index] for row in rn_stats if row[index] is not None]
            return pstdev(serie) if len(serie) > 1 else None

        context["stddev_peso_rn"] = _stddev(0)
        context["stddev_talla_rn"] = _stddev(1)
        context["stddev_apgar_rn"] = _stddev(2)

        # 5. Complicaciones
        # ¡LÓGICA CORREGIDA! Tu modelo usa TextField, no BooleanField.
        # Contamos los partos donde el campo 'complicaciones' NO está vacío.
        context["total_complicaciones"] = partos_qs.exclude(
            Q(complicaciones__isnull=True) | Q(complicaciones__exact='')
        ).count()


        # --- 3. NUEVAS CONSULTAS DEMOGRÁFICAS (Punto 2 y 3) ---
        
        # Moda de Pueblos Originarios
        pueblo_map = dict(Paciente.PuebloOriginarioChoices.choices)
        pueblos_raw = pacientes_qs.values('pueblo_originario').annotate(
            total=Count('id')
        ).order_by('-total') # Ordenamos de mayor a menor
        
        context["distribucion_pueblos"] = [
            {
                'pueblo_display': str(pueblo_map.get(item['pueblo_originario'], item['pueblo_originario'])),
                'total': item['total']
            } for item in pueblos_raw
        ]

        # Moda de Nivel Educacional
        educacion_map = dict(Paciente.NivelEducacionalChoices.choices)
        educacion_raw = pacientes_qs.values('nivel_educacional').annotate(
            total=Count('id')
        ).order_by('-total')
        
        context["distribucion_educacion"] = [
            {
                'educacion_display': str(educacion_map.get(item['nivel_educacional'], item['nivel_educacional'])),
                'total': item['total']
            } for item in educacion_raw
        ]
        
        # Moda de Estado Civil
        estado_civil_map = dict(Paciente.EstadoCivilChoices.choices)
        estado_civil_raw = pacientes_qs.values('estado_civil').annotate(
            total=Count('id')
        ).order_by('-total')
        
        context["distribucion_estado_civil"] = [
            {
                'estado_civil_display': str(estado_civil_map.get(item['estado_civil'], item['estado_civil'])),
                'total': item['total']
            } for item in estado_civil_raw
        ]
        
        # Moda de Nacionalidad
        nacionalidad_map = dict(Paciente.NacionalidadChoices.choices)
        nacionalidad_raw = pacientes_qs.values('nacionalidad').annotate(
            total=Count('id')
        ).order_by('-total')
        
        context["distribucion_nacionalidad"] = [
            {
                'nacionalidad_display': str(nacionalidad_map.get(item['nacionalidad'], item['nacionalidad'])),
                'total': item['total']
            } for item in nacionalidad_raw
        ]

        return context
