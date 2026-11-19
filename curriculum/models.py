"""
Modelos de datos para la aplicación de Curriculum (Hoja de Vida y Perfil).

Define las entidades que conforman el perfil profesional, habilidades y
conocimientos técnicos/blandos, trayectoria laboral, educación y referencias.
"""

from django.core.exceptions import ValidationError
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo base abstracto que provee marcas de tiempo de auditoría.

    Attributes:
        created_at: Fecha y hora en que se creó el registro.
        updated_at: Fecha y hora de la última modificación.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """
    Representa el titular de la hoja de vida / portafolio (Singleton lógico).

    Attributes:
        full_name: Nombre completo del profesional.
        headline: Titular profesional conciso (ej: Desarrollador Full Stack | Python & Data).
        bio: Resumen del perfil profesional y propuesta de valor.
        email: Correo electrónico principal de contacto.
        phone: Teléfono o WhatsApp de contacto directo.
        location: Ciudad y país de residencia.
        github_url: Enlace al perfil de GitHub.
        linkedin_url: Enlace al perfil de LinkedIn (opcional).
        avatar: Fotografía profesional (opcional).
    """

    full_name = models.CharField(
        max_length=150,
        verbose_name="Nombre completo",
    )
    headline = models.CharField(
        max_length=200,
        verbose_name="Titular profesional",
        help_text="Ej: Desarrollador Full Stack | Python (FastAPI, Django) & Data",
    )
    bio = models.TextField(
        verbose_name="Perfil profesional (Bio)",
        help_text="Resumen descriptivo de experiencia, especialidad y enfoque.",
    )
    email = models.EmailField(
        verbose_name="Correo electrónico",
    )
    phone = models.CharField(
        max_length=30,
        verbose_name="Teléfono de contacto",
    )
    location = models.CharField(
        max_length=100,
        default="Bogotá, Colombia",
        verbose_name="Ubicación",
    )
    github_url = models.URLField(
        max_length=255,
        default="https://github.com/johandcastro",
        verbose_name="URL de GitHub",
    )
    linkedin_url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="URL de LinkedIn",
    )
    avatar = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
    )

    class Meta:
        verbose_name = "Perfil Profesional"
        verbose_name_plural = "Perfil Profesional"

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        """Garantiza que exista únicamente un perfil activo en la base de datos."""
        if not self.pk and Profile.objects.exists():
            raise ValidationError(
                "Solo puede existir un registro de Perfil Profesional. Edite el existente."
            )


class SkillCategory(TimeStampedModel):
    """
    Categorías para agrupar habilidades y conocimientos técnicos o blandos.

    Ejemplos: Backend, Bases de datos, ETL / Data, Frontend, Infraestructura,
    DevOps / CI/CD, IA / LLMs, Habilidades Blandas.
    """

    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Nombre de la categoría",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden de visualización",
        help_text="Valor numérico para ordenar las categorías (menor a mayor).",
    )

    class Meta:
        verbose_name = "Categoría de Habilidad"
        verbose_name_plural = "Categorías de Habilidades"
        ordering = ("order", "name")

    def __str__(self) -> str:
        return self.name


