"""
Enrutamiento interno para la aplicación Proyectos.
"""

from django.urls import path

from .views import projects_catalog_view

app_name = "proyectos"

urlpatterns = [
    path("", projects_catalog_view, name="catalog"),
]
