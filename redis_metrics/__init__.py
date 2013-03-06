__version__ = "0.3.0"

try:
    from .utils import gauge, metric
    # placate pyflakes
    assert gauge
    assert metric
except ImportError:
    pass
