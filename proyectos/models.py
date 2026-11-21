"""
Modelos de datos para la aplicación de Proyectos (Catálogo Técnico y Casos de Estudio).

Define la clasificación funcional de soluciones (ej: RAG, POS, ETL) y el detalle
de cada proyecto desplegado, reutilizando el catálogo de habilidades de Curriculum
para mantener una fuente única de verdad en los filtros por stack tecnológico.
"""

from typing import Any

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from curriculum.models import Skill, TimeStampedModel


class ProjectType(models.TextChoices):
    """Tipos de entregable soportados para ajustar su presentación en el portafolio."""

    WEB = "WEB", "Aplicación Web (Iframe en vivo)"
    API = "API", "API / Microservicio (Documentación Markdown / PDF)"
    DESKTOP = "DESKTOP", "Aplicación Desktop / CLI"


class ProjectCategory(TimeStampedModel):
    """
    Categoría funcional o dominio de solución para agrupar proyectos.

    Ejemplos: RAG, POS, ETL / Data, Automatización, Backend API.

    Attributes:
        name: Nombre legible de la categoría funcional.
        slug: Identificador URL-safe para filtros interactivos.
        description: Breve explicación del dominio funcional (opcional).
        order: Prioridad de ordenamiento en los chips de filtro.
    """

    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Nombre de la categoría",
        help_text="Categoría funcional o de solución (ej: RAG, POS, ETL / Data, Automatización).",
    )
    slug = models.SlugField(
        max_length=90,
        unique=True,
        blank=True,
        verbose_name="Slug URL",
        help_text="Identificador para filtros (se autogenera si se deja en blanco).",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción corta",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Categoría de Proyecto"
        verbose_name_plural = "Categorías de Proyectos"
        ordering = ("order", "name")

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Autogenera el slug a partir del nombre cuando no se provee explícitamente."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Project(TimeStampedModel):
    """
    Proyecto técnico o caso de estudio desplegado en el portafolio.

    Attributes:
        title: Nombre del proyecto o producto.
        slug: Identificador URL-safe único del proyecto.
        project_type: Tipo de entregable (WEB, API o DESKTOP).
        category: Categoría funcional a la que pertenece.
        short_description: Resumen ejecutivo para tarjetas de catálogo.
        detailed_description: Documentación técnica o guía de uso en Markdown.
        documentation_pdf: Archivo PDF opcional con contrato o guía técnica.
        live_url: URL desplegada (subdominio VPS o enlace de release).
        preview_image: Captura o diagrama opcional para Desktop / API.
        repo_url: URL del repositorio público (si está vacío se asume privado).
        skills: Habilidades/tecnologías de Curriculum asociadas al stack.
        is_featured: Destaca el proyecto en el catálogo.
        is_visible: Controla si el proyecto es público en la web.
        order: Orden manual de presentación.
    """

    title = models.CharField(
        max_length=150,
        verbose_name="Título del proyecto",
    )
    slug = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        verbose_name="Slug URL",
        help_text="Identificador único para URL (se autogenera a partir del título si se deja vacío).",
    )
    project_type = models.CharField(
        max_length=15,
        choices=ProjectType.choices,
        default=ProjectType.WEB,
        verbose_name="Tipo de proyecto",
        help_text="Define el modo de presentación: Iframe vivo (Web), Documentación técnica (API) o Release/Captura (Desktop).",
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Categoría funcional",
    )
    short_description = models.CharField(
        max_length=280,
        verbose_name="Resumen ejecutivo",
        help_text="Descripción concisa para la tarjeta del proyecto.",
    )
    detailed_description = models.TextField(
        blank=True,
        verbose_name="Documentación técnica (Markdown)",
        help_text="Explicación de arquitectura, flujo funcional o guía de uso de API en formato Markdown (endpoints, cURL, respuestas).",
    )
    documentation_pdf = models.FileField(
        upload_to="projects/docs/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name="Documentación en PDF (opcional)",
        help_text="Guía de uso o contrato técnico en PDF descargable (ideal para APIs o manuales).",
    )
    live_url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="URL del proyecto desplegado",
        help_text="URL pública o subdominio del VPS (alimenta el enlace directo y el iframe de previsualización).",
    )
    preview_image = models.ImageField(
        upload_to="projects/previews/",
        blank=True,
        null=True,
        verbose_name="Imagen de vista previa (opcional)",
        help_text="Captura o diagrama opcional (recomendado para apps Desktop o arquitecturas API).",
    )
    repo_url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="URL del repositorio",
        help_text="Dejar en blanco si el repositorio es privado para omitir el enlace en la web.",
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
        verbose_name="Stack tecnológico",
        help_text="Tecnologías de la app Curriculum utilizadas en este proyecto.",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="¿Proyecto destacado?",
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="¿Visible en el portafolio?",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ("order", "-is_featured", "-created_at")

    @property
    def has_public_repo(self) -> bool:
        """Indica si el proyecto expone un repositorio público."""
        return bool(self.repo_url and self.repo_url.strip())

    @property
    def can_embed_preview(self) -> bool:
        """Indica si el proyecto web dispone de URL activa para previsualización en iframe."""
        return bool(
            self.project_type == ProjectType.WEB
            and self.live_url
            and self.live_url.strip()
        )

    @property
    def has_technical_docs(self) -> bool:
        """Indica si el proyecto cuenta con documentación Markdown o PDF adjunto."""
        return bool(
            (self.detailed_description and self.detailed_description.strip())
            or self.documentation_pdf
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Autogenera el slug a partir del título cuando no se provee explícitamente."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.category.name})"
