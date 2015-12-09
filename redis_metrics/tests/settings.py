from __future__ import unicode_literals
import os

BASE_PATH = os.path.dirname(__file__)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SITE_ID = 1
DEBUG = True
SECRET_KEY = "secret"
ROOT_URLCONF = 'redis_metrics.tests.urls'
STATIC_URL = '/static/'
TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, 'templates'),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'redis_metrics',
]

REDIS_METRICS = {
    'HOST': 'localhost',
    'PORT': '6379',
    'DB': 0,
    'PASSWORD': None,
    'SOCKET_TIMEOUT': None,
    'SOCKET_CONNECTION_POOL': None,
}
