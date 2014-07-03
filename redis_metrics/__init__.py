__version__ = "0.8.0a"

try:
    from .utils import gauge, metric  # NOQA
except ImportError:  # pragma: no cover
    pass  # pragma: no cover
