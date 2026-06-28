"""Liveness and readiness probes for containers / load balancers."""

from __future__ import annotations

from django.core.cache import cache
from django.db import connections
from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache


@never_cache
def liveness(request: HttpRequest) -> JsonResponse:
    """Process is up. Cheap; no external dependencies checked."""
    return JsonResponse({"status": "ok"})


@never_cache
def readiness(request: HttpRequest) -> JsonResponse:
    """Ready to serve traffic: database and cache are reachable."""
    checks: dict[str, str] = {}
    healthy = True

    try:
        connections["default"].cursor().execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 - report any failure mode
        checks["database"] = f"error: {exc}"
        healthy = False

    try:
        cache.set("readiness-probe", "1", timeout=5)
        checks["cache"] = "ok" if cache.get("readiness-probe") == "1" else "error"
        healthy = healthy and checks["cache"] == "ok"
    except Exception as exc:  # noqa: BLE001
        checks["cache"] = f"error: {exc}"
        healthy = False

    return JsonResponse(
        {"status": "ok" if healthy else "unavailable", "checks": checks},
        status=200 if healthy else 503,
    )
