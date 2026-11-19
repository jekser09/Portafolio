"""
Capa de selectores (Consultas de Lectura) para la app Curriculum.

Concentra todas las consultas del ORM para el perfil, habilidades, experiencia,
educación y referencias, aplicando optimizaciones estrictas (prefetch_related)
para eliminar cualquier posibilidad de consultas N+1.
"""

from typing import Any

from django.db.models import Prefetch, QuerySet

from .models import (
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Reference,
    Skill,
    SkillCategory,
)


def get_active_profile() -> Profile | None:
    """
    Obtiene el perfil profesional activo (Singleton).

    Returns:
        Instancia de Profile si existe, o None si aún no se ha creado.
    """
    return Profile.objects.first()


def list_skill_categories_with_skills() -> QuerySet[SkillCategory]:
    """
    Obtiene todas las categorías de habilidades con sus habilidades pre-cargadas.

    Aplica Prefetch ordenado para garantizar que tanto las categorías
    como las habilidades internas respeten su campo 'order'.

    Returns:
        QuerySet de SkillCategory con 'skills' pre-cargados.
    """
    skills_prefetch = Prefetch(
        "skills",
        queryset=Skill.objects.order_by("order", "name"),
    )
    return SkillCategory.objects.prefetch_related(skills_prefetch).order_by("order", "name")


def list_visible_experiences() -> QuerySet[Experience]:
    """
    Obtiene todas las experiencias laborales marcadas como visibles.

    Pre-carga los logros específicos asociados (highlights) ordenados por su
    campo 'order' para evitar consultas N+1 en las plantillas o serializadores.

    Returns:
        QuerySet de Experience con 'highlights' pre-cargados.
    """
    highlights_prefetch = Prefetch(
        "highlights",
        queryset=ExperienceHighlight.objects.order_by("order", "id"),
    )
    return (
        Experience.objects.filter(is_visible=True)
        .prefetch_related(highlights_prefetch)
        .order_by("order", "-start_date")
    )


def list_education() -> QuerySet[Education]:
    """
    Obtiene la lista de formación académica ordenada cronológicamente.

    Returns:
        QuerySet de Education ordenado por orden y año de finalización.
    """
    return Education.objects.order_by("order", "-year_completed")


def list_web_visible_references() -> QuerySet[Reference]:
    """
    Obtiene únicamente las referencias autorizadas para mostrarse en la web pública.

    Protege la privacidad excluyendo registros donde 'is_visible_on_web' sea False.

    Returns:
        QuerySet de Reference filtrado por visibilidad web.
    """
    return Reference.objects.filter(is_visible_on_web=True).order_by("order", "name")


def list_all_references_for_cv() -> QuerySet[Reference]:
    """
    Obtiene todas las referencias para inclusión en el generador privado de CV en PDF.

    Returns:
        QuerySet de todas las referencias ordenadas.
    """
    return Reference.objects.all().order_by("order", "name")


def get_cv_page_context() -> dict[str, Any]:
    """
    Agrupa todo el contexto necesario para la vista principal del CV y portafolio.

    Ejecuta un conjunto mínimo y optimizado de consultas para alimentar la plantilla
    web y el payload JSON inicial del constructor de PDF.

    Returns:
        Diccionario con las entidades estructuradas y listas para el template.
    """
    profile = get_active_profile()
    categories = list_skill_categories_with_skills()
    experiences = list_visible_experiences()
    education = list_education()
    references = list_web_visible_references()

    return {
        "profile": profile,
        "skill_categories": categories,
        "experiences": experiences,
        "education": education,
        "references": references,
    }
