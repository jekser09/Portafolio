# Feature: CV UX/UI Adjustments (`/CV/`)

- **Locator:** `odd/tasks/cv-ux-ui-adjustments.md`
- **Engram Topic Key:** `odd/cv-ux-ui-adjustments/tasks`
- **Branch:** `development`
- **Implementation Route:** `delegated direct` (Writer trigger: 2 non-trivial files — `curriculum/templates/curriculum/cv.html` and `curriculum/static/curriculum/js/cv.js`; independent verification via read-only verifier `Independent CV UI Verifier`)
- **TDD Mode:** `off` (source: `AGENTS.md` strict test pre-approval protocol — no new test files added without prior user approval; existing suite `uv run python manage.py test` + template rendering checks serve as functional verification)
- **Forecast & Observed Size:** ~90 authored adjustments in target features (full `cv.html` + `cv.js` diff vs HEAD also includes earlier UI redesign; `delivery_strategy: ask-on-risk`)
- **Rollback Boundary:** `curriculum/templates/curriculum/cv.html`, `curriculum/static/curriculum/js/cv.js`, `static/css/output.css` (uncommitted working-tree changes on `development`; revertible via `git checkout -- curriculum/templates/curriculum/cv.html curriculum/static/curriculum/js/cv.js static/css/output.css`)

## Objective & Scope

Apply 4 targeted UX/UI refinements to the `/CV/` resume document (`#cv-document`) and its external client controller (`cv.js`):
1. Make every container in **Contacto y Ubicación** fully clickable (Google Maps query URL for location, clipboard copy for email & phone, new-tab anchor without underline for GitHub & LinkedIn).
2. Reorganize each contact card into a 2-row layout: uppercase mono label at top-left, compact icon badge (`w-6 h-6` / `w-3.5 h-3.5`) at top-right, full-width single-line truncated value below (`whitespace-nowrap overflow-hidden text-ellipsis`).
3. Position `"Disponible para proyectos"` top-right above full name/headline, allowing name and headline to center cleanly across the full header width.
4. Justify large text blocks (`text-justify`) in **Perfil Profesional** and **Experiencia Laboral** highlights.

## Constraints

- Zero `<button>` elements inside `#cv-document` (email/phone cards use `<div role="button" tabindex="0">`).
- Zero inline JavaScript in templates; `cv.js` remains external with `defer` and no `DOMContentLoaded` wrapper.
- Do not modify `curriculum/tests.py` without prior user approval per `AGENTS.md`.
- Preserve dual layout (`two-col` / `ats`) and dark-default styling.

## Checklist

- [x] **T1 (Delegated Writer — `cv.html`):** Update `#cv-document` `<header>` layout (`lines 44-61`) so `"Disponible para proyectos"` sits top-right (`flex justify-end w-full`) above a centered full-width name/headline block (`w-full text-center space-y-2`).
- [x] **T2 (Delegated Writer — `cv.html`):** Refactor `#contact-cards-grid` cards (`lines 78-162`) to the 2-row compact-icon layout (`w-6 h-6` badge, `w-3.5 h-3.5` SVG), wrap Location/GitHub/LinkedIn in full-card `<a>` links (Google Maps query URL for Location, no `underline` on GitHub/LinkedIn), and turn Email/Phone into accessible `<div role="button" tabindex="0">` copy cards with `data-copy-text`, `data-copy-label`, and `[data-copy-feedback]`.
- [x] **T3 (Delegated Writer — `cv.html` & `cv.js`):** Add `text-justify` to **Perfil Profesional** (`line 259`) and **Experiencia Laboral** highlights (`line 292`) in `cv.html`, and add click/keyboard (`Enter`/` `) clipboard copy handling with `WeakMap` timer deduplication and `1800ms` `"¡COPIADO!"` feedback in `cv.js` (`lines 80-142`).
- [x] **T4 (Orchestrator & Independent Verification):** Recompiled Tailwind CSS (`output.css`, 24,936 bytes), ran `uv run python manage.py check`, `uv run python manage.py test`, verified `/CV/` HTTP 200 rendered HTML assertions, and completed read-only independent verification (`Independent CV UI Verifier`: PASS).
- [x] **T5 (Direct Inline — `cv.html`):** Removed the `"Disponible para proyectos"` header badge (`lines 43-53`) keeping full-width centered `full_name` and `headline`, and updated **Formación Académica** (`lines 205-207`) to render `(Culminado)` when `edu.is_in_progress` is false.

## Verification Evidence

- `.\bin\tailwindcss.exe -i .\static\css\input.css -o .\static\css\output.css --minify` (outside sandbox after sandbox `EPERM` on `output.css`) → `Done in 77ms`, verified `justify-end`, `text-center`, `text-ellipsis`, `text-justify`, `w-6`, `h-6`, `w-3.5`, `h-3.5`, `text-[10px]`, `contents` present in `static/css/output.css`.
- `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- `uv run python manage.py test` → `Ran 14 tests in 0.020s — OK` (verified by both orchestrator and independent verifier).
- `Client().get('/CV/')` render verification → `STATUS 200`, `MAPS_URL True`, `COPY_ATTRS True`, `NO_UNDERLINE_CONTACT True`, `NO_BUTTON_IN_CV True`, `JUSTIFY True`, `CENTERED_HDR True`.
- `Client().get('/CV/')` & `render_to_string('curriculum/cv.html', mock_ctx)` post-T5 verification → `STATUS 200`, `NO_BADGE_LIVE True`, `EDU_STATES True` (`(Culminado)` and `(En curso)` both rendered), `EDU_LIVE_HAS_STATUS True`.
- `uv run ruff check --no-cache curriculum/ portafolio/` → `0` errors in edited/application modules (`2` pre-existing `RUF012` notices in `curriculum/migrations/0001_initial.py`).
- `gentle-ai review mode status` / `gentle-ai review assess` → `state.json` access denied inside sandbox (`unknown` mode); `assess` flagged `unassessable` due to untracked `odd/` inventory, satisfied via delegated writer self-verification + independent read-only verifier (`PASS`). Changes remain uncommitted in working tree on `development` pending user visual check / commit decision.
