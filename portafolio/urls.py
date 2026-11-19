"""
URL configuration for portafolio project.

Prefijos de rutas por app:
- /chat/    -> jek_ia
- /CV/      -> curriculum
- /prodep/  -> proyectos
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("jek_ia.urls")),
    path("CV/", include("curriculum.urls")),
    path("prodep/", include("proyectos.urls")),
]

# Servir archivos multimedia subidos por usuarios en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
