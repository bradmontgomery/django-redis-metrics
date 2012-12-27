from .models import R


_r = R()


def metric(slug, num=1, **kwargs):
    """Create/Increment a metric."""
    _r.metric(slug, num)


def gague(slug, current_value):
    """Set a value for a Guage"""
    _r.gague(slug, current_value)


def generate_test_metrics(slug='test-metric', num=100):
    """Generate some dummy (but increasing) metrics for the given ``slug`` and
    the past ``num`` days."""
    import datetime
    today = datetime.date.today()
    dates = (today - datetime.timedelta(days=d) for d in range(num))

    i = 1
    for date in dates:
        for key in _r._build_keys(slug, date=date):
            # The following is normally done in _r.metric, but we're adding
            # "old" metrics here, so this is duplicate code.
            _r.r.sadd(_r._metric_slugs_key, key)  # keep track of the keys
            for x in range(i):
                _r.r.incr(key)  # incr the key an increasing number of times
        i += 1
