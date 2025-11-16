from django.urls import path
from UsuarioApp import views

urlpatterns = [
    path("usuarios/", views.UserListView.as_view(), name="User"),
    path("registro/", views.UserCreateView.as_view(), name="Register"),
    path("perfil/", views.ProfileUpdateView.as_view(), name="Profile"),
]
