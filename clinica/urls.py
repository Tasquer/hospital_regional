from django.urls import path
from . import views

app_name = "clinica"

urlpatterns = [
    path("pacientes/", views.PacienteListView.as_view(), name="paciente_list"),
    path("pacientes/nuevo/", views.PacienteCreateView.as_view(), name="paciente_create"),
    path("pacientes/<int:pk>/editar/", views.PacienteUpdateView.as_view(), name="paciente_update"),
    path("pacientes/<int:pk>/", views.PacienteDetailView.as_view(), name="paciente_detail"),
    path("casos/", views.CasoClinicoListView.as_view(), name="caso_list"),
    path("casos/nuevo/", views.CasoClinicoCreateView.as_view(), name="caso_create"),
    path("casos/<int:pk>/editar/", views.CasoClinicoUpdateView.as_view(), name="caso_update"),
    path("casos/<int:pk>/", views.CasoClinicoDetailView.as_view(), name="caso_detail"),
]
