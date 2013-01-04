VERSION = (0, 1, 2)

# Sigh. I want to be able to do this:
#   >>> from redis_metrics import metric
# BUT, that breaks setup (because setup reads the VERSION here), and
# the ``redis`` dependency hasn't yet been installed.
try:
    from .utils import gauge, metric
except ImportError:
    pass
