"""User API URLs (mounted under /api/v1/)."""

from django.urls import path

from apps.users.views import MeView

app_name = "users"

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
]
