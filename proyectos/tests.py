"""
Pruebas unitarias para los modelos de la aplicación Proyectos.

Verifica la autogeneración de slugs, ordenamiento de categorías funcionales,
reglas de exposición para proyectos WEB / API / DESKTOP (iframe, repositorios
privados, documentación técnica Markdown/PDF) y asociación M2M con Skill.
"""

import json
import re
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from curriculum.models import Skill, SkillCategory

from .models import Project, ProjectCategory, ProjectType
from .selectors import (
    list_active_project_categories,
    list_used_project_skills,
    list_visible_projects,
)
from .services import (
    build_projects_catalog_payload,
    filter_projects_payload,
    resolve_project_cta_label,
)


class ProjectCategoryModelTests(TestCase):
    """Pruebas del modelo ProjectCategory."""

    def test_category_autogenerates_slug_and_str(self) -> None:
        """Verifica la autogeneración de slug y representación textual."""
        category = ProjectCategory.objects.create(
            name="RAG Empresarial",
            order=1,
        )

        self.assertEqual(category.slug, "rag-empresarial")
        self.assertEqual(str(category), "RAG Empresarial")

    def test_category_ordering_by_order_then_name(self) -> None:
        """Comprueba el ordenamiento por prioridad numérica y luego nombre."""
        ProjectCategory.objects.create(name="POS", order=2)
        ProjectCategory.objects.create(name="Automatización", order=1)
        ProjectCategory.objects.create(name="RAG", order=1)

        ordered_names = list(ProjectCategory.objects.values_list("name", flat=True))
        self.assertEqual(ordered_names, ["Automatización", "RAG", "POS"])


class ProjectModelTests(TestCase):
    """Pruebas del modelo Project y sus propiedades de dominio."""

    def setUp(self) -> None:
        self.category_rag = ProjectCategory.objects.create(
            name="RAG",
            order=1,
        )

    def test_project_autogenerates_slug_and_str(self) -> None:
        """Verifica la autogeneración de slug y representación __str__."""
        project = Project.objects.create(
            title="Asistente RRHH PDF",
            category=self.category_rag,
            short_description="Chat RAG sobre políticas internas.",
        )

        self.assertEqual(project.slug, "asistente-rrhh-pdf")
        self.assertEqual(str(project), "Asistente RRHH PDF (RAG)")

    def test_web_project_embed_preview_and_private_repo_flags(self) -> None:
        """Valida flags de iframe y repositorio privado en proyectos WEB."""
        web_live_private_repo = Project.objects.create(
            title="Portal RAG RRHH",
            category=self.category_rag,
            project_type=ProjectType.WEB,
            short_description="Buscador semántico sobre documentos internos.",
            live_url="https://rag.tudominio.com",
            repo_url="   ",
        )
        web_no_live_public_repo = Project.objects.create(
            title="POS Core Web",
            category=self.category_rag,
            project_type=ProjectType.WEB,
            short_description="Sistema punto de venta web.",
            live_url="",
            repo_url="https://github.com/johandcastro/pos-core",
        )

        self.assertTrue(web_live_private_repo.can_embed_preview)
        self.assertFalse(web_live_private_repo.has_public_repo)

        self.assertFalse(web_no_live_public_repo.can_embed_preview)
        self.assertTrue(web_no_live_public_repo.has_public_repo)

    def test_api_and_desktop_projects_disable_iframe_and_detect_technical_docs(
        self,
    ) -> None:
        """Garantiza que API y DESKTOP nunca habiliten iframe y detecten docs."""
        with (
            tempfile.TemporaryDirectory() as temp_media_dir,
            override_settings(MEDIA_ROOT=temp_media_dir),
        ):
            api_markdown = Project.objects.create(
                title="API Ingesta Documental",
                category=self.category_rag,
                project_type=ProjectType.API,
                short_description="API REST para vectorización de PDFs.",
                live_url="https://api.tudominio.com",
                detailed_description="## Endpoints\nPOST /v1/query",
            )
            api_pdf = Project.objects.create(
                title="API Facturación DIAN",
                category=self.category_rag,
                project_type=ProjectType.API,
                short_description="Microservicio de validación XML.",
                live_url="https://api.tudominio.com",
                documentation_pdf=SimpleUploadedFile(
                    "guia.pdf",
                    b"%PDF-1.4",
                    content_type="application/pdf",
                ),
            )
            desktop_no_docs = Project.objects.create(
                title="POS Escritorio Offline",
                category=self.category_rag,
                project_type=ProjectType.DESKTOP,
                short_description="Cliente desktop multiplataforma.",
                live_url="https://github.com/johandcastro/pos/releases",
                detailed_description="",
            )

            self.assertFalse(api_markdown.can_embed_preview)
            self.assertTrue(api_markdown.has_technical_docs)

            self.assertFalse(api_pdf.can_embed_preview)
            self.assertTrue(api_pdf.has_technical_docs)

            self.assertFalse(desktop_no_docs.can_embed_preview)
            self.assertFalse(desktop_no_docs.has_technical_docs)

    def test_project_skills_m2m_association_with_curriculum_skill(self) -> None:
        """Valida la asociación M2M con curriculum.Skill y filtrado case-insensitive."""
        skill_category = SkillCategory.objects.create(name="Backend", order=1)
        python_skill = Skill.objects.create(
            category=skill_category,
            name="Python",
            order=1,
        )
        fastapi_skill = Skill.objects.create(
            category=skill_category,
            name="FastAPI",
            order=2,
        )
        project = Project.objects.create(
            title="Motor Vectorial Python",
            category=self.category_rag,
            short_description="Servicio de embeddings con FastAPI.",
        )
        project.skills.add(python_skill, fastapi_skill)

        self.assertEqual(project.skills.count(), 2)
        self.assertEqual(
            list(Project.objects.filter(skills__name__iexact="python")),
            [project],
        )


