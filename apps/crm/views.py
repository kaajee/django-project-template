"""CRM user-management views (server-rendered, HTMX-enhanced)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, QuerySet
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_ratelimit.decorators import ratelimit

from apps.common.mixins import HtmxResponseMixin
from apps.crm.forms import UserCreateForm, UserUpdateForm
from apps.users.models import User


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, HtmxResponseMixin, ListView):
    """Paginated, searchable user list.

    HTMX search requests (``HX-Request`` header) get only the table partial so
    the page filters live without a full reload.
    """

    model = User
    permission_required = "users.view_user"
    paginate_by = 25
    context_object_name = "users"
    template_name = "crm/user_list.html"
    partial_template_name = "crm/partials/_user_table.html"

    def get_queryset(self) -> QuerySet[User]:
        queryset = super().get_queryset()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("q", "")
        return context


class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    permission_required = "users.view_user"
    context_object_name = "object"
    template_name = "crm/user_detail.html"


@method_decorator(ratelimit(key="user_or_ip", rate="20/m", method="POST", block=True), name="post")
class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    permission_required = "users.add_user"
    template_name = "crm/user_form.html"
    success_url = reverse_lazy("crm:user-list")


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    permission_required = "users.change_user"
    template_name = "crm/user_form.html"
    success_url = reverse_lazy("crm:user-list")


class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    permission_required = "users.delete_user"
    template_name = "crm/user_confirm_delete.html"
    success_url = reverse_lazy("crm:user-list")
