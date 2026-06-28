"""Tests for the CRM user-management web UI."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.tests.factories import UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestAccessControl:
    def test_list_requires_login(self, client):
        resp = client.get(reverse("crm:user-list"))
        assert resp.status_code == 302
        assert "/accounts/login/" in resp.url

    def test_list_forbidden_without_permission(self, client):
        # Logged in but lacking users.view_user -> 403.
        client.force_login(UserFactory())
        resp = client.get(reverse("crm:user-list"))
        assert resp.status_code == 403


class TestUserList:
    def test_lists_users(self, web_client):
        UserFactory(email="findme@example.com")
        resp = web_client.get(reverse("crm:user-list"))
        assert resp.status_code == 200
        assert b"findme@example.com" in resp.content

    def test_search_filters(self, web_client):
        UserFactory(email="alice@example.com")
        UserFactory(email="bob@example.com")
        resp = web_client.get(reverse("crm:user-list"), {"q": "alice"})
        assert b"alice@example.com" in resp.content
        assert b"bob@example.com" not in resp.content

    def test_htmx_request_returns_partial(self, web_client):
        resp = web_client.get(reverse("crm:user-list"), headers={"HX-Request": "true"})
        assert resp.status_code == 200
        # Partial only: the table wrapper, not the full HTML document.
        assert b'id="user-table"' in resp.content
        assert b'<nav class="navbar' not in resp.content


class TestUserCrud:
    def test_create_user(self, web_client):
        resp = web_client.post(
            reverse("crm:user-create"),
            {
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "S3curePass!",
                "is_active": "on",
            },
        )
        assert resp.status_code == 302
        assert User.objects.filter(email="new@example.com").exists()

    def test_update_user(self, web_client):
        target = UserFactory(first_name="Old")
        resp = web_client.post(
            reverse("crm:user-update", args=[target.pk]),
            {"email": target.email, "first_name": "Updated", "last_name": target.last_name},
        )
        assert resp.status_code == 302
        target.refresh_from_db()
        assert target.first_name == "Updated"

    def test_delete_user(self, web_client):
        target = UserFactory()
        resp = web_client.post(reverse("crm:user-delete", args=[target.pk]))
        assert resp.status_code == 302
        assert not User.objects.filter(pk=target.pk).exists()
