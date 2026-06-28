# Django Project Template — Build Log

Hybrid Django template: DRF API + server-rendered web UI (HTMX + Bootstrap 5),
CRM user-management example. Plan: `~/.claude/plans/this-project-for-a-polished-wind.md`.

## Tasks
- [x] Scaffold project + pyproject.toml + deps (uv, ruff, mypy, pytest, coverage)
- [x] config/ package + settings split (base/dev/prod/test) + celery/urls/wsgi/asgi
- [x] apps.users custom email user model + manager + /me API + admin + migration
- [x] apps.common core utils (base models, pagination, exceptions, health, mixins)
- [x] Templates/static + DRF/spectacular + allauth (session + headless JWT) + CRM CRUD
- [x] Celery app + Sentry (prod) + Datadog (ddtrace entrypoint gating)
- [x] Tests + pre-commit + Docker (multi-stage uv) + compose + GitHub Actions CI + Makefile + docs
- [x] Verify: ruff, mypy, pytest, check --deploy, bandit, pip-audit, smoke test

## Review

### Outcome
A complete, verified, production-grade Django REST + web template.

### Verification results (all green)
- `ruff check` / `ruff format --check`: clean
- `mypy .`: no issues in 41 source files (pragmatic config: annotations enforced,
  Django/DRF generic CBVs not forced to carry type params)
- `pytest`: 19 passed, **86.79%** coverage (gate 85%)
- `manage.py check --deploy` (prod settings): no security issues
- `bandit`: no issues; `pip-audit`: no known vulnerabilities
- `collectstatic` (manifest storage): 175 files OK
- `spectacular` OpenAPI export: OK
- Live smoke test (test client): login/signup/swagger/redoc/schema = 200,
  `/crm/users/` = 302 (login required), `/api/v1/me/` = 401, headless config = 200

### Key decisions
- **Auth**: allauth is the single token issuer (HS256 JWT via `SECRET_KEY`,
  zero-config). Two surfaces: `/accounts/` (web session) + `/_allauth/` (headless
  API JWT). simplejwt installed but commented as an optional path.
- **Settings**: base/dev/prod/test. base has safe insecure defaults so settings
  import without `.env` (tests/mypy/dev); prod re-reads SECRET_KEY/DATABASE_URL
  with no defaults → fails loud.
- **mypy**: relaxed from `strict` to a curated config — strict mode is hostile to
  Django generic class-based views and would impose friction on template users.
- **pytest** bumped to 9.x to clear CVE-2025-71176.

### Notes / follow-ups for template users
- Set a real `DJANGO_SECRET_KEY` and PostgreSQL `DATABASE_URL` before deploy.
- Configure Google (or other) social provider credentials in admin/settings.
- `conftest.py` lives at repo root so fixtures are visible to all `apps/*` tests.
- Datadog tracing only activates when `DD_TRACE_ENABLED=true` (entrypoint).
