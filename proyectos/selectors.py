"""
Capa de selectores (Consultas de Lectura) para la app Proyectos.

Concentra todas las consultas del ORM para proyectos, categorías funcionales
y tecnologías asociadas, aplicando optimizaciones estrictas (select_related y
prefetch_related) para eliminar consultas N+1.
"""

from typing import Any

from django.db.models import Prefetch, QuerySet

from curriculum.models import Skill

from .models import Project, ProjectCategory


def list_visible_projects() -> QuerySet[Project]:
    """
    Obtiene todos los proyectos marcados como visibles con su categoría y stack.

    Pre-carga la categoría funcional mediante select_related y el stack de
    habilidades (con su categoría) mediante Prefetch ordenado para evitar
    consultas N+1 en plantillas o serializadores.

    Returns:
        QuerySet de Project visible ordenado por prioridad, destacado y creación.
    """
    skills_prefetch = Prefetch(
        "skills",
        queryset=Skill.objects.select_related("category").order_by(
            "category__order", "order", "name"
        ),
    )
    return (
        Project.objects.filter(is_visible=True)
        .select_related("category")
        .prefetch_related(skills_prefetch)
        .order_by("order", "-is_featured", "-created_at")
    )


def list_active_project_categories() -> QuerySet[ProjectCategory]:
    """
    Obtiene únicamente las categorías que poseen al menos un proyecto visible.

    Returns:
        QuerySet distinto de ProjectCategory ordenado por orden y nombre.
    """
    return (
        ProjectCategory.objects.filter(projects__is_visible=True)
        .distinct()
        .order_by("order", "name")
    )


def list_used_project_skills() -> QuerySet[Skill]:
    """
    Obtiene únicamente las habilidades usadas en al menos un proyecto visible.

    Returns:
        QuerySet distinto de Skill ordenado por categoría, orden y nombre.
    """
    return (
        Skill.objects.filter(projects__is_visible=True)
        .select_related("category")
        .distinct()
        .order_by("category__order", "order", "name")
    )


def get_projects_page_context() -> dict[str, Any]:
    """
    Agrupa todo el contexto inicial necesario para la vista /prodep/.

    Returns:
        Diccionario con proyectos visibles, categorías activas y stack usado.
    """
    return {
        "projects": list_visible_projects(),
        "categories": list_active_project_categories(),
        "skills": list_used_project_skills(),
    }
