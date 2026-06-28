"""Reusable view mixins for the server-rendered web UI."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpRequest


class StaffRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Require an authenticated user with explicit permissions.

    Subclasses set ``permission_required``. Combines authentication and
    authorization so CRM views need only one mixin.
    """


class HtmxResponseMixin:
    """Helper to branch templates for HTMX (partial) vs full-page requests.

    Set ``partial_template_name`` on the view; when the request carries the
    ``HX-Request`` header, that partial is rendered instead of the full page.
    """

    partial_template_name: str | None = None
    template_name: str | None = None

    request: HttpRequest

    def get_template_names(self) -> list[str]:
        if self.partial_template_name and self.request.headers.get("HX-Request"):
            return [self.partial_template_name]
        # Fall back to the standard resolution provided by the parent view.
        return super().get_template_names()  # type: ignore[misc]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["is_htmx"] = bool(self.request.headers.get("HX-Request"))
        return context
