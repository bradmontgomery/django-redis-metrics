VERSION = "2.1.0"
__version__ = VERSION

try:
    from .utils import gauge, metric, set_metric  # NOQA
except ImportError:  # pragma: no cover
    pass  # pragma: no cover

default_app_config = 'redis_metrics.apps.RedisMetricsConfig'
