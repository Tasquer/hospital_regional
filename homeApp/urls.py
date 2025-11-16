from django.urls import path
from homeApp import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="Home"),
]
