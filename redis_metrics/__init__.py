__version__ = "0.2.0"

# Sigh. I want to be able to do this:
#   >>> from redis_metrics import metric
# BUT, that breaks setup (because setup reads the VERSION here), and
# the ``redis`` dependency hasn't yet been installed.
try:
    from .utils import gauge, metric
    # placate pyflakes
    assert gauge
    assert metric
except ImportError:
    pass
