"""
Vistas de transporte HTTP para la aplicación Curriculum.

Responsabilidad exclusiva de recibir requests, invocar selectores/servicios
y retornar la respuesta HTTP. Cero lógica de negocio y cero ORM directo.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .selectors import get_cv_page_context
from .services import build_full_cv_payload


def cv_view(request: HttpRequest) -> HttpResponse:
    """
    Renderiza la vista de la Hoja de Vida interactiva.

    Obtiene los datos mediante selectores y serializa el payload base
    para el constructor de CV en PDF del lado del cliente.
    """
    context = get_cv_page_context()
    context["cv_payload"] = build_full_cv_payload()
    return render(request, "curriculum/cv.html", context)
