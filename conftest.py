"""Project-wide pytest fixtures."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from rest_framework.test import APIClient

from apps.users.tests.factories import SuperUserFactory, UserFactory

User = get_user_model()


@pytest.fixture
def user(db):
    """A plain, active user."""
    return UserFactory()


@pytest.fixture
def superuser(db):
    """A superuser (has all permissions)."""
    return SuperUserFactory()


@pytest.fixture
def user_with_crm_perms(db):
    """A user holding all user-management permissions (for CRM views)."""
    account = UserFactory(is_staff=True)
    perms = Permission.objects.filter(
        content_type__app_label="users",
        codename__in=["view_user", "add_user", "change_user", "delete_user"],
    )
    account.user_permissions.add(*perms)
    return account


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def auth_client(user) -> APIClient:
    """DRF API client authenticated as ``user``."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def web_client(user_with_crm_perms) -> Client:
    """Django test client logged in via session as a CRM-permitted user."""
    client = Client()
    client.force_login(user_with_crm_perms)
    return client
