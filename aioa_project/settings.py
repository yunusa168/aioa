"""
Django settings for aioa_project project.
"""

import os
from pathlib import Path
from decouple import config
os.environ['PATH'] += r';C:\poppler-26.02.0\Library\bin'

# ══════════════════════════════════════════
# CHEMINS
# ══════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════
# SÉCURITÉ
# ══════════════════════════════════════════
SECRET_KEY = 'django-insecure-@v)6th*3=6(vg&8t85ry*ur-f*-=_rxcj(4quz57axju3vcik$'
DEBUG = True
ALLOWED_HOSTS = []

# ══════════════════════════════════════════
# CLÉ API MISTRAL
# ══════════════════════════════════════════
MISTRAL_API_KEY = config('MISTRAL_API_KEY', default='')

# ══════════════════════════════════════════
# MEDIA (UPLOADS)
# ══════════════════════════════════════════
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 Mo
ALLOWED_UPLOAD_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']

# ══════════════════════════════════════════
# APPLICATIONS
# ══════════════════════════════════════════
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

# ══════════════════════════════════════════
# BASE DE DONNÉES
# ══════════════════════════════════════════
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aioa_bac_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ══════════════════════════════════════════
# VALIDATION MOTS DE PASSE
# ══════════════════════════════════════════
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ══════════════════════════════════════════
# INTERNATIONALISATION
# ══════════════════════════════════════════
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ══════════════════════════════════════════
# FICHIERS STATIQUES
# ══════════════════════════════════════════
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'