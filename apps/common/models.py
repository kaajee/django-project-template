"""Reusable abstract base models."""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Adds self-updating ``created_at`` and ``updated_at`` fields."""

    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Uses a non-sequential UUID primary key (good for public identifiers)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class UUIDTimeStampedModel(UUIDModel, TimeStampedModel):
    """Convenience base combining a UUID primary key with timestamps."""

    class Meta:
        abstract = True
