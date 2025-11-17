import json
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.translation import gettext as _  # Cambiado aquí
from UsuarioApp.models import Profile
from clinica.models import Parto


class HomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = "pages/index.html"

    def get_queryset(self):
        last_connected_users = User.objects.filter(
            Q(last_login__isnull=False)
        ).order_by("-last_login")[:5]
        return last_connected_users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agrega los usuarios activos al contexto
        recent_activity_cutoff = timezone.now() - timezone.timedelta(minutes=2)
        active_users = Profile.objects.filter(
            last_activity__gte=recent_activity_cutoff
        ).values_list("user_FK_id", flat=True)
        context["active_users"] = active_users
        
        # Datos para el gráfico de distribución de tipos de parto
        distribucion_partos = Parto.objects.values('tipo_parto').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Extraer labels y datos
        grafico_labels = []
        grafico_data = []
        
        # Crear diccionario de choices convertido a strings
        tipo_parto_dict = {key: str(value) for key, value in Parto.TipoPartoChoices.choices}
        
        for item in distribucion_partos:
            # Obtener el display name del tipo de parto y convertir a string
            tipo_display = tipo_parto_dict.get(
                item['tipo_parto'], 
                str(item['tipo_parto'])
            )
            grafico_labels.append(tipo_display)
            grafico_data.append(item['total'])
        
        # Convertir a JSON para pasar a JavaScript
        context['grafico_labels'] = json.dumps(grafico_labels)
        context['grafico_data'] = json.dumps(grafico_data)
        
        return context