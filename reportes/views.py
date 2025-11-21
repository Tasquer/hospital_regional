# reportes/views.py

import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime, timedelta
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, StdDev, Q
from django.db.models.functions import TruncDate
from django.template.loader import get_template
from xhtml2pdf import pisa
from clinica.models import Paciente, Parto, RecienNacido

# --- MIXIN DE FILTRADO ---
class ReporteFilterMixin:
    def get_filtered_querysets(self, request):
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_final_str = request.GET.get('fecha_final')

        partos_qs = Parto.objects.all()
        rn_qs = RecienNacido.objects.all()
        pacientes_qs = Paciente.objects.all()

        if fecha_inicio_str and fecha_final_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_final = datetime.strptime(fecha_final_str, '%Y-%m-%d').date()
                
                partos_qs = partos_qs.filter(fecha_hora__date__range=[fecha_inicio, fecha_final])
                rn_qs = rn_qs.filter(parto__fecha_hora__date__range=[fecha_inicio, fecha_final])
                
                ids = partos_qs.values_list('paciente_id', flat=True).distinct()
                pacientes_qs = Paciente.objects.filter(id__in=ids)
            except ValueError:
                pass
        else:
            ids = partos_qs.values_list('paciente_id', flat=True).distinct()
            pacientes_qs = Paciente.objects.filter(id__in=ids)

        return partos_qs, rn_qs, pacientes_qs, fecha_inicio_str, fecha_final_str


# --- VISTA DASHBOARD ---
class ReportesObstetriciaView(LoginRequiredMixin, ReporteFilterMixin, TemplateView):
    template_name = "reportes/dashboard_obstetricia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partos_qs, rn_qs, pacientes_qs, f_ini, f_fin = self.get_filtered_querysets(self.request)
        
        context.update({"fecha_inicio": f_ini, "fecha_final": f_fin})

        # Totales
        context["total_partos"] = partos_qs.count()
        context["total_recien_nacidos"] = rn_qs.count()
        context["total_complicaciones"] = partos_qs.exclude(Q(complicaciones__isnull=True) | Q(complicaciones__exact='')).count()

        # Listas Resumen
        tipo_map = dict(Parto.TipoPartoChoices.choices)
        tipo_raw = partos_qs.values('tipo_parto').annotate(total=Count('id')).order_by('tipo_parto')
        context["distribucion_tipo_parto"] = [{'tipo_display': str(tipo_map.get(i['tipo_parto'], i['tipo_parto'])), 'total': i['total']} for i in tipo_raw]

        pos_map = dict(Parto.PosicionPartoChoices.choices)
        pos_raw = partos_qs.values('posicion_parto').annotate(total=Count('id')).order_by('-total')
        context["distribucion_posicion_parto"] = [{'posicion_display': str(pos_map.get(i['posicion_parto'], i['posicion_parto'])), 'total': i['total']} for i in pos_raw if i['posicion_parto']]

        sex_map = dict(RecienNacido.SexoChoices.choices)
        sex_raw = rn_qs.values('sexo').annotate(total=Count('id')).order_by('sexo')
        context["distribucion_sexo_rn"] = [{'sexo_display': str(sex_map.get(i['sexo'], i['sexo'])), 'total': i['total']} for i in sex_raw]

        # Stats Vitales
        stats = rn_qs.aggregate(
            Avg('peso_gramos'), StdDev('peso_gramos'),
            Avg('talla_cm'), StdDev('talla_cm'),
            Avg('apgar5'), StdDev('apgar5')
        )
        context.update({
            "promedio_peso_rn": stats.get('peso_gramos__avg'), "stddev_peso_rn": stats.get('peso_gramos__stddev'),
            "promedio_talla_rn": stats.get('talla_cm__avg'), "stddev_talla_rn": stats.get('talla_cm__stddev'),
            "promedio_apgar_rn": stats.get('apgar5__avg'), "stddev_apgar_rn": stats.get('apgar5__stddev'),
        })

        # Demografía
        def get_dist(qs, field, choices):
            mapping = dict(choices.choices)
            data = qs.values(field).annotate(total=Count('id')).order_by('-total')
            return [{'display': str(mapping.get(i[field], i[field])), 'total': i['total']} for i in data if i[field]]

        context["distribucion_pueblos"] = get_dist(pacientes_qs, 'pueblo_originario', Paciente.PuebloOriginarioChoices)
        context["distribucion_educacion"] = get_dist(pacientes_qs, 'nivel_educacional', Paciente.NivelEducacionalChoices)
        context["distribucion_estado_civil"] = get_dist(pacientes_qs, 'estado_civil', Paciente.EstadoCivilChoices)
        context["distribucion_nacionalidad"] = get_dist(pacientes_qs, 'nacionalidad', Paciente.NacionalidadChoices)

        return context


