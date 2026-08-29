from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.users.choices import Role

from .models import Task
from .permissions import TaskPermission
from .serializers import TaskSerializer

# Fields an Employee (non-staff) is allowed to change on a task assigned
# to them. Anything outside this set in a PATCH body is rejected.
EMPLOYEE_EDITABLE_FIELDS = {"status"}


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.select_related("department", "assigned_to")
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "priority",
        "department",
        "assigned_to",
    ]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "due_date",
        "priority",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == Role.EMPLOYEE:
            return queryset.filter(assigned_to=user)

        return queryset

    def perform_update(self, serializer):
        user = self.request.user

        if user.role == Role.EMPLOYEE:
            submitted_fields = set(self.request.data.keys())
            disallowed_fields = submitted_fields - EMPLOYEE_EDITABLE_FIELDS

            if disallowed_fields:
                allowed = ", ".join(sorted(EMPLOYEE_EDITABLE_FIELDS))
                raise PermissionDenied(
                    f"Employees can only update: {allowed}."
                )

        serializer.save()