class Skill(TimeStampedModel):
    """
    Representa una habilidad, herramienta, lenguaje o competencia específica.

    Attributes:
        category: Categoría a la que pertenece la habilidad.
        name: Nombre de la habilidad (ej: Python, Polars, DuckDB, Pensamiento analítico).
        is_highlighted: Si se resalta en vistas resumidas o portada.
        order: Orden de presentación dentro de su categoría.
    """

    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="Categoría",
    )
    name = models.CharField(
        max_length=80,
        verbose_name="Nombre de la habilidad",
    )
    is_highlighted = models.BooleanField(
        default=False,
        verbose_name="¿Destacar en portada?",
        help_text="Marcar para resaltar como competencia principal.",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Habilidad / Conocimiento"
        verbose_name_plural = "Habilidades y Conocimientos"
        ordering = ("category__order", "order", "name")
        unique_together = ("category", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"


class Experience(TimeStampedModel):
    """
    Trayectoria y experiencia laboral.

    Attributes:
        company: Nombre de la empresa o cliente.
        role: Cargo o rol desempeñado.
        start_date: Fecha o mes/año de inicio.
        end_date: Fecha de finalización (dejar vacío si es el empleo actual).
        is_current: Indica si es el trabajo actual.
        is_visible: Permite ocultar temporalmente la experiencia sin borrarla.
        order: Orden de despliegue en CV y web (usualmente cronológico inverso).
    """

    company = models.CharField(
        max_length=120,
        verbose_name="Empresa",
    )
    role = models.CharField(
        max_length=120,
        verbose_name="Cargo / Rol",
    )
    start_date = models.DateField(
        verbose_name="Fecha de inicio",
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de finalización",
        help_text="Dejar en blanco si actualmente trabaja aquí.",
    )
    is_current = models.BooleanField(
        default=False,
        verbose_name="¿Trabajo actual?",
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="¿Visible?",
        help_text="Define si se muestra en la web pública.",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Menor valor indica mayor prioridad en la lista.",
    )

    class Meta:
        verbose_name = "Experiencia Laboral"
        verbose_name_plural = "Experiencias Laborales"
        ordering = ("order", "-start_date")

    def __str__(self) -> str:
        return f"{self.role} en {self.company}"


class ExperienceHighlight(TimeStampedModel):
    """
    Logros específicos y viñetas asociadas a una experiencia laboral.
    """

    experience = models.ForeignKey(
        Experience,
        on_delete=models.CASCADE,
        related_name="highlights",
        verbose_name="Experiencia",
    )
    description = models.TextField(
        verbose_name="Descripción del logro / responsabilidad",
        help_text="Detalle técnico y medible del logro.",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Logro de Experiencia"
        verbose_name_plural = "Logros de Experiencia"
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"Logro #{self.order} de {self.experience}"


class Education(TimeStampedModel):
    """
    Formación académica y técnica.

    Attributes:
        institution: Universidad, instituto o plataforma educativa.
        degree: Título o carrera obtenida.
        year_completed: Año de finalización o graduación.
        is_in_progress: Indica si los estudios están actualmente en curso.
        order: Orden de visualización.
    """

    institution = models.CharField(
        max_length=150,
        verbose_name="Institución",
    )
    degree = models.CharField(
        max_length=150,
        verbose_name="Título o Grado",
    )
    year_completed = models.PositiveIntegerField(
        verbose_name="Año de finalización / previsto",
    )
    is_in_progress = models.BooleanField(
        default=False,
        verbose_name="¿En curso?",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Formación Académica"
        verbose_name_plural = "Formación Académica"
        ordering = ("order", "-year_completed")

    def __str__(self) -> str:
        return f"{self.degree} — {self.institution} ({self.year_completed})"


class Reference(TimeStampedModel):
    """
    Referencias profesionales y laborales.

    Attributes:
        name: Nombre completo de la referencia.
        role: Cargo o relación laboral.
        phone: Teléfono de contacto.
        email: Correo electrónico (opcional).
        is_visible_on_web: Control de privacidad para no exponer teléfonos
            públicamente en la web sin consentimiento, pero mantenerlos disponibles
            para el generador de CV en PDF.
    """

    name = models.CharField(
        max_length=120,
        verbose_name="Nombre de la referencia",
    )
    role = models.CharField(
        max_length=120,
        verbose_name="Cargo / Rol",
    )
    phone = models.CharField(
        max_length=30,
        verbose_name="Teléfono",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico",
    )
    is_visible_on_web = models.BooleanField(
        default=False,
        verbose_name="¿Visible en la web pública?",
        help_text="Por privacidad, mantenga en falso para mostrar únicamente en el CV PDF descargable.",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Referencia Laboral"
        verbose_name_plural = "Referencias Laborales"
        ordering = ("order", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