# --- VISTA API (JSON) ---
class ChartDataView(LoginRequiredMixin, View):
    def get(self, request):
        metric = request.GET.get('metric')
        days_param = request.GET.get('days', '7')

        start_date = None
        title_suffix = ""

        if days_param == 'historic':
            start_date = None
            title_suffix = "(Histórico)"
        else:
            try:
                days = int(days_param)
                start_date = timezone.now().date() - timedelta(days=days)
                title_suffix = f"(Últimos {days} días)"
            except ValueError:
                days = 7
                start_date = timezone.now().date() - timedelta(days=7)
                title_suffix = "(Últimos 7 días)"

        data = {}

        # --- 1. EVOLUCIÓN TEMPORAL ---
        if metric == 'partos_evolucion':
            qs = Parto.objects.all()
            if start_date: qs = qs.filter(fecha_hora__date__gte=start_date)
            
            evo = qs.annotate(date=TruncDate('fecha_hora')).values('date').annotate(c=Count('id')).order_by('date')
            chart = [[i['date'].strftime('%Y-%m-%d'), i['c']] for i in evo]
            data = {'title': f'Partos {title_suffix}', 'type': 'line', 'series_data': chart, 'labels': [x[0] for x in chart], 'values': [x[1] for x in chart]}

        elif metric == 'vitales_peso_evolucion':
            qs = RecienNacido.objects.all()
            if start_date: qs = qs.filter(parto__fecha_hora__date__gte=start_date)

            evo = qs.annotate(date=TruncDate('parto__fecha_hora')).values('date').annotate(avg=Avg('peso_gramos')).order_by('date')
            chart = [[i['date'].strftime('%Y-%m-%d'), round(i['avg'], 1)] for i in evo]
            data = {'title': f'Peso Promedio {title_suffix}', 'type': 'line', 'color': '#34d399', 'series_data': chart, 'labels': [x[0] for x in chart], 'values': [x[1] for x in chart]}

        # --- 2. DISTRIBUCIONES (PIE/BARRA) ---
        # NUEVO: Complicaciones ahora es distribución (Torta) en vez de evolución (Línea)
        elif metric == 'complicaciones_distribucion':
             qs = Parto.objects.exclude(Q(complicaciones__isnull=True)|Q(complicaciones__exact=''))
             if start_date: qs = qs.filter(fecha_hora__date__gte=start_date)

             # Agrupamos por el texto de la complicación
             raw = qs.values('complicaciones').annotate(t=Count('id')).order_by('-t')
             # Tomamos las top 6 para que la torta no sea ilegible si hay muchas distintas
             top_raw = raw[:6]
             chart = [{'name': i['complicaciones'], 'value': i['t']} for i in top_raw]
             data = {'title': f'Tipos de Complicaciones {title_suffix}', 'type': 'pie', 'series_data': chart}

        elif metric == 'sexo_distribucion':
            qs = RecienNacido.objects.all()
            if start_date: qs = qs.filter(parto__fecha_hora__date__gte=start_date)

            mapping = dict(RecienNacido.SexoChoices.choices)
            raw = qs.values('sexo').annotate(t=Count('id'))
            chart = [{'name': str(mapping.get(i['sexo'], i['sexo'])), 'value': i['t']} for i in raw]
            data = {'title': f'Sexo RN {title_suffix}', 'type': 'pie', 'series_data': chart}

        elif metric == 'tipo_parto_distribucion':
            qs = Parto.objects.all()
            if start_date: qs = qs.filter(fecha_hora__date__gte=start_date)

            mapping = dict(Parto.TipoPartoChoices.choices)
            raw = qs.values('tipo_parto').annotate(t=Count('id'))
            chart = [{'name': str(mapping.get(i['tipo_parto'], i['tipo_parto'])), 'value': i['t']} for i in raw]
            data = {'title': f'Tipo Parto {title_suffix}', 'type': 'pie', 'series_data': chart}

        elif metric == 'posicion_distribucion':
            qs = Parto.objects.exclude(posicion_parto__exact='')
            if start_date: qs = qs.filter(fecha_hora__date__gte=start_date)

            mapping = dict(Parto.PosicionPartoChoices.choices)
            raw = qs.values('posicion_parto').annotate(t=Count('id')).order_by('-t')
            chart = [{'name': str(mapping.get(i['posicion_parto'], i['posicion_parto'])), 'value': i['t']} for i in raw]
            data = {'title': f'Posición {title_suffix}', 'type': 'bar_horizontal', 'series_data': chart, 'labels': [x['name'] for x in chart], 'values': [x['value'] for x in chart]}

        # --- 3. DEMOGRAFÍA ---
        elif metric in ['pueblo_distribucion', 'educacion_distribucion', 'estado_civil_distribucion', 'nacionalidad_distribucion']:
            qs_partos = Parto.objects.all()
            if start_date: qs_partos = qs_partos.filter(fecha_hora__date__gte=start_date)
            
            pacientes_qs = Paciente.objects.filter(partos__in=qs_partos).distinct()
            
            config = {
                'pueblo_distribucion': ('pueblo_originario', Paciente.PuebloOriginarioChoices, 'pie'),
                'educacion_distribucion': ('nivel_educacional', Paciente.NivelEducacionalChoices, 'bar'),
                'estado_civil_distribucion': ('estado_civil', Paciente.EstadoCivilChoices, 'pie'),
                'nacionalidad_distribucion': ('nacionalidad', Paciente.NacionalidadChoices, 'pie'),
            }
            fname, fchoices, ftype = config[metric]
            mapping = dict(fchoices.choices)
            raw = pacientes_qs.values(fname).annotate(t=Count('id')).order_by('-t')
            chart = [{'name': str(mapping.get(i[fname], i[fname])), 'value': i['t']} for i in raw if i[fname]]
            
            data = {'title': f'Distribución {title_suffix}', 'series_data': chart}
            if ftype == 'bar':
                data['type'] = 'bar'; data['labels'] = [x['name'] for x in chart]; data['values'] = [x['value'] for x in chart]
            else:
                data['type'] = 'pie'

        return JsonResponse(data)


