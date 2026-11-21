"""
Vistas de transporte HTTP para la aplicación Proyectos.

Responsabilidad exclusiva de recibir requests, invocar selectores/servicios
y retornar la respuesta HTTP. Cero lógica de negocio y cero ORM directo.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .selectors import get_projects_page_context
from .services import build_projects_catalog_payload


def projects_catalog_view(request: HttpRequest) -> HttpResponse:
    """
    Renderiza la vista del catálogo técnico de proyectos (/prodep/).

    Obtiene proyectos visibles, categorías funcionales y stack tecnológico vía
    selectores optimizados, e inyecta el payload JSON serializado mediante
    servicios para alimentar los filtros reactivos y visor de documentación.
    """
    context = get_projects_page_context()
    context["catalog_payload"] = build_projects_catalog_payload()
    return render(request, "proyectos/proyectos.html", context)
