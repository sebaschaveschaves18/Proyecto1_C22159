from django.urls import path
from . import views

# Rutas del módulo categorías (se incluyen en /api/categorias/)
urlpatterns = [
    path('', views.categorias_api, name='categorias_api'),
    path('<int:pk>/', views.categoria_detalle_api, name='categoria_detalle_api'),
]
