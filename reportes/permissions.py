from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS


class ReportePermisos(BasePermission):
    """Reglas para escribir reportes; las consultas quedan a IsAuthenticated."""
    def has_permission(self, request, view):
        usuario = request.user

        # Consultar: cualquier usuario autenticado
        if request.method in SAFE_METHODS:
            return True

        # Crear: pertenecer al grupo Ciudadanos y tener add_reporte
        if request.method == 'POST':
            pertenece_al_grupo = usuario.groups.filter(name='Ciudadanos').exists()
            tiene_permiso = usuario.has_perm('reportes.add_reporte')
            return pertenece_al_grupo and tiene_permiso

        # Actualizar (cambiar estado, corregir datos): permiso change_reporte (Operadores)
        if request.method in ['PUT', 'PATCH']:
            return usuario.has_perm('reportes.change_reporte')

        # Eliminar: solo administradores
        if request.method == 'DELETE':
            return IsAdminUser().has_permission(request, view)

        return False
