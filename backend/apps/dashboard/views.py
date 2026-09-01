from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.choices import TaskPriority, TaskStatus
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from apps.users.models import User
from apps.users.permissions import IsStaff

RECENT_TASKS_LIMIT = 5
UPCOMING_DEADLINES_LIMIT = 5


class DashboardSummaryAPIView(APIView):
    """Organization-level dashboard metrics. Manager/Admin only - per the
    spec, viewing org-wide numbers (not just your own tasks) is a staff
    privilege, so this uses IsStaff rather than IsStaffOrReadOnly."""

    permission_classes = [IsStaff]

    def get(self, request):
        today = timezone.localdate()
        tasks = Task.objects.select_related("department", "assigned_to")

        tasks_by_status = {
            value: tasks.filter(status=value).count()
            for value, _ in TaskStatus.choices
        }
        tasks_by_priority = {
            value: tasks.filter(priority=value).count()
            for value, _ in TaskPriority.choices
        }

        overdue_tasks = tasks.exclude(status=TaskStatus.COMPLETED).filter(
            due_date__lt=today
        )

        recent_tasks = tasks.order_by("-created_at")[:RECENT_TASKS_LIMIT]
        upcoming_deadlines = (
            tasks.exclude(status=TaskStatus.COMPLETED)
            .filter(due_date__gte=today)
            .order_by("due_date")[:UPCOMING_DEADLINES_LIMIT]
        )

        return Response(
            {
                "total_employees": User.objects.filter(is_active=True).count(),
                "total_tasks": tasks.count(),
                "completed_tasks": tasks_by_status[TaskStatus.COMPLETED],
                "in_progress_tasks": tasks_by_status[TaskStatus.IN_PROGRESS],
                "pending_tasks": tasks_by_status[TaskStatus.PENDING],
                "overdue_tasks": overdue_tasks.count(),
                "tasks_by_status": tasks_by_status,
                "tasks_by_priority": tasks_by_priority,
                "recent_tasks": TaskSerializer(recent_tasks, many=True).data,
                "upcoming_deadlines": TaskSerializer(
                    upcoming_deadlines, many=True
                ).data,
            }
        )
        