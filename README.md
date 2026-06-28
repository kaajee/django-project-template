# Django Project Template

A production-grade, opinionated **hybrid Django template**: a Django REST
Framework JSON API **and** a server-rendered web UI (HTMX + Bootstrap 5),
sharing one user model. It ships with authentication, background tasks,
observability, and a full development/CI toolchain pre-configured.

A **CRM-style user-management UI** is included as the worked example of the
template/web side.

## Stack

| Area | Choice |
|------|--------|
| Framework | Django 5.2 (LTS), Python 3.13 |
| API | Django REST Framework + drf-spectacular (OpenAPI 3) |
| Web UI | Django templates + HTMX + Bootstrap 5 + crispy-forms |
| Auth | django-allauth — **session** login (web) + **headless JWT** (API), custom email user model, MFA, social login |
| Tooling | uv (deps), ruff (lint/format), mypy (types) |
| Data | PostgreSQL (psycopg 3), Redis (cache + broker) |
| Async | Celery worker + beat (`django-celery-beat`) |
| Observability | Sentry, Datadog APM (ddtrace), structured JSON logs |
| Tests | pytest + pytest-django + factory_boy + coverage (≥85%) |
| Delivery | Docker (multi-stage, uv) + docker-compose + GitHub Actions CI |

## Quick start (local, no Docker)

```bash
cp .env.example .env          # set DJANGO_SECRET_KEY at minimum
make install                  # uv sync + pre-commit hooks
make migrate
make superuser
make run                      # http://127.0.0.1:8000/
```

The dev settings default to SQLite if `DATABASE_URL` is unset, so you can run
immediately; point `DATABASE_URL` at PostgreSQL when you want parity with prod.

## Quick start (Docker)

```bash
cp .env.example .env
make up                       # builds + starts web, db, redis, worker, beat
```

## Key URLs

| URL | Purpose |
|-----|---------|
| `/crm/users/` | CRM user-management UI (login required) |
| `/accounts/login/` | Web session login (allauth) |
| `/_allauth/` | Headless auth JSON API (register/verify/social/MFA, issues JWTs) |
| `/api/v1/me/` | Example REST endpoint (JWT-protected) |
| `/api/docs/` · `/api/redoc/` | Swagger / Redoc (offline sidecar assets) |
| `/api/schema/` | OpenAPI 3 schema |
| `/healthz/` · `/readyz/` | Liveness / readiness probes |
| `/admin/` | Django admin |

## Authentication

There are two auth surfaces over **one** custom email-based user model:

- **Web UI** uses allauth's standard template views and **session** cookies.
  CRM views are gated with `LoginRequiredMixin` + per-action permissions.
- **API** uses allauth **headless** mode, which handles registration, email
  verification, social login, and MFA over JSON at `/_allauth/`, and **issues
  the JWTs** used to protect DRF endpoints.

API login flow (app client):

```bash
# 1. Authenticate via headless; the JWTs come back in the response `meta`.
curl -X POST http://localhost:8000/_allauth/app/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"..."}'

# 2. Call protected endpoints with the access token.
curl http://localhost:8000/api/v1/me/ -H 'Authorization: Bearer <access_token>'
```

JWTs are HS256 (signed with `SECRET_KEY`) by default — zero config. For
asymmetric keys, set `HEADLESS_JWT_ALGORITHM=RS256` and provide a PEM
`HEADLESS_JWT_PRIVATE_KEY`.

> `djangorestframework-simplejwt` is installed and there are commented
> integration points in `config/settings/base.py` and `config/urls.py` if you
> prefer simplejwt to issue tokens instead. allauth is the default issuer.

## Settings

`config/settings/` is split into `base`, `dev`, `prod`, and `test`. Choose one
via `DJANGO_SETTINGS_MODULE` (defaults: `dev` locally, `prod` in the container,
`test` under pytest/mypy). All deployment-specific values are read from the
environment — see `.env.example`.

