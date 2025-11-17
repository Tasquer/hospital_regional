# reportes/urls.py

from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    # Dashboard principal de reportes de obstetricia
    path("", views.ReportesObstetriciaView.as_view(), name="dashboard_obstetricia"),
    
    # Aquí podrán agregar más rutas para reportes específicos
]