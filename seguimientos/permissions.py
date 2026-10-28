from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS


class SeguimientoPermisos(BasePermission):
    """Reglas para escribir seguimientos; las consultas quedan a IsAuthenticated."""
    def has_permission(self, request, view):
        usuario = request.user

        # Consultar: cualquier usuario autenticado (el ciudadano ve el avance)
        if request.method in SAFE_METHODS:
            return True

        # Crear: permiso add_seguimiento (grupo Operadores)
        if request.method == 'POST':
            return usuario.has_perm('seguimientos.add_seguimiento')

        # Actualizar: permiso change_seguimiento
        if request.method in ['PUT', 'PATCH']:
            return usuario.has_perm('seguimientos.change_seguimiento')

        # Eliminar: solo administradores
        if request.method == 'DELETE':
            return IsAdminUser().has_permission(request, view)

        return False
