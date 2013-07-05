import datetime
import random
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
    """Yields a generator of datetime.date objects for the past ``num`` days"""
    today = datetime.date.today()
    return (today - datetime.timedelta(days=d) for d in range(num))


def generate_test_metrics(slug='test-metric', num=100, randomize=False):
    """Generate some dummy (but increasing) metrics for the given ``slug`` and
    the past ``num`` days.

    If ``randomize`` is True, the metrics will be random integers.

    """
    _r = get_r()
    i = 100
    for date in _dates(num):
        for key in _r._build_keys(slug, date=date):
            # The following is normally done in _r.metric, but we're adding
            # metrics for past days here, so this is duplicate code.
            _r.r.sadd(_r._metric_slugs_key, key)  # keep track of the keys
            if randomize:
                random.seed()
                _r.r.incr(key, random.randint(0, i + 100))
            else:
                _r.r.incr(key, i)  # incr the key an increasing number of times
        i += 100


def delete_test_metrics(slug='test-metric', num=100):
    """Deletes the metrics created by ``generate_test_metrics``."""
    _r = get_r()
    for date in _dates(num):
        keys = _r._build_keys(slug, date=date)
        _r.r.srem(_r._metric_slugs_key, *keys)  # remove metric slugs
        _r.r.delete(*keys)  # delete the metrics
