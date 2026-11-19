# Portafolio Profesional & Generador Dinámico de CV (ATS-Friendly)

Aplicación web modular construida con **Django** y **Python 3.14.7**, diseñada como plataforma de exhibición técnica para reclutadores e ingenieros. Centraliza la presentación interactiva de trayectoria laboral, catálogo de proyectos técnicos y un constructor de currículum con generación de PDF vectorial en el cliente.

---

## 🎯 Propósito del Proyecto

1. **Portafolio Interactivo Centralizado:** Administrado dinámicamente desde el Django Admin, estructurado bajo un sistema de diseño **Editorial Técnico (Swiss Grid / Split Layout)** con soporte nativo para Modo Claro y Modo Oscuro.
2. **Generador de CV en PDF (Client-Side Offloading):** Permite a los reclutadores seleccionar granularmente qué experiencias, proyectos y certificaciones incluir, exportando un PDF **100% vectorial, con enlaces clicables y compatible con ATS (Applicant Tracking Systems)** mediante `pdfmake`.
3. **Plataforma Multi-Proyecto en VPS:** Arquitectura preparada para orquestación con Docker Compose y Traefik, sirviendo como base y punto de entrada para desplegar proyectos satélite en subdominios independientes.

---

## 🏛️ Decisiones de Arquitectura de Software (ADR)

* **Generación de PDF en el Cliente (`pdfmake`):** El backend se limita a consultar y serializar los datos en JSON estructurado (`cv_data`). El ensamblado del documento ocurre enteramente en el navegador del usuario, eliminando el consumo excesivo de CPU y memoria en el servidor asociado a herramientas de renderizado backend.
* **Manejo Seguro de Sesiones vs JWT:** Se implementan sesiones nativas de Django (`HttpOnly`, `SameSite=Lax`, CSRF). Al tratarse de una arquitectura monolítica con frontend del mismo origen, evita vulnerabilidades XSS en `localStorage` y la complejidad innecesaria de rotación de tokens, permitiendo además persistir el contexto de chat anónimo de manera segura.
* **Rendimiento de Estáticos (Production Performance):**
  * **Cache Busting / Hashing:** Almacenamiento por manifiesto que asigna hashes basados en contenido (`app.[hash].css`), garantizando que el navegador invalide la caché de inmediato ante cualquier cambio.
  * **Compresión Pre-Build:** Uso de WhiteNoise para precomprimir activos en **GZIP** y **Brotli** durante `collectstatic`, reduciendo el First Contentful Paint (FCP) sin sobrecargar el servidor en tiempo de ejecución.
  * **Tailwind Standalone CLI:** Compilación de estilos mediante el binario oficial de Tailwind sin intermediación de `npm` ni dependencias pesadas en `node_modules`.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Justificación |
| :--- | :--- | :--- |
| **Runtime** | **Python 3.14.7** | Rendimiento y características modernas del lenguaje. |
| **Package Manager** | **`uv`** | Resolución de dependencias ultrarrápida y gestión de entornos reproducibles. |
| **Backend** | **Django 6.x** | Arquitectura limpia (vistas delgadas, `services.py` y `selectors.py`), ORM robusto y panel administrativo avanzado. |
| **Servidor HTTP** | **Granian** | Servidor ASGI/WSGI de alto rendimiento escrito en Rust. |
| **Base de Datos** | **PostgreSQL** / **SQLite (WAL)** | PostgreSQL para producción; fallback automático a SQLite para desarrollo local ágil. |
| **Frontend** | **Django Templates + Tailwind CSS** | HTML semántico con diseño responsivo mobile-first en 3 breakpoints estándar (<768px, 768-1024px, >1024px). |
| **Scripts Cliente** | **Vanilla JavaScript (ES6+)** | Módulos nativos ligeros sin la sobrecarga de un framework SPA. |
| **Motor PDF** | **`pdfmake`** | Generación vectorial ATS-friendly ejecutada bajo demanda en el navegador. |
| **Calidad de Código** | **Ruff** | Linter y formateador estricto para mantener consistencia y apego a PEP 8. |

