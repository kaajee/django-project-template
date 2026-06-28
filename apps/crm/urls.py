"""CRM web UI URLs (mounted under /crm/)."""

from django.urls import path

from apps.crm import views

app_name = "crm"

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/new/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),
]
