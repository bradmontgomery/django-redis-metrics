__version__ = "0.5.1"

try:
    from .utils import gauge, metric
    # placate pyflakes
    assert gauge
    assert metric
except ImportError:  # pragma: no cover
    pass  # pragma: no cover
