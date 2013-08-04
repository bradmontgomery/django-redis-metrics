__version__ = "0.7.0"

try:
    from .utils import gauge, metric  # NOQA
except ImportError:  # pragma: no cover
    pass  # pragma: no cover