`prod.py` re-reads `DJANGO_SECRET_KEY` and `DATABASE_URL` with no defaults, so
production fails loudly if they are missing, and enables HTTPS/HSTS/secure
cookies, Sentry, and JSON logging.

## Observability

- **Sentry** initialises in `prod.py` only when `SENTRY_DSN` is set.
- **Datadog APM** is enabled by running the process under `ddtrace-run`; the
  container entrypoint does this automatically when `DD_TRACE_ENABLED=true`.

## Common commands

```bash
make lint        # ruff check + format check
make fmt         # ruff auto-fix + format
make typecheck   # mypy
make test        # pytest + coverage
make security    # bandit + pip-audit
make check-deploy
make ci          # lint + typecheck + test + security
```

## Project structure

```
django-project-template/
├── config/                       # Django project package (rename-free, generic)
│   ├── settings/
│   │   ├── base.py               # shared settings (12-factor, env-driven)
│   │   ├── dev.py                # local dev: DEBUG, console email, toolbar
│   │   ├── prod.py               # hardening, Sentry, JSON logs (fails loud)
│   │   └── test.py               # fast hermetic settings (pytest + mypy)
│   ├── celery.py                 # Celery app (autodiscovers tasks)
│   ├── urls.py                   # root URLconf (web + API + auth + docs)
│   ├── wsgi.py  asgi.py          # server entrypoints
│   └── __init__.py               # imports celery_app
│
├── apps/
│   ├── users/                    # custom email user model + REST API
│   │   ├── models.py             # User (email login, no username)
│   │   ├── managers.py           # email-based UserManager
│   │   ├── serializers.py        # UserSerializer / UserUpdateSerializer
│   │   ├── views.py  urls.py     # /api/v1/me/ endpoint
│   │   ├── admin.py              # email-tuned admin
│   │   ├── migrations/0001_initial.py
│   │   └── tests/                # factories.py + test_users.py
│   │
│   ├── crm/                      # server-rendered CRM (web UI example)
│   │   ├── views.py              # User CRUD (LoginRequired + perms, HTMX)
│   │   ├── forms.py              # crispy-bootstrap5 create/edit forms
│   │   ├── urls.py
│   │   └── tests/test_crm.py
│   │
│   └── common/                   # cross-cutting "core" utilities
│       ├── models.py             # TimeStamped / UUID abstract bases
│       ├── pagination.py         # DefaultPagination
│       ├── exceptions.py         # custom DRF error envelope
│       ├── health.py             # /healthz + /readyz probes
│       ├── mixins.py             # HtmxResponseMixin, StaffRequiredMixin
│       └── tests/test_health.py
│
├── templates/
│   ├── base.html                 # Bootstrap 5 + HTMX layout
│   ├── allauth/layouts/base.html # allauth pages → project chrome
│   ├── crm/                      # user_list / form / detail / delete
│   │   └── partials/             # _user_table, _user_row (HTMX fragments)
│   └── includes/_messages.html
│
├── static/css/app.css            # project styles (collected by WhiteNoise)
├── docker/entrypoint.sh          # web/worker/beat dispatch + ddtrace gating
├── tests/                        # project-level test package
├── conftest.py                   # shared pytest fixtures (root → all apps)
├── manage.py
│
├── pyproject.toml                # deps + ruff/mypy/pytest/coverage/bandit config
├── uv.lock                       # pinned dependency lockfile
├── .python-version               # 3.13
├── .env.example                  # documented environment variables
├── .pre-commit-config.yaml       # ruff, mypy, bandit, hygiene hooks
├── Dockerfile                    # multi-stage, uv-based, non-root
├── docker-compose.yml            # web, db, redis, worker, beat (healthchecks)
├── docker-compose.override.yml   # local dev overrides (bind mounts, autoreload)
├── Makefile                      # install/run/lint/test/ci/up shortcuts
├── .github/workflows/ci.yml      # lint · type-check · test · security
├── README.md  LICENSE
```

## License

Released under the [MIT License](LICENSE).
