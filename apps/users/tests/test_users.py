"""Tests for the custom user model and the user API."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.users.tests.factories import UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(email="a@example.com", password="pw12345!")
        assert user.email == "a@example.com"
        assert user.check_password("pw12345!")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError, match="email address must be set"):
            User.objects.create_user(email="", password="pw")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="pw")
        assert admin.is_staff
        assert admin.is_superuser

    def test_email_is_normalized(self):
        user = User.objects.create_user(email="User@Example.COM", password="pw")
        assert user.email == "User@example.com"

    def test_full_name(self):
        user = UserFactory(first_name="Ada", last_name="Lovelace")
        assert user.full_name == "Ada Lovelace"
        assert str(user) == user.email


class TestMeEndpoint:
    def test_requires_authentication(self, api_client):
        resp = api_client.get(reverse("users:me"))
        assert resp.status_code == 401

    def test_returns_current_user(self, auth_client, user):
        resp = auth_client.get(reverse("users:me"))
        assert resp.status_code == 200
        assert resp.data["email"] == user.email

    def test_can_update_profile(self, auth_client, user):
        resp = auth_client.patch(reverse("users:me"), {"first_name": "Grace"})
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Grace"
