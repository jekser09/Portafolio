"""
Enrutamiento interno para la aplicación Curriculum.
"""

from django.urls import path

from .views import cv_view

app_name = "curriculum"

urlpatterns = [
    path("", cv_view, name="cv_detail"),
]
