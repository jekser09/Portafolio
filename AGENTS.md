# AGENTS.md — Portafolio Profesional & Generador de CV Dinámico (Django)

Este archivo define las reglas de arquitectura, estándares de ingeniería, diseño visual y protocolos de desarrollo agéntico para este proyecto. **Todo código generado debe tratarse como código de producción de exhibición**: otros ingenieros y reclutadores auditarán este repositorio para evaluar criterio técnico, arquitectura y limpieza.

---

## 1. Visión del Proyecto y Arquitectura

El proyecto es una aplicación web en **Django** que cumple dos propósitos esenciales:
1. **Portafolio y Hoja de Vida interactiva:** Administrado dinámicamente desde el *Django Admin* (perfil, experiencia laboral detallada con logros, certificaciones, catálogo de proyectos con fichas técnicas y formulario de contacto).
2. **Constructor de CV en PDF (Client-Side Offloading):** Permite al usuario filtrar interactivamente qué experiencias, proyectos y certificaciones incluir, generando un PDF descargable en el navegador.

### Decisiones Arquitectónicas Clave
* **Generación de PDF en el Cliente:**
  * **Backend (Django):** Consulta, filtra y serializa los datos en JSON seguro vía template tag `{{ cv_data|json_script:"cv-data" }}` o endpoint `/api/cv-data/`.
  * **Frontend (Vanilla JS + pdfmake):** Maneja el estado reactivo de checkboxes, renderiza la previsualización y compila el PDF mediante **`pdfmake`** cargado de forma diferida (*lazy loading*).
  * **PROHIBICIÓN ESTRICTA:** No usar `html2canvas` ni `html2pdf.js`. El PDF debe ser **100% vectorial, con texto seleccionable, hipervínculos funcionales y compatible con ATS (Applicant Tracking Systems)**.
* **Manejo de Sesiones (Chat y Estado):**
  * Uso de **sesiones nativas de Django** mediante cookies seguras (`HttpOnly`, `SameSite=Lax`, protección CSRF).
  * **No usar JWT:** Al ser una arquitectura monolítica con frontend del mismo origen, las sesiones de Django evitan vulnerabilidades XSS en `localStorage` y complejidad innecesaria de tokens de refresco, permitiendo además persistir historial de chat anónimo de forma limpia.

---

## 2. Stack Tecnológico y Entorno

* **Runtime:** **Python 3.14.7**
* **Gestor de paquetes y entornos:** **`uv`** (usar siempre `uv add`, `uv run`, `uv sync`; nunca invocar `pip` directo).
* **Framework Backend:** **Django 5.x** (arquitectura en capas: vistas delgadas, `services.py` para lógica de negocio y `selectors.py` para consultas ORM).
* **Base de Datos:** **PostgreSQL** administrada estrictamente mediante el **ORM de Django**.
* **Frontend:** Django Templates + **Tailwind CSS** + **Vanilla JavaScript** (ES6+ modular, sin frameworks SPA pesados).
* **Motor PDF:** **`pdfmake`** (client-side).
* **Linting y Formateo:** **`ruff`** (verificación y formateo estricto).
* **Infraestructura de Despliegue:** Preparado para **VPS con Docker Compose + Traefik** (reverse proxy con SSL automático y soporte para múltiples proyectos en subdominios).

---

## 3. Metodología de Desarrollo Agéntico y Protocolo de Testing

### Metodología de Desarrollo
* Se adopta **ODD (Organic Driven Development)**: desarrollo guiado orgánicamente, priorizando fundamentos arquitectónicos, diseño modular y validación continua antes de generar código masivo.

### Protocolo Estricto de Testing (MANDATORIO)
* **Regla de Aprobación Previa:** Antes de escribir o modificar cualquier test en el proyecto, el agente o subagente **DEBE presentar obligatoriamente una lista numerada** indicando:
  1. Nombre de la clase y método de prueba.
  2. Escenario específico que evalúa.
  3. Datos de entrada / estado inicial.
  4. Aserción o resultado exacto esperado.
* **Detención obligatoria:** El agente debe **detenerse y esperar la aprobación o descarte del usuario** antes de crear los archivos o escribir el código de prueba.
* **Framework de Test:** Runner nativo de Django (`TestCase` / `TransactionTestCase`), manteniendo pruebas unitarias de servicios aisladas y pruebas de integración para endpoints clave.

---

## 4. Identidad Visual, Paleta de Colores y UI/UX Responsive

El estilo visual es **Editorial Técnico (Swiss Grid / Documento de Ingeniería)**: tipográfico, limpio, estructurado con líneas de 1px y de alto contraste descansado.

