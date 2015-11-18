from __future__ import unicode_literals
import random

from datetime import datetime, timedelta
from .models import R


_redis_model = None


def get_r():
    global _redis_model
    if not _redis_model:
        _redis_model = R()
    return _redis_model


def set_metric(slug, value, category=None, expire=None, date=None):
    """Create/Increment a metric."""
    get_r().set_metric(slug, value, category=category, expire=expire, date=date)


def metric(slug, num=1, category=None, expire=None, date=None):
    """Create/Increment a metric."""
    get_r().metric(slug, num=num, category=category, expire=expire, date=date)


def gauge(slug, current_value):
    """Set a value for a Gauge"""
    get_r().gauge(slug, current_value)


def generate_test_metrics(slug='test-metric', num=100, randomize=False,
                          cap=None, increment_value=100):
    """Generate some dummy metrics for the given ``slug``.

    * ``slug`` -- the Metric slug
    * ``num`` -- Number of days worth of metrics (default is 100)
    * ``randomize`` -- Generate random metric values (default is False)
    * ``cap`` -- If given, cap the maximum metric value.
    * ``increment_value`` -- The amount by which we increment metrics on
      subsequent days. If ``randomize`` is True, this value is used to
      generate a ceiling for random values.

    NOTE: This only generates metrics for daily and larger granularities.

    """
    r = get_r()
    i = 0
    if randomize:
        random.seed()

    r.r.sadd(r._metric_slugs_key, slug)  # Store the slug created.
    for date in r._date_range('daily', datetime.utcnow() - timedelta(days=num)):
        # Only keep the keys for daily and above granularities.
        keys = r._build_keys(slug, date=date)
        keys = [k for k in keys if k.split(":")[2] not in ['i', 's', 'h']]
        for key in keys:
            # The following is normally done in r.metric, but we're adding
            # metrics for past days here, so this is duplicate code.
            value = i
            if randomize:
                value = random.randint(0, i + increment_value)
            if cap and r.r.get(key) >= cap:
                value = 0  # Dont' increment this one any more.
            r.r.incr(key, value)
        i += increment_value


def delete_test_metrics(slug='test-metric', num=100):
    """Deletes the metrics created by ``generate_test_metrics``."""
    r = get_r()
    for date in r._date_range('daily', datetime.utcnow() - timedelta(days=num)):
        keys = r._build_keys(slug, date=date)
        r.r.srem(r._metric_slugs_key, slug)  # remove metric slugs
        r.r.delete(*keys)  # delete the metrics
