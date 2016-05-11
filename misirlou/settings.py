"""
Django settings for misirlou project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = []

# Use these keys to auto-configure the project settings for the deployment env.
SETTING_TYPE = None
if BASE_DIR == "/srv/webapps/musiclibs/dev":
    SETTING_TYPE = "dev"
if BASE_DIR == "/srv/webapps/musiclibs/prod":
    SETTING_TYPE = "prod"

# If a deployment SETTING_TYPE is chosen, configure as follows.
if SETTING_TYPE:
    # SSL settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

    # Passwords stored in un-committed text files.
    with open("/srv/webapps/musiclibs/configs/{}_secret_key.txt") as f:
        SECRET_KEY = f.read().strip()
    with open("/srv/webapps/musiclibs/configs/db_password.txt") as f:
        DB_PASS = f.read().strip()

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'misirlou',
    'rest_framework',
    'django_extensions',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'misirlou.urls'

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

WSGI_APPLICATION = 'misirlou.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# Use a
if SETTING_TYPE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '{}_musiclibs'.format(SETTING_TYPE),
            'USER': 'musiclibs',
            'PASSWORD': DB_PASS,
            'HOST': 'localhost',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'misirlou.db'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }


# Solr settings
SOLR_SERVER = "http://localhost:8983/solr/misirlou/"
SOLR_TEST = "http://localhost:8983/solr/misirlou_test/"

# Metadata mappings
reverse_map = {
    'title': ['title', 'titles', 'title(s)', 'titre'],
    'author': ['author', 'authors', 'author(s)'],
    'date': ['date', 'period', 'publication date'],
    'location': ['location'],
    'language': ['language'],
    'repository': ['repository']
}

SOLR_MAP = {}
for k, v in reverse_map.items():
    for vi in v:
        SOLR_MAP[vi] = k

# Status codes
ERROR = -1
SUCCESS = 0
PROGRESS = 1

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ('js', os.path.join(BASE_DIR, 'misirlou/frontend/js')),
)

DEBUG_CLIENT_SIDE = False

# Celery Settings
# ===============
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'redis://localhost/1'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_REDIS_MAX_CONNECTIONS = 1000
CELERY_TIMEZONE = 'UTC'

# Route celery settings for different configs.
if SETTING_TYPE:
    CELERY_QUEUE_DICT = {'queue': '{}_musiclibs'.format(SETTING_TYPE)}
    CELERY_ROUTES = {'misirlou.tasks.import_single_manifest': CELERY_QUEUE_DICT,
                     'misirlou.tasks.get_document': CELERY_QUEUE_DICT,
                     'misirlou.tasks.commit_solr': CELERY_QUEUE_DICT}
    num = 1 if SETTING_TYPE == 'prod' else 2
    CELERY_RESULT_BACKEND = 'redis://localhost/{}'.format(num)

CELERYBEAT_SCHEDULE = {
    'commit-solr-30-seconds': {
        'task': 'misirlou.tasks.commit_solr',
        'schedule': timedelta(seconds=30),
    },
}

try:
    from misirlou.local_settings import *
except ImportError:
    pass
