"""Custom DRF exception handling for consistent error payloads."""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Wrap DRF's default handler with a stable error envelope.

    Returns ``{"error": {"status_code": int, "detail": ...}}`` so clients can
    rely on a consistent shape regardless of the underlying exception.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    response.data = {
        "error": {
            "status_code": response.status_code,
            "detail": response.data,
        }
    }
    return response