class ProjectSelectorsTests(TestCase):
    """Pruebas unitarias para los selectores ORM optimizados de Proyectos."""

    def test_list_visible_projects_excludes_hidden_and_avoids_n_plus_one(self) -> None:
        """Verifica filtro de visibilidad y carga en 2 consultas sin N+1."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)
        cat_pos = ProjectCategory.objects.create(name="POS", order=2)

        skill_cat_backend = SkillCategory.objects.create(name="Backend", order=1)
        skill_cat_ia = SkillCategory.objects.create(name="IA / LLMs", order=2)
        skill_python = Skill.objects.create(
            category=skill_cat_backend,
            name="Python",
            order=1,
        )
        skill_rag = Skill.objects.create(
            category=skill_cat_ia,
            name="LangChain",
            order=1,
        )

        visible_one = Project.objects.create(
            title="RAG RRHH",
            category=cat_rag,
            short_description="Buscador documental RAG.",
            is_visible=True,
            order=1,
        )
        visible_one.skills.add(skill_python, skill_rag)

        visible_two = Project.objects.create(
            title="POS Tienda",
            category=cat_pos,
            short_description="Punto de venta.",
            is_visible=True,
            order=2,
        )
        visible_two.skills.add(skill_python)

        hidden_project = Project.objects.create(
            title="Proyecto Oculto",
            category=cat_pos,
            short_description="Borrador interno.",
            is_visible=False,
            order=3,
        )
        hidden_project.skills.add(skill_python)

        with self.assertNumQueries(2):
            projects = list(list_visible_projects())
            loaded_relations = [
                (
                    project.category.name,
                    [skill.category.name for skill in project.skills.all()],
                )
                for project in projects
            ]

        self.assertEqual(projects, [visible_one, visible_two])
        self.assertNotIn(hidden_project, projects)
        self.assertEqual(len(loaded_relations), 2)

    def test_active_categories_and_used_skills_exclude_unused_or_hidden(self) -> None:
        """Garantiza que categorías y skills sin proyectos visibles no aparezcan."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)
        cat_pos = ProjectCategory.objects.create(name="POS", order=2)
        ProjectCategory.objects.create(name="ETL", order=3)

        skill_cat = SkillCategory.objects.create(name="Backend", order=1)
        skill_python = Skill.objects.create(
            category=skill_cat,
            name="Python",
            order=1,
        )
        skill_docker = Skill.objects.create(
            category=skill_cat,
            name="Docker",
            order=2,
        )

        visible_project = Project.objects.create(
            title="RAG Activo",
            category=cat_rag,
            short_description="Proyecto visible.",
            is_visible=True,
        )
        visible_project.skills.add(skill_python)

        hidden_project = Project.objects.create(
            title="POS Oculto",
            category=cat_pos,
            short_description="Proyecto oculto.",
            is_visible=False,
        )
        hidden_project.skills.add(skill_docker)

        self.assertEqual(list(list_active_project_categories()), [cat_rag])
        self.assertEqual(list(list_used_project_skills()), [skill_python])


