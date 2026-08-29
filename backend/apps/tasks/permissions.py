from rest_framework.permissions import BasePermission

from apps.users.choices import Role


class TaskPermission(BasePermission):
    """
    - Manager/Admin: full access to all tasks (create, edit, delete, view all).
    - Employee: can only list/retrieve tasks assigned to them (queryset
      filtering happens in TaskViewSet.get_queryset) and can PATCH only the
      `status` field on their own tasks (enforced in
      TaskViewSet.perform_update). Employees cannot create, PUT, or delete
      tasks.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("POST", "PUT", "DELETE"):
            return request.user.role in (Role.MANAGER, Role.ADMIN)

        # GET / PATCH: allowed at the request level. Fine-grained scoping
        # for employees happens in the view (queryset filtering + the
        # editable-fields check on update).
        return True