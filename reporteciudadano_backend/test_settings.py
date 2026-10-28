from .settings import *  # noqa: F403

# Configuración solo para las pruebas automatizadas:
# usa una base SQLite en memoria para no necesitar permisos de MySQL
# para crear la base de datos de pruebas.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
# Hash rápido de contraseñas para que las pruebas corran más rápido
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
