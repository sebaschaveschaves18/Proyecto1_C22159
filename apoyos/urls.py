from django.urls import path
from . import views

# Rutas del módulo apoyos (se incluyen en /api/apoyos/)
urlpatterns = [
    path('', views.apoyos_api, name='apoyos_api'),
    path('<int:pk>/', views.apoyo_detalle_api, name='apoyo_detalle_api'),
]
