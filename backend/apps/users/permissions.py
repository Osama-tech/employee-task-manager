from rest_framework.permissions import BasePermission

from .models import Role


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == "GET":
            return True
            
        return request.user.role == Role.ADMIN