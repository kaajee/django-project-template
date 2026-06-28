"""Development settings: local convenience, relaxed security."""

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104  # nosec B104

# Console email backend so verification/reset emails print to the terminal.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Developer tooling.
INSTALLED_APPS += ["django_extensions", "debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(  # noqa: F405
    0, "debug_toolbar.middleware.DebugToolbarMiddleware"
)
INTERNAL_IPS = ["127.0.0.1"]

# Don't enforce email verification while developing locally.
ACCOUNT_EMAIL_VERIFICATION = "optional"

# Allow any localhost origin to talk to the API from a dev frontend.
CORS_ALLOWED_ORIGIN_REGEXES = [r"^http://localhost:\d+$", r"^http://127\.0\.0\.1:\d+$"]
