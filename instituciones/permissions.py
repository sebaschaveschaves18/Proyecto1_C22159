from rest_framework.permissions import SAFE_METHODS, BasePermission


class InstitucionPermisos(BasePermission):
    """GET es público; crear, editar y eliminar requieren el permiso de modelo."""
    def has_permission(self, request, view):
        # GET, HEAD y OPTIONS no modifican datos: acceso público
        if request.method in SAFE_METHODS:
            return True
        # Sin token -> no autenticado (DRF responde 401)
        if not request.user or not request.user.is_authenticated:
            return False

        # Cada método necesita su permiso de modelo (con token pero sin permiso -> 403)
        permisos = {
            'POST': 'instituciones.add_institucion',
            'PUT': 'instituciones.change_institucion',
            'PATCH': 'instituciones.change_institucion',
            'DELETE': 'instituciones.delete_institucion',
        }
        permiso = permisos.get(request.method)
        if permiso is None:
            return False
        return request.user.has_perm(permiso)
