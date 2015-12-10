"""
This module contains the settings for this app. We'll attempt to pull values
from django's settings, falling back to the default values.
"""
from __future__ import unicode_literals
from django.conf import settings

import warnings


class AppSettings(object):
    """This application-specific settings class will acts just like a
    dictionary or an object. It provides access to settings values via:

        app_settings['HOST']

    or as attribute values:

        app_settings.HOST

    On access, we'll first try to look up values in Django's settings, and
    if the setting is not found there, we'll provide a default value.
    """

    # list of (setting name, default value)
    _default_settings = {
        'CONNECTION_CLASS': None,
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': None,
        'SOCKET_TIMEOUT': None,
        'SOCKET_CONNECTION_POOL': None,
        'MIN_GRANULARITY': 'daily',
        'MAX_GRANULARITY': 'yearly',
        'MONDAY_FIRST_DAY_OF_WEEK': False,
    }

    # A mapping of our old settings names to the new name
    _old_settings = {
        'CONNECTION_CLASS': 'REDIS_METRICS_CONNECTION_CLASS',
        'HOST': 'REDIS_METRICS_HOST',
        'PORT': 'REDIS_METRICS_PORT',
        'DB': 'REDIS_METRICS_DB',
        'PASSWORD': 'REDIS_METRICS_PASSWORD',
        'SOCKET_TIMEOUT': 'REDIS_METRICS_SOCKET_TIMEOUT',
        'SOCKET_CONNECTION_POOL': 'REDIS_METRICS_SOCKET_CONNECTION_POOL',
        'MIN_GRANULARITY': 'REDIS_METRICS_MIN_GRANULARITY',
        'MAX_GRANULARITY': 'REDIS_METRICS_MAX_GRANULARITY',
        'MONDAY_FIRST_DAY_OF_WEEK': 'REDIS_METRICS_MONDAY_FIRST_DAY_OF_WEEK',
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
        try:
            # First try the project settings...
            return settings.REDIS_METRICS[key]
        except (AttributeError, KeyError):
            pass

        try:
            # Then, try one of the old settings keys.
            old_key = self._old_settings[key]
            msg = "{} is deprecated, use REDIS_METRICS['{}'] instead."
            warnings.warn(msg.format(old_key, key), DeprecationWarning, stacklevel=2)
            return getattr(settings, old_key)
        except AttributeError:
            pass

        # Fall back to the app's defaults.
        return getattr(settings, key, self._default_settings[key])


app_settings = AppSettings()


# All possible granularity values.
GRANULARITIES = ['seconds', 'minutes', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']
