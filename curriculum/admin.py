"""
Configuración del Django Admin para la aplicación de Curriculum.

Permite administrar el perfil, habilidades, experiencias con sus logros (vía
inlines), educación y referencias laborales.
"""

from django.contrib import admin

from .models import (
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Reference,
    Skill,
    SkillCategory,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Administración del perfil profesional (Singleton)."""

    list_display = ("full_name", "headline", "email", "phone", "location", "updated_at")
    fieldsets = (
        (
            "Información Personal",
            {
                "fields": ("full_name", "headline", "avatar", "bio"),
            },
        ),
        (
            "Contacto y Redes",
            {
                "fields": ("email", "phone", "location", "github_url", "linkedin_url"),
            },
        ),
    )


class SkillInline(admin.TabularInline):
    """Permite gestionar habilidades directamente dentro de su categoría."""

    model = Skill
    extra = 1
    fields = ("name", "is_highlighted", "order")


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Administración de categorías de habilidades."""

    list_display = ("name", "order", "total_skills", "updated_at")
    list_editable = ("order",)
    search_fields = ("name",)
    inlines = (SkillInline,)

    @admin.display(description="Total de Habilidades")
    def total_skills(self, obj: SkillCategory) -> int:
        return obj.skills.count()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Administración individual de habilidades."""

    list_display = ("name", "category", "is_highlighted", "order", "updated_at")
    list_filter = ("category", "is_highlighted")
    list_editable = ("is_highlighted", "order")
    search_fields = ("name", "category__name")


class ExperienceHighlightInline(admin.TabularInline):
    """Permite registrar logros específicos dentro de cada experiencia."""

    model = ExperienceHighlight
    extra = 2
    fields = ("description", "order")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Administración de experiencia laboral."""

    list_display = (
        "role",
        "company",
        "start_date",
        "end_date",
        "is_current",
        "is_visible",
        "order",
    )
    list_filter = ("is_current", "is_visible", "company")
    list_editable = ("is_visible", "order")
    search_fields = ("role", "company")
    date_hierarchy = "start_date"
    inlines = (ExperienceHighlightInline,)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Administración de formación académica."""

    list_display = (
        "degree",
        "institution",
        "year_completed",
        "is_in_progress",
        "order",
    )
    list_filter = ("is_in_progress",)
    list_editable = ("order",)
    search_fields = ("degree", "institution")


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    """Administración de referencias laborales."""

    list_display = ("name", "role", "phone", "email", "is_visible_on_web", "order")
    list_filter = ("is_visible_on_web",)
    list_editable = ("is_visible_on_web", "order")
    search_fields = ("name", "role")
