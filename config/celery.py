"""Celery application.

The app reads configuration from Django settings using the ``CELERY_`` prefix
(``namespace="CELERY"``) and autodiscovers ``tasks.py`` modules in each app.
"""

import os
from typing import Any

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self: Any) -> None:  # pragma: no cover - utility task
    """Print the request context; handy for verifying the worker is wired up."""
    print(f"Request: {self.request!r}")
