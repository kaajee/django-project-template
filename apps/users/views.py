"""User API views."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers

from apps.users.models import User
from apps.users.serializers import UserSerializer, UserUpdateSerializer


@extend_schema(tags=["users"])
class MeView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the currently authenticated user."""

    def get_object(self) -> User:
        return self.request.user  # type: ignore[return-value]

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer
