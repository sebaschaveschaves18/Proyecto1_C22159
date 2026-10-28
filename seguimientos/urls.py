from django.urls import path
from . import views

# Rutas del módulo seguimientos (se incluyen en /api/seguimientos/)
urlpatterns = [
    path('', views.seguimientos_api, name='seguimientos_api'),
    path('<int:pk>/', views.seguimiento_detalle_api, name='seguimiento_detalle_api'),
]
