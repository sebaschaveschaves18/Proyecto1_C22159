from django.urls import path
from . import views

# Rutas del módulo instituciones (se incluyen en /api/instituciones/)
urlpatterns = [
    path('', views.instituciones_api, name='instituciones_api'),
    path('<int:pk>/', views.institucion_detalle_api, name='institucion_detalle_api'),
]
