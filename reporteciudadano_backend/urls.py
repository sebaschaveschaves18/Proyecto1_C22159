from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from reportes.views import perfil_api

# Rutas principales: cada módulo tiene su propio urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api_token'),   # Obtener token con usuario/contraseña
    path('api/perfil/', perfil_api, name='api_perfil'),        # Datos y rol del usuario autenticado
    path('api/instituciones/', include('instituciones.urls')),
    path('api/categorias/', include('categorias.urls')),
    path('api/reportes/', include('reportes.urls')),
    path('api/seguimientos/', include('seguimientos.urls')),
    path('api/apoyos/', include('apoyos.urls')),
]
