__version__ = "2.0.0"

try:
    from .utils import gauge, metric, set_metric  # NOQA
except ImportError:  # pragma: no cover
    pass  # pragma: no cover

default_app_config = 'redis_metrics.apps.RedisMetricsConfig'
