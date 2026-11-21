"""
Capa de servicios (Lógica de Negocio y Transformaciones) para la app Proyectos.

Concentra la resolución de etiquetas CTA según el tipo de entregable,
el ensamblado del payload JSON seguro del catálogo de proyectos y el filtrado
interactivo por categoría funcional, tipo de proyecto o tecnología/texto.
"""

from typing import Any

from .models import Project, ProjectType
from .selectors import (
    list_active_project_categories,
    list_used_project_skills,
    list_visible_projects,
)

PROJECT_CTA_LABELS: dict[str, str] = {
    ProjectType.WEB: "Abrir Aplicación",
    ProjectType.API: "Ver Endpoint / Demo",
    ProjectType.DESKTOP: "Ver Release / Descargar",
}


def resolve_project_cta_label(project: Project) -> str:
    """
    Determina la etiqueta principal del botón de acción según el tipo de proyecto.

    Args:
        project: Instancia del modelo Project.

    Returns:
        Texto del CTA adaptado a proyecto WEB, API o DESKTOP.
    """
    return PROJECT_CTA_LABELS.get(project.project_type, "Ver Proyecto")


def build_projects_catalog_payload() -> dict[str, Any]:
    """
    Construye el payload del catálogo de proyectos serializado en tipos primitivos.

    Este payload se inyecta de forma segura mediante json_script para alimentar
    el filtrado en el cliente, la carga diferida de iframes y el visor de
    documentación técnica Markdown/PDF sin round-trips adicionales.

    Returns:
        Diccionario serializable a JSON con categorías, stack usado y proyectos.
    """
    categories = list_active_project_categories()
    skills = list_used_project_skills()
    projects = list_visible_projects()

    categories_data = [
        {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "order": category.order,
        }
        for category in categories
    ]

    skills_data = [
        {
            "id": skill.id,
            "name": skill.name,
            "category": skill.category.name,
        }
        for skill in skills
    ]

    projects_data: list[dict[str, Any]] = []
    for project in projects:
        project_skills = [
            {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category.name,
            }
            for skill in project.skills.all()
        ]
        skill_names = [skill["name"] for skill in project_skills]
        search_parts = [
            project.title,
            project.category.name,
            project.get_project_type_display(),
            project.short_description,
            *skill_names,
        ]
        search_index = " ".join(
            part.strip().lower() for part in search_parts if part and part.strip()
        )

        projects_data.append(
            {
                "id": project.id,
                "title": project.title,
                "slug": project.slug,
                "project_type": project.project_type,
                "project_type_label": project.get_project_type_display(),
                "category": {
                    "id": project.category.id,
                    "name": project.category.name,
                    "slug": project.category.slug,
                },
                "short_description": project.short_description,
                "detailed_description": project.detailed_description,
                "documentation_pdf_url": (
                    project.documentation_pdf.url if project.documentation_pdf else None
                ),
                "live_url": project.live_url.strip(),
                "preview_image_url": (
                    project.preview_image.url if project.preview_image else None
                ),
                "repo_url": project.repo_url.strip()
                if project.has_public_repo
                else None,
                "has_public_repo": project.has_public_repo,
                "can_embed_preview": project.can_embed_preview,
                "has_technical_docs": project.has_technical_docs,
                "cta_label": resolve_project_cta_label(project),
                "is_featured": project.is_featured,
                "skills": project_skills,
                "search_index": search_index,
            }
        )

    return {
        "categories": categories_data,
        "skills": skills_data,
        "projects": projects_data,
    }


def filter_projects_payload(
    catalog_payload: dict[str, Any],
    *,
    category_slug: str | None = None,
    tech_or_query: str | None = None,
    project_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Filtra el catálogo serializado por categoría, tecnología/búsqueda y tipo.

    Args:
        catalog_payload: Diccionario generado por build_projects_catalog_payload.
        category_slug: Slug de la categoría funcional (opcional).
        tech_or_query: Término de tecnología o búsqueda libre (ej: "PYTHON").
        project_type: Tipo de proyecto ("WEB", "API", "DESKTOP", opcional).

    Returns:
        Lista de proyectos que cumplen todos los criterios activos.
    """
    normalized_category = (
        category_slug.strip().lower()
        if category_slug and category_slug.strip()
        else None
    )
    normalized_type = (
        project_type.strip().upper() if project_type and project_type.strip() else None
    )
    normalized_query = (
        tech_or_query.strip().lower()
        if tech_or_query and tech_or_query.strip()
        else None
    )

    filtered: list[dict[str, Any]] = []
    for project in catalog_payload.get("projects", []):
        if (
            normalized_category
            and project.get("category", {}).get("slug", "").lower()
            != normalized_category
        ):
            continue

        if (
            normalized_type
            and project.get("project_type", "").upper() != normalized_type
        ):
            continue

        if normalized_query:
            skill_match = any(
                normalized_query in skill.get("name", "").lower()
                for skill in project.get("skills", [])
            )
            index_match = normalized_query in project.get("search_index", "")
            if not skill_match and not index_match:
                continue

        filtered.append(project)

    return filtered
