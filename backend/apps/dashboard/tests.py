from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.departments.models import Department
from apps.tasks.choices import TaskPriority, TaskStatus
from apps.tasks.models import Task
from apps.users.choices import Role
from apps.users.models import User


class DashboardSummaryTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.manager = User.objects.create_user(
            username="mgr", password="pass12345", role=Role.MANAGER
        )
        self.employee = User.objects.create_user(
            username="emp",
            password="pass12345",
            role=Role.EMPLOYEE,
            department=self.department,
        )

        today = timezone.localdate()

        Task.objects.create(
            title="Completed task",
            department=self.department,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.LOW,
            due_date=today - timedelta(days=5),
        )
        Task.objects.create(
            title="Overdue task",
            department=self.department,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            due_date=today - timedelta(days=1),
        )
        Task.objects.create(
            title="Upcoming task",
            department=self.department,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            due_date=today + timedelta(days=3),
        )

    def test_unauthenticated_cannot_access_dashboard(self):
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_sees_correct_summary_numbers(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get("/api/dashboard/summary/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data["total_tasks"], 3)
        self.assertEqual(data["completed_tasks"], 1)
        self.assertEqual(data["in_progress_tasks"], 1)
        self.assertEqual(data["pending_tasks"], 1)
        self.assertEqual(data["overdue_tasks"], 1)
        self.assertEqual(data["tasks_by_status"]["COMPLETED"], 1)
        self.assertEqual(data["tasks_by_priority"]["HIGH"], 1)
        self.assertEqual(len(data["upcoming_deadlines"]), 1)
        self.assertEqual(
            data["upcoming_deadlines"][0]["title"], "Upcoming task"
        )