# homeApp/views.py

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

# Importamos modelos de otras apps
from UsuarioApp.models import Profile
from clinica.models import Parto, Alta

class HomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = "pages/index.html"

    def get_queryset(self):
        # Mantenemos la lista de usuarios conectados recientemente (panel inferior)
        return User.objects.filter(Q(last_login__isnull=False)).order_by("-last_login")[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # --- DEFINICIÓN DE UMBRALES ---
        # El corte para pasar de "Recuperación" a "Sala" son 2 horas post-parto
        umbral_recuperacion = now - timedelta(hours=2)
        
        # --- COLUMNA 1: RECUPERACIÓN INMEDIATA (< 2 horas) ---
        # Ordenamos descendente (lo más reciente arriba)
        context["col_recuperacion"] = Parto.objects.filter(
            fecha_hora__gte=umbral_recuperacion
        ).select_related('paciente').prefetch_related('recien_nacidos').order_by('-fecha_hora')

        # --- COLUMNA 2: SALA / PUERPERIO (> 2 horas y sin Alta) ---
        # Ordenamos ascendente (FIFO: la que lleva más tiempo debería irse antes)
        context["col_sala"] = Parto.objects.filter(
            fecha_hora__lt=umbral_recuperacion,
            alta__isnull=True
        ).select_related('paciente').prefetch_related('recien_nacidos').order_by('fecha_hora')

        # --- COLUMNA 3: ALTAS DEL DÍA (Hoy) ---
        context["col_altas"] = Alta.objects.filter(
            fecha_alta__date=now.date()
        ).select_related('parto__paciente', 'profesional_responsable').order_by('-fecha_alta')

        # --- UTILITARIOS PARA EL FRONTEND ---
        # Calculamos totales para los badges de las columnas
        context["total_recuperacion"] = context["col_recuperacion"].count()
        context["total_sala"] = context["col_sala"].count()
        context["total_altas"] = context["col_altas"].count()

        # Mantenemos lógica de usuarios activos (círculo verde de online)
        recent_activity_cutoff = now - timedelta(minutes=2)
        active_users = Profile.objects.filter(
            last_activity__gte=recent_activity_cutoff
        ).values_list("user_FK_id", flat=True)
        context["active_users"] = list(active_users)

        return context