# Reporte Ciudadano

API REST desarrollada con Django y Django REST Framework para que los ciudadanos reporten problemas de su comunidad (cortes de luz, daños en carreteras, falta de agua, basura acumulada, entre otros) y las instituciones responsables les den seguimiento. Los datos se guardan en MySQL. El proyecto usa autenticación por token, grupos y permisos de modelo. No incluye interfaz gráfica: se prueba con Postman y con pruebas automatizadas.

## Proceso de negocio

1. El **administrador** registra las **instituciones** (AyA, CNFL, MOPT, Municipalidad) y las **categorías** de problemas que atiende cada una.
2. El **ciudadano** crea un **reporte** eligiendo una categoría. El sistema le asigna automáticamente el estado `RECIBIDO` y la prioridad de la categoría.
3. Otros ciudadanos afectados **apoyan** el reporte. Con 3 apoyos el sistema sube la prioridad a `ALTA`.
4. El **operador** registra **seguimientos** (inspección, reparación, comentario). El primer seguimiento pasa el reporte a `EN_PROCESO`.
5. El operador cierra el reporte como `RESUELTO` (se guarda la fecha de resolución) o `RECHAZADO`. Un reporte cerrado ya no se modifica.

## Módulos

| App | Responsabilidad | Relación principal |
|---|---|---|
| `instituciones` | Entidades que atienden los reportes | 1:N con categorías |
| `categorias` | Tipos de problema y su prioridad base | N:1 institución, 1:N reportes |
| `reportes` | Reportes de los ciudadanos, estadísticas y perfil | N:1 categoría, N:1 usuario |
| `seguimientos` | Avances registrados por los operadores | N:1 reporte, N:1 usuario |
| `apoyos` | Apoyos de ciudadanos a reportes de otros | N:M usuario ↔ reporte |

## Requisitos

- Python 3.12 o superior
- MySQL 8 (o MariaDB 10.5+) y MySQL Workbench
- Postman

## Instalación

Abrir la carpeta donde está `manage.py` en VS Code y ejecutar en la terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Creación de la base de datos

En MySQL Workbench ejecutar (cambiar la contraseña por una propia):

```sql
CREATE DATABASE reporteciudadano_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'reporteciudadano_user'@'localhost'
IDENTIFIED BY 'CambieEstaClave2026!';

GRANT ALL PRIVILEGES ON reporteciudadano_db.*
TO 'reporteciudadano_user'@'localhost';

FLUSH PRIVILEGES;
```

Luego escribir en `.env` los mismos datos (la contraseña debe coincidir con la del usuario de MySQL):

```
DJANGO_SECRET_KEY=una-clave-local
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=reporteciudadano_db
DB_USER=reporteciudadano_user
DB_PASSWORD=CambieEstaClave2026!
DB_HOST=localhost
DB_PORT=3306
```

## Migraciones y datos de prueba

```powershell
python manage.py check
python manage.py migrate
python manage.py loaddata datos_iniciales.json
```

`migrate` crea las tablas en MySQL y `loaddata` carga datos ficticios: 5 instituciones, 9 categorías, 8 reportes, 5 seguimientos, 5 apoyos, los grupos `Ciudadanos` y `Operadores` con sus permisos y los usuarios de prueba.

## Superusuario y usuarios de prueba

Los datos iniciales ya incluyen el superusuario. Si no se cargan los datos, se crea con:

```powershell
python manage.py createsuperuser
```

Usar usuario `admin` y contraseña `admin123`. Django avisa que la contraseña es muy común; responder `y` para crearlo de todas formas.

| Usuario | Contraseña | Perfil | Grupo |
|---|---|---|---|
| admin | admin123 | Administrador (`is_staff`, superusuario) | — |
| operador1 | Operador2026! | Operador | Operadores |
| ciudadano1 | Ciudadano2026! | Ciudadano | Ciudadanos |
| ciudadano2 | Ciudadano2026! | Ciudadano | Ciudadanos |
| ciudadano3 | Ciudadano2026! | Ciudadano | Ciudadanos |

Son credenciales ficticias, solo para la demostración local.

## Ejecución

```powershell
python manage.py runserver
```

Panel de administración: http://127.0.0.1:8000/admin/

## Autenticación

Obtener el token:

```
POST /api/token/
{"username": "ciudadano1", "password": "Ciudadano2026!"}
```

Enviar el token en las solicitudes protegidas:

```
Authorization: Token VALOR_DEL_TOKEN
```

## Pruebas automatizadas

```powershell
python manage.py test --settings=reporteciudadano_backend.test_settings
```

Las pruebas usan `test_settings.py`, que cambia la base de datos por SQLite en memoria. Así no se necesita permiso en MySQL para crear la base de datos de pruebas. Si el usuario de MySQL tiene permiso para crear bases de datos, también se puede ejecutar `python manage.py test`.

Son 36 pruebas: CRUD, reglas de negocio, permisos (401/403), conflictos (409), filtros, búsqueda y paginación. La evidencia de la ejecución está en `docs/evidencia_pruebas.txt`.

## Postman

Importar `postman/ReporteCiudadano.postman_collection.json` y el entorno `postman/ReporteCiudadano.postman_environment.json`. Ejecutar la colección en orden después de `migrate` y `loaddata`. Las primeras solicitudes obtienen los tokens y los guardan en variables. Cada solicitud indica la respuesta esperada y tiene una prueba del código HTTP (49 solicitudes).

Para repetir la colección desde cero, volver a crear la base de datos y ejecutar `migrate` y `loaddata`.

## Documentación

`docs/DOCUMENTO_TECNICO.md` contiene el diagrama entidad-relación, la matriz de permisos, las reglas de negocio, las consultas ORM y el catálogo de endpoints.

## Estructura

```
ReporteCiudadano/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── datos_iniciales.json
├── reporteciudadano_backend/   (settings, test_settings, urls)
├── instituciones/              (models, serializers, permissions, views, urls, tests, migrations)
├── categorias/
├── reportes/
├── seguimientos/
├── apoyos/
├── postman/
└── docs/
```

## Distribución de responsabilidades

| Integrante | Módulos a cargo | Revisa el código de |
|---|---|---|
| Integrante 1 | `instituciones`, `categorias`, configuración y MySQL | `reportes` |
| Integrante 2 | `reportes` (estadísticas, perfil, permisos) | `seguimientos`, `apoyos` |
| Integrante 3 | `seguimientos`, `apoyos`, Postman | `instituciones`, `categorias` |

## Limitaciones conocidas

- No hay frontend; todo se prueba con Postman.
- No se permite subir fotografías del problema en los reportes.
- La ubicación se registra como texto (distrito y dirección), sin coordenadas GPS.
- Los apoyos no se pueden editar (solo crear y eliminar), porque no tienen datos editables.
- La colección de Postman modifica datos; para repetirla se debe recargar la base de datos.
- No se envían notificaciones al ciudadano cuando cambia el estado de su reporte.

## Entrega

No se incluyen `.env`, `.venv`, `__pycache__`, contraseñas reales ni la base de datos. Sí se incluyen las migraciones, `.env.example` y `requirements.txt`.