---

## 📁 Estructura del Repositorio

```text
Portafolio/
├── bin/                       # Herramientas CLI locales (Tailwind Standalone CLI) [ignorado en Git]
├── curriculum/                # App: Trayectoria profesional, logros, educación y CV (/CV/)
│   ├── static/curriculum/     # Estáticos específicos de la app
│   └── templates/curriculum/  # Plantillas con espacio de nombres
├── jek_ia/                    # App: Asistente interactivo y chat de consulta (/chat/)
│   ├── static/jek_ia/
│   └── templates/jek_ia/
├── proyectos/                 # App: Fichas técnicas, arquitectura y catálogo (/prodep/)
│   ├── static/proyectos/
│   └── templates/proyectos/
├── portafolio/                # Módulo de configuración principal de Django (settings, urls, asgi, wsgi)
├── templates/                 # Plantillas maestras globales (base.html con slots y meta)
├── static/                    # Activos globales compartidos
│   ├── css/                   # input.css y output.css (compilado por Tailwind)
│   └── js/                    # main.js (lógica de tema y utilidades globales)
├── .env.template              # Plantilla de variables de entorno documentada
├── AGENTS.md                  # Reglas operativas y estándares técnicos para agentes de IA
├── pyproject.toml             # Manifiesto de dependencias y configuración de herramientas
└── tailwind.config.js         # Configuración del escaneo de clases y tokens de diseño
```

---

## 🎨 Sistema de Diseño y Paleta de Colores

Diseño tipográfico de alta legibilidad inspirado en la grilla suiza (*Swiss Grid*), estructurado con líneas de 1px y tokens CSS dinámicos:

* **Acento Principal:** `#22A6BF` (Cyan Técnico)
* **Modo Claro:** Fondo `#F8FAFB`, Superficie `#FFFFFF`, Texto `#0F172A`.
* **Modo Oscuro:** Fondo `#0B1118`, Superficie `#131C26`, Texto `#F1F5F9`.
* **Tipografías:**
  * *Títulos:* `Space Grotesk`
  * *Cuerpo:* `Inter`
  * *Metadatos y Código:* `JetBrains Mono`

---

## 🚀 Puesta en Marcha en Desarrollo Local

### 1. Prerrequisitos
* [uv](https://docs.astral.sh/uv/) instalado en el sistema.
* Python 3.14.7 disponible.

### 2. Clonación y Entorno
```bash
git clone <url-del-repositorio>
cd Portafolio

# Sincronizar dependencias en el entorno virtual
uv sync
```

### 3. Configuración de Variables de Entorno
Copiar el archivo de plantilla y ajustar según corresponda:
```bash
cp .env.template .env
```
*(Por defecto, si las credenciales de base de datos se dejan vacías, Django utilizará SQLite automáticamente).*

### 4. Migraciones Iniciales
```bash
uv run python manage.py migrate
```

### 5. Compilación de Estilos (Tailwind CSS)
En una terminal separada, ejecutar el compilador en modo escucha (*watch mode*):
```powershell
# En Windows
.\bin\tailwindcss.exe -i .\static\css\input.css -o .\static\css\output.css --watch
```

### 6. Ejecutar Servidor de Desarrollo
```bash
uv run python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

---

## 🧪 Estándares de Ingeniería y Testing

* **Metodología:** Desarrollo guiado orgánicamente (**ODD - Organic Driven Development**).
* **Protocolo de Pruebas:** Toda prueba automatizada requiere aprobación previa mediante una propuesta estructurada que defina clase, método, caso a evaluar y aserción exacta.
* **Verificación de Código:**
  ```bash
  uv run ruff check .
  uv run ruff format .
  uv run python manage.py check
  ```
