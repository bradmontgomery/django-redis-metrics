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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'redis_metrics',
]

REDIS_METRICS_HOST = 'localhost'
REDIS_METRICS_PORT = '6379'
REDIS_METRICS_DB = 0