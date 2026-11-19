"""
Pruebas unitarias para los modelos de la aplicación Curriculum.

Verifica el comportamiento de las entidades de perfil, habilidades,
experiencia laboral y referencias según las reglas de negocio aprobadas.
"""

from datetime import date

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from .models import (
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Reference,
    Skill,
    SkillCategory,
)
from .selectors import (
    get_cv_page_context,
    list_visible_experiences,
    list_web_visible_references,
)
from .services import (
    build_full_cv_payload,
    filter_cv_payload_by_selection,
    format_experience_period,
)


class ProfileModelTest(TestCase):
    """Pruebas del modelo Profile (Singleton)."""

    def setUp(self) -> None:
        self.profile = Profile.objects.create(
            full_name="Johand Esteban Castro Rodríguez",
            headline="Desarrollador Full Stack | Python & Data",
            bio="Resumen profesional de prueba.",
            email="jekser09@gmail.com",
            phone="302 464 9697",
            location="Bogotá, Colombia",
            github_url="https://github.com/johandcastro",
        )

    def test_profile_singleton_prevents_multiple_records(self) -> None:
        """Garantiza que clean() impida crear más de un registro de Profile."""
        second_profile = Profile(
            full_name="Otro Usuario",
            headline="Desarrollador Frontend",
            bio="Bio alternativa.",
            email="otro@gmail.com",
            phone="300 000 0000",
        )
        with self.assertRaises(ValidationError) as context:
            second_profile.clean()

        self.assertIn(
            "Solo puede existir un registro de Perfil Profesional",
            str(context.exception),
        )

    def test_profile_allows_updating_existing_instance(self) -> None:
        """Verifica que clean() y save() permitan actualizar la instancia existente."""
        self.profile.headline = "Senior Python Developer"
        # No debe lanzar ValidationError
        self.profile.clean()
        self.profile.save()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.headline, "Senior Python Developer")


class SkillModelTest(TestCase):
    """Pruebas para categorías y habilidades."""

    def setUp(self) -> None:
        self.category_backend = SkillCategory.objects.create(
            name="Backend",
            order=2,
        )
        self.category_data = SkillCategory.objects.create(
            name="Data",
            order=1,
        )

    def test_skill_unique_together_per_category(self) -> None:
        """Evita duplicar una habilidad con el mismo nombre en la misma categoría."""
        Skill.objects.create(
            category=self.category_backend,
            name="Python",
            order=1,
        )
        with self.assertRaises(IntegrityError):
            Skill.objects.create(
                category=self.category_backend,
                name="Python",
                order=2,
            )

    def test_skills_ordering_by_order_field(self) -> None:
        """Comprueba el ordenamiento de categorías y habilidades por el campo order."""
        # Las categorías se ordenan ascendentemente por 'order'
        categories = list(SkillCategory.objects.all())
        self.assertEqual(categories, [self.category_data, self.category_backend])

        # Las habilidades dentro de una categoría se ordenan por su 'order'
        skill_fastapi = Skill.objects.create(
            category=self.category_backend,
            name="FastAPI",
            order=10,
        )
        skill_django = Skill.objects.create(
            category=self.category_backend,
            name="Django",
            order=1,
        )

        skills = list(self.category_backend.skills.all())
        self.assertEqual(skills, [skill_django, skill_fastapi])


class ExperienceModelTest(TestCase):
    """Pruebas para experiencia laboral y viñetas de logros."""

    def test_experience_highlights_cascade_deletion(self) -> None:
        """Verifica que al eliminar una experiencia se borren sus logros en cascada."""
        experience = Experience.objects.create(
            company="PRODUCTOS LÁCTEOS PACOS",
            role="Desarrollador de Software",
            start_date=date(2025, 1, 1),
            is_current=True,
        )
        ExperienceHighlight.objects.create(
            experience=experience,
            description="Desarrollo de ERP con Django.",
            order=1,
        )
        ExperienceHighlight.objects.create(
            experience=experience,
            description="Integración de hardware biométrico.",
            order=2,
        )

        self.assertEqual(ExperienceHighlight.objects.count(), 2)

        # Al borrar la experiencia padre, los logros deben desaparecer
        experience.delete()
        self.assertEqual(ExperienceHighlight.objects.count(), 0)


