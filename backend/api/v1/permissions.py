from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticatedOrReadOnly,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class ModifiPerm(BasePermission):
    """Разрешает чтение всем, а изменение только
       авторизованным пользователям"""

    def has_permission(self, request, view):
        return (
            isinstance(request.user, User)
            or request.method in SAFE_METHODS
            )


class OnlyAuthPerm(BasePermission):
    """Разрешает чтение, изменение и удаление только
       авторизованным пользователям"""

    def has_permission(self, request, view):
        return isinstance(request.user, User)