### Paleta de Colores (Tokens CSS en `:root` y `.dark`)
El color de acento principal es **`#22A6BF`** (Cyan Técnico). Toda la interfaz debe soportar **Modo Claro** y **Modo Oscuro**:

| Token CSS | Modo Claro | Modo Oscuro | Función |
| :--- | :--- | :--- | :--- |
| `--bg-base` | `#F8FAFB` (Gris hielo suave) | `#0B1118` (Azul medianoche profundo) | Fondo principal de la aplicación |
| `--bg-surface` | `#FFFFFF` | `#131C26` (Superficie petróleo) | Tarjetas, bloques de código, modales |
| `--border-subtle` | `#E2E8F0` | `#1E2D3D` (Líneas sutiles de 1px) | Grilla estructural editorial |
| `--text-primary` | `#0F172A` (Slate 900) | `#F1F5F9` (Gris perla) | Títulos y texto de alta jerarquía |
| `--text-secondary`| `#475569` (Slate 600) | `#94A3B8` (Gris pizarra) | Metadatos, fechas, tags y descripciones |
| `--accent-primary`| **`#22A6BF`** | **`#22A6BF`** | CTAs, links activos, checkboxes, foco |
| `--accent-hover` | `#1B8599` | `#45C5DE` | Estado hover de interactivos |

### Breakpoints y Adaptabilidad (Mobile-First en CSS)
El código CSS/Tailwind se escribe bajo metodología **Mobile-First** (`min-width`) y debe responder con precisión a 3 dimensiones estándar:
1. **Móvil (`< 768px`)**: Layout vertical en columna única. Navegación mediante dock inferior flotante para ergonomía de uso con pulgar.
2. **Tablet (`768px - 1024px`)**: Contenedor central fluido con espaciado técnico y navegación condensada.
3. **Escritorio (`> 1024px`)**: **Split Layout Asimétrico**:
   * **Columna izquierda fija (Sticky Rail, ~32%)**: Identidad, bio técnica, selector de tema, navegación vertical con indicador activo y acceso al constructor de CV.
   * **Columna derecha deslizable (Canvas, ~68%)**: Cuadrícula de experiencia, certificaciones, fichas técnicas de proyectos y contacto.

### Tipografía
* **Títulos:** Sans-serif geométrica con carácter (`Space Grotesk`).
* **Cuerpo:** Sans-serif de alta legibilidad (`Inter`).
* **Metadatos, fechas, stack y métricas:** Monospace (`JetBrains Mono`).

### Arquitectura de Templates y Estáticos (Herencia Global vs Modular)
* **Raíz (`templates/` y `static/`):**
  * `templates/base.html`: Shell maestro de la aplicación (metadatos, `head`, tokens de diseño, navbar/dock, contenedor de tema oscuro/claro y scripts globales).
  * `static/css/`: Archivo de entrada de Tailwind (`input.css`) y CSS compilado global (`output.css`).
  * `bin/`: Aloja herramientas CLI y binarios de compilación del entorno local (`tailwindcss.exe`). Esta carpeta **NUNCA se versiona en Git**.
* **Específico de cada App (`curriculum/`, `jek_ia/`, `proyectos/`):**
  * Cada app que exponga una vista debe crear su propia estructura de plantillas con espacio de nombres: `<app>/templates/<app>/<vista>.html` heredando siempre de `base.html` vía `{% extends 'base.html' %}`.
  * Archivos estáticos propios de la app van en `<app>/static/<app>/css/` o `<app>/static/<app>/js/`.

---

## 5. Modelo de Datos (Django ORM)

Modelos estructurados por dominio y responsabilidad:

### App `curriculum/` (Hoja de Vida y Perfil):
1. **`Profile`**: Singleton lógico del titular (`full_name`, `headline`, `bio`, `email`, `phone`, `location`, `github_url`, `linkedin_url`, `avatar`).
2. **`SkillCategory`**: Categorías de habilidades y conocimientos (`name`, `order`).
3. **`Skill`**: Habilidades técnicas y blandas (`name`, `category` ForeignKey, `is_highlighted`, `order`).
4. **`Experience`**: Trayectoria laboral (`company`, `role`, `start_date`, `end_date`, `is_current`, `is_visible`, `order`).
5. **`ExperienceHighlight`**: Viñetas de logros específicos asociadas a `Experience` (`ForeignKey`, `description`, `order`).
6. **`Education`**: Formación académica (`institution`, `degree`, `year_completed`, `is_in_progress`, `order`).
7. **`Reference`**: Referencias profesionales (`name`, `role`, `phone`, `email`, `is_visible_on_web`, `order`).

