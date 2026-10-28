from django.urls import path
from . import views

# Rutas del módulo reportes (se incluyen en /api/reportes/)
urlpatterns = [
    path('', views.reportes_api, name='reportes_api'),
    path('mis-reportes/', views.mis_reportes_api, name='mis_reportes_api'),
    path('estadisticas/', views.estadisticas_api, name='estadisticas_api'),
    path('<int:pk>/', views.reporte_detalle_api, name='reporte_detalle_api'),
    path('<int:pk>/historial/', views.historial_reporte_api, name='historial_reporte_api'),
]