class ReferenceModelTest(TestCase):
    """Pruebas para referencias laborales y políticas de privacidad."""

    def test_reference_privacy_default_is_false(self) -> None:
        """Asegura que is_visible_on_web sea False por defecto para proteger privacidad."""
        reference = Reference.objects.create(
            name="Miguel Forero",
            role="Director de T.I",
            phone="3187080252",
        )
        self.assertFalse(reference.is_visible_on_web)


class EducationModelTest(TestCase):
    """Pruebas para formación académica."""

    def test_education_creation_and_string_representation(self) -> None:
        """Verifica la correcta representación en cadena del modelo Education."""
        education = Education.objects.create(
            institution="Universidad Central",
            degree="Ingeniería de Sistemas",
            year_completed=2025,
            is_in_progress=False,
            order=1,
        )
        self.assertEqual(
            str(education),
            "Ingeniería de Sistemas — Universidad Central (2025)",
        )


class CurriculumSelectorsTest(TestCase):
    """Pruebas unitarias para la capa de selectores optimizados."""

    def setUp(self) -> None:
        self.profile = Profile.objects.create(
            full_name="Johand Esteban Castro Rodríguez",
            headline="Desarrollador Full Stack | Python & Data",
            bio="Resumen profesional.",
            email="jekser09@gmail.com",
            phone="302 464 9697",
        )
        self.category = SkillCategory.objects.create(name="Backend", order=1)
        self.skill = Skill.objects.create(category=self.category, name="Python", order=1)

    def test_list_visible_experiences_excludes_hidden_and_prefetches_highlights(self) -> None:
        """Verifica filtro de visibilidad y prefetch_related sin consultas N+1."""
        exp_visible = Experience.objects.create(
            company="PACOS",
            role="Dev",
            start_date=date(2025, 1, 1),
            is_visible=True,
            order=1,
        )
        ExperienceHighlight.objects.create(
            experience=exp_visible,
            description="Logro 1",
            order=1,
        )
        ExperienceHighlight.objects.create(
            experience=exp_visible,
            description="Logro 2",
            order=2,
        )

        Experience.objects.create(
            company="EMPRESA OCULTA",
            role="Rol Antiguo",
            start_date=date(2020, 1, 1),
            is_visible=False,
            order=2,
        )

        # 2 queries: 1 para las experiencias visibles y 1 para prefetch de highlights
        with self.assertNumQueries(2):
            experiences = list_visible_experiences()
            self.assertEqual(len(experiences), 1)
            self.assertEqual(experiences[0].company, "PACOS")

            # Iterar los highlights no debe ejecutar consultas adicionales
            highlights = list(experiences[0].highlights.all())
            self.assertEqual(len(highlights), 2)

    def test_list_web_visible_references_enforces_privacy(self) -> None:
        """Asegura que solo las referencias marcadas para web se listen en el selector público."""
        Reference.objects.create(
            name="Ref Pública",
            role="Líder",
            phone="111",
            is_visible_on_web=True,
        )
        Reference.objects.create(
            name="Ref Privada",
            role="Gerente",
            phone="222",
            is_visible_on_web=False,
        )

        web_refs = list(list_web_visible_references())
        self.assertEqual(len(web_refs), 1)
        self.assertEqual(web_refs[0].name, "Ref Pública")

    def test_get_cv_page_context_payload_structure(self) -> None:
        """Comprueba que el payload estructurado contenga todas las claves requeridas."""
        context = get_cv_page_context()

        expected_keys = {
            "profile",
            "skill_categories",
            "experiences",
            "education",
            "references",
        }
        self.assertEqual(set(context.keys()), expected_keys)
        self.assertEqual(context["profile"], self.profile)


