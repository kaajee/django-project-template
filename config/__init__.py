"""Project package.

Import the Celery app so that the ``@shared_task`` decorator picks up the
configured app when Django starts.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
