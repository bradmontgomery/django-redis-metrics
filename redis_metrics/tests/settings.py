import os

# Django 1.7 needs different settings than 1.4 - 1.6; see below.
DJANGO_VERSION = os.environ.get('DJANGO', '')

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

if DJANGO_VERSION.startswith("1.7"):
    # Django 1.7 removed a bunch of defaults, but we currently require Session and
    # authentication (since we have a few restricted views).
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
    'redis_metrics',
]

REDIS_METRICS_HOST = 'localhost'
REDIS_METRICS_PORT = '6379'
REDIS_METRICS_DB = 0
REDIS_METRICS_PASSWORD = None
REDIS_METRICS_SOCKET_TIMEOUT = None
REDIS_METRICS_SOCKET_CONNECTION_POOL = None
