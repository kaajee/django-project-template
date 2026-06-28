"""Test settings: fast and hermetic (used by pytest and mypy/django-stubs)."""

from .base import *  # noqa: F403

# Provide safe defaults so the test suite never depends on a real .env.
SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105  # nosec B105
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Fast password hashing in tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# In-memory cache; no Redis needed for unit tests.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Run Celery tasks eagerly and surface exceptions.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Locmem email backend for assertions.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Don't require email verification in tests.
ACCOUNT_EMAIL_VERIFICATION = "none"

# Plain static storage: avoids needing a collectstatic manifest during tests.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
