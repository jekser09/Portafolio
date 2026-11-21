"""
Configuración del Django Admin para la aplicación de Proyectos.

Permite administrar categorías funcionales (RAG, POS, ETL, etc.) y proyectos
técnicos con selector horizontal de stack tecnológico, búsqueda y control de
visibilidad/prioridad.
"""

from typing import ClassVar

from django.contrib import admin

from .models import Project, ProjectCategory


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """Administración de categorías funcionales de proyectos."""

    list_display = ("name", "slug", "order", "total_projects", "updated_at")
    list_editable = ("order",)
    search_fields = ("name", "description")
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("name",)}

    @admin.display(description="Total de Proyectos")
    def total_projects(self, obj: ProjectCategory) -> int:
        """Retorna la cantidad de proyectos asociados a la categoría."""
        return obj.projects.count()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administración de proyectos técnicos y casos de estudio."""

    list_display = (
        "title",
        "project_type",
        "category",
        "is_featured",
        "is_visible",
        "has_live_preview",
        "has_docs",
        "has_repo",
        "order",
        "updated_at",
    )
    list_filter = ("project_type", "category", "is_featured", "is_visible", "skills")
    list_editable = ("is_featured", "is_visible", "order")
    search_fields = (
        "title",
        "short_description",
        "detailed_description",
        "skills__name",
        "category__name",
    )
    prepopulated_fields: ClassVar[dict[str, tuple[str, ...]]] = {"slug": ("title",)}
    filter_horizontal = ("skills",)
    fieldsets = (
        (
            "Identidad y Clasificación Funcional",
            {
                "fields": ("title", "slug", "project_type", "category"),
            },
        ),
        (
            "Descripción, Documentación (Markdown / PDF) y Stack",
            {
                "fields": (
                    "short_description",
                    "detailed_description",
                    "documentation_pdf",
                    "skills",
                ),
            },
        ),
        (
            "Despliegue, Vista Previa y Repositorio",
            {
                "fields": ("live_url", "preview_image", "repo_url"),
            },
        ),
        (
            "Visibilidad y Prioridad",
            {
                "fields": ("is_featured", "is_visible", "order"),
            },
        ),
    )

    @admin.display(boolean=True, description="Preview Iframe")
    def has_live_preview(self, obj: Project) -> bool:
        """Indica en el listado si el proyecto web tiene URL desplegada para iframe."""
        return obj.can_embed_preview

    @admin.display(boolean=True, description="Doc Técnica")
    def has_docs(self, obj: Project) -> bool:
        """Indica en el listado si el proyecto posee documentación Markdown o PDF."""
        return obj.has_technical_docs

    @admin.display(boolean=True, description="Repo Público")
    def has_repo(self, obj: Project) -> bool:
        """Indica en el listado si el proyecto cuenta con repositorio público."""
        return obj.has_public_repo
