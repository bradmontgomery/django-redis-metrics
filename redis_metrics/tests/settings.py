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
TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, 'templates'),
)

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
REDIS_METRICS_PASSWORD = None
REDIS_METRICS_SOCKET_TIMEOUT = None
REDIS_METRICS_SOCKET_CONNECTION_POOL = None
