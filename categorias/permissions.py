from rest_framework.permissions import SAFE_METHODS, BasePermission


class CategoriaPermisos(BasePermission):
    """GET es público; crear, editar y eliminar requieren el permiso de modelo."""
    def has_permission(self, request, view):
        # Consultar categorías es público (el ciudadano necesita verlas para reportar)
        if request.method in SAFE_METHODS:
            return True
        # Sin token -> 401
        if not request.user or not request.user.is_authenticated:
            return False

        # Con token pero sin el permiso del método -> 403
        permisos = {
            'POST': 'categorias.add_categoria',
            'PUT': 'categorias.change_categoria',
            'PATCH': 'categorias.change_categoria',
            'DELETE': 'categorias.delete_categoria',
        }
        permiso = permisos.get(request.method)
        if permiso is None:
            return False
        return request.user.has_perm(permiso)
