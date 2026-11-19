"""
Capa de servicios (Lógica de Negocio y Transformaciones) para la app Curriculum.

Concentra las reglas de negocio, formateo de periodos laborales y ensamblado
del payload JSON estructurado para el generador de CV en PDF (pdfmake)
en el navegador del cliente.
"""

from typing import Any

from .models import Experience
from .selectors import (
    get_active_profile,
    list_all_references_for_cv,
    list_education,
    list_skill_categories_with_skills,
    list_visible_experiences,
    list_web_visible_references,
)

SPANISH_MONTHS = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def format_experience_period(experience: Experience) -> str:
    """
    Formatea el rango de fechas de una experiencia laboral en formato legible.

    Ejemplo: 'Enero 2025 a Septiembre 2026' o 'Enero 2025 a Presente'.

    Args:
        experience: Instancia del modelo Experience.

    Returns:
        Cadena de texto con el periodo formateado.
    """
    start_month = SPANISH_MONTHS.get(experience.start_date.month, "")
    start_str = f"{start_month} {experience.start_date.year}"

    if experience.is_current or not experience.end_date:
        end_str = "Presente"
    else:
        end_month = SPANISH_MONTHS.get(experience.end_date.month, "")
        end_str = f"{end_month} {experience.end_date.year}"

    return f"{start_str} a {end_str}"


def build_full_cv_payload(*, include_all_references: bool = False) -> dict[str, Any]:
    """
    Construye el payload completo de datos del CV serializado en tipos primitivos.

    Este payload se inyecta de forma segura en la plantilla mediante
    json_script para que el script cliente (pdfmake) pueda operar de
    forma reactiva sin necesidad de round-trips adicionales.

    Args:
        include_all_references: Si es True, incluye todas las referencias (para CV
            privado). Si es False, solo incluye referencias autorizadas para web.

    Returns:
        Diccionario serializable a JSON con el perfil, categorías de habilidades,
        experiencias con logros, educación y referencias.
    """
    profile = get_active_profile()
    skill_categories = list_skill_categories_with_skills()
    experiences = list_visible_experiences()
    education = list_education()

    if include_all_references:
        references = list_all_references_for_cv()
    else:
        references = list_web_visible_references()

    profile_data: dict[str, Any] = {}
    if profile:
        profile_data = {
            "full_name": profile.full_name,
            "headline": profile.headline,
            "bio": profile.bio,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
            "github_url": profile.github_url,
            "linkedin_url": profile.linkedin_url,
            "avatar_url": profile.avatar.url if profile.avatar else None,
        }

    skills_data = [
        {
            "id": category.id,
            "name": category.name,
            "order": category.order,
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "is_highlighted": skill.is_highlighted,
                    "order": skill.order,
                }
                for skill in category.skills.all()
            ],
        }
        for category in skill_categories
    ]

    experiences_data = [
        {
            "id": exp.id,
            "company": exp.company,
            "role": exp.role,
            "period": format_experience_period(exp),
            "is_current": exp.is_current,
            "order": exp.order,
            "highlights": [
                {
                    "id": h.id,
                    "description": h.description,
                    "order": h.order,
                }
                for h in exp.highlights.all()
            ],
        }
        for exp in experiences
    ]

    education_data = [
        {
            "id": edu.id,
            "institution": edu.institution,
            "degree": edu.degree,
            "year_completed": edu.year_completed,
            "is_in_progress": edu.is_in_progress,
            "order": edu.order,
        }
        for edu in education
    ]

    references_data = [
        {
            "id": ref.id,
            "name": ref.name,
            "role": ref.role,
            "phone": ref.phone,
            "email": ref.email,
            "is_visible_on_web": ref.is_visible_on_web,
        }
        for ref in references
    ]

    return {
        "profile": profile_data,
        "skills_by_category": skills_data,
        "experiences": experiences_data,
        "education": education_data,
        "references": references_data,
    }


def filter_cv_payload_by_selection(
    full_payload: dict[str, Any],
    *,
    selected_experience_ids: list[int] | None = None,
    selected_category_ids: list[int] | None = None,
    selected_skill_ids: list[int] | None = None,
    include_references: bool = False,
) -> dict[str, Any]:
    """
    Filtra un payload de CV basándose en la selección granular del usuario.

    Permite generar variantes a medida del CV (ej: solo Backend, o solo ciertas empresas).

    Args:
        full_payload: Diccionario base generado por build_full_cv_payload.
        selected_experience_ids: Lista de IDs de experiencias a incluir (None = todas).
        selected_category_ids: Lista de IDs de categorías a incluir (None = todas).
        selected_skill_ids: Lista de IDs de habilidades específicas a incluir (None = todas).
        include_references: Si se deben incluir las referencias en el documento final.

    Returns:
        Diccionario filtrado listo para la compilación del PDF.
    """
    filtered = {
        "profile": full_payload.get("profile", {}),
        "education": full_payload.get("education", []),
        "references": full_payload.get("references", []) if include_references else [],
    }

    # Filtrar experiencias
    if selected_experience_ids is None:
        filtered["experiences"] = full_payload.get("experiences", [])
    else:
        exp_id_set = set(selected_experience_ids)
        filtered["experiences"] = [
            exp for exp in full_payload.get("experiences", []) if exp["id"] in exp_id_set
        ]

    # Filtrar categorías y habilidades
    categories = full_payload.get("skills_by_category", [])
    if selected_category_ids is not None:
        cat_id_set = set(selected_category_ids)
        categories = [cat for cat in categories if cat["id"] in cat_id_set]

    if selected_skill_ids is not None:
        skill_id_set = set(selected_skill_ids)
        filtered_categories = []
        for cat in categories:
            filtered_skills = [s for s in cat["skills"] if s["id"] in skill_id_set]
            if filtered_skills:
                cat_copy = dict(cat)
                cat_copy["skills"] = filtered_skills
                filtered_categories.append(cat_copy)
        filtered["skills_by_category"] = filtered_categories
    else:
        filtered["skills_by_category"] = categories

    return filtered
