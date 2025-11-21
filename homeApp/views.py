# homeApp/views.py
import json
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from UsuarioApp.models import Profile
from clinica.models import Parto, RecienNacido


class HomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = "pages/index.html"

    def get_queryset(self):
        # Usuarios recientemente conectados
        return User.objects.filter(
            Q(last_login__isnull=False)
        ).order_by("-last_login")[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Usuarios activos (últimos 2 minutos)
        recent_activity_cutoff = timezone.now() - timedelta(minutes=2)
        active_users = Profile.objects.filter(
            last_activity__gte=recent_activity_cutoff
        ).values_list("user_FK_id", flat=True)
        context["active_users"] = list(active_users)
        
        # --- DATOS DEL TURNO (HOY) ---
        inicio_hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Partos hoy
        partos_hoy_qs = Parto.objects.filter(fecha_hora__gte=inicio_hoy)
        context["partos_hoy"] = partos_hoy_qs.count()
        
        # RN hoy
        rn_hoy_qs = RecienNacido.objects.filter(parto__fecha_hora__gte=inicio_hoy)
        context["rn_hoy"] = rn_hoy_qs.count()
        
        # Peso promedio RN de hoy
        if context["rn_hoy"] > 0:
            context["peso_promedio_hoy"] = rn_hoy_qs.aggregate(
                Avg('peso_gramos')
            )['peso_gramos__avg']
        
        # --- ALERTAS ACTIVAS ---
        alertas_count = 0
        alertas_criticas = []
        
        # 1. RN con APGAR bajo hoy
        rn_apgar_bajo = rn_hoy_qs.filter(apgar1__lt=7)
        context["rn_apgar_bajo_hoy"] = rn_apgar_bajo.count()
        alertas_count += context["rn_apgar_bajo_hoy"]
        
        # Agregar a alertas críticas
        for rn in rn_apgar_bajo[:3]:  # Máximo 3
            alertas_criticas.append({
                'tipo': 'APGAR',
                'descripcion': f'RN {rn.identificador} - APGAR 1\': {rn.apgar1}',
                'url': f'/clinica/recien-nacidos/{rn.pk}/'
            })
        
        # 2. RN bajo peso hoy
        rn_bajo_peso = rn_hoy_qs.filter(peso_gramos__lt=2500)
        context["rn_bajo_peso_hoy"] = rn_bajo_peso.count()
        alertas_count += context["rn_bajo_peso_hoy"]
        
        # Agregar a alertas críticas
        for rn in rn_bajo_peso[:2]:
            if len(alertas_criticas) < 5:  # Máximo 5 alertas totales
                alertas_criticas.append({
                    'tipo': 'PESO',
                    'descripcion': f'RN {rn.identificador} - {rn.peso_gramos}g (bajo peso)',
                    'url': f'/clinica/recien-nacidos/{rn.pk}/'
                })
        
        # 3. RN normales (para estadística)
        context["rn_normales_hoy"] = context["rn_hoy"] - context["rn_apgar_bajo_hoy"] - context["rn_bajo_peso_hoy"]
        
        # 4. Partos con complicaciones hoy
        partos_complicaciones_hoy = partos_hoy_qs.exclude(
            Q(complicaciones__isnull=True) | Q(complicaciones__exact='')
        )
        alertas_count += partos_complicaciones_hoy.count()
        
        # Agregar a alertas críticas
        for parto in partos_complicaciones_hoy[:2]:
            if len(alertas_criticas) < 5:
                alertas_criticas.append({
                    'tipo': 'COMPLIC',
                    'descripcion': f'Parto #{parto.id} - {parto.paciente.nombre_completo[:30]}',
                    'url': f'/clinica/partos/{parto.pk}/'
                })
        
        context["alertas_activas"] = alertas_count
        context["alertas_criticas"] = alertas_criticas if alertas_criticas else None
        
        # --- PARTOS PENDIENTES DE ALTA ---
        hace_48_horas = timezone.now() - timedelta(hours=48)
        context["partos_sin_alta"] = Parto.objects.filter(
            fecha_hora__gte=hace_48_horas,
            alta__isnull=True
        ).count()
        
        # --- PARTO RECIENTE (para animación) ---
        hace_30_min = timezone.now() - timedelta(minutes=30)
        context["parto_reciente"] = Parto.objects.filter(
            fecha_hora__gte=hace_30_min
        ).exists()
        
        # --- TIPOS DE PARTO HOY ---
        tipo_parto_dict = dict(Parto.TipoPartoChoices.choices)
        tipos_parto_raw = partos_hoy_qs.values('tipo_parto').annotate(
            total=Count('id')
        ).order_by('-total')
        
        tipos_parto_hoy = []
        for item in tipos_parto_raw:
            nombre = tipo_parto_dict.get(item['tipo_parto'], item['tipo_parto'])
            total = item['total']
            porcentaje = round((total / context["partos_hoy"] * 100), 2) if context["partos_hoy"] > 0 else 0
            tipos_parto_hoy.append({
                'nombre': nombre,
                'total': total,
                'porcentaje': porcentaje
            })
        
        context["tipos_parto_hoy"] = tipos_parto_hoy
        
        # --- ACTIVIDAD DEL TURNO (ÚLTIMAS 24 HORAS POR HORA) ---
        hace_24_horas = timezone.now() - timedelta(hours=24)
        
        # Generar todas las horas del período
        horas_labels = []
        horas_data = []
        
        for i in range(24, -1, -1):  # De hace 24 horas hasta ahora
            hora_inicio = timezone.now() - timedelta(hours=i)
            hora_fin = hora_inicio + timedelta(hours=1)
            
            # Formatear etiqueta
            horas_labels.append(hora_inicio.strftime("%d/%m %H:%M"))
            
            # Contar partos en esa hora
            partos_en_hora = Parto.objects.filter(
                fecha_hora__gte=hora_inicio,
                fecha_hora__lt=hora_fin
            ).count()
            
            horas_data.append(partos_en_hora)
        
        context['turno_labels'] = json.dumps(horas_labels)
        context['turno_data'] = json.dumps(horas_data)
        
        return context