from .models import R


_r = R()


def metric(slug, num=1, **kwargs):
    """Create/Increment a metric."""
    _r.metric(slug, num)


def gague(slug, current_value):
    """Set a value for a Guage"""
    _r.gague(slug, current_value)
