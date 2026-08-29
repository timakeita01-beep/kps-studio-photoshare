"""
Django settings for KPS Studio / PhotoShare.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# --- Core ---------------------------------------------------------------

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-only-change-me')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]


# --- Applications ---------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.accounts',
    'apps.events',
    'apps.gallery',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# --- Database --------------------------------------------------------------
# SQLite par défaut pour le développement. Définir DATABASE_URL dans .env
# (ex: postgres://user:password@localhost:5432/kps_studio) pour basculer vers
# PostgreSQL sans changer le code.

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# --- Auth --------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'events:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'


# --- Internationalization --------------------------------------------------

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True


# --- Static & media files ----------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Email -------------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# --- Règles métier KPS Studio / PhotoShare ---------------------------------

EVENT_DEFAULT_EXPIRATION_DAYS = int(os.environ.get('EVENT_DEFAULT_EXPIRATION_DAYS', 15))
PURGE_AFTER_EXPIRATION_DAYS = int(os.environ.get('PURGE_AFTER_EXPIRATION_DAYS', 15))

MAX_PHOTO_SIZE_MB = 20
MAX_PHOTOS_PER_UPLOAD = 50
# Une requête d'upload multiple peut contenir jusqu'à MAX_PHOTOS_PER_UPLOAD fichiers de MAX_PHOTO_SIZE_MB chacun.
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_PHOTO_SIZE_MB * MAX_PHOTOS_PER_UPLOAD * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_PHOTO_SIZE_MB * 1024 * 1024

# --- Sécurité (production) --------------------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