### App `proyectos/` (Catálogo Técnico y Casos de Estudio):
1. **`ProjectCategory`**: Categorías técnicas de proyectos (ej. *Backend*, *Cloud & DevOps*, *Fullstack*).
2. **`Project`**: Casos de estudio y aplicaciones (`title`, `slug`, `short_description`, `detailed_description`, `repo_url`, `live_url`, `category`, `skills` ManyToManyField, `is_featured`, `is_visible`, `order`).

---

## 6. Rendimiento y Gestión de Archivos Estáticos (Production Performance)

Para optimizar velocidad de carga (Core Web Vitals) y evitar problemas de caché en clientes:

* **Cache Busting / Hashing (Serialización de Estáticos):**
  * Obligatorio el uso de almacenamiento basado en manifiesto (`whitenoise.storage.CompressedManifestStaticFilesStorage` o `ManifestStaticFilesStorage` de Django).
  * Cada archivo CSS y JS genera un hash de contenido único en tiempo de `collectstatic` (ej. `app.a8f23c10.css`). Si el archivo cambia, el hash cambia e invalida la caché del navegador de inmediato.
* **Compresión (GZIP y Brotli):**
  * Compresión previa en compilación (*pre-compressed assets*) usando WhiteNoise para evitar consumo innecesario de CPU en el servidor por petición.
  * Generación automática de versiones `.gz` y `.br` con cabeceras HTTP `Cache-Control: public, max-age=31536000, immutable`.
* **Minificación Obligatoria:**
  * **CSS:** Tailwind CSS compila con bandera `--minify` eliminando clases no usadas y reduciendo el peso al mínimo.
  * **JavaScript:** Los módulos Vanilla JS deben pasar por minificación para producción (sin comentarios ni espacios en blanco).

---

## 7. Estándares de Código, Documentación y Seguridad

* **Separación Estricta de Capas (Vistas Delgadas vs. Services/Selectors):**
  * **`views.py` (Capa de Transporte HTTP):** CERO lógica de negocio y CERO consultas ORM directas. Su única responsabilidad es:
    1. Validar la petición HTTP (métodos GET/POST, headers, parámetros de entrada).
    2. Invocar la función correspondiente en `services.py` (para mutaciones/acciones) o `selectors.py` (para lecturas/queries).
    3. Construir y devolver la respuesta HTTP (`render()`, `JsonResponse()`, redirects o códigos de estado).
  * **`services.py` (Lógica de Negocio y Operaciones de Escritura):** Concentra todas las reglas de negocio, mutaciones, transformaciones de datos, envío de correos y orquestaciones.
  * **`selectors.py` (Consultas y Operaciones de Lectura):** Concentra las consultas del ORM con optimizaciones (`select_related`, `prefetch_related`, agregaciones), aislando el acceso a datos.
* **Estándares de JavaScript y Scripts Frontend:**
  * **Cero JavaScript inline:** Prohibido colocar código JS embebido dentro de etiquetas `<script>` en los templates HTML. Todo código debe residir en archivos externos modulares (`.js`) dentro de las carpetas `static/` correspondientes.
  * **Uso obligatorio de `defer`:** Toda inclusión de scripts debe usar el atributo `defer` (ej. `<script defer src="{% static '...' %}"></script>`). Al postergar la ejecución hasta que el DOM esté completamente parseado, **no se debe encapsular el código en listeners como `DOMContentLoaded` o `window.onload`**, manteniendo los archivos JS directos, planos y limpios.
* **Docstrings Google Style:** Obligatorios en vistas, modelos, servicios, selectores y utilidades.
* **Type Hints:** Obligatorios en todas las firmas de funciones en `services.py` y `selectors.py`.
* **Optimización de Consultas:** Cero consultas N+1. Obligatorio el uso de `select_related()` y `prefetch_related()`.
* **Django Admin:** Configuración rica mediante `TabularInline` para logros, filtros facetados y búsqueda.
* **Seguridad:** Cero secretos en código (`python-dotenv` / variables de entorno). Formulario de contacto protegido con técnica de *honeypot* y limitación de tasa (*rate limiting*).
* **README vivo:** Documentación actualizada de arquitectura, decisiones técnicas (ADR) y despliegue.

---

## 8. Comandos de Referencia (`uv`)

```bash
# Ejecutar servidor de desarrollo con Python 3.14.7
uv run python manage.py runserver

# Gestión de migraciones de base de datos
uv run python manage.py makemigrations
uv run python manage.py migrate

# Ejecución de pruebas unitarias y de integración
uv run python manage.py test

# Formateo y análisis estático con Ruff
uv run ruff check .
uv run ruff format .
```
