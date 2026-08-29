from rest_framework.permissions import BasePermission, SAFE_METHODS

from .choices import Role


class IsStaff(BasePermission):
    """Manager or Admin only. No read-only carve-out."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.MANAGER, Role.ADMIN)
        )


class IsStaffOrReadOnly(BasePermission):
    """Any authenticated user can read (GET/HEAD/OPTIONS).
    Only Manager or Admin can create, update, or delete."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in (Role.MANAGER, Role.ADMIN)