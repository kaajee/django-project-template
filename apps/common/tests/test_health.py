"""Tests for health probes and the custom exception handler."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_liveness(client):
    resp = client.get(reverse("healthz"))
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readiness(client):
    resp = client.get(reverse("readyz"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["cache"] == "ok"


def test_exception_handler_envelope(api_client):
    """A 401 from the API is wrapped in the standard error envelope."""
    resp = api_client.get(reverse("users:me"))
    assert resp.status_code == 401
    assert "error" in resp.data
    assert resp.data["error"]["status_code"] == 401