# --- VISTA EXPORTAR EXCEL (Sin cambios) ---
class ExportarReporteExcelView(LoginRequiredMixin, ReporteFilterMixin, View):
    def get(self, request):
        partos_qs, rn_qs, _, f_ini, f_fin = self.get_filtered_querysets(request)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Resumen Obstétrico"
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F81BD")
        
        ws['A1'] = f"Reporte: {f_ini or 'Histórico'} - {f_fin or 'Hoy'}"
        ws['A3'] = "Total Partos"; ws['B3'] = partos_qs.count()
        
        cols = ["Fecha", "Paciente", "Edad", "Pueblo", "Educación", "Tipo", "Posición", "Sexo RN", "Peso", "Talla"]
        for idx, title in enumerate(cols, 1):
            c = ws.cell(row=6, column=idx, value=title)
            c.font = header_font; c.fill = header_fill

        row = 7
        for p in partos_qs.select_related('paciente').prefetch_related('recien_nacidos'):
            rn = p.recien_nacidos.first()
            edad = "N/A"
            if p.paciente.fecha_nacimiento:
                hoy = timezone.now().date()
                fn = p.paciente.fecha_nacimiento
                edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))

            ws.append([
                p.fecha_hora.strftime('%d/%m/%Y'), str(p.paciente), edad,
                p.paciente.get_pueblo_originario_display(), p.paciente.get_nivel_educacional_display(),
                p.get_tipo_parto_display(), p.get_posicion_parto_display(),
                rn.get_sexo_display() if rn else "-", rn.peso_gramos if rn else "-", rn.talla_cm if rn else "-"
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Reporte_{datetime.now().strftime("%Y%m%d")}.xlsx'
        wb.save(response)
        return response


# --- VISTA EXPORTAR PDF (Sin cambios) ---
class ExportarReportePDFView(LoginRequiredMixin, ReporteFilterMixin, View):
    def get(self, request):
        view = ReportesObstetriciaView()
        view.request = request
        context = view.get_context_data()
        template = get_template('reportes/reporte_pdf.html')
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Reporte.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response