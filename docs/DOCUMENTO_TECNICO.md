# Documento técnico - Reporte Ciudadano

Sistema para que los ciudadanos reporten problemas de su comunidad (falta de luz, daños en carreteras, problemas de agua, basura) y las instituciones responsables les den seguimiento.

## Módulos

- **Instituciones:** entidades que atienden los reportes (AyA, CNFL, MOPT, Municipalidad).
- **Categorías:** tipos de problema. Cada una pertenece a una institución y tiene una prioridad base.
- **Reportes:** los crea el ciudadano. Toman la prioridad de su categoría.
- **Seguimientos:** avances que registra el operador sobre un reporte.
- **Apoyos:** un ciudadano apoya el reporte de otro. Con 3 apoyos la prioridad sube a ALTA.

Apoyos no tiene editar (PUT/PATCH) porque un apoyo no tiene datos que cambiar; solo se crea o se elimina.

## Diagrama entidad-relación

![Diagrama ER](diagrama_er.png)

- Institución 1:N Categoría (PROTECT: no se borra una institución con categorías).
- Categoría 1:N Reporte (PROTECT: no se borra una categoría con reportes).
- Usuario 1:N Reporte (PROTECT).
- Reporte 1:N Seguimiento (CASCADE: si se borra el reporte, se borran sus seguimientos).
- Usuario N:M Reporte por medio de Apoyo (CASCADE), con restricción única: un apoyo por usuario y reporte.

## Matriz de permisos

| Recurso | Anónimo | Ciudadano | Operador | Administrador |
|---|---|---|---|---|
| Ver instituciones y categorías | Sí | Sí | Sí | Sí |
| Crear, editar o eliminar instituciones y categorías | No (401) | No (403) | No (403) | Sí |
| Ver reportes | No (401) | Sí | Sí | Sí |
| Crear reporte | No (401) | Sí | No (403) | No (403) |
| Editar reporte o cambiar su estado | No (401) | No (403) | Sí | Sí |
| Eliminar reporte | No (401) | No (403) | No (403) | Sí |
| Ver estadísticas | No (401) | No (403) | No (403) | Sí |
| Crear o editar seguimiento | No (401) | No (403) | Sí | Sí |
| Apoyar reporte | No (401) | Sí | No (403) | No (403) |
| Eliminar apoyo | No (401) | Solo el suyo | No (403) | Sí |

## Reglas de negocio

1. El nombre y las siglas de una institución no se repiten.
2. El nombre de una categoría no se repite y no se puede asignar a una institución inactiva.
3. La descripción del reporte debe tener al menos 10 caracteres.
4. No se puede crear un reporte en una categoría inactiva.
5. Un ciudadano no puede tener dos reportes abiertos de la misma categoría en el mismo distrito.
6. Los estados solo avanzan así: RECIBIDO → EN_PROCESO → RESUELTO, o pasan a RECHAZADO. Un reporte cerrado ya no se modifica.
7. Al crear un reporte se copia la prioridad de la categoría, y al resolverlo se guarda la fecha de resolución.
8. No se registran seguimientos en un reporte cerrado. El primer seguimiento pasa el reporte a EN_PROCESO.
9. Un ciudadano no puede apoyar su propio reporte ni un reporte cerrado.
10. Un ciudadano solo puede apoyar una vez el mismo reporte (409).
11. No se puede eliminar una institución con categorías ni una categoría con reportes (409).

Si alguna regla no se cumple, la API responde 400 con el mensaje del error, salvo los casos marcados con 409.

## Catálogo de endpoints

**Autenticación**
- `POST /api/token/`: obtener token.
- `GET /api/perfil/`: datos y rol del usuario.

**Instituciones**
- `GET, POST /api/instituciones/`: listar (filtro `activo`, orden `ordering=nombre`, paginado) y crear.
- `GET, PUT, PATCH, DELETE /api/instituciones/<id>/`: detalle, editar y eliminar.

**Categorías**
- `GET, POST /api/categorias/`: listar (filtros `institucion`, `prioridad`, `activo`, paginado) y crear.
- `GET, PUT, PATCH, DELETE /api/categorias/<id>/`: detalle, editar y eliminar.

**Reportes**
- `GET, POST /api/reportes/`: listar (filtros `estado`, `prioridad`, `distrito`, `categoria`, `institucion`, búsqueda `buscar`, orden `ordering`, paginado) y crear.
- `GET, PUT, PATCH, DELETE /api/reportes/<id>/`: detalle, editar o cambiar estado, y eliminar.
- `GET /api/reportes/mis-reportes/`: reportes del usuario.
- `GET /api/reportes/<id>/historial/`: reporte con sus seguimientos y apoyos.
- `GET /api/reportes/estadisticas/`: estadísticas (solo administrador).

**Seguimientos**
- `GET, POST /api/seguimientos/`: listar (filtros `reporte`, `tipo`, paginado) y registrar.
- `GET, PUT, PATCH, DELETE /api/seguimientos/<id>/`: detalle, editar y eliminar.

**Apoyos**
- `GET, POST /api/apoyos/`: listar (filtro `reporte`) y apoyar.
- `GET, DELETE /api/apoyos/<id>/`: detalle y eliminar.
