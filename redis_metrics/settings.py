"""
This module contains the settings for this app. We'll attempt to pull values
from django's settings, falling back to the default values.
"""
from django.conf import settings


app_settings = {
    'REDIS_METRICS_HOST': getattr(settings, 'REDIS_METRICS_HOST', 'localhost'),
    'REDIS_METRICS_PORT': int(getattr(settings, 'REDIS_METRICS_PORT', 6379)),
    'REDIS_METRICS_DB': int(getattr(settings, 'REDIS_METRICS_DB', 0)),
    'REDIS_METRICS_PASSWORD': getattr(settings, 'REDIS_METRICS_PASSWORD', None),
    'REDIS_METRICS_SOCKET_TIMEOUT': getattr(
        settings, 'REDIS_METRICS_SOCKET_TIMEOUT', None
    ),
    'REDIS_METRICS_SOCKET_CONNECTION_POOL': getattr(
        settings, 'REDIS_METRICS_SOCKET_CONNECTION_POOL', None
    ),
}
