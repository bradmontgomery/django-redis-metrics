#!/usr/bin/env python
import sys

try:
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        ROOT_URLCONF="redis_metrics.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "user_sessions",
            "django_redis",
            "django.contrib.sessions",
            "redis_metrics",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        SECRET_KEY="notasecret",
        NOSE_ARGS=["-s"],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": ["redis_metrics/templatetags", "redis_metrics/templates"],
            }
        ],
    )
    django.setup()
except ImportError:
    raise ImportError("To fix this error, run: pip install -r requirements.txt")


if __name__ == "__main__":
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["redis_metrics.tests"])
    sys.exit(bool(failures))
