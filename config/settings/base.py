"""Base settings shared across all environments.

Environment-specific modules (``dev``, ``prod``, ``test``) import everything
from here with ``from .base import *`` and then override as needed.

Configuration is 12-factor: every deployment-specific value is read from the
environment via ``django-environ``. See ``.env.example`` for the full list.
"""

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
# BASE_DIR points at the repository root (two levels up from this file).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Read a local .env file if present (not committed). In production, real
# environment variables take precedence and the file may be absent.
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
# Safe insecure default keeps settings importable for tests / mypy / local dev.
# `prod.py` re-reads this from the environment with NO default, so production
# fails loudly if a real secret is not provided.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-CHANGEME-do-not-use-in-prod")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_celery_beat",
    "crispy_forms",
    "crispy_bootstrap5",
    # allauth: standard (template) views + headless (API) live side by side.
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.mfa",
    "allauth.headless",
]

LOCAL_APPS = [
    "apps.common",
    "apps.users",
    "apps.crm",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    # CORS must come before CommonMiddleware (and anything that can short-circuit).
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files in production right after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Required by django-allauth; must be last.
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database (PostgreSQL via DATABASE_URL)
# ---------------------------------------------------------------------------
# Default to local SQLite so settings import without env (tests/mypy/dev). Real
# deployments set DATABASE_URL to PostgreSQL; `prod.py` requires it explicitly.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DJANGO_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# ---------------------------------------------------------------------------
# Cache (Redis via django-redis)
# ---------------------------------------------------------------------------
CACHES = {
    "default": env.cache(
        "REDIS_URL",
        backend="django_redis.cache.RedisCache",
        default="redis://localhost:6379/0",
    ),
}

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Argon2 first; PBKDF2 retained for verifying any legacy hashes.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/crm/users/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ---------------------------------------------------------------------------
# django-allauth
# ---------------------------------------------------------------------------
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION", default="mandatory")
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# MFA (TOTP, recovery codes, WebAuthn/passkeys).
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes", "webauthn"]

# Headless API: enabled alongside the standard template views (HEADLESS_ONLY=False
# because we serve a server-rendered web UI). Tokens are issued by allauth itself.
HEADLESS_ONLY = False
HEADLESS_CLIENTS = ("app", "browser")
HEADLESS_TOKEN_STRATEGY = "allauth.headless.tokens.strategies.jwt.strategy.JWTTokenStrategy"  # nosec B105
# HS256 keeps the template zero-config: an empty private key falls back to
# SECRET_KEY. Switch to RS256 + HEADLESS_JWT_PRIVATE_KEY (PEM) for asymmetric keys.
HEADLESS_JWT_ALGORITHM = env("HEADLESS_JWT_ALGORITHM", default="HS256")
HEADLESS_JWT_PRIVATE_KEY = env("HEADLESS_JWT_PRIVATE_KEY", default="")
HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN = env.int("HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN", default=300)
HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN = env.int(
    "HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN", default=86400
)
HEADLESS_JWT_ROTATE_REFRESH_TOKEN = True
HEADLESS_JWT_AUTHORIZATION_HEADER_SCHEME = "Bearer"
# Where the frontend hosts pages allauth links to (email verification, resets...).
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": env(
        "FRONTEND_EMAIL_CONFIRM_URL", default="/accounts/confirm-email/{key}"
    ),
    "account_reset_password_from_key": env(
        "FRONTEND_RESET_PASSWORD_URL", default="/accounts/password/reset/key/{key}"
    ),
}

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # allauth-issued JWT is the primary API auth mechanism.
        "allauth.headless.contrib.rest_framework.authentication.JWTTokenAuthentication",
        # SessionAuthentication keeps the browsable API usable while logged in.
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.DefaultPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("DRF_THROTTLE_ANON", default="60/min"),
        "user": env("DRF_THROTTLE_USER", default="1000/min"),
    },
}

# Optional simplejwt path (NOT active by default; allauth issues the JWTs).
# Uncomment SIMPLE_JWT and the simplejwt auth class / token URLs to use it.
# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
#     "ROTATE_REFRESH_TOKENS": True,
# }
_ = timedelta  # keep the import available for the commented simplejwt config

# ---------------------------------------------------------------------------
# drf-spectacular (OpenAPI 3)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": env("API_TITLE", default="Django Project Template API"),
    "DESCRIPTION": "Production-grade hybrid Django API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# crispy-forms (Bootstrap 5)
# ---------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=env("REDIS_URL", default="redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=env("REDIS_URL", default="redis://localhost:6379/0")
)
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270
CELERY_TASK_ACKS_LATE = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="webmaster@localhost")

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Logging (structured JSON; trace-id injection works under ddtrace-run)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "console": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": env("DJANGO_LOG_FORMATTER", default="console"),
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("DJANGO_LOG_LEVEL", default="INFO"),
    },
}
