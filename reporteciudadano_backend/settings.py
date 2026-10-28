import os
from pathlib import Path
from dotenv import load_dotenv

# Carpeta principal del proyecto (donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Lee las variables del archivo .env (este archivo NO se sube al repositorio)
load_dotenv(BASE_DIR / '.env')

# Clave secreta de Django: se toma del .env
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-clave-solo-para-desarrollo-local'
)
# DEBUG en True solo para desarrollo
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
# Hosts permitidos, separados por coma en el .env
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

# Aplicaciones registradas en el proyecto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',             # Django REST Framework
    'rest_framework.authtoken',   # Tabla y endpoint de tokens
    'instituciones',              # Módulo 1: instituciones responsables
    'categorias',                 # Módulo 2: tipos de reporte
    'reportes',                   # Módulo 3: reportes ciudadanos
    'seguimientos',               # Módulo 4: avances de los operadores
    'apoyos',                     # Módulo 5: apoyos de ciudadanos (N:M)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reporteciudadano_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'reporteciudadano_backend.wsgi.application'
ASGI_APPLICATION = 'reporteciudadano_backend.asgi.application'

# Conexión a MySQL: los datos se leen del .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'reporteciudadano_db'),
        'USER': os.getenv('DB_USER', 'reporteciudadano_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cr'
TIME_ZONE = 'America/Costa_Rica'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración global de DRF: autenticación por token.
# Los permisos se definen en cada vista con @permission_classes.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
