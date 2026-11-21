# Feature: App `proyectos` — Catálogo Técnico y Casos de Estudio (`/prodep/`) — COMPLETED

- **Locator:** `odd/tasks/proyectos-catalog.md`
- **Engram Topic Key:** `presentation/proyectos-catalog-view`
- **Branch:** `main`
- **TDD Mode:** `off` (source: `AGENTS.md` strict test pre-approval protocol — las 14 pruebas de `proyectos` fueron propuestas en 3 lotes y aprobadas explícitamente por el usuario antes de escribirse)

## Objective & Scope

Construir la aplicación modular `proyectos` bajo ruta `/prodep/` respetando la separación estricta de capas (`models.py`, `selectors.py`, `services.py`, `views.py` delgadas) y la estética Editorial Técnico (Swiss Grid / Tailwind CSS):
1. **Categorización Funcional (`ProjectCategory`):** Agrupación de proyectos por dominio o solución (`RAG`, `POS`, `ETL / Data`, `Automatización`, etc.) con chips de filtro rápido.
2. **Clasificación por Tipo de Entregable (`ProjectType`: `WEB`, `API`, `DESKTOP`):**
   - **`WEB`:** Previsualización viva mediante `<iframe>` diferido apuntando a `live_url` (compatible con `Content-Security-Policy: frame-ancestors` en VPS con Traefik).
   - **`API`:** Enfoque Zero-Exposure (sin exponer Swagger en vivo ni `<iframe>`); presenta blueprint técnico y documentación Zero-Downtime almacenada en el portafolio mediante Markdown (`detailed_description`) y/o archivo PDF descargable opcional (`documentation_pdf`).
   - **`DESKTOP`:** Captura/diagrama opcional (`preview_image`) o blueprint técnico de ventana/terminal + enlace a release o documentación.
3. **Filtrado por Stack Tecnológico:** Asociación `ManyToManyField` directa con `curriculum.Skill` como fuente única de verdad para permitir filtros reactivos por tecnología (ej. `Python`, `FastAPI`, `Docker`) y búsqueda textual.
4. **Descripción y Enlaces Condicionales:** Resumen ejecutivo (`short_description`), enlace al sitio/release desplegado (`live_url`) y enlace opcional al repositorio (`repo_url`) que se omite en la interfaz cuando el repositorio es privado.
5. **Animaciones Verticales y Micro-interacciones Tailwind:** Revelado progresivo en scroll vertical (`IntersectionObserver` desde módulo JS externo con `defer`, sin JS inline) y transiciones `group-hover` con Tailwind CSS.

## Checklist

- [x] **Fase 1 — Capa de Datos y Admin (`proyectos/models.py`, `proyectos/admin.py`, `proyectos/migrations/0001_initial.py`):**
  - `ProjectType(TextChoices)` (`WEB`, `API`, `DESKTOP`), `ProjectCategory` y `Project` heredando `TimeStampedModel` de `curriculum.models`, con relación `skills` M2M hacia `curriculum.Skill`, `documentation_pdf` validado para `.pdf`, `preview_image` opcional, autogeneración de `slug` y propiedades `has_public_repo`, `can_embed_preview` (solo `WEB` con `live_url`) y `has_technical_docs`.
  - Panel administrativo (`ProjectCategoryAdmin` y `ProjectAdmin`) con `filter_horizontal`, `prepopulated_fields`, búsqueda, filtros por `project_type`/categoría/stack y columnas booleanas `has_live_preview`, `has_docs` y `has_repo`.
  - Migración inicial única `0001_initial.py` regenerada limpiamente y aplicada en SQLite local.
- [x] **Fase 1B — Pruebas Unitarias de Modelos (`proyectos/tests.py`):** Implementadas y aprobadas las 6 pruebas unitarias para `ProjectCategory` y `Project`.
- [x] **Fase 2 — Selectores y Servicios (`proyectos/selectors.py`, `proyectos/services.py`):**
  - Selectores optimizados sin N+1 (`list_visible_projects`, `list_active_project_categories`, `list_used_project_skills`, `get_projects_page_context`) usando `select_related` y `Prefetch` ordenado.
  - Servicios (`resolve_project_cta_label`, `build_projects_catalog_payload`, `filter_projects_payload`) con serialización JSON-safe para `json_script`, omisión de `repo_url` privado (`None`) e índice de búsqueda case-insensitive (`search_index`).
- [x] **Fase 2B — Pruebas Unitarias de Selectores y Servicios (`proyectos/tests.py`):** Implementadas las 5 pruebas aprobadas (`ProjectSelectorsTests` con `assertNumQueries(2)` y `ProjectServicesTests`).
- [x] **Fase 3 — Capa HTTP, Templates, JS y CSS (`/prodep/`):**
  - Vista delgada `projects_catalog_view` en `proyectos/views.py` y ruta `proyectos:catalog` en `proyectos/urls.py`.
  - Plantilla `proyectos/templates/proyectos/proyectos.html` con filtros reactivos, grilla de tarjetas con hover Tailwind, `<iframe>` diferido exclusivo para `WEB`, fallback Blueprint Técnico para `API`/`DESKTOP`, ocultamiento de repos privados, modal visor de Markdown/PDF e inyección `json_script`.
  - Módulo externo `proyectos/static/proyectos/js/proyectos.js` (`defer`, sin `DOMContentLoaded`) con filtrado multi-criterio, `IntersectionObserver` de scroll vertical e iframe diferido, y parser Markdown XSS-safe.
  - Tailwind CSS recompilado y minificado en `static/css/output.css`.
- [x] **Fase 3B — Pruebas de Integración de Vista (`proyectos/tests.py`):** Implementadas y aprobadas las 3 pruebas de integración de `/prodep/` (`ProjectCatalogViewTests` con `@override_settings(STORAGES=...)` para aislar el test del manifiesto WhiteNoise).

## Verification Evidence (Final)

- `.\bin\tailwindcss.exe -i .\static\css\input.css -o .\static\css\output.css --minify` (fuera de sandbox por `EPERM` en Windows sobre `output.css`) → `Done in 103ms` (`static/css/output.css`: 35,640 bytes, incluye `scale-25` y `-translate-y-1`).
- `node --check proyectos/static/proyectos/js/proyectos.js` → Exit `0`.
- `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- `uv run python manage.py test` → `Ran 28 tests in 0.151s` (`OK`: 14 pruebas de `curriculum` + 14 pruebas de `proyectos`).
- `uv run ruff check --no-cache proyectos/models.py proyectos/admin.py proyectos/selectors.py proyectos/services.py proyectos/views.py proyectos/urls.py proyectos/tests.py` → `All checks passed!`
- `uv run ruff format --no-cache --check proyectos/models.py proyectos/admin.py proyectos/selectors.py proyectos/services.py proyectos/views.py proyectos/urls.py proyectos/tests.py` → `7 files already formatted`.
