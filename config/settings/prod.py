"""Production settings: security hardening + observability."""

from .base import *  # noqa: F403

# ---------------------------------------------------------------------------
# Fail loudly in production if required secrets are missing (no defaults).
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")  # noqa: F405
DATABASES = {"default": env.db("DATABASE_URL")}  # noqa: F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DJANGO_CONN_MAX_AGE", default=60)  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# ---------------------------------------------------------------------------
# HTTPS / transport security
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)  # noqa: F405
# Trust the X-Forwarded-Proto header set by the load balancer / reverse proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------------------
# Cookies & headers
# ---------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

# Email links built by allauth must use https.
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Structured JSON logs in production.
LOGGING["handlers"]["console"]["formatter"] = "json"  # type: ignore[index]  # noqa: F405

# ---------------------------------------------------------------------------
# Sentry (only when a DSN is configured)
# ---------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),  # noqa: F405
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", default="production"),  # noqa: F405
        release=env("SENTRY_RELEASE", default=None),  # noqa: F405
    )

# Datadog APM is enabled by running the process under `ddtrace-run` (see the
# Docker entrypoint), NOT by importing ddtrace here. This keeps tracing out of
# local/test runs and ensures it instruments before Django imports.