class CurriculumServicesTest(TestCase):
    """Pruebas unitarias para la capa de servicios y formateo de CV."""

    def setUp(self) -> None:
        self.profile = Profile.objects.create(
            full_name="Johand Esteban Castro Rodríguez",
            headline="Desarrollador Full Stack | Python & Data",
            bio="Resumen profesional de prueba.",
            email="jekser09@gmail.com",
            phone="302 464 9697",
        )
        self.category = SkillCategory.objects.create(name="Backend", order=1)
        self.skill = Skill.objects.create(category=self.category, name="Python", order=1)
        self.experience = Experience.objects.create(
            company="PRODUCTOS LÁCTEOS PACOS",
            role="Desarrollador de Software",
            start_date=date(2025, 1, 1),
            end_date=date(2026, 9, 30),
            is_current=False,
            is_visible=True,
            order=1,
        )
        self.highlight = ExperienceHighlight.objects.create(
            experience=self.experience,
            description="Desarrollo de ERP con Django.",
            order=1,
        )

    def test_format_experience_period_with_start_and_end_date(self) -> None:
        """Comprueba el formateo correcto de periodos laborales cerrados."""
        period_str = format_experience_period(self.experience)
        self.assertEqual(period_str, "Enero 2025 a Septiembre 2026")

    def test_format_experience_period_for_current_job(self) -> None:
        """Comprueba el formateo de periodos laborales para empleos activos."""
        current_exp = Experience.objects.create(
            company="Empresa Actual",
            role="Lead Developer",
            start_date=date(2025, 1, 1),
            is_current=True,
        )
        period_str = format_experience_period(current_exp)
        self.assertEqual(period_str, "Enero 2025 a Presente")

    def test_build_full_cv_payload_serialization(self) -> None:
        """Verifica la serialización completa de entidades relacionales hacia el diccionario base."""
        payload = build_full_cv_payload()

        self.assertIn("profile", payload)
        self.assertEqual(payload["profile"]["full_name"], "Johand Esteban Castro Rodríguez")

        self.assertIn("skills_by_category", payload)
        self.assertEqual(len(payload["skills_by_category"]), 1)
        self.assertEqual(payload["skills_by_category"][0]["name"], "Backend")
        self.assertEqual(payload["skills_by_category"][0]["skills"][0]["name"], "Python")

        self.assertIn("experiences", payload)
        self.assertEqual(len(payload["experiences"]), 1)
        self.assertEqual(payload["experiences"][0]["company"], "PRODUCTOS LÁCTEOS PACOS")
        self.assertEqual(len(payload["experiences"][0]["highlights"]), 1)
        self.assertEqual(
            payload["experiences"][0]["highlights"][0]["description"],
            "Desarrollo de ERP con Django.",
        )

    def test_filter_cv_payload_by_selection(self) -> None:
        """Valida la capacidad de recortar y personalizar el CV según la selección del usuario."""
        mock_payload = {
            "profile": {"full_name": "Johand"},
            "experiences": [
                {"id": 1, "company": "Empresa 1"},
                {"id": 2, "company": "Empresa 2"},
            ],
            "skills_by_category": [
                {
                    "id": 100,
                    "name": "Backend",
                    "skills": [
                        {"id": 10, "name": "Python"},
                        {"id": 20, "name": "FastAPI"},
                    ],
                }
            ],
            "education": [{"id": 1, "degree": "Ingeniería"}],
            "references": [{"id": 1, "name": "Ref 1"}],
        }

        filtered = filter_cv_payload_by_selection(
            mock_payload,
            selected_experience_ids=[1],
            selected_skill_ids=[10],
            include_references=False,
        )

        # Solo experiencia con ID 1
        self.assertEqual(len(filtered["experiences"]), 1)
        self.assertEqual(filtered["experiences"][0]["id"], 1)

        # Solo habilidad con ID 10
        self.assertEqual(len(filtered["skills_by_category"]), 1)
        skills = filtered["skills_by_category"][0]["skills"]
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["id"], 10)

        # Referencias excluidas
        self.assertEqual(filtered["references"], [])


