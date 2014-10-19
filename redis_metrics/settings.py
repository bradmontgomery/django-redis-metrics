"""
This module contains the settings for this app. We'll attempt to pull values
from django's settings, falling back to the default values.
"""
from django.conf import settings


class AppSettings(object):
    """This application-specific settings class will acts just like a
    dictionary or an object. It provides access to settings values via:

        app_settings['REDIS_METRICS_HOST']

    or as attribute values:

        app_settings.REDIS_METRICS_HOST

    On access, we'll first try to look up values in Django's settings, and
    if the setting is not found there, we'll provide a default value.
    """

    # list of (setting name, default value)
    _default_settings = {
        'REDIS_METRICS_HOST': 'localhost',
        'REDIS_METRICS_PORT': 6379,
        'REDIS_METRICS_DB': 0,
        'REDIS_METRICS_PASSWORD': None,
        'REDIS_METRICS_SOCKET_TIMEOUT': None,
        'REDIS_METRICS_SOCKET_CONNECTION_POOL': None,
        'REDIS_METRICS_MIN_GRANULARITY': 'daily',
        'REDIS_METRICS_MAX_GRANULARITY': 'yearly',
    }

    def __getattr__(self, name):
        """Access settings as an attribute."""
        try:
            return self[name]
        except KeyError as e:
            # Failed attribute access should raise an AttributeError
            raise AttributeError(e)

    def __getitem__(self, key):
        """Access settings as a dictionary key."""
        return getattr(settings, key, self._default_settings[key])


app_settings = AppSettings()


# All possible granularity values.
GRANULARITIES = ['seconds', 'minutes', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']


# The Redis metric key and date formatting patterns for each key, by granularity
METRIC_KEY_PATTERNS = {
    "seconds": {"key": "m:{0}:s:{1}", "date_format": "%Y-%m-%d-%H-%M-%S"},
    "minutes": {"key": "m:{0}:i:{1}", "date_format": "%Y-%m-%d-%H-%M"},
    "hourly": {"key": "m:{0}:h:{1}", "date_format": "%Y-%m-%d-%H"},
    "daily": {"key": "m:{0}:{1}", "date_format": "%Y-%m-%d"},
    "weekly": {"key": "m:{0}:w:{1}", "date_format": "%Y-%U"},
    "monthly": {"key": "m:{0}:m:{1}", "date_format": "%Y-%m"},
    "yearly": {"key": "m:{0}:y:{1}", "date_format": "%Y"},
}
