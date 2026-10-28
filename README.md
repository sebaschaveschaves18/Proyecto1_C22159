# Reporte ciudadano

API REST hecha con Django y Django REST Framework para que los ciudadanos reporten problemas de su comunidad, como falta de luz, daños en carreteras o problemas de agua, y las instituciones les den seguimiento. Usa MySQL, autenticación por token y permisos. No tiene interfaz gráfica; se prueba con Postman.

## Requisito

- Python 3.12 o superior
- MySQL y MySQL Workbench
- Postman

## Instalacion

En la carpeta donde está `manage.py`:

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Creacion de la base de datos

En MySQL Workbench:

```sql
CREATE DATABASE reporteciudadano_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reporteciudadano_user'@'localhost' IDENTIFIED BY 'su_clave';
GRANT ALL PRIVILEGES ON reporteciudadano_db.* TO 'reporteciudadano_user'@'localhost';
FLUSH PRIVILEGES;
```

Luego, en el archivo `.env`, escribir en `DB_PASSWORD` la misma clave usada en MySQL.

# Migraciobes

```
python manage.py migrate
python manage.py loaddata datos_iniciales.json
```

`loaddata` carga datos de prueba: instituciones, categorías, reportes, los grupos Ciudadanos y Operadores, y los usuarios de prueba.

## Superusuario

Los datos de prueba ya incluyen el superusuario `admin` con contraseña `admin123`. Si no se cargan los datos, se crea con:

```
python manage.py createsuperuser
```

Otros usuarios de prueba: `operador1` (Operador2026!) y `ciudadano1`, `ciudadano2`, `ciudadano3` (Ciudadano2026!).

## Ejecucion

```
python manage.py runserver
```

El token se obtiene con `POST /api/token/` enviando usuario y contraseña, y se usa en el header `Authorization: Token <valor>`.

La colección de Postman está en la carpeta `postman` y el documento técnico, con los endpoints, en la carpeta `docs`.

## Pruebas

```
python manage.py test --settings=reporteciudadano_backend.test_settings
```

## Limitaciones

- No tiene interfaz gráfica.
- No permite subir fotos en los reportes.
- La ubicación se escribe como texto, sin mapa.
- No envía notificaciones al ciudadano cuando cambia el estado de su reporte.
