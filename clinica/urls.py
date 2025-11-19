from django.urls import path
from . import views

app_name = "clinica"

urlpatterns = [
    path("pacientes/", views.PacienteListView.as_view(), name="paciente_list"),
    path("pacientes/nuevo/", views.PacienteCreateView.as_view(), name="paciente_create"),
    path("pacientes/<int:pk>/editar/", views.PacienteUpdateView.as_view(), name="paciente_update"),
    path("pacientes/<int:pk>/", views.PacienteDetailView.as_view(), name="paciente_detail"),
    path(
        "pacientes/<int:pk>/trazabilidad/",
        views.PacienteTrazabilidadDetailView.as_view(),
        name="paciente_trazabilidad",
    ),
    path("casos/", views.CasoClinicoListView.as_view(), name="caso_list"),
    path("casos/nuevo/", views.CasoClinicoCreateView.as_view(), name="caso_create"),
    path("casos/<int:pk>/editar/", views.CasoClinicoUpdateView.as_view(), name="caso_update"),
    path("casos/<int:pk>/", views.CasoClinicoDetailView.as_view(), name="caso_detail"),
    
    path("partos/", views.PartoListView.as_view(), name="parto_list"),
    path("partos/nuevo/", views.PartoCreateView.as_view(), name="parto_create"),
    path("partos/<int:pk>/editar/", views.PartoUpdateView.as_view(), name="parto_update"),

    path(
        "recien-nacidos/",
        views.RecienNacidoListView.as_view(),
        name="recien_nacido_list",
    ),
    path(
        "recien-nacidos/nuevo/",
        views.RecienNacidoCreateView.as_view(),
        name="recien_nacido_create",
    ),
    path(
        "recien-nacidos/<int:pk>/editar/",
        views.RecienNacidoUpdateView.as_view(),
        name="recien_nacido_update",
    ),
    path(
        "recien-nacidos/<int:pk>/",
        views.RecienNacidoDetailView.as_view(),
        name="recien_nacido_detail",
    ),
]
