"""Forms for the CRM user-management UI (rendered with crispy-bootstrap5)."""

from __future__ import annotations

from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.password_validation import validate_password

from apps.users.models import User


class _CrispyMixin(forms.ModelForm):
    """Attach a Bootstrap submit button via crispy-forms."""

    submit_label = "Save"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", self.submit_label, css_class="btn-primary"))


class UserCreateForm(_CrispyMixin):
    """Create a user with a validated password."""

    submit_label = "Create user"

    password = forms.CharField(widget=forms.PasswordInput, strip=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "is_staff"]

    def clean_password(self) -> str:
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserUpdateForm(_CrispyMixin):
    """Edit an existing user's profile and status (password unchanged here)."""

    submit_label = "Save changes"

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active", "is_staff"]
