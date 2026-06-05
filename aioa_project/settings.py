"""
Django settings for aioa_project project.
Utilise python-decouple pour lire les variables depuis .env
"""

import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════════
# SÉCURITÉ — chargé depuis .env, jamais en dur
# ══════════════════════════════════════════════════════════════
SECRET_KEY = config('SECRET_KEY')
DEBUG       = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# ══════════════════════════════════════════════════════════════
# CLÉ API MISTRAL
# ══════════════════════════════════════════════════════════════
MISTRAL_API_KEY = config('MISTRAL_API_KEY', default='')

# ══════════════════════════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════════════════════════
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'orientation',
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

ROOT_URLCONF = 'aioa_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aioa_project.wsgi.application'

# ══════════════════════════════════════════════════════════════
# BASE DE DONNÉES — MySQL en dev, PostgreSQL en prod via .env
# ══════════════════════════════════════════════════════════════
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.mysql')

if DB_ENGINE == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     config('DB_NAME',     default='aioa_db'),
            'USER':     config('DB_USER',     default='aioa_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST':     config('DB_HOST',     default='localhost'),
            'PORT':     config('DB_PORT',     default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME':     config('DB_NAME',     default='aioa_bac_db'),
            'USER':     config('DB_USER',     default='root'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST':     config('DB_HOST',     default='127.0.0.1'),
            'PORT':     config('DB_PORT',     default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# ══════════════════════════════════════════════════════════════
# SESSIONS
# ══════════════════════════════════════════════════════════════
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE   = not DEBUG  # True en prod (HTTPS)
SESSION_ENGINE          = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE      = 60 * 60 * 8  # 8 heures

# ══════════════════════════════════════════════════════════════
# SÉCURITÉ HTTP (activé en production seulement)
# ══════════════════════════════════════════════════════════════
if not DEBUG:
    SECURE_HSTS_SECONDS        = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT        = True
    CSRF_COOKIE_SECURE         = True
    X_FRAME_OPTIONS            = 'DENY'

# ══════════════════════════════════════════════════════════════
# UPLOADS
# ══════════════════════════════════════════════════════════════
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL  = '/media/'
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_UPLOAD_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']

# ══════════════════════════════════════════════════════════════
# INTERNATIONALISATION
# ══════════════════════════════════════════════════════════════
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Abidjan'
USE_I18N = True
USE_TZ   = True

# ══════════════════════════════════════════════════════════════
# FICHIERS STATIQUES
# ══════════════════════════════════════════════════════════════
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class':     'logging.handlers.RotatingFileHandler',
            'filename':  BASE_DIR / 'logs' / 'aioa.log',
            'maxBytes':  5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'orientation': {
            'handlers':  ['console', 'file'],
            'level':     'INFO' if not DEBUG else 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
    },
}