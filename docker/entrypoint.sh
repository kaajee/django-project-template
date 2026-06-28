#!/usr/bin/env bash
# Container entrypoint. Dispatches on the first argument:
#   web    -> migrate + collectstatic, then gunicorn
#   worker -> celery worker
#   beat   -> celery beat (DatabaseScheduler)
# Datadog APM wraps the process via `ddtrace-run` only when DD_TRACE_ENABLED=true.
set -euo pipefail

run() {
  if [ "${DD_TRACE_ENABLED:-false}" = "true" ]; then
    exec ddtrace-run "$@"
  else
    exec "$@"
  fi
}

case "${1:-web}" in
  web)
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    run gunicorn config.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers "${GUNICORN_WORKERS:-3}" \
      --timeout "${GUNICORN_TIMEOUT:-60}" \
      --access-logfile - \
      --error-logfile -
    ;;
  worker)
    run celery -A config worker -l "${CELERY_LOG_LEVEL:-info}"
    ;;
  beat)
    run celery -A config beat -l "${CELERY_LOG_LEVEL:-info}" \
      --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ;;
  *)
    exec "$@"
    ;;
esac
