from rest_framework.permissions import BasePermission, SAFE_METHODS


class ApoyoPermisos(BasePermission):
    """Reglas para apoyos; las consultas quedan a IsAuthenticated."""
    def has_permission(self, request, view):
        usuario = request.user

        # Consultar: cualquier usuario autenticado
        if request.method in SAFE_METHODS:
            return True

        # Crear: pertenecer al grupo Ciudadanos y tener add_apoyo
        if request.method == 'POST':
            pertenece_al_grupo = usuario.groups.filter(name='Ciudadanos').exists()
            tiene_permiso = usuario.has_perm('apoyos.add_apoyo')
            return pertenece_al_grupo and tiene_permiso

        # Eliminar: permiso delete_apoyo (en la vista se revisa que sea el dueño o admin)
        if request.method == 'DELETE':
            return usuario.has_perm('apoyos.delete_apoyo')

        return False