class ProjectServicesTests(TestCase):
    """Pruebas unitarias para la capa de servicios de Proyectos."""

    def test_resolve_project_cta_label_by_project_type(self) -> None:
        """Verifica la etiqueta CTA devuelta según WEB, API o DESKTOP."""
        web_project = Project(project_type=ProjectType.WEB)
        api_project = Project(project_type=ProjectType.API)
        desktop_project = Project(project_type=ProjectType.DESKTOP)

        self.assertEqual(resolve_project_cta_label(web_project), "Abrir Aplicación")
        self.assertEqual(resolve_project_cta_label(api_project), "Ver Endpoint / Demo")
        self.assertEqual(
            resolve_project_cta_label(desktop_project),
            "Ver Release / Descargar",
        )

    def test_build_projects_catalog_payload_structure_and_privacy(self) -> None:
        """Valida serialización JSON, omisión de repo privado y search_index."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)
        skill_cat = SkillCategory.objects.create(name="Backend", order=1)
        skill_python = Skill.objects.create(
            category=skill_cat,
            name="Python",
            order=1,
        )

        visible_web = Project.objects.create(
            title="Asistente Documental",
            category=cat_rag,
            project_type=ProjectType.WEB,
            short_description="Consulta inteligente de PDFs.",
            live_url="https://rag.tudominio.com",
            repo_url="",
            is_visible=True,
        )
        visible_web.skills.add(skill_python)

        Project.objects.create(
            title="Proyecto Privado Oculto",
            category=cat_rag,
            short_description="No debe serializarse.",
            is_visible=False,
        )

        payload = build_projects_catalog_payload()
        self.assertEqual(len(payload["projects"]), 1)

        serialized = payload["projects"][0]
        self.assertIsNone(serialized["repo_url"])
        self.assertFalse(serialized["has_public_repo"])
        self.assertTrue(serialized["can_embed_preview"])
        self.assertIn("python", serialized["search_index"])

        dumped = json.dumps(payload)
        self.assertEqual(json.loads(dumped)["projects"][0]["slug"], visible_web.slug)

    def test_filter_projects_payload_by_category_skill_and_type(self) -> None:
        """Comprueba filtrado por categoría, tecnología y tipo de entregable."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)
        cat_pos = ProjectCategory.objects.create(name="POS", order=2)

        skill_cat = SkillCategory.objects.create(name="Lenguajes", order=1)
        skill_python = Skill.objects.create(
            category=skill_cat,
            name="Python",
            order=1,
        )
        skill_fastapi = Skill.objects.create(
            category=skill_cat,
            name="FastAPI",
            order=2,
        )
        skill_csharp = Skill.objects.create(
            category=skill_cat,
            name="C#",
            order=3,
        )

        rag_project = Project.objects.create(
            title="RAG RRHH",
            category=cat_rag,
            project_type=ProjectType.WEB,
            short_description="Motor RAG en Python.",
        )
        rag_project.skills.add(skill_python, skill_fastapi)

        pos_project = Project.objects.create(
            title="POS Facturación",
            category=cat_pos,
            project_type=ProjectType.DESKTOP,
            short_description="Terminal POS en C#.",
        )
        pos_project.skills.add(skill_csharp)

        payload = build_projects_catalog_payload()

        by_python = filter_projects_payload(payload, tech_or_query="PYTHON")
        self.assertEqual([item["title"] for item in by_python], ["RAG RRHH"])

        mismatched = filter_projects_payload(
            payload,
            category_slug="pos",
            project_type=ProjectType.WEB,
        )
        self.assertEqual(mismatched, [])

        by_desktop = filter_projects_payload(payload, project_type=ProjectType.DESKTOP)
        self.assertEqual([item["title"] for item in by_desktop], ["POS Facturación"])


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class ProjectCatalogViewTests(TestCase):
    """Pruebas de integración para la vista HTTP del catálogo (/prodep/)."""

    def test_catalog_view_renders_empty_state_with_http_200(self) -> None:
        """Verifica respuesta 200, estado vacío y carga diferida de proyectos.js."""
        response = self.client.get("/prodep/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "proyectos/proyectos.html")
        self.assertContains(response, "Catálogo en preparación")
        self.assertContains(
            response,
            'defer src="/static/proyectos/js/proyectos.js"',
        )

    def test_catalog_view_renders_web_iframe_api_docs_and_hides_private_repo(
        self,
    ) -> None:
        """Valida renderizado simultáneo de iframe WEB, blueprint API y privacidad."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)

        Project.objects.create(
            title="Portal RAG RRHH",
            category=cat_rag,
            project_type=ProjectType.WEB,
            short_description="Buscador semántico privado.",
            live_url="https://rag.tudominio.com",
            repo_url="",
        )
        api_project = Project.objects.create(
            title="API RAG Consultas",
            category=cat_rag,
            project_type=ProjectType.API,
            short_description="Microservicio de inferencia.",
            live_url="https://api.tudominio.com",
            detailed_description="## Endpoints",
            repo_url="https://github.com/johandcastro/api-rag",
        )

        response = self.client.get("/prodep/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-src="https://rag.tudominio.com"')
        self.assertContains(response, "Repo Privado")
        self.assertContains(response, "Blueprint API // Zero-Exposure")
        self.assertContains(response, f'data-open-docs="{api_project.slug}"')
        self.assertContains(response, "https://github.com/johandcastro/api-rag")

    def test_catalog_view_excludes_hidden_projects_and_embeds_json_payload(
        self,
    ) -> None:
        """Garantiza exclusión de proyectos ocultos en HTML y en json_script."""
        cat_rag = ProjectCategory.objects.create(name="RAG", order=1)
        skill_cat = SkillCategory.objects.create(name="Lenguajes", order=1)
        skill_python = Skill.objects.create(
            category=skill_cat,
            name="Python",
            order=1,
        )
        skill_rust = Skill.objects.create(
            category=skill_cat,
            name="Rust",
            order=2,
        )

        visible_project = Project.objects.create(
            title="Proyecto Público",
            category=cat_rag,
            short_description="Proyecto visible en catálogo.",
            is_visible=True,
        )
        visible_project.skills.add(skill_python)

        hidden_project = Project.objects.create(
            title="Proyecto Secreto",
            category=cat_rag,
            short_description="No debe mostrarse.",
            is_visible=False,
        )
        hidden_project.skills.add(skill_rust)

        response = self.client.get("/prodep/")
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Proyecto Público")
        self.assertNotContains(response, "Proyecto Secreto")
        self.assertNotContains(response, "Rust")

        payload_projects = response.context["catalog_payload"]["projects"]
        self.assertEqual(
            [item["title"] for item in payload_projects],
            ["Proyecto Público"],
        )

        script_match = re.search(
            r'<script id="projects-catalog-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(script_match)
        embedded_payload = json.loads(script_match.group(1))
        self.assertEqual(
            [item["title"] for item in embedded_payload["projects"]],
            ["Proyecto Público"],
        )
        self.assertNotIn("Rust", json.dumps(embedded_payload))
