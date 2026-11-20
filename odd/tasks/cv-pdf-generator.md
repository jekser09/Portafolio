# Feature: Dual PDF CV Generator (`pdfmake` Client-Side Offloading)

- **Locator:** `odd/tasks/cv-pdf-generator.md`
- **Engram Topic Key:** `odd/cv-pdf-generator/tasks`
- **Branch:** `development`
- **Implementation Route:** `delegated direct` (Writer trigger: 3 files — `curriculum/static/curriculum/js/cv-pdf.js`, `curriculum/static/curriculum/js/cv.js`, `curriculum/templates/curriculum/cv.html`; independent verification via read-only verifier `Independent PDF Generator Verifier`)
- **TDD Mode:** `off` (source: `AGENTS.md` strict test pre-approval protocol — no new test files added without prior user approval; verified via `node --check`, Node VM doc-definition checks, `uv run python manage.py check`, `uv run python manage.py test`, and `/CV/` render checks)
- **Forecast & Observed Size:** ~300+ new lines (`cv-pdf.js` 620 lines + wiring in `cv.js` and `cv.html`; `delivery_strategy: ask-on-risk`)
- **Rollback Boundary:** `curriculum/static/curriculum/js/cv-pdf.js` (untracked new file), `curriculum/static/curriculum/js/cv.js`, `curriculum/templates/curriculum/cv.html`

## Objective & Scope

Implement 100% vector, selectable-text, ATS-friendly client-side PDF generation using lazy-loaded `pdfmake` v0.2.12, tied directly to the active presentation selector (`two-col` vs `ats`) in `/CV/`:
1. Create `curriculum/static/curriculum/js/cv-pdf.js` (`defer`, no `DOMContentLoaded`) exposing `window.generateCvPdf(cvData, layoutMode)` with lazy loading of `pdfmake.min.js` + `vfs_fonts.min.js` from CDN (`0.2.12`).
2. Build shared vector helpers (`splitNormalizedParagraphs`, `cleanUrlDisplay`, `buildSectionHeading`, `buildHeaderBanner`, `buildProfileBlocks`, `buildExperienceBlocks`, `buildEducationBlocks`, `buildReferencesBlocks`, `getNonEmptySkillCategories`) and dual `pdfmake` document definitions:
   - `buildAtsDocDefinition(cvData)` (1-column linear flow inspired by `temp/HV JOHAND VC1.pdf`).
   - `buildTwoColDocDefinition(cvData)` (asymmetric 2-column layout with `#F1F5F9` side panel inspired by `temp/HV JOHAND VC2.pdf`).
3. Wire `#download-cv-btn` and `#download-cv-label` in `curriculum/templates/curriculum/cv.html` and `curriculum/static/curriculum/js/cv.js` so the active layout selector dynamically updates the button label (`Descargar CV (2 Columnas)` / `Descargar CV (1 Columna ATS)`) and triggers generation of the corresponding PDF file (`HV_<Nombre>_2_Columnas.pdf` / `HV_<Nombre>_ATS.pdf`) with `"Generando PDF..."` loading state.

## Constraints

- Strict prohibition from `AGENTS.md`: no `html2canvas` or `html2pdf.js`; PDF must be 100% vector via `pdfmake`.
- Zero inline JavaScript in HTML templates; load `cv-pdf.js` with `defer` before `cv.js`.
- Zero `<button>` elements inside `#cv-document`.
- Do not modify `curriculum/tests.py` without prior user approval per `AGENTS.md`.
- Note on `curriculum/services.py`: `build_full_cv_payload()` defaults `include_all_references=False` (only `is_visible_on_web=True` references are exposed publicly in `cv-data`), so `cv-pdf.js` safely handles `references` being empty or populated.

## Checklist

- [x] **T1 (Delegated Writer — `cv-pdf.js`):** Created `curriculum/static/curriculum/js/cv-pdf.js` (620 lines) with cached sequential lazy loading of `pdfmake` v0.2.12 + `vfs_fonts`, text/URL normalization helpers, clickable `#1C3D63` header banner, `buildAtsDocDefinition`, `buildTwoColDocDefinition`, ASCII-safe filename generator, and `window.generateCvPdf`.
- [x] **T2 (Delegated Writer — `cv.html` & `cv.js`):** Added `#download-cv-label` and `<script defer src="{% static 'curriculum/js/cv-pdf.js' %}"></script>` before `cv.js` in `cv.html` (`lines 34, 320-321`); updated `cv.js` (`lines 29-43, 49-82, 157-202`) to track `currentLayout`, sync `#download-cv-label`, disable/restore `#download-cv-btn` during async generation, and invoke `window.generateCvPdf(cvData, currentLayout)`.
- [x] **T3 (Orchestrator & Independent Verification):** Validated JS syntax (`node --check`), ran `uv run python manage.py check`, `uv run python manage.py test`, verified `/CV/` HTTP 200 render check (`cv-pdf.js` before `cv.js`, `#download-cv-label`, `#cv-data`), confirmed no Tailwind rebuild needed (no new utility classes added), and completed independent verification (`Independent PDF Generator Verifier`: PASS).
- [x] **T4 (Direct Inline — `cv.html` & `cv.js`):** Simplified selector button labels to `"2 Columnas"` and `"1 Columna"` (`cv.html:21-28`) and fixed `#download-cv-label` to static `"Descargar CV (PDF)"` (`cv.html:34`, `cv.js:29, 193`) so switching layouts no longer mutates the download button text.

## Verification Evidence

- `node --check curriculum/static/curriculum/js/cv-pdf.js` & `node --check curriculum/static/curriculum/js/cv.js` → Exit code `0` (verified by writer, orchestrator, and independent verifier).
- `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- `uv run python manage.py test` → `Ran 14 tests in 0.019s` (`OK`, verified by writer, independent verifier, and orchestrator spot check).
- `Client().get('/CV/')` render verification → `STATUS 200`, `HAS_PDF_SCRIPT True`, `HAS_DL_LABEL True`, `order ok: True` (`cv-pdf.js` before `cv.js`).
- `node --check curriculum/static/curriculum/js/cv.js` & `Client().get('/CV/')` post-T4 verification → `STATUS 200`, `LABELS_OK True` (`2 Columnas`, `1 Columna`, `Descargar CV (PDF)`), `OLD_LABELS_GONE True`.
- Node VM doc-definition execution (by `Independent PDF Generator Verifier`) → confirmed resilience on empty/null `references`, `highlights`, `skills`, and `linkedin_url`.
- **Non-executed scope note:** Live CDN network download and actual browser PDF binary rendering were not run inside a headless browser; manual verification in `runserver` is the final user step before committing on `development`.
