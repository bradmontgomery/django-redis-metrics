import random

from datetime import datetime, timedelta
from .models import R


_redis_model = None


def get_r():
    global _redis_model
    if not _redis_model:
        _redis_model = R()
    return _redis_model


def metric(slug, num=1, category=None, expire=None):
    """Create/Increment a metric."""
    get_r().metric(slug, num=num, category=category, expire=expire)


def gauge(slug, current_value):
    """Set a value for a Gauge"""
    get_r().gauge(slug, current_value)


def _dates(num):
    """Yields a generator of datetime objects for the past ``num`` days"""
    now = datetime.utcnow()
    return (now - timedelta(days=d) for d in range(num))


def generate_test_metrics(slug='test-metric', num=100, randomize=False, cap=None):
    """Generate some dummy metrics for the given ``slug``.

    * ``slug`` -- the Metric slug
    * ``num`` -- Number of days worth of metrics (default is 100)
    * ``randomize`` -- Generate random metric values (default is False)
    * ``cap`` -- If given, cap the maximum metric value.

    """
    _r = get_r()
    i = 100
    if randomize:
        random.seed()

    for date in _dates(num):
        for key in _r._build_keys(slug, date=date):
            # The following is normally done in _r.metric, but we're adding
            # metrics for past days here, so this is duplicate code.
            _r.r.sadd(_r._metric_slugs_key, key)  # keep track of the keys
            value = i
            if randomize:
                value = random.randint(0, i + 100)
            if cap and _r.r.get(key) >= cap:
                value = 0  # Dont' increment this one any more.
            _r.r.incr(key, value)

        i += 100


def delete_test_metrics(slug='test-metric', num=100):
    """Deletes the metrics created by ``generate_test_metrics``."""
    _r = get_r()
    for date in _dates(num):
        keys = _r._build_keys(slug, date=date)
        _r.r.srem(_r._metric_slugs_key, *keys)  # remove metric slugs
        _r.r.delete(*keys)  # delete the metrics
